// HISTORICAL / SUPERSEDED: 27-table literal-body output evidence only; not current source or generator input.
// Generated-like identity runtime table constants.
// Source-owned firmware constants, not runtime-loaded config.
// Values are source-authored, not generated at runtime.
// Do not treat this as serial/device write behavior.
// Values must remain source-synced with the generated-config/tooling checks.

constexpr StickPoint kDefaultTable[9] = {
    {0, 0}, {128, 0}, {255, 0},
    {0, 128}, {128, 128}, {255, 128},
    {0, 255}, {128, 255}, {255, 255},
};

constexpr StickPoint kModeDefaultTable[9] = {
    {1, 1}, {128, 1}, {254, 1},
    {1, 128}, {128, 128}, {254, 128},
    {1, 254}, {128, 254}, {254, 254},
};

constexpr StickPoint kX1Table[9] = {
    {2, 2}, {128, 2}, {253, 2},
    {2, 128}, {128, 128}, {253, 128},
    {2, 253}, {128, 253}, {253, 253},
};

constexpr StickPoint kX2Table[9] = {
    {3, 3}, {128, 3}, {252, 3},
    {3, 128}, {128, 128}, {252, 128},
    {3, 252}, {128, 252}, {252, 252},
};

constexpr StickPoint kMX1Table[9] = {
    {4, 4}, {128, 4}, {251, 4},
    {4, 128}, {128, 128}, {251, 128},
    {4, 251}, {128, 251}, {251, 251},
};

constexpr StickPoint kMX2Table[9] = {
    {5, 5}, {128, 5}, {250, 5},
    {5, 128}, {128, 128}, {250, 128},
    {5, 250}, {128, 250}, {250, 250},
};

constexpr StickPoint kY1Table[9] = {
    {6, 6}, {128, 6}, {249, 6},
    {6, 128}, {128, 128}, {249, 128},
    {6, 249}, {128, 249}, {249, 249},
};

constexpr StickPoint kMY1Table[9] = {
    {7, 7}, {128, 7}, {248, 7},
    {7, 128}, {128, 128}, {248, 128},
    {7, 248}, {128, 248}, {248, 248},
};

// RF3 under LF7/LF8 layer is a normal x-only 41px modifier over default y rows.
constexpr StickPoint kLayerNormalXTable[9] = {
    {8, 8}, {128, 8}, {247, 8},
    {8, 128}, {128, 128}, {247, 128},
    {8, 247}, {128, 247}, {247, 247},
};

constexpr StickPoint kMLayerNormalXTable[9] = {
    {9, 9}, {128, 9}, {246, 9},
    {9, 128}, {128, 128}, {246, 128},
    {9, 246}, {128, 246}, {246, 246},
};

// RF4 under LF7/LF8 layer is an x-only flipper modifier over default y rows.
constexpr StickPoint kLayerFlipperTable[9] = {
    {10, 10}, {128, 10}, {245, 10},
    {10, 128}, {128, 128}, {245, 128},
    {10, 245}, {128, 245}, {245, 245},
};

constexpr StickPoint kMLayerFlipperTable[9] = {
    {11, 11}, {128, 11}, {244, 11},
    {11, 128}, {128, 128}, {244, 128},
    {11, 244}, {128, 244}, {244, 244},
};

constexpr StickPoint kY1Tilt1Table[9] = {
    {12, 12}, {128, 12}, {243, 12},
    {12, 128}, {128, 128}, {243, 128},
    {12, 243}, {128, 243}, {243, 243},
};

constexpr StickPoint kMY1Tilt1Table[9] = {
    {13, 13}, {128, 13}, {242, 13},
    {13, 128}, {128, 128}, {242, 128},
    {13, 242}, {128, 242}, {242, 242},
};

constexpr StickPoint kY1LayerFlipperTable[9] = {
    {14, 14}, {128, 14}, {241, 14},
    {14, 128}, {128, 128}, {241, 128},
    {14, 241}, {128, 241}, {241, 241},
};

constexpr StickPoint kMY1LayerFlipperTable[9] = {
    {15, 15}, {128, 15}, {240, 15},
    {15, 128}, {128, 128}, {240, 128},
    {15, 240}, {128, 240}, {240, 240},
};

constexpr StickPoint kY1LayerNormalXTable[9] = {
    {16, 16}, {128, 16}, {239, 16},
    {16, 128}, {128, 128}, {239, 128},
    {16, 239}, {128, 239}, {239, 239},
};

constexpr StickPoint kMY1LayerNormalXTable[9] = {
    {17, 17}, {128, 17}, {238, 17},
    {17, 128}, {128, 128}, {238, 128},
    {17, 238}, {128, 238}, {238, 238},
};

constexpr StickPoint kTilt1Table[9] = {
    {18, 18}, {128, 18}, {237, 18},
    {18, 128}, {128, 128}, {237, 128},
    {18, 237}, {128, 237}, {237, 237},
};

constexpr StickPoint kTilt2Table[9] = {
    {19, 19}, {128, 19}, {236, 19},
    {19, 128}, {128, 128}, {236, 128},
    {19, 236}, {128, 236}, {236, 236},
};

constexpr StickPoint kTilt3Table[9] = {
    {20, 20}, {128, 20}, {235, 20},
    {20, 128}, {128, 128}, {235, 128},
    {20, 235}, {128, 235}, {235, 235},
};

constexpr StickPoint kTilt1Minus41Table[9] = {
    {21, 21}, {128, 21}, {234, 21},
    {21, 128}, {128, 128}, {234, 128},
    {21, 234}, {128, 234}, {234, 234},
};

// RT1+RF4 custom modifier. Direction 5 is source-encoded center because table
// selection requires a 9-point table and the requested neutral behavior is unchanged.
constexpr StickPoint kRT1RF4CustomTable[9] = {
    {22, 22}, {128, 22}, {233, 22},
    {22, 128}, {128, 128}, {233, 128},
    {22, 233}, {128, 233}, {233, 233},
};

constexpr StickPoint kMTilt1Table[9] = {
    {23, 23}, {128, 23}, {232, 23},
    {23, 128}, {128, 128}, {232, 128},
    {23, 232}, {128, 232}, {232, 232},
};

constexpr StickPoint kMTilt2Table[9] = {
    {24, 24}, {128, 24}, {231, 24},
    {24, 128}, {128, 128}, {231, 128},
    {24, 231}, {128, 231}, {231, 231},
};

constexpr StickPoint kMTilt3Table[9] = {
    {25, 25}, {128, 25}, {230, 25},
    {25, 128}, {128, 128}, {230, 128},
    {25, 230}, {128, 230}, {230, 230},
};

// LT5/RF11 provide Z plus a low-magnitude left-stick override for neutral-airdodge-safe output.
constexpr StickPoint kLt1LowMagnitudeTable[9] = {
    {26, 26}, {128, 26}, {229, 26},
    {26, 128}, {128, 128}, {229, 128},
    {26, 229}, {128, 229}, {229, 229},
};
