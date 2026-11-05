// Included only by the package-enabled production ProfileStore translation unit.
// The owner unions above are shared by synchronous core0 phases; this file adds
// no Config, root, record or classifier image storage.
namespace {
using package_storage::ClassificationWorkspace;
using package_storage::ClassifierOwners;
using package_storage::Classification;
using package_storage::Floor;
using package_storage::Logical;
using package_storage::IntentFacts;
using package_storage::NamespaceReader;
using package_storage::NamespaceObject;
using package_storage::RootFacts;
using package_storage::RootView;
using package_storage::Probe;
using package_storage::RecordIdentity;
using package_storage::AdmissionArithmetic;
using package_storage::ClassifyNamespace;
using package_storage::RecordValid;
using package_storage::RecordMatchesIntent;
using package_storage::RecordPath;
using package_storage::FinishRoot;
using package_storage::FinishControl;
using package_storage::ControlValid;
using package_storage::RootValid;
using package_storage::FileCharge;
using package_storage::EmptyIntent;
using package_storage::IntentValid;
using package_storage::MakeRecordHeader;
using package_storage::ExactGeometry;
using package_storage::AdmissionNeed;
constexpr const char *kPackageCurrent = "/config-v2.bin";
constexpr const char *kPackagePrior = "/config-v2.prev";
constexpr const char *kPackageStaged = "/config-v2.tmp";

ClassificationWorkspace &PackageWorkspace() {
    return *reinterpret_cast<ClassificationWorkspace *>(publication_readback);
}
ClassifierOwners PackageOwners() {
    return {PackageWorkspace(), RootReadWire(), directory_publication_wire,
        control_publication_wire, initialization_owner.intent, prepared_record.record};
}
void BeginClassifierOwner() { ::new (publication_readback) ClassificationWorkspace; }
void EndClassifierOwner() { PackageWorkspace().~ClassificationWorkspace(); }
void SetObservedFence(const Classification &c) {
    using C = PackageStorageFence::Classification;
    PackageStorageFence::Classify(c.write_fenced ?
        (c.floor == Floor::Unsupported ? C::Unsupported : C::Unresolved) :
        (c.floor == Floor::NoManaged ? C::LegacyHealthy : C::ManagedHealthy));
}
void ApplyRuntimeFence(Classification &c) {
    if(!c.write_fenced&&PackageStorageFence::MutationFenced()) {
        c.write_fenced=true;c.floor=Floor::Unresolved;
    }
}
unsigned SelectedObservedRoot(const ClassificationWorkspace &w) {
    return Get32(w.roots[1].prefix + 8) > Get32(w.roots[0].prefix + 8) ? 1 : 0;
}
// Strict DecodeCanonicalRequest already proved canonical byte equality.
// Encoding that exact immutable message with token2 omitted is byte-identical
// to removing only the canonical token field from the admitted raw request.
// This pure noinline frame ends before any persistent operation.
__attribute__((noinline)) bool PackageCreateDigest(const glyph_package::EnvelopePhase &phase,uint8_t out[32]) {
    if(phase.request.operation!=PackageOperation_CREATE_PACKAGE||!phase.package.seen)return false;
    PackageEnvelope semantic=phase.request;semantic.request_token=0;
    Sha256 hash;static constexpr char domain[]="Glyph.Package.Create.v1";hash.Update(domain,sizeof(domain));
    pb_ostream_t stream{};stream.state=&hash;stream.max_size=SIZE_MAX;
    stream.callback=[](pb_ostream_t *s,const pb_byte_t *bytes,size_t size)->bool {
        static_cast<Sha256 *>(s->state)->Update(bytes,size);return true;
    };
    if(!pb_encode(&stream,PackageEnvelope_fields,&semantic))return false;
    hash.Final(out);return true;
}
void InitPackageResponse(PackageResponse &r, uint64_t token) {
    r = PackageResponse_init_zero;
    r.protocol_version=3; r.request_token=token;
    r.status=ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN;
    r.capability_version=1; r.logical=PackageLogicalDisposition_UNRESOLVED;
    r.write_fenced=true;
    r.storage_floor=PackageStorageFloor_FLOOR_UNRESOLVED;
    r.supported_package_format=1; r.supported_root_format=3;
    r.supported_record_format=2; r.supported_receipt_format=1;
    r.package_schema_version=1; r.max_create_request_bytes=4564;
    r.max_create_frame_bytes=4580; r.max_query_request_bytes=57;
    r.max_response_bytes=228; r.max_response_frame_bytes=231;
    r.max_query_frame_bytes=60; r.capability_bits=31; r.max_package_body_bytes=4491;
}
void ClearPackageReceipt(PackageResponse &r) {
    r.profile_id=0; r.profile_revision=0; r.transaction_operation=0;
    r.has_row_index=false; r.row_index=0; r.rgb_index=0;
    r.has_semantic_digest=false; r.has_config_sha=false; r.has_record_sha=false;
    std::memset(r.semantic_digest,0,32); std::memset(r.config_sha,0,32);
    std::memset(r.record_sha,0,32); r.record_publication_generation=0;
}
void UnavailablePackageResponse(PackageResponse &r) {
    ClearPackageReceipt(r);
    r.status=ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN;
    r.logical=PackageLogicalDisposition_UNRESOLVED;
    r.write_fenced=true; r.storage_floor=PackageStorageFloor_FLOOR_UNRESOLVED;
    r.store_generation=0; r.config_generation=0;
    r.store_incarnation=0; r.transaction_token_high_water=0;
}
void ObservedPackageResponse(PackageResponse &r, const Classification &c,
                             const ClassificationWorkspace &w) {
    r.logical=PackageLogicalDisposition_LOGICAL_NONE;
    r.write_fenced=c.write_fenced;
    r.storage_floor=c.floor==Floor::NoManaged ? PackageStorageFloor_NO_MANAGED :
        c.floor==Floor::Supported ? PackageStorageFloor_SUPPORTED :
        c.floor==Floor::Unsupported ? PackageStorageFloor_UNSUPPORTED_FORMAT :
        PackageStorageFloor_FLOOR_UNRESOLVED;
    if(c.logical!=Logical::Unresolved) {
        r.store_incarnation=c.incarnation; r.store_generation=c.generation;
        r.config_generation=w.current.body_bytes ? w.current.crc : 0;
        r.transaction_token_high_water=c.high_token;
    }
    r.status=c.floor==Floor::Unsupported ? ProfileStoreStatus_PROFILE_STORE_UNSUPPORTED :
        c.logical==Logical::Unresolved||c.write_fenced ? ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN :
        ProfileStoreStatus_PROFILE_STORE_OK;
}
void IntentReceipt(PackageResponse &r,const IntentFacts &i,const ClassificationWorkspace &w,
                   Logical logical) {
    r.profile_id=i.id; r.profile_revision=1; r.transaction_operation=15;
    r.has_row_index=true; r.row_index=i.row; r.rgb_index=i.rgb;
    r.has_semantic_digest=r.has_config_sha=r.has_record_sha=true;
    std::memcpy(r.semantic_digest,i.digest,32);
    std::memcpy(r.config_sha,logical==Logical::Committed?w.current.sha:i.final_config,32);
    std::memcpy(r.record_sha,i.record,32);
    r.record_publication_generation=i.generation;
    r.logical=logical==Logical::Committed ? PackageLogicalDisposition_COMMITTED :
        logical==Logical::ProvenAborted ? PackageLogicalDisposition_PROVEN_ABORTED :
        PackageLogicalDisposition_INCOMPLETE;
    r.status=logical==Logical::ProvenAborted ? ProfileStoreStatus_PROFILE_STORE_TRANSACTION_ABORTED :
        logical==Logical::Committed&&!r.write_fenced ? ProfileStoreStatus_PROFILE_STORE_OK :
        ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN;
}
void HashBytes(const uint8_t *b,size_t n,uint8_t out[32]) { Sha256 h; h.Update(b,n); h.Final(out); }
bool PackageRecordName(const char *p) {
    const auto n=std::strlen(p);
    return n==29 && !std::strncmp(p,"/ultpkg-",8) && !std::strcmp(p+n-4,".bin");
}
// Caller first obtained complete positive classification. Inspect all current
// and protected receipts BEFORE deciding conflict, expiry or stale CREATE guards.
// No writer acquisition, checkpoint, reconciliation or cleanup occurs here.
bool QueryObservedPackage(NamespaceReader &reader,const Classification &c,
                          const ClassificationWorkspace &w,uint64_t token,
                          const uint8_t digest[32],uint32_t incarnation,
                          PackageResponse &r) {
    ObservedPackageResponse(r,c,w); ClearPackageReceipt(r);
    if(c.floor==Floor::Unsupported)return true;
    if(c.logical==Logical::Unresolved) { r.logical=PackageLogicalDisposition_UNRESOLVED; return true; }
    if(c.incarnation && c.incarnation!=incarnation) {
        r.status=ProfileStoreStatus_PROFILE_STORE_CONFLICT; return true;
    }
    bool matched=false, conflict=false, installed=false;
    for(unsigned k=0;k<3;++k) {
        const auto &root=w.roots[k]; if(!root.present)continue;
        if(Get64(root.prefix+24)==token) {
            matched=true;
            const bool package=root.intent.operation==15&&root.intent.token==token;
            conflict|=!package||std::memcmp(root.prefix+32,digest,32);
        }
    }
    for(const auto *cfg:{&w.current,&w.prior}) if(cfg->reference_token==token) {
        matched=true; conflict=true; // operation10 can never be package15
    }
    const auto &intent=w.roots[2].intent;
    if(intent.operation==15&&intent.token==token) {
        matched=true; conflict|=std::memcmp(intent.digest,digest,32)!=0;
    }
    const RootFacts *installed_root=nullptr;
    if(w.current.managed_format==1) {
        for(unsigned k=0;k<2;++k) {
            const auto &root=w.roots[k];
            if(root.present&&root.format==3&&Get32(root.prefix+300)==w.current.sequence&&
               (!installed_root||Get32(root.prefix+8)>Get32(installed_root->prefix+8))) installed_root=&root;
        }
        if(!installed_root)return false;
    }
    for(size_t index=0;;++index) {
        NamespaceObject object{}; bool eof=false;
        if(!reader.ObjectAt(index,object,eof))return false;
        if(eof)break;
        if(!PackageRecordName(object.path))continue;
        if(object.bytes<=128||object.bytes>3469||
           !reader.Read(object.path,0,prepared_record.record,object.bytes)||
           !RecordValid(prepared_record.record,object.bytes))return false;
        const auto *record=prepared_record.record;
        if(Get32(record+8)!=c.incarnation||Get64(record+32)>c.high_token)return false;
        if(Get64(record+32)!=token)continue;
        matched=true; conflict|=std::memcmp(record+40,digest,32)!=0;
        if(!installed_root)continue;
        for(size_t j=0;j<Get16(installed_root->prefix+6);++j) {
            const auto *entry=installed_root->prefix+320+j*56;
            if(!entry[53]||Get32(entry)!=Get32(record+12))continue;
            if(Get32(record+16)!=1||Get32(record+72)+1!=entry[54]||Get32(record+76)!=entry[55])return false;
            if(installed&&r.profile_id!=Get32(record+12))return false;
            installed=true;
            r.profile_id=Get32(record+12); r.profile_revision=1; r.transaction_operation=15;
            r.has_row_index=true; r.row_index=Get32(record+72); r.rgb_index=Get32(record+76);
            r.has_semantic_digest=r.has_config_sha=r.has_record_sha=true;
            std::memcpy(r.semantic_digest,record+40,32); std::memcpy(r.config_sha,w.current.sha,32);
            HashBytes(record,object.bytes,r.record_sha);
            r.record_publication_generation=Get32(record+120);
        }
    }
    if(reader.ObservationFailed())return false;
    if(conflict) { ClearPackageReceipt(r); r.status=ProfileStoreStatus_PROFILE_STORE_CONFLICT; return true; }
    if(intent.operation==15&&intent.token==token) {
        IntentReceipt(r,intent,w,c.logical); return true;
    }
    if(installed) {
        r.logical=PackageLogicalDisposition_COMMITTED;
        r.status=r.write_fenced?ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN:ProfileStoreStatus_PROFILE_STORE_OK;
        return true;
    }
    ClearPackageReceipt(r);
    if(matched) { r.logical=PackageLogicalDisposition_UNRESOLVED; r.write_fenced=true;
        r.storage_floor=PackageStorageFloor_FLOOR_UNRESOLVED;
        r.status=ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN; return true; }
    r.status=token<=c.high_token ? ProfileStoreStatus_PROFILE_STORE_TRANSACTION_EXPIRED : ProfileStoreStatus_PROFILE_STORE_NOT_FOUND;
    return true;
}
} // namespace
namespace {
enum class PackageWritePhase : uint8_t { Idle, Control, Record, Root, Config, Garbage };
struct PackageCallState { ProfileStore *owner=nullptr; uint64_t token=0; PackageWritePhase phase=PackageWritePhase::Idle; ProfileStoreStorage *storage=nullptr; } package_call;
bool SamePath(const char *a,const char *b) {
    if(!a||!b)return false;
    if(*a=='/')++a;
    if(*b=='/')++b;
    return !std::strcmp(a,b);
}
bool PackageWriteAuthorized(void *context,PackageStorageFence::WriteKind kind,uint64_t token,
                            CheckedStorage::Operation operation,const char *path,const char *destination) {
    const auto &call=*static_cast<const PackageCallState *>(context);
    if(kind!=PackageStorageFence::WriteKind::Package||!call.owner||call.token!=token||!token)return false;
    const char *temporary=nullptr,*final=nullptr;
    switch(call.phase) {
    case PackageWritePhase::Control: temporary=kControlTemp; final=kControl; break;
    case PackageWritePhase::Record: temporary=prepared_record.temp; final=prepared_record.path; break;
    case PackageWritePhase::Root: temporary=directory_publication_temp; final=directory_publication_path; break;
    case PackageWritePhase::Config: temporary=kPackageStaged; final=kPackageCurrent; break;
    default: return false;
    }
    if(operation==CheckedStorage::Operation::Rename) {
        return (SamePath(path,temporary)&&SamePath(destination,final))||
            (call.phase==PackageWritePhase::Config&&SamePath(path,kPackageCurrent)&&SamePath(destination,kPackagePrior));
    }
    // No deletion, format, destination truncation or broad package bypass.
    return (operation==CheckedStorage::Operation::OpenWrite||operation==CheckedStorage::Operation::Write||
            operation==CheckedStorage::Operation::Seek||operation==CheckedStorage::Operation::Read||
            operation==CheckedStorage::Operation::Sync||operation==CheckedStorage::Operation::Close)&&
            SamePath(path,temporary)&&!destination;
}
const char *SegmentTemp() { return publication_owner.package.prefix_bytes==3920?kControlTemp:directory_publication_temp; }
const char *SegmentFinal() { return publication_owner.package.prefix_bytes==3920?kControl:directory_publication_path; }
size_t SegmentBytes() { return publication_owner.package.prefix_bytes+516; }
__attribute__((noinline)) void SegmentOpenWrite() {
    publication_result=CheckedStorage::Open(mounted_write_file,SegmentTemp(),true,Kind::Root);
}
__attribute__((noinline)) void SegmentWritePrefix() {
    const auto &s=publication_owner.package;
    publication_result=CheckedStorage::Write(mounted_write_file,s.prefix,s.prefix_bytes);
    if(publication_result&&publication_result.bytes!=s.prefix_bytes)publication_result={Outcome::Failed,0,0};
}
__attribute__((noinline)) void SegmentWriteIntent() {
    publication_result=CheckedStorage::Write(mounted_write_file,publication_owner.package.intent,512);
    if(publication_result&&publication_result.bytes!=512)publication_result={Outcome::Failed,0,0};
}
__attribute__((noinline)) void SegmentWriteTrailer() {
    publication_result=CheckedStorage::Write(mounted_write_file,publication_owner.package.trailer,4);
    if(publication_result&&publication_result.bytes!=4)publication_result={Outcome::Failed,0,0};
}
__attribute__((noinline)) void SegmentSync() { publication_result=CheckedStorage::Sync(mounted_write_file); }
__attribute__((noinline)) void SegmentClose() {
    if(!publication_result)PackageStorageFence::Fence();
    const auto closed=CheckedStorage::Close(mounted_write_file);
    if(!closed) { publication_result=closed; PackageStorageFence::Fence(); }
}
__attribute__((noinline)) bool SegmentStat(bool final) {
    size_t extent=0;
    publication_result=CheckedStorage::Stat(final?SegmentFinal():SegmentTemp(),&extent,Kind::Root);
    if(publication_result&&extent!=SegmentBytes())publication_result={Outcome::Failed,0,0};
    return bool(publication_result);
}
__attribute__((noinline)) void SegmentOpenRead(bool final) {
    publication_result=CheckedStorage::Open(mounted_write_file,final?SegmentFinal():SegmentTemp(),false,Kind::Root);
}
__attribute__((noinline)) void SegmentReadChunk() {
    size_t n=SegmentBytes()-publication_owner.package.offset;
    if(n>sizeof(publication_readback))n=sizeof(publication_readback);
    publication_result=CheckedStorage::Read(mounted_write_file,publication_readback,n);
    if(publication_result&&publication_result.bytes!=n)publication_result={Outcome::Failed,0,0};
}
__attribute__((noinline)) void SegmentCompareChunk() {
    auto &s=publication_owner.package;
    for(size_t i=0;i<publication_result.bytes;++i,++s.offset) {
        size_t at=s.offset; uint8_t expected;
        if(at<s.prefix_bytes)expected=s.prefix[at];
        else { at-=s.prefix_bytes; expected=at<512?s.intent[at]:s.trailer[at-512]; }
        if(publication_readback[i]!=expected) { publication_result={Outcome::Failed,0,0}; return; }
    }
}
__attribute__((noinline)) bool VerifySegment(bool final) {
    if(!SegmentStat(final))return false;
    SegmentOpenRead(final);
    if(publication_result) {
        publication_owner.package.offset=0;
        while(publication_owner.package.offset<SegmentBytes()) {
            SegmentReadChunk(); if(!publication_result)break;
            SegmentCompareChunk(); if(!publication_result)break;
        }
    }
    // A lost Open acknowledgement can still own the native handle.
    if(mounted_write_file.opened)SegmentClose();
    return bool(publication_result);
}
__attribute__((noinline)) void SegmentRename() {
    publication_result=CheckedStorage::Rename(SegmentTemp(),SegmentFinal(),Kind::Root);
}
__attribute__((noinline)) bool SegmentSourceAbsent() {
    publication_result=CheckedStorage::Stat(SegmentTemp(),nullptr,Kind::Root);
    if(publication_result.outcome==Outcome::NotFound) { publication_result={Outcome::Ok,0,0}; return true; }
    return false;
}
__attribute__((always_inline)) inline bool ExecuteSegmentedPublication() {
    SegmentOpenWrite();
    if(publication_result) {
        SegmentWritePrefix(); if(publication_result)SegmentWriteIntent();
        if(publication_result)SegmentWriteTrailer();
        if(publication_result)SegmentSync();
    }
    if(mounted_write_file.opened)SegmentClose();
    if(!publication_result||!VerifySegment(false)) { PackageStorageFence::Fence(); return false; }
    SegmentRename();
    if(!publication_result||!SegmentSourceAbsent()||!VerifySegment(true)) {
        PackageStorageFence::Fence(); return false;
    }
    return true;
}
__attribute__((noinline)) bool PreparePackageControl(uint32_t phase,ProfileStoreStorage *storage) {
    std::memcpy(control_publication_wire+16,directory_publication_wire,3908);
    auto root=RootView{control_publication_wire+16,initialization_owner.intent,control_publication_wire+3920};
    FinishRoot(control_publication_wire+16,initialization_owner.intent,control_publication_wire+3920);
    FinishControl(control_publication_wire,root,phase);
    ::new(&publication_owner.package)PackagePublication{control_publication_wire,initialization_owner.intent,
        control_publication_wire+3920,3920,0,0,storage};
    package_call.phase=PackageWritePhase::Control;
    return ControlValid(control_publication_wire,root);
}
__attribute__((noinline)) bool PreparePackageRoot(ProfileStoreStorage *storage) {
    FinishRoot(directory_publication_wire,initialization_owner.intent,directory_publication_wire+3904);
    const unsigned slot=Get32(directory_publication_wire+8)&1;
    RootPath(directory_publication_path,sizeof(directory_publication_path),slot);
    RootTemp(directory_publication_temp,sizeof(directory_publication_temp),slot);
    ::new(&publication_owner.package)PackagePublication{directory_publication_wire,initialization_owner.intent,
        directory_publication_wire+3904,3904,0,0,storage};
    package_call.phase=PackageWritePhase::Root;
    return RootValid({directory_publication_wire,initialization_owner.intent,directory_publication_wire+3904});
}
__attribute__((noinline)) bool VerifyPublishedManagedRecord(ProfileStoreStorage &storage) {
    size_t bytes=0;
    if(!storage.Probe(prepared_record.path,&bytes)||bytes!=prepared_record.n||
       !storage.CheckedRead(prepared_record.path,publication_readback,bytes,Kind::Record)||
       std::memcmp(publication_readback,prepared_record.record,bytes)||
       storage.Probe(prepared_record.temp).outcome!=Outcome::NotFound)return false;
    return RecordValid(publication_readback,bytes)&&RecordMatchesIntent(publication_readback,bytes,initialization_owner.intent);
}
} // namespace
namespace {
// Every reference slot is scalar and reproducible from already checked roots.
// O(n^2) duplicate suppression replaces another retained profile-ID/path array.
bool ProtectedReference(const ClassificationWorkspace &w,size_t ordinal,uint32_t active_id,
                        uint32_t active_revision,uint32_t &id,uint32_t &revision,bool &managed) {
    id=revision=0; managed=false;
    if(ordinal==393) { id=active_id; revision=active_revision;
        for(unsigned r=0;r<3;++r)if(w.roots[r].present)
            for(size_t i=0;i<Get16(w.roots[r].prefix+6);++i) {
                const auto *entry=w.roots[r].prefix+320+i*56;
                if(Get32(entry)==id)managed=entry[53]!=0;
            }
        return id&&revision;
    }
    const auto &root=w.roots[ordinal/131]; if(!root.present)return false;
    const size_t slot=ordinal%131;
    if(slot<128) {
        const size_t index=slot/2; if(index>=Get16(root.prefix+6))return false;
        const auto *entry=root.prefix+320+index*56;
        id=Get32(entry); revision=Get32(entry+(slot%2?8:4)); managed=entry[53]!=0;
    } else if(slot<130) {
        const size_t i=slot-128; if(i>=Get32(root.prefix+84))return false;
        id=Get32(root.prefix+120+i*4); revision=Get32(root.prefix+128+i*4);
    } else if(root.intent.operation) { id=root.intent.id; revision=root.intent.revision; managed=true; }
    return id&&revision;
}
__attribute__((noinline)) bool PackageProtectedBytes(NamespaceReader &reader,ClassificationWorkspace &w,
                                                    uint32_t active_id,uint32_t active_revision,uint64_t &protected_bytes) {
    w.logical_bytes=0;
    protected_bytes=0;
    for(size_t i=0;;++i) {
        bool eof=false; if(!reader.ObjectAt(i,w.object,eof))return false; if(eof)break;
        uint64_t charge=0;
        if(!FileCharge(w.object.bytes,charge)||protected_bytes>UINT64_MAX-charge||
           w.logical_bytes>UINT64_MAX-w.object.bytes)return false;
        protected_bytes+=charge;
        w.logical_bytes+=w.object.bytes;
    }
    for(size_t i=0;i<394;++i) {
        uint32_t id,revision; bool managed;
        if(!ProtectedReference(w,i,active_id,active_revision,id,revision,managed))continue;
        bool duplicate=false;
        for(size_t j=0;j<i&&!duplicate;++j) {
            uint32_t earlier_id,earlier_revision; bool earlier_managed;
            duplicate=ProtectedReference(w,j,active_id,active_revision,earlier_id,earlier_revision,earlier_managed)&&
                id==earlier_id&&revision==earlier_revision&&managed==earlier_managed;
        }
        if(duplicate)continue;
        char path[32];
        if(managed) { if(!RecordPath(path,sizeof(path),id,revision,false))return false; }
        else ProfileStorePaths::RecordPath(path,sizeof(path),id,revision);
        size_t extent=0; const auto state=reader.Extent(path,extent);
        if(state==Probe::Error)return false;
        if(state==Probe::Absent)return false;
    }
    return !reader.ObservationFailed();
}
void AppendPackageRow(Config &config,const PackageBody &body,uint32_t id) {
    auto &row=config.game_mode_configs[config.game_mode_configs_count++];
    std::memset(&row,0,sizeof(row));
    const auto &source=body.row;
    row.mode_id=GameModeId_MODE_ULTIMATE;
    std::memcpy(row.name,source.name,sizeof(row.name));
#define COPY_REPEATED(name) row.name##_count=source.name##_count; std::memcpy(row.name,source.name,sizeof(source.name))
    COPY_REPEATED(socd_pairs); COPY_REPEATED(button_remapping); COPY_REPEATED(activation_binding);
    COPY_REPEATED(applicable_backends); COPY_REPEATED(menu_button_icon);
#undef COPY_REPEATED
    row.layout_plate=source.layout_plate;
    row.ultimate_profile_id=id; row.ultimate_profile_engine=1; row.managed_format=1;
    if(body.has_rgb) { config.rgb_configs[config.rgb_configs_count++]=body.rgb; row.rgb_config=config.rgb_configs_count; }
    config.ultimate_profile_root_format=3; config.managed_format=1; ++config.managed_sequence;
}
__attribute__((noinline)) bool ComputePackageAggregate(NamespaceReader &reader,ClassificationWorkspace &w,
                                                       const Config &candidate,uint32_t new_id) {
    auto &hash=w.aggregate_hash; hash.~Sha256(); ::new(&hash)Sha256;
    static constexpr char domain[]="Glyph.Package.Set.v1";
    hash.Update(domain,sizeof(domain)); uint8_t numbers[16];
    Put32(numbers,candidate.ultimate_profile_store_incarnation);
    uint32_t managed_count=0;
    for(size_t i=0;i<Get16(directory_publication_wire+6);++i)managed_count+=directory_publication_wire[320+i*56+53]!=0;
    Put32(numbers+4,managed_count); hash.Update(numbers,8);
    uint32_t previous=0;
    for(uint32_t item=0;item<managed_count;++item) {
        const uint8_t *entry=nullptr;
        for(size_t i=0;i<Get16(directory_publication_wire+6);++i) {
            const auto *e=directory_publication_wire+320+i*56;
            if(e[53]&&Get32(e)>previous&&(!entry||Get32(e)<Get32(entry)))entry=e;
        }
        if(!entry)return false;
        const uint32_t id=Get32(entry); previous=id;
        Put32(numbers,id); Put32(numbers+4,Get32(entry+4)); Put32(numbers+8,entry[54]); Put32(numbers+12,entry[55]);
        hash.Update(numbers,16);
        if(id==new_id) {
            hash.Update(w.row_sha,32);
            if(entry[55])hash.Update(w.rgb_sha,32);
            else { HashBytes(nullptr,0,w.digest); hash.Update(w.digest,32); }
            HashBytes(prepared_record.record,prepared_record.n,w.record_sha); hash.Update(w.record_sha,32);
        } else {
            if(!reader.Row(kPackageCurrent,entry[54]-1,w.row))return false;
            hash.Update(w.row.sha,32);
            if(entry[55]) { if(!reader.Rgb(kPackageCurrent,entry[55]-1,w.digest))return false; }
            else HashBytes(nullptr,0,w.digest);
            hash.Update(w.digest,32);
            char path[32]; size_t extent=0;
            if(!RecordPath(path,sizeof(path),id,Get32(entry+4),false)||reader.Extent(path,extent)!=Probe::Present||
               extent>4128||!reader.Read(path,0,ProfileReadWire(),extent)||!RecordValid(ProfileReadWire(),extent))return false;
            HashBytes(ProfileReadWire(),extent,w.digest); hash.Update(w.digest,32);
        }
        HashBytes(entry,56,w.digest); hash.Update(w.digest,32);
    }
    hash.Final(directory_publication_wire+264);
    return !reader.ObservationFailed();
}
bool RecheckPackageBaselineRoots(NamespaceReader &reader,ClassificationWorkspace &w) {
    const char *paths[]={"/ultimate-v2-0.bin","/ultimate-v2-1.bin","/ultimate-v2.ctrl"};
    for(unsigned k=0;k<3;++k) {
        const auto &root=w.roots[k]; if(!root.present)return false;
        size_t extent=0;const size_t lead=k==2?16:0;
        const size_t expected=(root.format==3?4420:3908)+lead;
        if(reader.Extent(paths[k],extent)!=Probe::Present||extent!=expected)return false;
        auto &hash=w.hash;hash.~Sha256();::new(&hash)Sha256;
        if(lead) {
            if(!reader.Read(paths[k],0,w.read_chunk,16)||std::memcmp(w.read_chunk,control_publication_wire,16))return false;
        }
        for(size_t at=lead;at<extent;) {
            size_t bytes=extent-at;if(bytes>sizeof(w.read_chunk))bytes=sizeof(w.read_chunk);
            if(!reader.Read(paths[k],at,w.read_chunk,bytes))return false;
            hash.Update(w.read_chunk,bytes);at+=bytes;
        }
        hash.Final(w.entry_sha);if(std::memcmp(w.entry_sha,root.sha,32))return false;
    }
    return !reader.ObservationFailed();
}
void ConstructPackageIntent(const ClassificationWorkspace &w,const Classification &c,
                            const PackageResponse &r,const uint8_t baseline_root[32],uint32_t baseline_high_id) {
    auto *intent=initialization_owner.intent;
    initialization_owner.intent[0]=0; EmptyIntent(intent);
    Put32(intent+8,15); Put32(intent+12,1); Put32(intent+20,r.rgb_index?1:0);
    Put64(intent+24,r.request_token); std::memcpy(intent+32,r.semantic_digest,32);
    Put32(intent+64,c.incarnation); Put32(intent+68,r.profile_id); Put32(intent+72,1);
    Put32(intent+76,c.generation); Put32(intent+80,c.generation+1); Put32(intent+84,c.package_sequence+1);
    Put32(intent+88,w.current.crc); Put32(intent+92,w.scan_config.crc);
    Put32(intent+96,r.row_index); Put32(intent+100,r.rgb_index);
    std::memcpy(intent+104,w.current.sha,32); std::memcpy(intent+136,w.scan_config.sha,32);
    std::memcpy(intent+168,r.record_sha,32); std::memcpy(intent+200,w.row_sha,32);
    if(r.rgb_index)std::memcpy(intent+232,w.rgb_sha,32);
    std::memcpy(intent+264,baseline_root,32); std::memcpy(intent+296,directory_publication_wire+264,32);
    HashBytes(prepared_record.record,128,intent+328);
    Put32(intent+360,prepared_record.n); Put32(intent+364,w.scan_config.body_bytes);
    Put32(intent+368,c.package_sequence); Put32(intent+372,w.current.rows); Put32(intent+376,w.current.rows+1);
    Put32(intent+380,w.current.rgbs); Put32(intent+384,w.current.rgbs+(r.rgb_index?1:0));
    Put64(intent+388,c.high_token); Put32(intent+396,baseline_high_id);
}
}
bool ProfileStore::BeginPackageObservation(bool recovery) {
    if(package_owner_live)return false;
    package_owner_live=true; BeginClassifierOwner();
    GlyphPackageSourceReader reader(*this,persistence,true);
    auto classification=ClassifyNamespace(reader,PackageOwners());
    SetObservedFence(classification); ApplyRuntimeFence(classification);
    auto &work=PackageWorkspace();
    bool legacy_bootstrap=false, result=false;
    _package_visible=false;
    if(classification.logical!=Logical::Unresolved&&classification.floor!=Floor::Unsupported) {
        if(work.roots[0].present&&work.roots[1].present) {
            const unsigned selected=SelectedObservedRoot(work);
            const auto &root=work.roots[selected];
            result=(!_expected_incarnation||classification.incarnation==_expected_incarnation)&&
                DecodeDirectory(root.prefix,3908,_directory,root.format==3);
            if(result) {
                _ready=true; _v2=true; _root_invalid=false;
                _read_only_recovery=recovery||classification.write_fenced;
                _uncertain=classification.write_fenced;
                _package_visible=!classification.write_fenced;
                const auto &other=work.roots[1-selected];
                DecodeDirectory(other.prefix,3908,_other,other.format==3);
            }
        } else legacy_bootstrap=classification.floor==Floor::NoManaged&&!classification.write_fenced;
    }
    if(!result&&!legacy_bootstrap) { _ready=false; _read_only_recovery=true; _root_invalid=true; }
    EndClassifierOwner(); package_owner_live=false;
    if(legacy_bootstrap)return ExecuteBootstrap(PrepareBootstrap(recovery));
    return result;
}

bool ProfileStore::DispatchPackage(glyph_package::EnvelopePhase &phase,PackageResponse &response) {
    ::new(&prepared_create_owner.package)PackageDispatchInputs{&phase,&response,false};
    if(PreparePackageDispatch())FinishPackageDispatch(PublishPackageTransaction());
    return ReleasePackageDispatch();
}
__attribute__((noinline)) bool ProfileStore::PreparePackageDispatch() {
    auto &in=prepared_create_owner.package;
    in.respond=true; InitPackageResponse(*in.response,in.phase->request.request_token);
    if(package_owner_live)return false;
    package_owner_live=true;
    if(!ObservePackageTransaction(*in.phase,*in.response))return false;
    return PreparePackageTransaction(*in.phase,*in.response);
}
__attribute__((noinline)) void ProfileStore::FinishPackageDispatch(bool success) {
    auto &in=prepared_create_owner.package;
    FinishPackageTransaction(*in.phase,*in.response,success);
}
__attribute__((noinline)) bool ProfileStore::ReleasePackageDispatch() {
    auto &in=prepared_create_owner.package;
    const bool response=in.respond;
    _candidate_profile.native_payload={};
    in.phase->Release(); package_call={}; package_owner_live=false;
    in={}; return response;
}

__attribute__((noinline)) bool ProfileStore::ObservePackageTransaction(glyph_package::EnvelopePhase &phase,PackageResponse &response) {
    BeginClassifierOwner();
    GlyphPackageSourceReader reader(*this,persistence,true);
    auto &work=PackageWorkspace();
    auto &classification=work.classification;
    classification=ClassifyNamespace(reader,PackageOwners());
    SetObservedFence(classification); ApplyRuntimeFence(classification);
    ObservedPackageResponse(response,classification,work);
    if(phase.request.operation==PackageOperation_PACKAGE_STATUS) {
        EndClassifierOwner(); return false;
    }
    if(classification.logical==Logical::Unresolved||classification.floor==Floor::Unsupported) {
        if(classification.floor!=Floor::Unsupported)response.logical=PackageLogicalDisposition_UNRESOLVED;
        EndClassifierOwner(); return false;
    }
    if(phase.request.operation==PackageOperation_QUERY_PACKAGE) {
        if(!QueryObservedPackage(reader,classification,work,phase.request.request_token,
                                 phase.request.expected_digest,phase.request.expected_store_incarnation,response))
            UnavailablePackageResponse(response);
        EndClassifierOwner(); return false;
    }
    if(!PackageCreateDigest(phase,work.digest)) {
        response.status=ProfileStoreStatus_PROFILE_STORE_INVALID; EndClassifierOwner(); return false;
    }
    // Matching durable receipts win over stale baseline guards and never write.
    if(!QueryObservedPackage(reader,classification,work,phase.request.request_token,work.digest,
                             phase.request.expected_store_incarnation,response)) {
        UnavailablePackageResponse(response); EndClassifierOwner(); return false;
    }
    if(response.status!=ProfileStoreStatus_PROFILE_STORE_NOT_FOUND) { EndClassifierOwner(); return false; }
    response.status=ProfileStoreStatus_PROFILE_STORE_CONFLICT;
    if(classification.write_fenced||!classification.incarnation||!work.roots[0].present||!work.roots[1].present||
       phase.request.expected_store_incarnation!=classification.incarnation||
       phase.request.expected_store_generation!=classification.generation||
       phase.request.expected_config_generation!=work.current.crc||
       !work.current.source_valid||(work.prior.body_bytes&&!work.prior.source_valid)||
       std::memcmp(phase.request.expected_config_sha256,work.current.sha,32)) {
        EndClassifierOwner(); return false;
    }
    return true;
}
bool ProfileStore::PreparePackageTransaction(glyph_package::EnvelopePhase &phase,PackageResponse &response) {
    GlyphPackageSourceReader reader(*this,persistence,true);
    auto &work=PackageWorkspace();
    const auto &classification=work.classification;
    const unsigned selected=SelectedObservedRoot(work);
    if(!DecodeDirectory(work.roots[selected].prefix,3908,_directory,work.roots[selected].format==3)) {
        UnavailablePackageResponse(response); EndClassifierOwner(); return false;
    }
    response.status=ProfileStoreStatus_PROFILE_STORE_FULL;
    if(_directory->count>=64||work.current.rows>=30||work.current.rgbs>30||
       _directory->high_water_id==UINT32_MAX||classification.generation==UINT32_MAX||
       classification.package_sequence==UINT32_MAX||phase.request.request_token<=classification.high_token) {
        EndClassifierOwner(); return false;
    }
    // Decoded body replaces only the no-longer-needed borrowed intent bytes.
    ::new(&initialization_owner.body)PackageBody;
    auto &body=initialization_owner.body;
    response.status=ProfileStoreStatus_PROFILE_STORE_INVALID;
    if(!glyph_package::DecodeCanonicalBody(phase,body)||!ValidName(body.name)) {
        body.native_body={}; EndClassifierOwner(); return false;
    }
    if(body.has_rgb&&work.current.rgbs>=30) {
        response.status=ProfileStoreStatus_PROFILE_STORE_FULL;
        body.native_body={}; EndClassifierOwner(); return false;
    }
    // Reload the exact baseline into Persistence's existing scratch, then copy
    // it once into the approved third Config owner before append-only derivation.
    if(!reader.Config(kPackageCurrent,8191,work.scan_config)||
       !work.scan_config.source_valid||std::memcmp(work.scan_config.sha,work.current.sha,32)) {
        body.native_body={}; UnavailablePackageResponse(response); EndClassifierOwner(); return false;
    }
    Config &candidate=ConfigWriteCandidate(); candidate=persistence.PackageConfigScratch();
    const uint32_t id=_directory->high_water_id+1;
    for(size_t i=0;i<candidate.game_mode_configs_count;++i) {
        const auto &old=candidate.game_mode_configs[i];
        if(old.ultimate_profile_id==id||(body.has_rgb&&old.rgb_config==work.current.rgbs+1)) {
            body.native_body={}; EndClassifierOwner(); return false;
        }
    }
    AppendPackageRow(candidate,body,id);
    if(!reader.DescribeConfig(candidate,work.scan_config)||!work.scan_config.source_valid) {
        body.native_body={}; EndClassifierOwner(); return false;
    }
    // Source Prepare/semantic/context validation uses the existing native
    // candidate owner. The borrowed RX lease ends before any storage writes.
    ultimate_native::PayloadLease native_lease;
    native_lease.bytes=phase.native.bytes; native_lease.size=phase.native.size; native_lease.live=true;
    _candidate_profile=UltimateProfile_init_default; _candidate_profile.schema_version=5;
    ultimate_native::Bind(_candidate_profile,native_lease);
    const bool native_ok=ValidateProfile(_candidate_profile)&&
        ultimate_native::ContextMatches(ultimate_native::CandidateView(),candidate.game_mode_configs[work.current.rows]);
    prepared_record.stream=pb_ostream_from_buffer(prepared_record.record+128,3341);
    const bool encoded=native_ok&&pb_encode(&prepared_record.stream,UltimateProfile_fields,&_candidate_profile);
    prepared_record.n=128+prepared_record.stream.bytes_written;
    _candidate_profile.native_payload={}; native_lease.Release(); body.native_body={};
    if(!encoded) { EndClassifierOwner(); return false; }
    response.profile_id=id; response.profile_revision=1;
    response.row_index=work.current.rows; response.rgb_index=body.has_rgb?work.current.rgbs+1:0;
    std::memcpy(response.semantic_digest,work.digest,32);
    const RecordIdentity identity{classification.incarnation,id,response.row_index,response.rgb_index,
        classification.generation+1,classification.package_sequence+1,phase.request.request_token,
        response.semantic_digest,work.current.sha};
    if(!MakeRecordHeader(prepared_record.record,prepared_record.record+128,prepared_record.n-128,identity)||
       !HashMessage(GameModeConfig_fields,&candidate.game_mode_configs[work.current.rows],work.row_sha)||
       (body.has_rgb&&!HashMessage(RgbConfig_fields,&candidate.rgb_configs[work.current.rgbs],work.rgb_sha))||
       !RecordPath(prepared_record.path,sizeof(prepared_record.path),id,1,false)||
       !RecordPath(prepared_record.temp,sizeof(prepared_record.temp),id,1,true)) {
        ClearPackageReceipt(response); EndClassifierOwner(); return false;
    }
    *_next=*_directory; ++_next->generation; _next->high_water_id=id;
    _next->managed_format=1; _next->package_sequence=classification.package_sequence+1;
    auto &entry=_next->entries[_next->count++];
    entry=Entry{}; entry.id=id; entry.revision=1; entry.payload_version=5; entry.rank=body.display_rank;
    std::memcpy(entry.name,body.name,sizeof(entry.name));
    entry.managed_format=1; entry.owned_row1=work.current.rows+1; entry.owned_rgb1=response.rgb_index;
    _next->last_identity.token=phase.request.request_token;
    std::memcpy(_next->last_identity.digest,response.semantic_digest,32);
    _next->last_result={Status::Ok,id,1,_next->generation};
    uint64_t needed=0;
    if(!PackageProtectedBytes(reader,work,_active_id,_active_revision,needed)||
       !EncodeDirectory(*_next,directory_publication_wire)||
       !ComputePackageAggregate(reader,work,candidate,id)) {
        ClearPackageReceipt(response); UnavailablePackageResponse(response); EndClassifierOwner(); return false;
    }
    std::memcpy(_next->managed_aggregate,directory_publication_wire+264,32);
    HashBytes(prepared_record.record,prepared_record.n,response.record_sha);
    CheckedStorage::Geometry geometry{};
    const AdmissionArithmetic arithmetic{geometry.used_bytes,geometry.free_bytes,geometry.total_bytes,
        needed,phase.request.request_token,classification.high_token,work.current.rows,work.current.rgbs,
        uint32_t(_directory->count),_directory->high_water_id,classification.generation,classification.package_sequence,
        uint32_t(work.namespace_files),work.scan_config.body_bytes,uint32_t(prepared_record.n),body.has_rgb};
    // Geometry is read afresh in the same serialized preflight domain.
    AdmissionArithmetic checked=arithmetic;
    if(!_storage->Geometry(geometry)||!ExactGeometry(geometry)||geometry.used_bytes<work.logical_bytes) {
        ClearPackageReceipt(response); UnavailablePackageResponse(response); EndClassifierOwner(); return false;
    }
    checked.used=geometry.used_bytes; checked.free=geometry.free_bytes; checked.total=geometry.total_bytes;
    response.status=ProfileStoreStatus_PROFILE_STORE_FULL;
    if(!AdmissionNeed(checked,needed)) { ClearPackageReceipt(response); EndClassifierOwner(); return false; }
    // Re-read baseline Config after every source callback/capacity probe and
    // before PREPARED. It also detects source facts drifting during preflight.
    if(!reader.Config(kPackageCurrent,8191,work.prior)||!work.prior.source_valid||
       work.prior.crc!=work.current.crc||std::memcmp(work.prior.sha,work.current.sha,32)||
       !RecheckPackageBaselineRoots(reader,work)||reader.ObservationFailed()) {
        ClearPackageReceipt(response); response.status=ProfileStoreStatus_PROFILE_STORE_CONFLICT;
        EndClassifierOwner(); return false;
    }
    // Body is fully materialized and no longer needed; construct the immutable
    // intent in precisely its shared initialization owner before first mutation.
    initialization_owner.body.~PackageBody();
    ConstructPackageIntent(work,classification,response,work.roots[selected].sha,_directory->high_water_id);
    if(!IntentValid(initialization_owner.intent)) {
        ClearPackageReceipt(response); UnavailablePackageResponse(response); EndClassifierOwner(); return false;
    }
    EndClassifierOwner();
    std::memcpy(phase.request.expected_digest,response.semantic_digest,32);
    package_call={this,phase.request.request_token,PackageWritePhase::Control,_storage};
    return true;
}

__attribute__((noinline)) bool ProfileStore::PublishPackageConfigStage() {
        package_call.phase=PackageWritePhase::Config;
        Config &candidate=ConfigWriteCandidate();
        bool success=true;
        auto *facts=::new (publication_readback) Persistence::PackageConfigFacts[2];
        auto &baseline=facts[0]; auto &final=facts[1];
        std::memcpy(baseline.sha,initialization_owner.intent+104,32);
        baseline.crc=Get32(initialization_owner.intent+88);
        // Original source canonical length is proven by the fresh read above.
        // Prefix size is not retained in intent; use the exact known baseline
        // source Config scratch which still contains that verified baseline.
        baseline.bytes=0;
        success=pb_get_encoded_size(&prepared_record.n,Config_fields,&persistence.PackageConfigScratch())&&prepared_record.n<=8191;
        baseline.bytes=uint32_t(prepared_record.n);
        std::memcpy(final.sha,initialization_owner.intent+136,32);
        final.crc=Get32(initialization_owner.intent+92); final.bytes=Get32(initialization_owner.intent+364);
        if(success)success=persistence.PublishPackageConfig(candidate,baseline,final,package_call.owner,package_call.token)==Persistence::SaveResult::Saved;
    return success;
}

__attribute__((noinline)) void ProfileStore::FinishPackageWriteScope(bool success) {
    if(!success) { PackageStorageFence::Fence(); _uncertain=true; _read_only_recovery=true; _package_visible=false; }
    PackageStorageFence::EndWrite(this); package_call={};
    if(success) { *_directory=*_next; _ready=true; _v2=true; _protected_ready=false;
        _uncertain=false; _read_only_recovery=false; _package_visible=true; }
}

__attribute__((noinline)) bool ProfileStore::BeginPackageWriteScope() {
    return PackageStorageFence::BeginWrite(this,PackageStorageFence::WriteKind::Package,
        package_call.token,PackageWriteAuthorized,&package_call);
}

bool ProfileStore::PublishPackageTransaction() {

    if(!package_call.owner->BeginPackageWriteScope())return false;
    bool success=PreparePackageControl(1,package_call.storage)&&ExecuteSegmentedPublication();
    if(success) {
        package_call.phase=PackageWritePhase::Record;
        publication_owner.legacy={package_call.storage,prepared_record.temp,prepared_record.path,
            prepared_record.record,prepared_record.n,Kind::Record,&_last_io_stage};
        ExecutePublication();
        success=bool(publication_result)&&VerifyPublishedManagedRecord(*package_call.storage);
    }
    if(success) { Put32(initialization_owner.intent+12,2);
        success=PreparePackageControl(2,package_call.storage)&&ExecuteSegmentedPublication(); }
    if(success) { Put32(initialization_owner.intent+12,3);
        success=PreparePackageRoot(package_call.storage)&&ExecuteSegmentedPublication(); }
    if(success)success=PreparePackageControl(2,package_call.storage)&&ExecuteSegmentedPublication();
    if(success)success=package_call.owner->PublishPackageConfigStage();
    if(success) { Put32(initialization_owner.intent+12,4);
        success=PreparePackageControl(2,package_call.storage)&&ExecuteSegmentedPublication(); }
    if(success) { Put32(initialization_owner.intent+12,5); Put32(initialization_owner.intent+16,3);
        success=PreparePackageRoot(package_call.storage)&&ExecuteSegmentedPublication(); }
    if(success)success=PreparePackageControl(3,package_call.storage)&&ExecuteSegmentedPublication();
    package_call.owner->FinishPackageWriteScope(success);
    return success;
}

void ProfileStore::FinishPackageTransaction(glyph_package::EnvelopePhase &phase,PackageResponse &response,bool success) {
    // Final response is a fresh read-only classification, also on failure/lost
    // acknowledgement. It never repeats any publication or clears a sticky fence.
    BeginClassifierOwner();
    GlyphPackageSourceReader final_reader(*this,persistence,true);
    auto final_classification=ClassifyNamespace(final_reader,PackageOwners());
    ApplyRuntimeFence(final_classification);
    if(!QueryObservedPackage(final_reader,final_classification,PackageWorkspace(),phase.request.request_token,
                             phase.request.expected_digest,phase.request.expected_store_incarnation,response))
        UnavailablePackageResponse(response);
    if(!success&&(response.status==ProfileStoreStatus_PROFILE_STORE_NOT_FOUND||
                  response.status==ProfileStoreStatus_PROFILE_STORE_TRANSACTION_EXPIRED||
                  response.status==ProfileStoreStatus_PROFILE_STORE_CONFLICT)) {
        ClearPackageReceipt(response);response.status=ProfileStoreStatus_PROFILE_STORE_IO_FAILURE;
        response.logical=PackageLogicalDisposition_LOGICAL_NONE;response.storage_floor=PackageStorageFloor_FLOOR_UNRESOLVED;
        response.write_fenced=true;
    }
    if(!success&&response.status==ProfileStoreStatus_PROFILE_STORE_OK) {
        response.status=ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN;
        response.storage_floor=PackageStorageFloor_FLOOR_UNRESOLVED; response.write_fenced=true;
    }
    EndClassifierOwner();
}
namespace {
bool OrdinaryConfigAuthorized(void *context,PackageStorageFence::WriteKind kind,uint64_t token,
                              CheckedStorage::Operation operation,const char *path,const char *destination) {
    const auto &call=*static_cast<const PackageCallState *>(context);
    if(kind!=PackageStorageFence::WriteKind::Legacy||!call.owner||call.token!=token||call.phase!=PackageWritePhase::Config)return false;
    if(operation==CheckedStorage::Operation::Rename)
        return (SamePath(path,kPackageCurrent)&&SamePath(destination,kPackagePrior))||
               (SamePath(path,kPackageStaged)&&SamePath(destination,kPackageCurrent));
    if(operation==CheckedStorage::Operation::Remove)return SamePath(path,kPackageStaged)&&!destination;
    return SamePath(path,kPackageStaged)&&!destination&&
        (operation==CheckedStorage::Operation::OpenWrite||operation==CheckedStorage::Operation::Write||
         operation==CheckedStorage::Operation::Read||operation==CheckedStorage::Operation::Seek||
         operation==CheckedStorage::Operation::Sync||operation==CheckedStorage::Operation::Close);
}
}
bool ProfileStore::BeginOrdinaryConfigWrite(const Config &candidate) {
    if(package_owner_live||package_call.owner||&candidate==&persistence.PackageConfigScratch())return false;
    package_owner_live=true; BeginClassifierOwner();
    GlyphPackageSourceReader reader(*this,persistence,false);
    const auto state=ClassifyNamespace(reader,PackageOwners()); auto &w=PackageWorkspace();
    SetObservedFence(state);
    bool valid=!state.write_fenced&&(state.floor==Floor::NoManaged||state.floor==Floor::Supported)&&
        (!w.prior.body_bytes||w.prior.source_valid)&&
        reader.DescribeConfig(candidate,w.scan_config)&&w.scan_config.source_valid&&
        reader.Config(kPackageCurrent,8191,w.prior)&&w.prior.source_valid;
    if(valid) {
        const Config &baseline=persistence.PackageConfigScratch();
        valid=candidate.ultimate_profile_store_format==baseline.ultimate_profile_store_format&&
            candidate.ultimate_profile_store_incarnation==baseline.ultimate_profile_store_incarnation&&
            candidate.ultimate_profile_root_format==baseline.ultimate_profile_root_format&&
            candidate.managed_format==baseline.managed_format&&candidate.managed_sequence==baseline.managed_sequence&&
            !std::memcmp(candidate.ultimate_profile_migration_receipt,baseline.ultimate_profile_migration_receipt,
                         sizeof(candidate.ultimate_profile_migration_receipt));
        for(size_t i=0;i<baseline.game_mode_configs_count&&valid;++i) {
            const auto &row=baseline.game_mode_configs[i];
            if(!row.managed_format)continue;
            valid=i<candidate.game_mode_configs_count&&
                HashMessage(GameModeConfig_fields,&row,w.row_sha)&&
                HashMessage(GameModeConfig_fields,&candidate.game_mode_configs[i],w.digest)&&
                !std::memcmp(w.row_sha,w.digest,32);
            if(valid&&row.rgb_config)valid=row.rgb_config<=candidate.rgb_configs_count&&
                HashMessage(RgbConfig_fields,&baseline.rgb_configs[row.rgb_config-1],w.rgb_sha)&&
                HashMessage(RgbConfig_fields,&candidate.rgb_configs[row.rgb_config-1],w.digest)&&
                !std::memcmp(w.rgb_sha,w.digest,32);
            for(size_t j=0;j<candidate.game_mode_configs_count&&valid;++j)if(j!=i) {
                const auto &other=candidate.game_mode_configs[j];
                valid=other.ultimate_profile_id!=row.ultimate_profile_id&&
                    (!row.rgb_config||other.rgb_config!=row.rgb_config);
            }
        }
        for(size_t i=0;i<candidate.game_mode_configs_count&&valid;++i)
            if(candidate.game_mode_configs[i].managed_format)
                valid=i<baseline.game_mode_configs_count&&baseline.game_mode_configs[i].managed_format==1;
        // Unchanged receipt means an unrelated default save. A new G6 receipt
        // consumes the shared high-water and cannot collide with a package/raw
        // receipt; its row must remain unmanaged. Full reference semantics are
        // supplied by the configured source validator above.
        if(valid&&candidate.profile_reference_token!=baseline.profile_reference_token) {
            valid=candidate.profile_reference_token>state.high_token&&
                w.scan_config.reference_digest_valid&&w.scan_config.reference_row<candidate.game_mode_configs_count&&
                w.scan_config.reference_generation==state.generation&&
                !candidate.game_mode_configs[w.scan_config.reference_row].managed_format;
            if(valid) {
                const auto &row=candidate.game_mode_configs[w.scan_config.reference_row];
                valid=row.mode_id==GameModeId_MODE_ULTIMATE&&
                    row.ultimate_profile_id==w.scan_config.reference_id&&!row.ultimate_profile_config;
                if(valid&&w.scan_config.reference_id) {
                    const int index=Find(w.scan_config.reference_id);
                    valid=index>=0&&!_directory->entries[index].managed_format&&
                        row.ultimate_profile_engine==(_directory->entries[index].payload_version==5?1u:0u);
                } else if(valid)valid=!row.ultimate_profile_engine;
            }
        } else if(valid)valid=w.scan_config.reference_token==w.current.reference_token&&
            !std::memcmp(w.scan_config.reference_digest,w.current.reference_digest,32)&&
            w.scan_config.reference_id==w.current.reference_id&&w.scan_config.reference_row==w.current.reference_row&&
            w.scan_config.reference_generation==w.current.reference_generation;
    }
    const uint64_t token=valid?w.scan_config.reference_token:0;
    valid=valid&&!reader.ObservationFailed(); EndClassifierOwner(); package_owner_live=false;
    if(!valid)return false;
    package_call={this,token,PackageWritePhase::Config};
    if(!PackageStorageFence::BeginWrite(this,PackageStorageFence::WriteKind::Legacy,token,
                                      OrdinaryConfigAuthorized,&package_call)) { package_call={}; return false; }
    return true;
}
void ProfileStore::EndOrdinaryConfigWrite() {
    if(package_call.owner==this&&package_call.phase==PackageWritePhase::Config) {
        PackageStorageFence::EndWrite(this); package_call={};
    }
}
namespace {
bool OrdinaryStoreAuthorized(void *context,PackageStorageFence::WriteKind kind,uint64_t token,
                             CheckedStorage::Operation operation,const char *path,const char *destination) {
    const auto &call=*static_cast<const PackageCallState *>(context);
    if(kind!=PackageStorageFence::WriteKind::Legacy||!call.owner||call.token!=token)return false;
    if(operation==CheckedStorage::Operation::Remove) {
        return call.phase==PackageWritePhase::Garbage&&SamePath(path,prepared_record.temp)&&!destination&&
            std::strstr(prepared_record.temp,"/ultimate-")==prepared_record.temp;
    }
    const char *temporary=nullptr,*final=nullptr;
    switch(call.phase) {
    case PackageWritePhase::Control: temporary=kControlTemp; final=kControl; break;
    case PackageWritePhase::Record: temporary=prepared_record.temp; final=prepared_record.path; break;
    case PackageWritePhase::Root: temporary=directory_publication_temp; final=directory_publication_path; break;
    default:return false;
    }
    if(operation==CheckedStorage::Operation::Rename)return SamePath(path,temporary)&&SamePath(destination,final);
    return SamePath(path,temporary)&&!destination&&
        (operation==CheckedStorage::Operation::OpenWrite||operation==CheckedStorage::Operation::Write||
         operation==CheckedStorage::Operation::Read||operation==CheckedStorage::Operation::Seek||
         operation==CheckedStorage::Operation::Sync||operation==CheckedStorage::Operation::Close);
}
}
bool ProfileStore::IsOrdinaryStoreWriteActive() const {
    return package_call.owner==this&&ordinary_store_scope;
}
bool ProfileStore::BeginOrdinaryStoreWrite(const TransactionIdentity *identity,uint32_t target_id) {
    if(package_owner_live||package_call.owner||!_ready||!_storage)return false;
    package_owner_live=true; BeginClassifierOwner();
    GlyphPackageSourceReader reader(*this,persistence,true);
    const auto state=ClassifyNamespace(reader,PackageOwners()); auto &w=PackageWorkspace();
    SetObservedFence(state);
    bool valid=!state.write_fenced&&(state.floor==Floor::NoManaged||state.floor==Floor::Supported)&&
        w.roots[0].present&&w.roots[1].present;
    unsigned selected=0;
    if(valid) {
        selected=SelectedObservedRoot(w);
        valid=DecodeDirectory(w.roots[selected].prefix,3908,_directory,w.roots[selected].format==3)&&
            DecodeDirectory(w.roots[1-selected].prefix,3908,_other,w.roots[1-selected].format==3);
        if(identity) {
            const auto &latest=w.roots[selected];
            const bool raw_receipt=identity->SameRequest(_directory->last_identity)&&
                !(latest.intent.operation==15&&latest.intent.token==identity->token);
            valid=valid&&identity->token&&(identity->token>state.high_token||raw_receipt);
        }
        for(size_t i=0;i<_directory->count&&valid;++i)
            if(_directory->entries[i].id==target_id&&_directory->entries[i].managed_format)valid=false;
        if(valid&&w.roots[selected].format==3) {
            const char *path=selected?"/ultimate-v2-1.bin":"/ultimate-v2-0.bin";
            valid=reader.Read(path,3904,initialization_owner.intent,512)&&IntentValid(initialization_owner.intent);
        }
    }
    valid=valid&&!reader.ObservationFailed(); EndClassifierOwner();
    if(!valid) { package_owner_live=false; return false; }
    _package_visible=true; _protected_ready=true;
    prepared_record.path[0]=prepared_record.temp[0]=0;
    package_call={this,identity?identity->token:0,PackageWritePhase::Idle,_storage};
    if(!PackageStorageFence::BeginWrite(this,PackageStorageFence::WriteKind::Legacy,package_call.token,
                                      OrdinaryStoreAuthorized,&package_call)) {
        package_owner_live=false; package_call={}; return false;
    }
    ordinary_store_scope=true;
    return true;
}
void ProfileStore::EndOrdinaryStoreWrite() {
    if(package_call.owner==this) { PackageStorageFence::EndWrite(this); package_call={}; }
    package_owner_live=false; ordinary_store_scope=false;
}
__attribute__((always_inline)) inline bool ProfileStore::PublishManagedDirectory(const Directory &next) {
    if(!package_owner_live||package_call.owner!=this||!_ready||_read_only_recovery||_uncertain||
       !next.managed_format||!IntentValid(initialization_owner.intent)||
       Get32(initialization_owner.intent+12)!=5||Get32(initialization_owner.intent+16)!=3||
       !EncodeDirectory(next,directory_publication_wire))return false;
    // Raw source identity advances; exact terminal package identity/aggregate
    // remains immutable. A raw pending control is a V3 terminal wrapper whose
    // planned newer source root does not yet match the selected persisted root;
    // the namespace classifier fences that interruption and never runs V2 phases.
    if(!PreparePackageControl(3,_storage)||!ExecuteSegmentedPublication()) { _uncertain=true; return false; }
    if(!PreparePackageRoot(_storage)||!ExecuteSegmentedPublication()) { _uncertain=true; return false; }
    if(!PreparePackageControl(3,_storage)||!ExecuteSegmentedPublication()) { _uncertain=true; return false; }
    *_directory=next; _protected_ready=false;
    return true;
}

namespace {
void OrdinaryRecordPhase(){if(ordinary_store_scope)package_call.phase=PackageWritePhase::Record;}
void OrdinaryControlPhase(){if(ordinary_store_scope)package_call.phase=PackageWritePhase::Control;}
void OrdinaryRootPhase(){if(ordinary_store_scope)package_call.phase=PackageWritePhase::Root;}
void OrdinaryGarbagePhase(const char *path){
    if(ordinary_store_scope&&std::strlen(path)<sizeof(prepared_record.temp)) {
        std::strcpy(prepared_record.temp,path);package_call.phase=PackageWritePhase::Garbage;
    }
}
}

bool ProfileStore::ValidateManagedCompactReceipt(const Config &config) const {
    if(package_owner_live||!_ready||!_directory||!_directory->managed_format)return false;
    package_owner_live=true;BeginClassifierOwner();
    auto &self=*const_cast<ProfileStore *>(this);
    GlyphPackageSourceReader reader(self,persistence,false);
    auto state=ClassifyNamespace(reader,PackageOwners());SetObservedFence(state);ApplyRuntimeFence(state);
    auto &work=PackageWorkspace();
    const bool valid=!state.write_fenced&&state.floor==Floor::Supported&&state.logical==Logical::Committed&&
        state.incarnation==_directory->incarnation&&state.generation==_directory->generation&&
        HashMessage(Config_fields,&config,work.digest)&&!std::memcmp(work.digest,work.current.sha,32)&&
        !reader.ObservationFailed();
    EndClassifierOwner();package_owner_live=false;return valid;
}
