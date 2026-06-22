// Generated-like identity runtime table constants.
// Source-owned firmware constants, not runtime-loaded config.
// Values are source-authored, not generated at runtime.
// Do not treat this as serial/device write behavior.
// Values must remain source-synced with the generated-config/tooling checks.

constexpr StickPoint kDefaultTable[9] = {
    {61, 51}, {128, 51}, {195, 51},
    {61, 128}, {128, 128}, {195, 128},
    {61, 195}, {128, 195}, {195, 195},
};

constexpr StickPoint kModeDefaultTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kX1Table[9] = {
    {98, 100}, {128, 100}, {158, 100},
    {98, 128}, {128, 128}, {158, 128},
    {98, 156}, {128, 156}, {158, 156},
};

constexpr StickPoint kX2Table[9] = {
    {81, 81}, {128, 81}, {175, 81},
    {81, 128}, {128, 128}, {175, 128},
    {81, 175}, {128, 175}, {175, 175},
};

constexpr StickPoint kMX1Table[9] = {
    {92, 92}, {128, 92}, {164, 92},
    {92, 128}, {128, 128}, {164, 128},
    {92, 164}, {128, 164}, {164, 164},
};

constexpr StickPoint kMX2Table[9] = {
    {71, 71}, {128, 71}, {185, 71},
    {71, 128}, {128, 128}, {185, 128},
    {71, 185}, {128, 185}, {185, 185},
};

constexpr StickPoint kY1Table[9] = {
    {98, 100}, {128, 100}, {158, 100},
    {98, 128}, {128, 128}, {158, 128},
    {98, 156}, {128, 156}, {158, 156},
};

constexpr StickPoint kMY1Table[9] = {
    {92, 92}, {128, 92}, {164, 92},
    {92, 128}, {128, 128}, {164, 128},
    {92, 164}, {128, 164}, {164, 164},
};

// Friend profile branch: unused layer tables carry the provided X3/Y3 table.
constexpr StickPoint kLayerNormalXTable[9] = {
    {69, 69}, {128, 69}, {187, 69},
    {69, 128}, {128, 128}, {187, 128},
    {69, 187}, {128, 187}, {187, 187},
};

constexpr StickPoint kMLayerNormalXTable[9] = {
    {87, 87}, {128, 87}, {169, 87},
    {87, 128}, {128, 128}, {169, 128},
    {87, 169}, {128, 169}, {169, 169},
};

// Friend profile branch: unused layer-flipper tables carry the same X3/Y3 data.
constexpr StickPoint kLayerFlipperTable[9] = {
    {69, 69}, {128, 69}, {187, 69},
    {69, 128}, {128, 128}, {187, 128},
    {69, 187}, {128, 187}, {187, 187},
};

constexpr StickPoint kMLayerFlipperTable[9] = {
    {87, 87}, {128, 87}, {169, 87},
    {87, 128}, {128, 128}, {169, 128},
    {87, 169}, {128, 169}, {169, 169},
};

constexpr StickPoint kY1Tilt1Table[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kMY1Tilt1Table[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kY1LayerFlipperTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kMY1LayerFlipperTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kY1LayerNormalXTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kMY1LayerNormalXTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kTilt1Table[9] = {
    {69, 87}, {128, 87}, {187, 87},
    {69, 128}, {128, 128}, {187, 128},
    {69, 167}, {128, 167}, {187, 167},
};

constexpr StickPoint kTilt2Table[9] = {
    {59, 88}, {128, 88}, {197, 88},
    {59, 128}, {128, 128}, {197, 128},
    {59, 168}, {128, 168}, {197, 168},
};

constexpr StickPoint kTilt3Table[9] = {
    {92, 83}, {128, 83}, {164, 83},
    {92, 128}, {128, 128}, {164, 128},
    {92, 172}, {128, 172}, {164, 172},
};

constexpr StickPoint kTilt1Minus41Table[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

// No friend-specific composite left-stick table was provided.
constexpr StickPoint kRT1RF4CustomTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};

constexpr StickPoint kMTilt1Table[9] = {
    {87, 94}, {128, 94}, {169, 94},
    {87, 128}, {128, 128}, {169, 128},
    {87, 162}, {128, 162}, {169, 162},
};

constexpr StickPoint kMTilt2Table[9] = {
    {87, 78}, {128, 78}, {169, 78},
    {87, 128}, {128, 128}, {169, 128},
    {87, 178}, {128, 178}, {169, 178},
};

constexpr StickPoint kMTilt3Table[9] = {
    {101, 101}, {128, 101}, {155, 101},
    {101, 128}, {128, 128}, {155, 128},
    {101, 155}, {128, 155}, {155, 155},
};

// No friend-specific low-magnitude Z-airdodge table was provided.
constexpr StickPoint kLt1LowMagnitudeTable[9] = {
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
    {128, 128}, {128, 128}, {128, 128},
};
