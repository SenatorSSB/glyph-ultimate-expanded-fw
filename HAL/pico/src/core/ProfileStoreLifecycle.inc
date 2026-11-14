// Included with ProfileStorePackage.inc. The original directory and Config are
// immutable preflight inputs. Only their dedicated candidates are compacted.
namespace {
bool LifecycleName(const char *name) {
    return name && *name && ProfileStoreNameValid(name,18);
}

void RemoveOwnedRgb(Config &config, ProfileStore::Directory &directory, unsigned rgb) {
    for(size_t i=rgb;i<config.rgb_configs_count;++i) config.rgb_configs[i-1]=config.rgb_configs[i];
    --config.rgb_configs_count;
    for(size_t i=0;i<config.game_mode_configs_count;++i) {
        auto &slot=config.game_mode_configs[i].rgb_config;
        if(slot>rgb)--slot;
    }
    for(size_t i=0;i<directory.count;++i)
        if(directory.entries[i].owned_rgb1>rgb)--directory.entries[i].owned_rgb1;
}

bool DeleteOwnedRow(Config &config, ProfileStore::Directory &directory, size_t entry_index,
                    uint32_t executing_id) {
    const auto target=directory.entries[entry_index];
    const size_t row=target.owned_row1-1;
    if(target.id==executing_id) return false;
    // A G6 receipt contains the exact historical index and ID. Do not rewrite
    // its meaning to make a compaction fit.
    if(config.profile_reference_token && (config.profile_reference_result_id==target.id ||
       config.profile_reference_result_mode_index>=row))return false;
    for(size_t i=0;i<config.communication_backend_configs_count;++i) {
        auto &destination=config.communication_backend_configs[i].default_mode_config;
        if(destination==target.owned_row1)return false;
        if(destination>target.owned_row1)--destination;
    }
    for(size_t i=0;i<config.game_mode_configs_count;++i) {
        const auto &other=config.game_mode_configs[i];
        if(i!=row && (other.ultimate_profile_id==target.id ||
           (target.owned_rgb1 && other.rgb_config==target.owned_rgb1)))return false;
    }
    for(size_t i=row+1;i<config.game_mode_configs_count;++i)
        config.game_mode_configs[i-1]=config.game_mode_configs[i];
    --config.game_mode_configs_count;
    if(target.owned_rgb1)RemoveOwnedRgb(config,directory,target.owned_rgb1);
    for(size_t i=entry_index+1;i<directory.count;++i)directory.entries[i-1]=directory.entries[i];
    --directory.count;
    for(size_t i=0;i<directory.count;++i)
        if(directory.entries[i].owned_row1>target.owned_row1)--directory.entries[i].owned_row1;
    return true;
}

bool ReadLifecycleRecord(NamespaceReader &reader,const ProfileStore::Entry &entry,
                         uint32_t incarnation,uint8_t old_sha[32]) {
    if(!RecordPath(prepared_record.path,sizeof(prepared_record.path),entry.id,entry.revision,false) ||
       reader.Extent(prepared_record.path,prepared_record.n)!=Probe::Present ||
       prepared_record.n>package_storage::kRecordMaxBytes ||
       !reader.Read(prepared_record.path,0,prepared_record.record,prepared_record.n) ||
       !RecordValid(prepared_record.record,prepared_record.n))return false;
    if(Get32(prepared_record.record+8)!=incarnation || Get32(prepared_record.record+12)!=entry.id ||
       Get32(prepared_record.record+16)!=entry.revision)return false;
    HashBytes(prepared_record.record,prepared_record.n,old_sha);
    return true;
}

__attribute__((noinline)) bool RetirePreviousPackageRecord() {
    const auto *intent=initialization_owner.intent;
    if(!RecordPath(prepared_record.path,sizeof(prepared_record.path),Get32(intent+68),Get32(intent+400),false))
        return false;
    size_t size=0;
    if(!package_call.storage->Probe(prepared_record.path,&size) || size>sizeof(prepared_record.record) ||
       !package_call.storage->CheckedRead(prepared_record.path,prepared_record.record,size,Kind::Record))return false;
    // The publication readback lease has ended before retirement.
    HashBytes(prepared_record.record,size,publication_readback);
    if(std::memcmp(publication_readback,intent+412,32))return false;
    package_call.phase=PackageWritePhase::Garbage;
    return CheckedStorage::Remove(prepared_record.path) &&
        CheckedStorage::Stat(prepared_record.path).outcome==Outcome::NotFound;
}
}

bool ProfileStore::PrepareLifecycleTransaction(glyph_package::EnvelopePhase &phase,PackageResponse &response) {
    auto &reader=PackageReader(*this,persistence);
    auto &work=PackageWorkspace();
    const auto &state=work.classification;
    const auto selected=SelectedObservedRoot(work);
    const auto &request=phase.request;
    auto refuse=[&](ProfileStoreStatus status) {
        if(reader.ObservationFailed())UnavailablePackageResponse(response);
        else { ClearPackageReceipt(response);response.status=status; }
        EndClassifierOwner();
        return false;
    };
    const int index=Find(request.target_id);
    if(index<0 || !_directory->entries[index].managed_format || state.floor!=Floor::Supported)
        return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
    const auto &old=_directory->entries[index];
    const uint32_t row=old.owned_row1-1;
    const uint32_t operation=request.operation;
    const bool removing=operation==20, updating=operation==17;
    if(old.revision!=request.expected_revision || row>=work.current.rows || old.owned_rgb1>work.current.rgbs)
        return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
    if(old.revision==UINT32_MAX || state.generation==UINT32_MAX || state.package_sequence==UINT32_MAX)
        return refuse(ProfileStoreStatus_PROFILE_STORE_FULL);
    // Retiring the wrapper of a currently executing revision is unsafe until
    // reboot. The native RAM view alone is not a durable protected reference.
    if(old.id==_active_id)return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
    if(!reader.Config(kPackageCurrent,8191,work.scan_config) || !work.scan_config.source_valid ||
       std::memcmp(work.scan_config.sha,work.current.sha,32))return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
    Config &candidate=ConfigWriteCandidate();
    candidate=persistence.PackageConfigScratch();
    *_next=*_directory;
    auto &target=_next->entries[index];
    auto &mode=candidate.game_mode_configs[row];
    if(mode.managed_format!=1 || mode.ultimate_profile_id!=old.id || mode.rgb_config!=old.owned_rgb1)
        return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
    // Classification has returned. Reuse its retired-record digest slots until
    // ConstructPackageIntent copies the new operation into the intent owner.
    if(!ReadLifecycleRecord(reader,old,state.incarnation,work.old_record_sha))
        return refuse(ProfileStoreStatus_PROFILE_STORE_IO_FAILURE);
    HashBytes(prepared_record.record+128,prepared_record.n-128,work.old_wrapper_sha);
    std::memcpy(response.semantic_digest,work.digest,32);
    if(removing) {
        if(!DeleteOwnedRow(candidate,*_next,index,_active_id))return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
        prepared_record.n=0;
    } else {
        ++target.revision;
        if(updating) {
            auto &body=*::new(&initialization_owner.body)PackageBody;
            if(!glyph_package::DecodeCanonicalBody(phase,body) || !LifecycleName(body.name) ||
               std::strcmp(body.row.name,body.name) || body.row.layout_plate<1 || body.row.layout_plate>4)
                return refuse(ProfileStoreStatus_PROFILE_STORE_INVALID);
            SetPackageRow(mode,body,old.id);
            if(body.has_rgb) {
                if(!old.owned_rgb1 && candidate.rgb_configs_count>=30)return refuse(ProfileStoreStatus_PROFILE_STORE_FULL);
                target.owned_rgb1=old.owned_rgb1?old.owned_rgb1:++candidate.rgb_configs_count;
                mode.rgb_config=target.owned_rgb1;
                candidate.rgb_configs[target.owned_rgb1-1]=body.rgb;
            } else if(old.owned_rgb1) {
                RemoveOwnedRgb(candidate,*_next,old.owned_rgb1);
                target.owned_rgb1=0;
            }
            std::memcpy(target.name,body.name,sizeof(target.name));
            target.rank=body.display_rank;
            auto &lease=PackagePreparation().native_lease;
            lease.bytes=phase.native.bytes;lease.size=phase.native.size;lease.live=true;
            _candidate_profile=UltimateProfile_init_default;
            _candidate_profile.schema_version=5;
            ultimate_native::Bind(_candidate_profile,lease);
            prepared_record.stream=pb_ostream_from_buffer(prepared_record.record+128,3341);
            const bool valid=ValidateProfile(_candidate_profile) &&
                ultimate_native::ContextMatches(ultimate_native::CandidateView(),mode) &&
                pb_encode(&prepared_record.stream,UltimateProfile_fields,&_candidate_profile);
            prepared_record.n=128+prepared_record.stream.bytes_written;
            _candidate_profile.native_payload={};lease.Release();body.native_body={};
            if(!valid)return refuse(ProfileStoreStatus_PROFILE_STORE_INVALID);
        } else if(operation==18) {
            if(!LifecycleName(request.replacement_name))return refuse(ProfileStoreStatus_PROFILE_STORE_INVALID);
            std::memset(target.name,0,sizeof(target.name));
            std::memcpy(target.name,request.replacement_name,std::strlen(request.replacement_name));
            std::memcpy(mode.name,request.replacement_name,sizeof(mode.name));
        } else target.rank=request.replacement_rank;
    }
    ++candidate.managed_sequence;++_next->generation;++_next->package_sequence;
    if(removing || candidate.rgb_configs_count<work.current.rgbs)
        _next->compaction_sequence=_next->package_sequence;
    response.profile_id=old.id;response.profile_revision=old.revision+1;
    response.row_index=row;response.rgb_index=removing?old.owned_rgb1:target.owned_rgb1;
    _next->last_result={Status::Ok,old.id,old.revision+1,_next->generation};
    _next->last_identity.token=request.request_token;
    std::memcpy(_next->last_identity.digest,response.semantic_digest,32);
    if(!reader.DescribeConfig(candidate,work.scan_config) || !work.scan_config.source_valid)
        return refuse(ProfileStoreStatus_PROFILE_STORE_INVALID);
    if(!removing) {
        auto &identity=PackagePreparation().identity;
        identity={state.incarnation,old.id,row,target.owned_rgb1,_next->generation,_next->package_sequence,
            request.request_token,response.semantic_digest,work.current.sha,old.revision+1,2,operation};
        if(!MakeRecordHeader(prepared_record.record,prepared_record.record+128,prepared_record.n-128,identity) ||
           !RecordPath(prepared_record.path,sizeof(prepared_record.path),old.id,old.revision+1,false) ||
           !RecordPath(prepared_record.temp,sizeof(prepared_record.temp),old.id,old.revision+1,true) ||
           !HashMessage(GameModeConfig_fields,&mode,work.row_sha) ||
           (target.owned_rgb1 && !HashMessage(RgbConfig_fields,&candidate.rgb_configs[target.owned_rgb1-1],work.rgb_sha)))
            return refuse(ProfileStoreStatus_PROFILE_STORE_INVALID);
        HashBytes(prepared_record.record,prepared_record.n,response.record_sha);
    }
    auto &protected_bytes=PackagePreparation().needed;
    if(!PackageProtectedBytes(reader,work,_active_id,_active_revision,protected_bytes) ||
       !EncodeDirectory(*_next,directory_publication_wire) ||
       !ComputePackageAggregate(reader,work,candidate,removing?0:old.id))
        return refuse(ProfileStoreStatus_PROFILE_STORE_IO_FAILURE);
    std::memcpy(_next->managed_aggregate,directory_publication_wire+264,32);
    auto &geo=PackagePreparation().geometry;
    if(!_storage->Geometry(geo)||!ExactGeometry(geo)||geo.used_bytes<work.logical_bytes)
        return refuse(ProfileStoreStatus_PROFILE_STORE_IO_FAILURE);
    auto &arith=PackagePreparation().admission;
    arith={geo.used_bytes,geo.free_bytes,geo.total_bytes,protected_bytes,request.request_token,state.high_token,
        work.current.rows,work.current.rgbs,uint32_t(_directory->count),_directory->high_water_id,state.generation,
        state.package_sequence,uint32_t(work.namespace_files),work.scan_config.body_bytes,uint32_t(prepared_record.n),
        candidate.rgb_configs_count>work.current.rgbs,operation};
    if(!AdmissionNeed(arith,protected_bytes))return refuse(ProfileStoreStatus_PROFILE_STORE_FULL);
    if(!reader.Config(kPackageCurrent,8191,work.prior)||!work.prior.source_valid||
       std::memcmp(work.prior.sha,work.current.sha,32)||!RecheckPackageBaselineRoots(reader,work))
        return refuse(ProfileStoreStatus_PROFILE_STORE_CONFLICT);
    if(updating)initialization_owner.body.~PackageBody();
    ConstructPackageIntent(work,state,response,work.roots[selected].sha,_directory->high_water_id);
    auto *intent=initialization_owner.intent;
    Put16(intent+4,2);Put32(intent+8,operation);Put32(intent+72,old.revision+1);
    Put32(intent+376,candidate.game_mode_configs_count);Put32(intent+384,candidate.rgb_configs_count);
    Put32(intent+400,old.revision);Put32(intent+404,row);Put32(intent+408,old.owned_rgb1);
    std::memcpy(intent+412,work.old_record_sha,32);
    std::memcpy(intent+444,work.old_wrapper_sha,32);
    if(removing){std::memset(intent+168,0,96);std::memset(intent+328,0,32);}
    if(!IntentValid(intent))return refuse(ProfileStoreStatus_PROFILE_STORE_INVALID);
    EndClassifierOwner();
    std::memcpy(phase.request.expected_digest,response.semantic_digest,32);
    package_call={this,request.request_token,PackageWritePhase::Control,_storage};
    return true;
}
