#pragma once

#include <cstddef>
#include <cstdint>

// Source-owned runtime config interpreter boundary.
// Source-owned firmware constants, not runtime-loaded config.
// Values are source-authored, not generated at runtime.
// Do not treat this as serial/device write behavior.
// Values must remain source-synced with the checker suite.
// validation-before-use and fallback-to-known-good are explicit in the helpers below.

constexpr const char kRuntimeConfigSchemaName[] = "glyph_runtime_config_interpreter_source_baseline";
constexpr size_t kRuntimeConfigSchemaVersion = 1;
constexpr size_t kRuntimeTableCount = 28;
constexpr size_t kRuntimeTablePointCount = 9;
constexpr size_t kRuntimeTableCenterIndex = 4;

enum class RuntimeTableId : uint8_t {
    Default,
    ModeDefault,
    X1,
    X2,
    MX1,
    MX2,
    Y1,
    Y2,
    MY1,
    LayerNormalX,
    MLayerNormalX,
    LayerFlipper,
    MLayerFlipper,
    Y1Tilt1,
    MY1Tilt1,
    Y1LayerFlipper,
    MY1LayerFlipper,
    Y1LayerNormalX,
    MY1LayerNormalX,
    Tilt1,
    Tilt2,
    Tilt3,
    Tilt1Minus41,
    RT1RF4Custom,
    MTilt1,
    MTilt2,
    MTilt3,
    Lt1LowMagnitude,
};

constexpr const char *kRuntimeTableSymbolNames[kRuntimeTableCount] = {
    "kDefaultTable",
    "kModeDefaultTable",
    "kX1Table",
    "kX2Table",
    "kMX1Table",
    "kMX2Table",
    "kY1Table",
    "kY2Table",
    "kMY1Table",
    "kLayerNormalXTable",
    "kMLayerNormalXTable",
    "kLayerFlipperTable",
    "kMLayerFlipperTable",
    "kY1Tilt1Table",
    "kMY1Tilt1Table",
    "kY1LayerFlipperTable",
    "kMY1LayerFlipperTable",
    "kY1LayerNormalXTable",
    "kMY1LayerNormalXTable",
    "kTilt1Table",
    "kTilt2Table",
    "kTilt3Table",
    "kTilt1Minus41Table",
    "kRT1RF4CustomTable",
    "kMTilt1Table",
    "kMTilt2Table",
    "kMTilt3Table",
    "kLt1LowMagnitudeTable",
};

struct RuntimeTableView {
    RuntimeTableId id;
    const char *symbol_name;
    const StickPoint *table;
    size_t point_count;
};

struct RuntimeConfigView {
    const char *schema_name;
    size_t schema_version;
    const RuntimeTableView *tables;
    size_t table_count;
    RuntimeTableId fallback_table_id;
};

constexpr RuntimeTableView kSourceOwnedCurrentBaselineRuntimeTables[kRuntimeTableCount] = {
    {RuntimeTableId::Default, "kDefaultTable", kDefaultTable, kRuntimeTablePointCount},
    {RuntimeTableId::ModeDefault, "kModeDefaultTable", kModeDefaultTable, kRuntimeTablePointCount},
    {RuntimeTableId::X1, "kX1Table", kX1Table, kRuntimeTablePointCount},
    {RuntimeTableId::X2, "kX2Table", kX2Table, kRuntimeTablePointCount},
    {RuntimeTableId::MX1, "kMX1Table", kMX1Table, kRuntimeTablePointCount},
    {RuntimeTableId::MX2, "kMX2Table", kMX2Table, kRuntimeTablePointCount},
    {RuntimeTableId::Y1, "kY1Table", kY1Table, kRuntimeTablePointCount},
    {RuntimeTableId::Y2, "kY2Table", kY2Table, kRuntimeTablePointCount},
    {RuntimeTableId::MY1, "kMY1Table", kMY1Table, kRuntimeTablePointCount},
    {RuntimeTableId::LayerNormalX, "kLayerNormalXTable", kLayerNormalXTable, kRuntimeTablePointCount},
    {RuntimeTableId::MLayerNormalX, "kMLayerNormalXTable", kMLayerNormalXTable, kRuntimeTablePointCount},
    {RuntimeTableId::LayerFlipper, "kLayerFlipperTable", kLayerFlipperTable, kRuntimeTablePointCount},
    {RuntimeTableId::MLayerFlipper, "kMLayerFlipperTable", kMLayerFlipperTable, kRuntimeTablePointCount},
    {RuntimeTableId::Y1Tilt1, "kY1Tilt1Table", kY1Tilt1Table, kRuntimeTablePointCount},
    {RuntimeTableId::MY1Tilt1, "kMY1Tilt1Table", kMY1Tilt1Table, kRuntimeTablePointCount},
    {RuntimeTableId::Y1LayerFlipper, "kY1LayerFlipperTable", kY1LayerFlipperTable, kRuntimeTablePointCount},
    {RuntimeTableId::MY1LayerFlipper, "kMY1LayerFlipperTable", kMY1LayerFlipperTable, kRuntimeTablePointCount},
    {RuntimeTableId::Y1LayerNormalX, "kY1LayerNormalXTable", kY1LayerNormalXTable, kRuntimeTablePointCount},
    {RuntimeTableId::MY1LayerNormalX, "kMY1LayerNormalXTable", kMY1LayerNormalXTable, kRuntimeTablePointCount},
    {RuntimeTableId::Tilt1, "kTilt1Table", kTilt1Table, kRuntimeTablePointCount},
    {RuntimeTableId::Tilt2, "kTilt2Table", kTilt2Table, kRuntimeTablePointCount},
    {RuntimeTableId::Tilt3, "kTilt3Table", kTilt3Table, kRuntimeTablePointCount},
    {RuntimeTableId::Tilt1Minus41, "kTilt1Minus41Table", kTilt1Minus41Table, kRuntimeTablePointCount},
    {RuntimeTableId::RT1RF4Custom, "kRT1RF4CustomTable", kRT1RF4CustomTable, kRuntimeTablePointCount},
    {RuntimeTableId::MTilt1, "kMTilt1Table", kMTilt1Table, kRuntimeTablePointCount},
    {RuntimeTableId::MTilt2, "kMTilt2Table", kMTilt2Table, kRuntimeTablePointCount},
    {RuntimeTableId::MTilt3, "kMTilt3Table", kMTilt3Table, kRuntimeTablePointCount},
    {RuntimeTableId::Lt1LowMagnitude, "kLt1LowMagnitudeTable", kLt1LowMagnitudeTable, kRuntimeTablePointCount},
};

constexpr RuntimeConfigView kKnownGoodRuntimeConfig = {
    kRuntimeConfigSchemaName,
    1,
    kSourceOwnedCurrentBaselineRuntimeTables,
    kRuntimeTableCount,
    RuntimeTableId::Default
};

constexpr RuntimeConfigView kSourceOwnedCurrentBaselineRuntimeConfig = kKnownGoodRuntimeConfig;

constexpr size_t RuntimeTableIdIndex(RuntimeTableId table_id) {
    return static_cast<size_t>(table_id);
}

constexpr RuntimeTableId kRuntimeTableIdOrder[kRuntimeTableCount] = {
    RuntimeTableId::Default,
    RuntimeTableId::ModeDefault,
    RuntimeTableId::X1,
    RuntimeTableId::X2,
    RuntimeTableId::MX1,
    RuntimeTableId::MX2,
    RuntimeTableId::Y1,
    RuntimeTableId::Y2,
    RuntimeTableId::MY1,
    RuntimeTableId::LayerNormalX,
    RuntimeTableId::MLayerNormalX,
    RuntimeTableId::LayerFlipper,
    RuntimeTableId::MLayerFlipper,
    RuntimeTableId::Y1Tilt1,
    RuntimeTableId::MY1Tilt1,
    RuntimeTableId::Y1LayerFlipper,
    RuntimeTableId::MY1LayerFlipper,
    RuntimeTableId::Y1LayerNormalX,
    RuntimeTableId::MY1LayerNormalX,
    RuntimeTableId::Tilt1,
    RuntimeTableId::Tilt2,
    RuntimeTableId::Tilt3,
    RuntimeTableId::Tilt1Minus41,
    RuntimeTableId::RT1RF4Custom,
    RuntimeTableId::MTilt1,
    RuntimeTableId::MTilt2,
    RuntimeTableId::MTilt3,
    RuntimeTableId::Lt1LowMagnitude,
};

constexpr const char *RuntimeTableIdSymbolName(RuntimeTableId table_id) {
    switch (table_id) {
        case RuntimeTableId::Default:
            return "kDefaultTable";
        case RuntimeTableId::ModeDefault:
            return "kModeDefaultTable";
        case RuntimeTableId::X1:
            return "kX1Table";
        case RuntimeTableId::X2:
            return "kX2Table";
        case RuntimeTableId::MX1:
            return "kMX1Table";
        case RuntimeTableId::MX2:
            return "kMX2Table";
        case RuntimeTableId::Y1:
            return "kY1Table";
        case RuntimeTableId::Y2:
            return "kY2Table";
        case RuntimeTableId::MY1:
            return "kMY1Table";
        case RuntimeTableId::LayerNormalX:
            return "kLayerNormalXTable";
        case RuntimeTableId::MLayerNormalX:
            return "kMLayerNormalXTable";
        case RuntimeTableId::LayerFlipper:
            return "kLayerFlipperTable";
        case RuntimeTableId::MLayerFlipper:
            return "kMLayerFlipperTable";
        case RuntimeTableId::Y1Tilt1:
            return "kY1Tilt1Table";
        case RuntimeTableId::MY1Tilt1:
            return "kMY1Tilt1Table";
        case RuntimeTableId::Y1LayerFlipper:
            return "kY1LayerFlipperTable";
        case RuntimeTableId::MY1LayerFlipper:
            return "kMY1LayerFlipperTable";
        case RuntimeTableId::Y1LayerNormalX:
            return "kY1LayerNormalXTable";
        case RuntimeTableId::MY1LayerNormalX:
            return "kMY1LayerNormalXTable";
        case RuntimeTableId::Tilt1:
            return "kTilt1Table";
        case RuntimeTableId::Tilt2:
            return "kTilt2Table";
        case RuntimeTableId::Tilt3:
            return "kTilt3Table";
        case RuntimeTableId::Tilt1Minus41:
            return "kTilt1Minus41Table";
        case RuntimeTableId::RT1RF4Custom:
            return "kRT1RF4CustomTable";
        case RuntimeTableId::MTilt1:
            return "kMTilt1Table";
        case RuntimeTableId::MTilt2:
            return "kMTilt2Table";
        case RuntimeTableId::MTilt3:
            return "kMTilt3Table";
        case RuntimeTableId::Lt1LowMagnitude:
            return "kLt1LowMagnitudeTable";
    }

    return "kDefaultTable";
}

constexpr bool StringsEqual(const char *lhs, const char *rhs) {
    if (lhs == nullptr || rhs == nullptr) {
        return false;
    }

    while (*lhs != '\0' && *rhs != '\0') {
        if (*lhs != *rhs) {
            return false;
        }
        ++lhs;
        ++rhs;
    }

    return *lhs == *rhs;
}

static_assert(
    StringsEqual(kRuntimeConfigSchemaName, "glyph_runtime_config_interpreter_source_baseline"),
    "runtime config schema marker must stay source-synced"
);

constexpr const RuntimeTableView *FindRuntimeTableView(const RuntimeConfigView &config, RuntimeTableId table_id) {
    if (config.tables == nullptr) {
        return nullptr;
    }

    const size_t target_index = RuntimeTableIdIndex(table_id);
    if (target_index >= kRuntimeTableCount) {
        return nullptr;
    }

    for (size_t index = 0; index < config.table_count; ++index) {
        const RuntimeTableView &table_view = config.tables[index];
        if (RuntimeTableIdIndex(table_view.id) == target_index) {
            return &table_view;
        }
    }

    return nullptr;
}

constexpr bool ValidateRuntimeConfigView(const RuntimeConfigView &config) {
    if (!StringsEqual(config.schema_name, kRuntimeConfigSchemaName)) {
        return false;
    }
    if (config.schema_version != kRuntimeConfigSchemaVersion) {
        return false;
    }
    if (config.table_count != kRuntimeTableCount) {
        return false;
    }
    if (config.tables == nullptr) {
        return false;
    }

    const size_t fallback_index = RuntimeTableIdIndex(config.fallback_table_id);
    if (fallback_index >= kRuntimeTableCount) {
        return false;
    }

    bool seen[kRuntimeTableCount] = {};
    for (size_t index = 0; index < config.table_count; ++index) {
        const RuntimeTableView &table_view = config.tables[index];
        if (table_view.symbol_name == nullptr) {
            return false;
        }
        if (!StringsEqual(table_view.symbol_name, kRuntimeTableSymbolNames[index])) {
            return false;
        }
        if (table_view.id != kRuntimeTableIdOrder[index]) {
            return false;
        }
        const size_t table_index = RuntimeTableIdIndex(table_view.id);
        if (table_index >= kRuntimeTableCount) {
            return false;
        }
        if (seen[table_index]) {
            return false;
        }
        seen[table_index] = true;

        if (table_view.table == nullptr) {
            return false;
        }
        if (table_view.point_count != kRuntimeTablePointCount) {
            return false;
        }
        if (!StringsEqual(table_view.symbol_name, RuntimeTableIdSymbolName(table_view.id))) {
            return false;
        }

        // StickPoint coordinates are byte-typed (uint8_t) in firmware.
        // Source-parsed table literals are byte-range checked (0..255) by
        // tools/extract_glyph_identity_runtime_tables.py and
        // tools/check_glyph_identity_runtime_table_source_sync.py before firmware merge.
        // Future runtime-loaded config parsing must validate raw values before narrowing
        // to uint8_t before invoking this boundary.
    }

    if (!seen[fallback_index]) {
        return false;
    }
    for (size_t index = 0; index < kRuntimeTableCount; ++index) {
        if (!seen[index]) {
            return false;
        }
    }

    return true;
}

constexpr const RuntimeConfigView &ResolveRuntimeConfigView(const RuntimeConfigView &config) {
    return ValidateRuntimeConfigView(config) ? config : kKnownGoodRuntimeConfig;
}

constexpr const StickPoint *LookupRuntimeTable(const RuntimeConfigView &config, RuntimeTableId table_id) {
    const RuntimeConfigView &resolved_config = ResolveRuntimeConfigView(config);

    const RuntimeTableView *table_view = FindRuntimeTableView(resolved_config, table_id);
    if (table_view != nullptr && table_view->table != nullptr && table_view->point_count == kRuntimeTablePointCount) {
        return table_view->table;
    }

    const RuntimeTableView *fallback_view = FindRuntimeTableView(resolved_config, resolved_config.fallback_table_id);
    if (fallback_view != nullptr && fallback_view->table != nullptr && fallback_view->point_count == kRuntimeTablePointCount) {
        return fallback_view->table;
    }

    const RuntimeTableView *known_good_fallback_view =
        FindRuntimeTableView(kKnownGoodRuntimeConfig, kKnownGoodRuntimeConfig.fallback_table_id);
    if (known_good_fallback_view != nullptr && known_good_fallback_view->table != nullptr) {
        return known_good_fallback_view->table;
    }

    return kDefaultTable;
}

constexpr StickPoint LookupRuntimeStickPoint(
    const RuntimeConfigView &config,
    RuntimeTableId table_id,
    size_t direction_index
) {
    const StickPoint *table = LookupRuntimeTable(config, table_id);
    const size_t clamped_direction_index = direction_index < kRuntimeTablePointCount
        ? direction_index
        : kRuntimeTableCenterIndex;
    return table[clamped_direction_index];
}

static_assert(ValidateRuntimeConfigView(kKnownGoodRuntimeConfig), "known-good runtime config must validate");
static_assert(
    ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig),
    "source-owned current baseline runtime config must validate"
);
