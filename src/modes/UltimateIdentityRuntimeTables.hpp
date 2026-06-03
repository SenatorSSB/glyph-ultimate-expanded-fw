// Generated-like identity runtime table constants.
// Source-owned firmware constants, not runtime-loaded config.
// Do not treat this as serial/device write behavior.
// Values must remain source-synced with the generated-config/tooling checks.

constexpr StickPoint kDefaultTable[9] = {
    {61, 51}, {128, 51}, {195, 51},
    {61, 128}, {128, 128}, {195, 128},
    {61, 205}, {128, 205}, {195, 205},
};

constexpr StickPoint kModeDefaultTable[9] = {
    {14, 87}, {128, 87}, {242, 87},
    {14, 169}, {128, 169}, {242, 169},
    {14, 169}, {128, 169}, {242, 169},
};

constexpr StickPoint kX1Table[9] = {
    {93, 51}, {128, 51}, {163, 51},
    {93, 128}, {128, 128}, {163, 128},
    {93, 205}, {128, 205}, {163, 205},
};

constexpr StickPoint kX2Table[9] = {
    {82, 51}, {128, 51}, {174, 51},
    {82, 128}, {128, 128}, {174, 128},
    {82, 205}, {128, 205}, {174, 205},
};

constexpr StickPoint kMX1Table[9] = {
    {78, 87}, {128, 87}, {178, 87},
    {78, 169}, {128, 169}, {178, 169},
    {78, 169}, {128, 169}, {178, 169},
};

constexpr StickPoint kMX2Table[9] = {
    {65, 87}, {128, 87}, {191, 87},
    {65, 169}, {128, 169}, {191, 169},
    {65, 169}, {128, 169}, {191, 169},
};

constexpr StickPoint kY1Table[9] = {
    {61, 99}, {128, 99}, {195, 99},
    {61, 128}, {128, 128}, {195, 128},
    {61, 157}, {128, 157}, {195, 157},
};

constexpr StickPoint kMY1Table[9] = {
    {14, 179}, {128, 179}, {242, 179},
    {14, 169}, {128, 169}, {242, 169},
    {14, 77}, {128, 77}, {242, 77},
};

// RF3 under LF7/LF8 layer is a normal x-only 41px modifier over default y rows.
constexpr StickPoint kLayerNormalXTable[9] = {
    {87, 51}, {128, 51}, {169, 51},
    {87, 128}, {128, 128}, {169, 128},
    {87, 205}, {128, 205}, {169, 205},
};

constexpr StickPoint kMLayerNormalXTable[9] = {
    {87, 87}, {128, 87}, {169, 87},
    {87, 169}, {128, 169}, {169, 169},
    {87, 169}, {128, 169}, {169, 169},
};

// RF4 under LF7/LF8 layer is an x-only flipper modifier over default y rows.
constexpr StickPoint kLayerFlipperTable[9] = {
    {169, 51}, {128, 51}, {87, 51},
    {169, 128}, {128, 128}, {87, 128},
    {169, 205}, {128, 205}, {87, 205},
};

constexpr StickPoint kMLayerFlipperTable[9] = {
    {169, 87}, {128, 87}, {87, 87},
    {169, 169}, {128, 169}, {87, 169},
    {169, 169}, {128, 169}, {87, 169},
};

constexpr StickPoint kY1Tilt1Table[9] = {
    {169, 99}, {128, 99}, {87, 99},
    {169, 128}, {128, 128}, {87, 128},
    {169, 157}, {128, 157}, {87, 157},
};

constexpr StickPoint kMY1Tilt1Table[9] = {
    {169, 179}, {128, 179}, {87, 179},
    {169, 169}, {128, 169}, {87, 169},
    {169, 77}, {128, 77}, {87, 77},
};

constexpr StickPoint kY1LayerFlipperTable[9] = {
    {169, 99}, {128, 99}, {87, 99},
    {169, 128}, {128, 128}, {87, 128},
    {169, 157}, {128, 157}, {87, 157},
};

constexpr StickPoint kMY1LayerFlipperTable[9] = {
    {169, 179}, {128, 179}, {87, 179},
    {169, 169}, {128, 169}, {87, 169},
    {169, 77}, {128, 77}, {87, 77},
};

constexpr StickPoint kY1LayerNormalXTable[9] = {
    {87, 99}, {128, 99}, {169, 99},
    {87, 128}, {128, 128}, {169, 128},
    {87, 157}, {128, 157}, {169, 157},
};

constexpr StickPoint kMY1LayerNormalXTable[9] = {
    {87, 179}, {128, 179}, {169, 179},
    {87, 169}, {128, 169}, {169, 169},
    {87, 77}, {128, 77}, {169, 77},
};

constexpr StickPoint kTilt1Table[9] = {
    {187, 47}, {128, 47}, {69, 47},
    {187, 128}, {128, 128}, {69, 128},
    {187, 209}, {128, 209}, {69, 209},
};

constexpr StickPoint kTilt2Table[9] = {
    {88, 79}, {128, 79}, {168, 79},
    {88, 128}, {128, 128}, {168, 128},
    {88, 177}, {128, 177}, {168, 177},
};

constexpr StickPoint kTilt3Table[9] = {
    {75, 86}, {128, 86}, {181, 86},
    {75, 128}, {128, 128}, {181, 128},
    {75, 170}, {128, 170}, {181, 170},
};

constexpr StickPoint kMTilt1Table[9] = {
    {169, 88}, {128, 88}, {87, 88},
    {169, 169}, {128, 169}, {87, 169},
    {169, 168}, {128, 168}, {87, 168},
};

constexpr StickPoint kMTilt2Table[9] = {
    {96, 82}, {128, 82}, {160, 82},
    {96, 169}, {128, 169}, {160, 169},
    {96, 174}, {128, 174}, {160, 174},
};

constexpr StickPoint kMTilt3Table[9] = {
    {96, 86}, {128, 86}, {160, 86},
    {96, 169}, {128, 169}, {160, 169},
    {96, 170}, {128, 170}, {160, 170},
};

// LT5/RF11 provide Z plus a low-magnitude left-stick override for neutral-airdodge-safe output.
constexpr StickPoint kLt1LowMagnitudeTable[9] = {
    {89, 89}, {128, 79}, {167, 89},
    {79, 128}, {128, 128}, {177, 128},
    {89, 167}, {128, 177}, {167, 167},
};
