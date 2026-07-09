// Generated-like identity runtime table constants.
// Source-owned firmware constants, not runtime-loaded config.
// Values are source-authored, not generated at runtime.
// Do not treat this as serial/device write behavior.
// Values must remain source-synced with the generated-config/tooling checks.
// Table bodies are adapted from the generated source-owned baseline artifact.

#include "runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"

#define SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, POINT_INDEX) \
    { \
        glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigTables[TABLE_INDEX][POINT_INDEX][0], \
        glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigTables[TABLE_INDEX][POINT_INDEX][1], \
    }

#define SOURCE_OWNED_GENERATED_TABLE(TABLE_SYMBOL, TABLE_INDEX) \
    constexpr StickPoint TABLE_SYMBOL[9] = { \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 0), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 1), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 2), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 3), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 4), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 5), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 6), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 7), \
        SOURCE_OWNED_GENERATED_TABLE_POINT(TABLE_INDEX, 8), \
    }
SOURCE_OWNED_GENERATED_TABLE(kDefaultTable, 0);
SOURCE_OWNED_GENERATED_TABLE(kModeDefaultTable, 1);
SOURCE_OWNED_GENERATED_TABLE(kX1Table, 2);
SOURCE_OWNED_GENERATED_TABLE(kX2Table, 3);
SOURCE_OWNED_GENERATED_TABLE(kMX1Table, 4);
SOURCE_OWNED_GENERATED_TABLE(kMX2Table, 5);
SOURCE_OWNED_GENERATED_TABLE(kY1Table, 6);
SOURCE_OWNED_GENERATED_TABLE(kY2Table, 7);
SOURCE_OWNED_GENERATED_TABLE(kMY1Table, 8);

// RF3 under LF7/LF8 layer is a normal x-only 41px modifier over default y rows.
SOURCE_OWNED_GENERATED_TABLE(kLayerNormalXTable, 9);
SOURCE_OWNED_GENERATED_TABLE(kMLayerNormalXTable, 10);

// RF4 under LF7/LF8 layer is an x-only flipper modifier over default y rows.
SOURCE_OWNED_GENERATED_TABLE(kLayerFlipperTable, 11);
SOURCE_OWNED_GENERATED_TABLE(kMLayerFlipperTable, 12);
SOURCE_OWNED_GENERATED_TABLE(kY1Tilt1Table, 13);
SOURCE_OWNED_GENERATED_TABLE(kMY1Tilt1Table, 14);
SOURCE_OWNED_GENERATED_TABLE(kY1LayerFlipperTable, 15);
SOURCE_OWNED_GENERATED_TABLE(kMY1LayerFlipperTable, 16);
SOURCE_OWNED_GENERATED_TABLE(kY1LayerNormalXTable, 17);
SOURCE_OWNED_GENERATED_TABLE(kMY1LayerNormalXTable, 18);
SOURCE_OWNED_GENERATED_TABLE(kTilt1Table, 19);
SOURCE_OWNED_GENERATED_TABLE(kTilt2Table, 20);
SOURCE_OWNED_GENERATED_TABLE(kTilt3Table, 21);
SOURCE_OWNED_GENERATED_TABLE(kTilt1Minus41Table, 22);

// RT1+RF4 custom modifier. Direction 5 is source-encoded center because table
// selection requires a 9-point table and the requested neutral behavior is unchanged.
SOURCE_OWNED_GENERATED_TABLE(kRT1RF4CustomTable, 23);

SOURCE_OWNED_GENERATED_TABLE(kMTilt1Table, 24);
SOURCE_OWNED_GENERATED_TABLE(kMTilt2Table, 25);
SOURCE_OWNED_GENERATED_TABLE(kMTilt3Table, 26);

// LT5/RF11 provide Z plus a low-magnitude left-stick override for neutral-airdodge-safe output.
SOURCE_OWNED_GENERATED_TABLE(kLt1LowMagnitudeTable, 27);

#undef SOURCE_OWNED_GENERATED_TABLE
#undef SOURCE_OWNED_GENERATED_TABLE_POINT
