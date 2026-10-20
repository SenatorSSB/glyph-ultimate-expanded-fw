# M1 exact production Nanopb reconciliation

Result: **NO NUMERIC ABI OR NATIVE LAYOUT DRIFT** from earlier explicitly Nanopb0.4.91 probes to freshly built production dependency Nanopb0.4.92. This is isolated schema/descriptor/ABI measurement, not firmware source implementation, a firmware rebuild, full-stack bound or hardware acceptance. Parent reports exact baseline976ba2195b72046b32f7ecdd41063e7bad791ded owner-terminal build PASS RAM187344/flash477452; this worker did not rerun build/install.

Inputs verified before generation:

- Chapter `.pio/libdeps/glyph_mk6/Nanopb/.piopm` version0.4.92.
- Actual pb.h SHA256 `e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2`.
- Actual generator SHA256 `67d3c5e6de1e5dbd9f45bb4e5b7055d888d1afd6d6e1690791ab8607b6c6b738`.
- Installed chapter ARM toolchain5.120300.240127. Explicit `-fshort-enums` and `-fno-short-enums` probes.

Fresh baseline generated files are **byte-identical** to owner's actual new baseline build `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.{h,c}`: headerSHA `c2a289d304a74c2a875d3fb2413a9afc0880f758cb1f5d7781c450b7841f51a0`, sourceSHA `fce08045cd7da7795357dff85827a634ef6a7f3fb21ec32e89b0e84817c54750`. This independently reconciles generator/options/bindings to the actual baseline descriptor inputs.

Proposed temp-only schema remains exactly native_payload bytescallbacktag8 and GameModeConfig ultimate_profile_engine tag205 intsize8; no production schema changed. Both fresh generated descriptor translation units compile to isolated ARM objects successfully. Native callback field is `pb_callback_t`; field descriptor `CALLBACK,SINGULAR,BYTES,native_payload,8`; profile callback `pb_default_field_callback`. Engine is generated uint8_t with static UINT32 wire field205. Shapes/counts match earlier measurements.

|type|baseline short|proposed short|delta|baseline no-short|proposed no-short|delta|
|---|---:|---:|---:|---:|---:|---:|
|Config|31312|31456|144|56152|56288|136|
|GameModeConfig|220|224|4|764|768|4|
|UltimateProfile|2152|2160|8|2344|2352|8|
|ProfileStore|4352|4368|16|4736|4752|16|
|ProfileStoreRequest|2304|2312|8|2496|2504|8|
|ProfileStoreResponse|3024|3032|8|3216|3224|8|

Every individual type previously measured has zero drift for each ABI, including table22,condition22,role24,routing2,rule26 and output effect/program36/436(short),52/628(no-short). Known threeConfig+store+request+response growth remains464bytes short/440bytes no-short before nativeowned/view/frame state.

Fresh maximum macro behavior also unchanged: UltimateProfile_size5740,ProfileStoreRequest_size5919,ProfileStoreResponse_size6756 disappear under callback; GameModeConfig_size561→565; Config_size remains variable; condition45/effect92 unchanged. Existing RuntimeProfileDigest.hpp and directly affected fixtures still need their reviewed explicit bounded replacements; variable callbacks do not provide an automatic protobuf maximum bound.

Recompiled designer's concrete native ownership/view/frame source against these exact production dependencies and proposed descriptors:

|structure witness|bytes, both ABIs|
|---|---:|
|prepared view|556|
|owned active program|3892|
|candidate workspace|3900|
|active+candidate|7792|
|frame state|132|
|resolved input context|12|
|two input copies|48|
|validation locals|180|

All native witness values and static assertions match prior measurements (zero drift). Additive known static witness growth7792+464=8256bytes short is arithmetic only; final source build/link/stack and callbackownership remain gates. Frame/locals are objectsizeof measurements, not composed stack-frame measurements. Bytecodec max3336body/3341wrapper is independent of Nanopb enum ABI and unchanged; its semantic/resource acceptance is the design/converter proof, not inferred solely from these layouts.

Evidence directory `/private/tmp/glyph-native-production-abi/` contains baseline/proposed copied exact schemas/options, fresh generated descriptors, C descriptor objects, C++ layout objects, per-command logs and raw nm, native layout source/objects/logs, report.json hashes/argv/drift, reproducible run.py. An initial native-layout compile lacked the temporary stdlib.hpp include directory; that isolated probe was corrected by adding its local include path, then all assertions passed. No production source, Git state, build, installer/network or device action changed in this reconciliation. Tracked status was clean afterward.
