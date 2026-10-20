# M1 proposed callback schema — exact ARM ABI probe

Temp-only extension of frozen source976ba2195b72046b32f7ecdd41063e7bad791ded: `UltimateProfile.native_payload` bytes tag8 with `type:FT_CALLBACK`; `GameModeConfig.ultimate_profile_engine` uint32 tag205 with `int_size:IS_8`. No production source/schema/options changed, no installer/build/device action. Fresh exact Nanopb0.4.91 generation succeeds with error-on-unmatched. Complete copied proposed schema/options, fresh generated descriptors, layout source, compile logs, objects, raw nm, exact argv and hashes are in `/private/tmp/glyph-native-proposed-abi/`; `report.json` holds machine results.

|type|baseline ARM short|proposed short|delta|baseline ARM no-short|proposed no-short|delta|
|---|---:|---:|---:|---:|---:|---:|
|Config|31312|31456|144|56152|56288|136|
|GameModeConfig|220|224|4|764|768|4|
|UltimateProfile|2152|2160|8|2344|2352|8|
|ProfileStore|4352|4368|16|4736|4752|16|
|ProfileStoreRequest|2304|2312|8|2496|2504|8|
|ProfileStoreResponse|3024|3032|8|3216|3224|8|

The three known wholeConfig instances +store+request+response gain464bytes ARM-short or440bytes ARM-no-short, before any native owned bodies/metadata/view/frame state. Those native structures are measured separately by designer. Profile callback itself adds8bytes/profile, not the3336-byte body per embedded instance; GameMode field costs4bytes/row duealignment. This is target ARM pointer ABI, not host pointer ABI. Explicit `-fshort-enums` and `-fno-short-enums` were used; compiler default itself is short enum.

Generated macro results:

- `UltimateProfile_size`5740 disappears; fresh header says depends on runtime parameters.
- `ProfileStoreRequest_size`5919 disappears.
- `ProfileStoreResponse_size`6756 disappears.
- `GameModeConfig_size`561→565.
- Config_size already variable, remains variable; condition45/effect92 maximum macros unchanged.

Generated field list is `CALLBACK,SINGULAR,BYTES,native_payload,8`; `UltimateProfile_CALLBACK` changes to `pb_default_field_callback`. Engine field is static UINT32 backed by generated uint8 storage. Fresh generated config.pb.c sourcehash equals baseline because it consists of PB_BIND invocations; changed field definitions/descriptors are generated from the changed header macros when compiling. Pin BOTH header and source, not .c hash alone.

Concrete affected existing bound consumer: `include/core/RuntimeProfileDigest.hpp:18` references disappearing UltimateProfile_size and therefore will not compile unmodified. Observer fixture references it at150. ProfileStore read observer fixture statically asserts disappearing response macro and prints profile/response bounds. The M1 plan must replace these with explicit validated legacy/native/envelope caps and actual callback encoded-size checks; do not replace with unbounded SIZE_MAX in finite frame/digest encoders. Encoded native3336body/3341wrapper is designer measurement, not remeasured by this ABI batch. Native wrapper must be rejected if mixed with legacyfields and callback leases validated before digest/frame encoding. This ABI proof does not prove callback lifetime, payload copying, semantic parity, full firmware RAM/stack, or hardware acceptance.
