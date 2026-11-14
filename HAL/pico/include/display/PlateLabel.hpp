#pragma once
#include <config.pb.h>

constexpr const char *dashboard_plate_label(LayoutPlate plate) {
    switch (plate) {
        case LAYOUT_PLATE_UNSPECIFIED: return "Unknown Plate";
        case LAYOUT_PLATE_EVERYTHING: return "Full";
        case LAYOUT_PLATE_FGC: return "FGC";
        case LAYOUT_PLATE_SPLIT_FGC: return "Split FGC";
        case LAYOUT_PLATE_PLATFORM_FIGHTER: return "Plat Fighter";
    }
    return "Unknown Plate";
}
