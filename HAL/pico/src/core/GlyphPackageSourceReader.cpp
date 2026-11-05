#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
#include "core/GlyphPackageSourceReader.hpp"
#include "core/CheckedStorage.hpp"
#include "core/ConfigWireValidator.hpp"
#include "core/PackageStorageFence.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
#include "core/ProfileStoreName.hpp"
#include "core/Sha256.hpp"
#include "core/config_validation.hpp"
#include <pb_encode.h>
#include <cstring>
#include <climits>

namespace {
using package_storage::Get32;
using package_storage::RecordValid;
struct EnumerationSelection {
    size_t wanted, seen;
    package_storage::NamespaceObject *out;
    bool found;
};
bool SelectObject(void *context,const CheckedStorage::Entry &entry) {
    auto &selection=*static_cast<EnumerationSelection *>(context);
    if(selection.seen==selection.wanted){
        // Same-mount name_max31; reserve slash/NUL without truncating a name.
        size_t n=0;while(n<sizeof(entry.name)&&entry.name[n])++n;
        if(!n||n>31||n==sizeof(entry.name))return false;
        selection.out->path[0]='/';
        std::memcpy(selection.out->path+1,entry.name,n);
        selection.out->path[n+1]=0;
        selection.out->bytes=entry.bytes;
        selection.out->directory=entry.directory;
        selection.found=true;
    }
    if(selection.seen==SIZE_MAX)return false;
    ++selection.seen;
    return true; // Enumerate ALL names; callback performs no file operations.
}
bool SelectConfig(const char *path,Persistence::PackageConfigFile &file) {
    if(!path)return false;
    const char *name=path[0]=='/'?path+1:path;
    if(!std::strcmp(name,"config-v2.bin"))file=Persistence::PackageConfigFile::Current;
    else if(!std::strcmp(name,"config-v2.prev"))file=Persistence::PackageConfigFile::Prior;
    else if(!std::strcmp(name,"config-v2.tmp"))file=Persistence::PackageConfigFile::Staged;
    else if(!std::strcmp(name,"config.bin"))file=Persistence::PackageConfigFile::Legacy;
    else if(!std::strcmp(name,"ultimate-migration.src"))file=Persistence::PackageConfigFile::MigrationSource;
    else if(!std::strcmp(name,"ultimate-migration.tmp"))file=Persistence::PackageConfigFile::MigrationTemporary;
    else return false;
    return true;
}
__attribute__((noinline)) bool HashMessage(const pb_msgdesc_t *fields,const void *message,uint8_t out[32]) {
    Sha256 hash;
    pb_ostream_t stream{};
    stream.callback=[](pb_ostream_t *s,const pb_byte_t *bytes,size_t n){
        static_cast<Sha256 *>(s->state)->Update(bytes,n);return true;
    };
    stream.state=&hash;stream.max_size=SIZE_MAX;
    if(!pb_encode(&stream,fields,message))return false;
    hash.Final(out);return true;
}

bool ExtractConfigFacts(const ::Config &config,package_storage::ConfigFacts &facts){
    facts.rows=config.game_mode_configs_count;facts.rgbs=config.rgb_configs_count;
    facts.store_format=config.ultimate_profile_store_format;facts.incarnation=config.ultimate_profile_store_incarnation;
    facts.root_format=config.ultimate_profile_root_format;facts.managed_format=config.managed_format;facts.sequence=config.managed_sequence;
    facts.embedded_profiles=config.ultimate_profiles_count;facts.reference_token=config.profile_reference_token;
    facts.reference_id=config.profile_reference_result_id;facts.reference_generation=config.profile_reference_result_store_generation;facts.reference_row=config.profile_reference_result_mode_index;
    static_assert(sizeof(config.profile_reference_digest)==32&&sizeof(config.ultimate_profile_migration_receipt)==32,"source fixed32 digest fields");
    std::memcpy(facts.reference_digest,config.profile_reference_digest,32);std::memcpy(facts.migration_receipt,config.ultimate_profile_migration_receipt,32);
    facts.reference_digest_valid=true;
    if(config.game_mode_configs_count>sizeof(config.game_mode_configs)/sizeof(config.game_mode_configs[0]))return false;
    for(size_t i=0;i<config.game_mode_configs_count;++i){facts.any_row_marker|=config.game_mode_configs[i].managed_format!=0;facts.newer_row_marker|=config.game_mode_configs[i].managed_format>1;}
    return true;
}
struct ConfigEncodingFacts {Sha256 hash;config_wire::Workspace wire;uint32_t crc=~0u;};
__attribute__((noinline)) bool EncodeConfigFacts(const ::Config &config,package_storage::ConfigFacts &facts){
    size_t bytes=0;if(!pb_get_encoded_size(&bytes,Config_fields,&config)||!bytes||bytes>8191)return false;
    ConfigEncodingFacts encoding;pb_ostream_t stream{};
    if(!config_wire::Begin(encoding.wire,bytes))return false;
    stream.state=&encoding;stream.max_size=8191;
    stream.callback=[](pb_ostream_t *out,const pb_byte_t *bytes,size_t n){
        auto &state=*static_cast<ConfigEncodingFacts *>(out->state);
        if(!config_wire::Consume(state.wire,bytes,n))return false;
        state.hash.Update(bytes,n);
        while(n--){state.crc^=*bytes++;for(unsigned j=0;j<8;++j)state.crc=(state.crc>>1)^(0xedb88320u&(0u-(state.crc&1)));}
        return true;
    };
    if(!pb_encode(&stream,Config_fields,&config)||stream.bytes_written!=bytes||!config_wire::Finish(encoding.wire))return false;
    encoding.hash.Final(facts.sha);facts.crc=~encoding.crc;facts.body_bytes=stream.bytes_written;return true;
}

uint32_t AppendCrc(uint32_t crc,uint8_t byte){crc^=byte;for(unsigned i=0;i<8;++i)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1)));return crc;}
struct AppendCursor {
    CheckedStorage::File file;
    bool &failed;
    const char *path=nullptr;
    uint32_t left=0,crc=~0u,expected_crc=0,body_bytes=0;
    uint8_t cache[16]{};
    uint8_t position=0,available=0;
    explicit AppendCursor(bool &f):failed(f){}
    ~AppendCursor(){Close();}
    bool Close(){
        if(!file.opened)return !failed;
        const auto result=CheckedStorage::Close(file);
        if(!result)failed=true;
        return bool(result);
    }
    bool Open(const char *name,uint32_t bytes,uint32_t expected){
        path=name;body_bytes=bytes;expected_crc=expected;size_t size=0;
        auto operation=CheckedStorage::Stat(path,&size,CheckedStorage::Kind::Config);
        if(!operation){failed=true;return false;}
        if(size!=size_t(bytes)+8)return false;
        operation=CheckedStorage::Open(file,path,false,CheckedStorage::Kind::Config);
        if(!operation){failed=true;return false;}
        uint8_t header[8];operation=CheckedStorage::Read(file,header,8);
        if(!operation||operation.bytes!=8){failed=true;return false;}
        if(Get32(header)!=bytes||Get32(header+4)!=expected)return false;
        left=bytes;return true;
    }
    bool Byte(uint8_t &byte){
        if(!left)return false;
        if(position==available){
            const size_t count=left<sizeof(cache)?left:sizeof(cache);
            const auto read=CheckedStorage::Read(file,cache,count);
            if(!read||read.bytes!=count){failed=true;return false;}
            position=0;available=count;
        }
        byte=cache[position++];--left;crc=AppendCrc(crc,byte);return true;
    }
    bool Finish(){
        if(left||position!=available||~crc!=expected_crc)return false;
        size_t size=0;const auto stat=CheckedStorage::Stat(path,&size,CheckedStorage::Kind::Config);
        if(!stat){failed=true;return false;}
        return size==size_t(body_bytes)+8;
    }
};
struct AppendField {
    uint32_t tag=0,length=0;
    uint64_t scalar=0;
    uint8_t key[5]{},size_bytes[5]{},value[10]{};
    uint8_t key_count=0,size_count=0,value_count=0,wire=0;
};
bool AppendVarint(AppendCursor &cursor,uint8_t *raw,uint8_t &count,unsigned maximum,uint64_t &value){
    value=0;count=0;
    for(unsigned i=0;i<maximum;++i){uint8_t byte;if(!cursor.Byte(byte))return false;raw[count++]=byte;
        if(i==9&&byte>1)return false;
        if(maximum==5&&i==4&&byte>15)return false;
        value|=uint64_t(byte&127)<<(7*i);
        if(!(byte&128))return count==1||byte!=0;
    }return false;
}
bool ReadAppendField(AppendCursor &cursor,AppendField &field){
    uint64_t value=0;field={};
    if(!AppendVarint(cursor,field.key,field.key_count,5,value)||!(field.tag=uint32_t(value)>>3))return false;
    field.wire=value&7;
    if(field.wire==0)return AppendVarint(cursor,field.value,field.value_count,10,field.scalar);
    if(field.wire==2){
        if(!AppendVarint(cursor,field.size_bytes,field.size_count,5,value)||value>cursor.left)return false;
        field.length=value;return true;
    }
    if(field.wire==1)field.length=8;
    else if(field.wire==5)field.length=4;
    else return false;
    return field.length<=cursor.left;
}
bool SkipAppendField(AppendCursor &cursor,const AppendField &field){
    for(uint32_t i=0;i<field.length;++i){uint8_t ignored;if(!cursor.Byte(ignored))return false;}return true;
}
struct AppendShape {
    uint8_t rows,rgbs,root,managed;
    uint32_t sequence;
};
struct AppendProgress {uint32_t rows=0,rgbs=0;uint8_t markers=0;};
bool NextAppendField(AppendCursor &cursor,AppendField &field,const AppendShape &shape,
                     uint32_t kept_rows,uint32_t kept_rgbs,AppendProgress &progress,bool &eof){
    eof=false;
    while(cursor.left){
        if(!ReadAppendField(cursor,field))return false;
        if(field.tag==210||field.tag==211||field.tag==212){
            const unsigned shift=field.tag-210;const auto expected=shift==0?shape.root:shift==1?shape.managed:shape.sequence;
            if(field.wire!=0||field.scalar!=expected||(progress.markers&(1u<<shift)))return false;
            progress.markers|=1u<<shift;continue;
        }
        if(field.tag==1){
            if(field.wire!=2||++progress.rows>shape.rows)return false;
            if(progress.rows>kept_rows){if(!SkipAppendField(cursor,field))return false;continue;}
        }
        if(field.tag==5){
            if(field.wire!=2||++progress.rgbs>shape.rgbs)return false;
            if(progress.rgbs>kept_rgbs){if(!SkipAppendField(cursor,field))return false;continue;}
        }
        return true;
    }
    if(progress.rows!=shape.rows||progress.rgbs!=shape.rgbs||
       (shape.root&&!(progress.markers&1))||(shape.managed&&!(progress.markers&2))||
       (shape.sequence&&!(progress.markers&4)))return false;
    eof=true;return cursor.Finish();
}
__attribute__((noinline)) bool CompareAppendFiles(bool &failed,const char *baseline,const char *current,
    const AppendShape &old,const AppendShape &next,uint32_t old_bytes,uint32_t old_crc,uint32_t next_bytes,uint32_t next_crc){
    AppendCursor a(failed),b(failed);
    if(!a.Open(baseline,old_bytes,old_crc)||!b.Open(current,next_bytes,next_crc))return false;
    AppendProgress ap{},bp{};AppendField af{},bf{};
    for(;;){bool aeof=false,beof=false;
        if(!NextAppendField(a,af,old,old.rows,old.rgbs,ap,aeof)||!NextAppendField(b,bf,next,old.rows,old.rgbs,bp,beof))return false;
        if(aeof||beof){
            if(aeof!=beof)return false;
            const bool ac=a.Close(),bc=b.Close();return ac&&bc&&!failed;
        }
        if(af.key_count!=bf.key_count||std::memcmp(af.key,bf.key,af.key_count)||
           af.size_count!=bf.size_count||std::memcmp(af.size_bytes,bf.size_bytes,af.size_count)||
           af.value_count!=bf.value_count||std::memcmp(af.value,bf.value,af.value_count)||af.length!=bf.length)return false;
        for(uint32_t i=0;i<af.length;++i){uint8_t x,y;if(!a.Byte(x)||!b.Byte(y)||x!=y)return false;}
    }
}
struct ProfileComparison {const uint8_t *bytes;size_t length,offset;};
bool CompareProfile(pb_ostream_t *stream,const pb_byte_t *bytes,size_t n) {
    auto &comparison=*static_cast<ProfileComparison *>(stream->state);
    if(comparison.offset>comparison.length||n>comparison.length-comparison.offset||
       std::memcmp(bytes,comparison.bytes+comparison.offset,n))return false;
    comparison.offset+=n;return true;
}
}
GlyphPackageSourceReader::GlyphPackageSourceReader(ProfileStore &store,Persistence &persistence,bool allow_projection_scratch)
 :_store(store),_persistence(persistence){(void)allow_projection_scratch;}
GlyphPackageSourceReader::~GlyphPackageSourceReader(){ClearProfileLease();}
bool GlyphPackageSourceReader::MountedAndConfigured()const{return _persistence.IsAvailable()&&PackageStorageFence::Available();}
bool GlyphPackageSourceReader::ObservationFailed()const{return _failed;}
__attribute__((noinline)) bool GlyphPackageSourceReader::ObjectAt(size_t index,package_storage::NamespaceObject &out,bool &eof){
    out={};eof=false;
    EnumerationSelection selection{index,0,&out,false};
    const auto result=CheckedStorage::Enumerate("/",SelectObject,&selection);
    if(!result){_failed=true;return false;}
    eof=!selection.found;return true;
}
__attribute__((noinline)) package_storage::Probe GlyphPackageSourceReader::Extent(const char *path,size_t &bytes){
    bytes=0;const auto result=CheckedStorage::Stat(path,&bytes);
    if(result.outcome==CheckedStorage::Outcome::NotFound)return package_storage::Probe::Absent;
    if(!result){_failed=true;return package_storage::Probe::Error;}
    return package_storage::Probe::Present;
}
__attribute__((noinline)) bool GlyphPackageSourceReader::Read(const char *path,size_t offset,uint8_t *out,size_t bytes){
    if(offset>INT32_MAX||bytes>SIZE_MAX-offset||(!out&&bytes))return false;
    CheckedStorage::File file;
    auto result=CheckedStorage::Open(file,path,false,CheckedStorage::Kind::Root);
    bool ok=bool(result);
    if(ok)ok=bool(CheckedStorage::Seek(file,offset));
    if(ok){result=CheckedStorage::Read(file,out,bytes);ok=bool(result)&&result.bytes==bytes;}
    // Failed/lost-open acknowledgement may still own a native handle under a
    // different test adapter; exactly one checked close is mandatory if owned.
    if(file.opened){const auto closed=CheckedStorage::Close(file);if(!closed)ok=false;}
    if(!ok)_failed=true;
    return ok;
}
__attribute__((noinline)) bool GlyphPackageSourceReader::LoadNamedConfig(
    const char *path,uint32_t maximum,uint8_t *sha,uint32_t *crc,uint32_t *bytes,bool *source_valid){
    Persistence::PackageConfigFile file;
    if(!SelectConfig(path,file))return false;
    Persistence::PackageConfigFacts facts{};
    bool valid=false;
    ::Config &scratch=_persistence.PackageConfigScratch();
    const auto result=_persistence.ObservePackageConfig(file,scratch,facts,valid);
    if(result==Persistence::LoadResult::StorageFailure)_failed=true;
    if(result!=Persistence::LoadResult::Loaded||facts.bytes>maximum)return false;
    if(sha)std::memcpy(sha,facts.sha,32);
    if(crc)*crc=facts.crc;
    if(bytes)*bytes=facts.bytes;
    if(source_valid)*source_valid=valid;
    return true;
}
__attribute__((noinline)) bool GlyphPackageSourceReader::Config(const char *path,uint32_t maximum,package_storage::ConfigFacts &facts){
    std::memset(static_cast<void *>(&facts),0,sizeof(facts));
    if(!LoadNamedConfig(path,maximum,facts.sha,&facts.crc,&facts.body_bytes,&facts.source_valid))return false;
    // Source-invalid canonical objects still expose positive future markers.
    return ExtractConfigFacts(_persistence.PackageConfigScratch(),facts);
}
__attribute__((noinline)) bool GlyphPackageSourceReader::Row(const char *path,size_t index,package_storage::RowFacts &facts){
    std::memset(static_cast<void *>(&facts),0,sizeof(facts));
    if(!LoadNamedConfig(path,8191))return false;
    const auto &config=_persistence.PackageConfigScratch();
    if(index>=config.game_mode_configs_count||index>=sizeof(config.game_mode_configs)/sizeof(config.game_mode_configs[0]))return false;
    const auto &row=config.game_mode_configs[index];
    facts.mode=row.mode_id;facts.id=row.ultimate_profile_id;facts.engine=row.ultimate_profile_engine;facts.marker=row.managed_format;facts.rgb=row.rgb_config;facts.legacy=row.ultimate_profile_config;facts.custom=row.custom_mode_config;facts.keyboard=row.keyboard_mode_config;
    return HashMessage(GameModeConfig_fields,&row,facts.sha);
}
__attribute__((noinline)) bool GlyphPackageSourceReader::Rgb(const char *path,size_t index,uint8_t sha[32]){
    if(!LoadNamedConfig(path,8191))return false;
    const auto &config=_persistence.PackageConfigScratch();
    if(index>=config.rgb_configs_count||index>=sizeof(config.rgb_configs)/sizeof(config.rgb_configs[0]))return false;
    return HashMessage(RgbConfig_fields,&config.rgb_configs[index],sha);
}
__attribute__((noinline)) void GlyphPackageSourceReader::ClearProfileLease(){
    _store._candidate_profile.native_payload={};_profile_lease.Release();
}
__attribute__((noinline)) bool GlyphPackageSourceReader::ValidateCandidateProfile(){
    ConfigValidationError error;
    // Source schema5 path calls ultimate_native::ValidProfile -> Prepare ->
    // CopyProgram into the existing CandidateWorkspace. No new PreparedView.
    return validate_ultimate_profile_semantics(_store._candidate_profile,error);
}
__attribute__((noinline)) bool GlyphPackageSourceReader::CanonicalCandidateProfile(const uint8_t *bytes,size_t size){
    ProfileComparison comparison{bytes,size,0};pb_ostream_t stream{};
    stream.callback=CompareProfile;stream.state=&comparison;stream.max_size=size;
    return pb_encode(&stream,UltimateProfile_fields,&_store._candidate_profile)&&comparison.offset==size;
}
__attribute__((noinline)) bool GlyphPackageSourceReader::LegacyProfile(const uint8_t *body,size_t bytes){
    ClearProfileLease();
    const bool valid=ultimate_native::DecodeProfile(body,bytes,_store._candidate_profile,_profile_lease)&&
        ValidateCandidateProfile()&&CanonicalCandidateProfile(body,bytes);
    ClearProfileLease();return valid;
}
__attribute__((noinline)) bool GlyphPackageSourceReader::Native(const char *path,size_t index,const uint8_t *record,size_t bytes){
    ClearProfileLease();
    bool source_valid=false;
    if(!RecordValid(record,bytes)||!LoadNamedConfig(path,8191,nullptr,nullptr,nullptr,&source_valid)||!source_valid)return false;
    const auto &config=_persistence.PackageConfigScratch();
    if(index>=config.game_mode_configs_count||index>=sizeof(config.game_mode_configs)/sizeof(config.game_mode_configs[0]))return false;
    const auto &row=config.game_mode_configs[index];
    if(!ProfileStoreNameValid(row.name,sizeof(row.name))||row.mode_id!=MODE_ULTIMATE||row.ultimate_profile_id!=Get32(record+12)||row.ultimate_profile_engine!=1||row.managed_format!=1||row.ultimate_profile_config||row.custom_mode_config||row.keyboard_mode_config||row.rgb_config!=Get32(record+76)||Get32(record+72)!=index)return false;
    const bool valid=ultimate_native::DecodeProfile(record+128,bytes-128,_store._candidate_profile,_profile_lease)&&
        _store._candidate_profile.schema_version==ultimate_native::kSchema&&ValidateCandidateProfile()&&
        ultimate_native::ContextMatches(ultimate_native::CandidateView(),row)&&CanonicalCandidateProfile(record+128,bytes-128);
    ClearProfileLease();return valid;
}

#endif

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
__attribute__((noinline)) bool GlyphPackageSourceReader::DescribeConfig(const ::Config &config,package_storage::ConfigFacts &facts){
    std::memset(static_cast<void *>(&facts),0,sizeof(facts));
    if(!ExtractConfigFacts(config,facts)||!EncodeConfigFacts(config,facts))return false;
    ConfigValidationError error;facts.source_valid=_persistence.ValidateConfig(config,error);return true;
}
#endif

#if defined(GLYPH_PACKAGE_V1) && GLYPH_PACKAGE_V1
__attribute__((noinline)) bool GlyphPackageSourceReader::AppendConfig(const char *baseline,const char *current){
    uint32_t old_crc=0,old_bytes=0,next_crc=0,next_bytes=0;bool valid=false;
    if(!LoadNamedConfig(baseline,8191,nullptr,&old_crc,&old_bytes,&valid)||!valid)return false;
    const auto &first=_persistence.PackageConfigScratch();
    if(first.game_mode_configs_count>=30||first.rgb_configs_count>30||first.managed_sequence==UINT32_MAX||first.ultimate_profile_root_format!=(first.managed_sequence?3u:2u)||first.managed_format!=(first.managed_sequence?1u:0u))return false;
    const AppendShape old{uint8_t(first.game_mode_configs_count),uint8_t(first.rgb_configs_count),uint8_t(first.ultimate_profile_root_format),uint8_t(first.managed_format),first.managed_sequence};
    if(!LoadNamedConfig(current,8191,nullptr,&next_crc,&next_bytes,&valid)||!valid)return false;
    const auto &second=_persistence.PackageConfigScratch();
    if(second.game_mode_configs_count!=unsigned(old.rows)+1||second.rgb_configs_count>30||(second.rgb_configs_count!=old.rgbs&&second.rgb_configs_count!=unsigned(old.rgbs)+1)||second.ultimate_profile_root_format!=3||second.managed_format!=1||second.managed_sequence!=old.sequence+1)return false;
    const AppendShape next{uint8_t(second.game_mode_configs_count),uint8_t(second.rgb_configs_count),3,1,second.managed_sequence};
    return CompareAppendFiles(_failed,baseline,current,old,next,old_bytes,old_crc,next_bytes,next_crc);
}
#endif
