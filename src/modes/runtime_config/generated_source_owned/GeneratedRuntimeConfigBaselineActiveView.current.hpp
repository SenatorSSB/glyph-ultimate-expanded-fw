#pragma once

#include "GeneratedRuntimeConfigBaseline.current.hpp"

// generated source-owned RuntimeConfigView wrapper
// source-owned immutable active diagnostic data
// table pointers target generated source-owned StickPoint tables, not RAM storage

constexpr StickPoint GeneratedSourceOwnedBaselinePoint(size_t table_index, size_t point_index) {
    return {
        glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigTables[table_index][point_index][0],
        glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigTables[table_index][point_index][1],
    };
}

static_assert(
    glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigTableCount == kRuntimeTableCount,
    "generated source-owned baseline table count must match RuntimeConfigView shape"
);
static_assert(
    glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigPointsPerTable == kRuntimeTablePointCount,
    "generated source-owned baseline point count must match RuntimeConfigView shape"
);
static_assert(
    glyph::runtime_config::generated_source_owned::fixtures::kGeneratedSourceOwnedRuntimeConfigAxesPerPoint == 2u,
    "generated source-owned baseline artifact must remain two-axis stick data"
);

constexpr StickPoint kGeneratedSourceOwnedBaselineRuntimePoints[kRuntimeTableCount][kRuntimeTablePointCount] = {
    {
        GeneratedSourceOwnedBaselinePoint(0, 0), GeneratedSourceOwnedBaselinePoint(0, 1), GeneratedSourceOwnedBaselinePoint(0, 2),
        GeneratedSourceOwnedBaselinePoint(0, 3), GeneratedSourceOwnedBaselinePoint(0, 4), GeneratedSourceOwnedBaselinePoint(0, 5),
        GeneratedSourceOwnedBaselinePoint(0, 6), GeneratedSourceOwnedBaselinePoint(0, 7), GeneratedSourceOwnedBaselinePoint(0, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(1, 0), GeneratedSourceOwnedBaselinePoint(1, 1), GeneratedSourceOwnedBaselinePoint(1, 2),
        GeneratedSourceOwnedBaselinePoint(1, 3), GeneratedSourceOwnedBaselinePoint(1, 4), GeneratedSourceOwnedBaselinePoint(1, 5),
        GeneratedSourceOwnedBaselinePoint(1, 6), GeneratedSourceOwnedBaselinePoint(1, 7), GeneratedSourceOwnedBaselinePoint(1, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(2, 0), GeneratedSourceOwnedBaselinePoint(2, 1), GeneratedSourceOwnedBaselinePoint(2, 2),
        GeneratedSourceOwnedBaselinePoint(2, 3), GeneratedSourceOwnedBaselinePoint(2, 4), GeneratedSourceOwnedBaselinePoint(2, 5),
        GeneratedSourceOwnedBaselinePoint(2, 6), GeneratedSourceOwnedBaselinePoint(2, 7), GeneratedSourceOwnedBaselinePoint(2, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(3, 0), GeneratedSourceOwnedBaselinePoint(3, 1), GeneratedSourceOwnedBaselinePoint(3, 2),
        GeneratedSourceOwnedBaselinePoint(3, 3), GeneratedSourceOwnedBaselinePoint(3, 4), GeneratedSourceOwnedBaselinePoint(3, 5),
        GeneratedSourceOwnedBaselinePoint(3, 6), GeneratedSourceOwnedBaselinePoint(3, 7), GeneratedSourceOwnedBaselinePoint(3, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(4, 0), GeneratedSourceOwnedBaselinePoint(4, 1), GeneratedSourceOwnedBaselinePoint(4, 2),
        GeneratedSourceOwnedBaselinePoint(4, 3), GeneratedSourceOwnedBaselinePoint(4, 4), GeneratedSourceOwnedBaselinePoint(4, 5),
        GeneratedSourceOwnedBaselinePoint(4, 6), GeneratedSourceOwnedBaselinePoint(4, 7), GeneratedSourceOwnedBaselinePoint(4, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(5, 0), GeneratedSourceOwnedBaselinePoint(5, 1), GeneratedSourceOwnedBaselinePoint(5, 2),
        GeneratedSourceOwnedBaselinePoint(5, 3), GeneratedSourceOwnedBaselinePoint(5, 4), GeneratedSourceOwnedBaselinePoint(5, 5),
        GeneratedSourceOwnedBaselinePoint(5, 6), GeneratedSourceOwnedBaselinePoint(5, 7), GeneratedSourceOwnedBaselinePoint(5, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(6, 0), GeneratedSourceOwnedBaselinePoint(6, 1), GeneratedSourceOwnedBaselinePoint(6, 2),
        GeneratedSourceOwnedBaselinePoint(6, 3), GeneratedSourceOwnedBaselinePoint(6, 4), GeneratedSourceOwnedBaselinePoint(6, 5),
        GeneratedSourceOwnedBaselinePoint(6, 6), GeneratedSourceOwnedBaselinePoint(6, 7), GeneratedSourceOwnedBaselinePoint(6, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(7, 0), GeneratedSourceOwnedBaselinePoint(7, 1), GeneratedSourceOwnedBaselinePoint(7, 2),
        GeneratedSourceOwnedBaselinePoint(7, 3), GeneratedSourceOwnedBaselinePoint(7, 4), GeneratedSourceOwnedBaselinePoint(7, 5),
        GeneratedSourceOwnedBaselinePoint(7, 6), GeneratedSourceOwnedBaselinePoint(7, 7), GeneratedSourceOwnedBaselinePoint(7, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(8, 0), GeneratedSourceOwnedBaselinePoint(8, 1), GeneratedSourceOwnedBaselinePoint(8, 2),
        GeneratedSourceOwnedBaselinePoint(8, 3), GeneratedSourceOwnedBaselinePoint(8, 4), GeneratedSourceOwnedBaselinePoint(8, 5),
        GeneratedSourceOwnedBaselinePoint(8, 6), GeneratedSourceOwnedBaselinePoint(8, 7), GeneratedSourceOwnedBaselinePoint(8, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(9, 0), GeneratedSourceOwnedBaselinePoint(9, 1), GeneratedSourceOwnedBaselinePoint(9, 2),
        GeneratedSourceOwnedBaselinePoint(9, 3), GeneratedSourceOwnedBaselinePoint(9, 4), GeneratedSourceOwnedBaselinePoint(9, 5),
        GeneratedSourceOwnedBaselinePoint(9, 6), GeneratedSourceOwnedBaselinePoint(9, 7), GeneratedSourceOwnedBaselinePoint(9, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(10, 0), GeneratedSourceOwnedBaselinePoint(10, 1), GeneratedSourceOwnedBaselinePoint(10, 2),
        GeneratedSourceOwnedBaselinePoint(10, 3), GeneratedSourceOwnedBaselinePoint(10, 4), GeneratedSourceOwnedBaselinePoint(10, 5),
        GeneratedSourceOwnedBaselinePoint(10, 6), GeneratedSourceOwnedBaselinePoint(10, 7), GeneratedSourceOwnedBaselinePoint(10, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(11, 0), GeneratedSourceOwnedBaselinePoint(11, 1), GeneratedSourceOwnedBaselinePoint(11, 2),
        GeneratedSourceOwnedBaselinePoint(11, 3), GeneratedSourceOwnedBaselinePoint(11, 4), GeneratedSourceOwnedBaselinePoint(11, 5),
        GeneratedSourceOwnedBaselinePoint(11, 6), GeneratedSourceOwnedBaselinePoint(11, 7), GeneratedSourceOwnedBaselinePoint(11, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(12, 0), GeneratedSourceOwnedBaselinePoint(12, 1), GeneratedSourceOwnedBaselinePoint(12, 2),
        GeneratedSourceOwnedBaselinePoint(12, 3), GeneratedSourceOwnedBaselinePoint(12, 4), GeneratedSourceOwnedBaselinePoint(12, 5),
        GeneratedSourceOwnedBaselinePoint(12, 6), GeneratedSourceOwnedBaselinePoint(12, 7), GeneratedSourceOwnedBaselinePoint(12, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(13, 0), GeneratedSourceOwnedBaselinePoint(13, 1), GeneratedSourceOwnedBaselinePoint(13, 2),
        GeneratedSourceOwnedBaselinePoint(13, 3), GeneratedSourceOwnedBaselinePoint(13, 4), GeneratedSourceOwnedBaselinePoint(13, 5),
        GeneratedSourceOwnedBaselinePoint(13, 6), GeneratedSourceOwnedBaselinePoint(13, 7), GeneratedSourceOwnedBaselinePoint(13, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(14, 0), GeneratedSourceOwnedBaselinePoint(14, 1), GeneratedSourceOwnedBaselinePoint(14, 2),
        GeneratedSourceOwnedBaselinePoint(14, 3), GeneratedSourceOwnedBaselinePoint(14, 4), GeneratedSourceOwnedBaselinePoint(14, 5),
        GeneratedSourceOwnedBaselinePoint(14, 6), GeneratedSourceOwnedBaselinePoint(14, 7), GeneratedSourceOwnedBaselinePoint(14, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(15, 0), GeneratedSourceOwnedBaselinePoint(15, 1), GeneratedSourceOwnedBaselinePoint(15, 2),
        GeneratedSourceOwnedBaselinePoint(15, 3), GeneratedSourceOwnedBaselinePoint(15, 4), GeneratedSourceOwnedBaselinePoint(15, 5),
        GeneratedSourceOwnedBaselinePoint(15, 6), GeneratedSourceOwnedBaselinePoint(15, 7), GeneratedSourceOwnedBaselinePoint(15, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(16, 0), GeneratedSourceOwnedBaselinePoint(16, 1), GeneratedSourceOwnedBaselinePoint(16, 2),
        GeneratedSourceOwnedBaselinePoint(16, 3), GeneratedSourceOwnedBaselinePoint(16, 4), GeneratedSourceOwnedBaselinePoint(16, 5),
        GeneratedSourceOwnedBaselinePoint(16, 6), GeneratedSourceOwnedBaselinePoint(16, 7), GeneratedSourceOwnedBaselinePoint(16, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(17, 0), GeneratedSourceOwnedBaselinePoint(17, 1), GeneratedSourceOwnedBaselinePoint(17, 2),
        GeneratedSourceOwnedBaselinePoint(17, 3), GeneratedSourceOwnedBaselinePoint(17, 4), GeneratedSourceOwnedBaselinePoint(17, 5),
        GeneratedSourceOwnedBaselinePoint(17, 6), GeneratedSourceOwnedBaselinePoint(17, 7), GeneratedSourceOwnedBaselinePoint(17, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(18, 0), GeneratedSourceOwnedBaselinePoint(18, 1), GeneratedSourceOwnedBaselinePoint(18, 2),
        GeneratedSourceOwnedBaselinePoint(18, 3), GeneratedSourceOwnedBaselinePoint(18, 4), GeneratedSourceOwnedBaselinePoint(18, 5),
        GeneratedSourceOwnedBaselinePoint(18, 6), GeneratedSourceOwnedBaselinePoint(18, 7), GeneratedSourceOwnedBaselinePoint(18, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(19, 0), GeneratedSourceOwnedBaselinePoint(19, 1), GeneratedSourceOwnedBaselinePoint(19, 2),
        GeneratedSourceOwnedBaselinePoint(19, 3), GeneratedSourceOwnedBaselinePoint(19, 4), GeneratedSourceOwnedBaselinePoint(19, 5),
        GeneratedSourceOwnedBaselinePoint(19, 6), GeneratedSourceOwnedBaselinePoint(19, 7), GeneratedSourceOwnedBaselinePoint(19, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(20, 0), GeneratedSourceOwnedBaselinePoint(20, 1), GeneratedSourceOwnedBaselinePoint(20, 2),
        GeneratedSourceOwnedBaselinePoint(20, 3), GeneratedSourceOwnedBaselinePoint(20, 4), GeneratedSourceOwnedBaselinePoint(20, 5),
        GeneratedSourceOwnedBaselinePoint(20, 6), GeneratedSourceOwnedBaselinePoint(20, 7), GeneratedSourceOwnedBaselinePoint(20, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(21, 0), GeneratedSourceOwnedBaselinePoint(21, 1), GeneratedSourceOwnedBaselinePoint(21, 2),
        GeneratedSourceOwnedBaselinePoint(21, 3), GeneratedSourceOwnedBaselinePoint(21, 4), GeneratedSourceOwnedBaselinePoint(21, 5),
        GeneratedSourceOwnedBaselinePoint(21, 6), GeneratedSourceOwnedBaselinePoint(21, 7), GeneratedSourceOwnedBaselinePoint(21, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(22, 0), GeneratedSourceOwnedBaselinePoint(22, 1), GeneratedSourceOwnedBaselinePoint(22, 2),
        GeneratedSourceOwnedBaselinePoint(22, 3), GeneratedSourceOwnedBaselinePoint(22, 4), GeneratedSourceOwnedBaselinePoint(22, 5),
        GeneratedSourceOwnedBaselinePoint(22, 6), GeneratedSourceOwnedBaselinePoint(22, 7), GeneratedSourceOwnedBaselinePoint(22, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(23, 0), GeneratedSourceOwnedBaselinePoint(23, 1), GeneratedSourceOwnedBaselinePoint(23, 2),
        GeneratedSourceOwnedBaselinePoint(23, 3), GeneratedSourceOwnedBaselinePoint(23, 4), GeneratedSourceOwnedBaselinePoint(23, 5),
        GeneratedSourceOwnedBaselinePoint(23, 6), GeneratedSourceOwnedBaselinePoint(23, 7), GeneratedSourceOwnedBaselinePoint(23, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(24, 0), GeneratedSourceOwnedBaselinePoint(24, 1), GeneratedSourceOwnedBaselinePoint(24, 2),
        GeneratedSourceOwnedBaselinePoint(24, 3), GeneratedSourceOwnedBaselinePoint(24, 4), GeneratedSourceOwnedBaselinePoint(24, 5),
        GeneratedSourceOwnedBaselinePoint(24, 6), GeneratedSourceOwnedBaselinePoint(24, 7), GeneratedSourceOwnedBaselinePoint(24, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(25, 0), GeneratedSourceOwnedBaselinePoint(25, 1), GeneratedSourceOwnedBaselinePoint(25, 2),
        GeneratedSourceOwnedBaselinePoint(25, 3), GeneratedSourceOwnedBaselinePoint(25, 4), GeneratedSourceOwnedBaselinePoint(25, 5),
        GeneratedSourceOwnedBaselinePoint(25, 6), GeneratedSourceOwnedBaselinePoint(25, 7), GeneratedSourceOwnedBaselinePoint(25, 8),
    },
    {
        GeneratedSourceOwnedBaselinePoint(26, 0), GeneratedSourceOwnedBaselinePoint(26, 1), GeneratedSourceOwnedBaselinePoint(26, 2),
        GeneratedSourceOwnedBaselinePoint(26, 3), GeneratedSourceOwnedBaselinePoint(26, 4), GeneratedSourceOwnedBaselinePoint(26, 5),
        GeneratedSourceOwnedBaselinePoint(26, 6), GeneratedSourceOwnedBaselinePoint(26, 7), GeneratedSourceOwnedBaselinePoint(26, 8),
    },
};

constexpr RuntimeTableView kGeneratedSourceOwnedBaselineRuntimeTables[kRuntimeTableCount] = {
    {RuntimeTableId::Default, "kDefaultTable", kGeneratedSourceOwnedBaselineRuntimePoints[0], kRuntimeTablePointCount},
    {RuntimeTableId::ModeDefault, "kModeDefaultTable", kGeneratedSourceOwnedBaselineRuntimePoints[1], kRuntimeTablePointCount},
    {RuntimeTableId::X1, "kX1Table", kGeneratedSourceOwnedBaselineRuntimePoints[2], kRuntimeTablePointCount},
    {RuntimeTableId::X2, "kX2Table", kGeneratedSourceOwnedBaselineRuntimePoints[3], kRuntimeTablePointCount},
    {RuntimeTableId::MX1, "kMX1Table", kGeneratedSourceOwnedBaselineRuntimePoints[4], kRuntimeTablePointCount},
    {RuntimeTableId::MX2, "kMX2Table", kGeneratedSourceOwnedBaselineRuntimePoints[5], kRuntimeTablePointCount},
    {RuntimeTableId::Y1, "kY1Table", kGeneratedSourceOwnedBaselineRuntimePoints[6], kRuntimeTablePointCount},
    {RuntimeTableId::MY1, "kMY1Table", kGeneratedSourceOwnedBaselineRuntimePoints[7], kRuntimeTablePointCount},
    {RuntimeTableId::LayerNormalX, "kLayerNormalXTable", kGeneratedSourceOwnedBaselineRuntimePoints[8], kRuntimeTablePointCount},
    {RuntimeTableId::MLayerNormalX, "kMLayerNormalXTable", kGeneratedSourceOwnedBaselineRuntimePoints[9], kRuntimeTablePointCount},
    {RuntimeTableId::LayerFlipper, "kLayerFlipperTable", kGeneratedSourceOwnedBaselineRuntimePoints[10], kRuntimeTablePointCount},
    {RuntimeTableId::MLayerFlipper, "kMLayerFlipperTable", kGeneratedSourceOwnedBaselineRuntimePoints[11], kRuntimeTablePointCount},
    {RuntimeTableId::Y1Tilt1, "kY1Tilt1Table", kGeneratedSourceOwnedBaselineRuntimePoints[12], kRuntimeTablePointCount},
    {RuntimeTableId::MY1Tilt1, "kMY1Tilt1Table", kGeneratedSourceOwnedBaselineRuntimePoints[13], kRuntimeTablePointCount},
    {RuntimeTableId::Y1LayerFlipper, "kY1LayerFlipperTable", kGeneratedSourceOwnedBaselineRuntimePoints[14], kRuntimeTablePointCount},
    {RuntimeTableId::MY1LayerFlipper, "kMY1LayerFlipperTable", kGeneratedSourceOwnedBaselineRuntimePoints[15], kRuntimeTablePointCount},
    {RuntimeTableId::Y1LayerNormalX, "kY1LayerNormalXTable", kGeneratedSourceOwnedBaselineRuntimePoints[16], kRuntimeTablePointCount},
    {RuntimeTableId::MY1LayerNormalX, "kMY1LayerNormalXTable", kGeneratedSourceOwnedBaselineRuntimePoints[17], kRuntimeTablePointCount},
    {RuntimeTableId::Tilt1, "kTilt1Table", kGeneratedSourceOwnedBaselineRuntimePoints[18], kRuntimeTablePointCount},
    {RuntimeTableId::Tilt2, "kTilt2Table", kGeneratedSourceOwnedBaselineRuntimePoints[19], kRuntimeTablePointCount},
    {RuntimeTableId::Tilt3, "kTilt3Table", kGeneratedSourceOwnedBaselineRuntimePoints[20], kRuntimeTablePointCount},
    {RuntimeTableId::Tilt1Minus41, "kTilt1Minus41Table", kGeneratedSourceOwnedBaselineRuntimePoints[21], kRuntimeTablePointCount},
    {RuntimeTableId::RT1RF4Custom, "kRT1RF4CustomTable", kGeneratedSourceOwnedBaselineRuntimePoints[22], kRuntimeTablePointCount},
    {RuntimeTableId::MTilt1, "kMTilt1Table", kGeneratedSourceOwnedBaselineRuntimePoints[23], kRuntimeTablePointCount},
    {RuntimeTableId::MTilt2, "kMTilt2Table", kGeneratedSourceOwnedBaselineRuntimePoints[24], kRuntimeTablePointCount},
    {RuntimeTableId::MTilt3, "kMTilt3Table", kGeneratedSourceOwnedBaselineRuntimePoints[25], kRuntimeTablePointCount},
    {RuntimeTableId::Lt1LowMagnitude, "kLt1LowMagnitudeTable", kGeneratedSourceOwnedBaselineRuntimePoints[26], kRuntimeTablePointCount},
};

constexpr RuntimeConfigView kGeneratedSourceOwnedBaselineRuntimeConfig = {
    kRuntimeConfigSchemaName,
    kRuntimeConfigSchemaVersion,
    kGeneratedSourceOwnedBaselineRuntimeTables,
    kRuntimeTableCount,
    RuntimeTableId::Default,
};

static_assert(
    ValidateRuntimeConfigView(kGeneratedSourceOwnedBaselineRuntimeConfig),
    "generated source-owned baseline RuntimeConfigView must validate"
);
