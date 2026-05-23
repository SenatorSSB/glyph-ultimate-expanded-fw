#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_DIRECTION_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_DIRECTION_HPP

#include "prototypes/senscope/SenscopePrototypeTypes.hpp"

#include <cstdint>

namespace senscope::prototype {

enum class SenscopePrototypeDirectionStatus : uint8_t {
    Resolved = 0,
    InvalidDirectionRoleMask,
};

enum class SenscopePrototypeDirectionDiagnosticCode : uint8_t {
    None = 0,
    UnknownDirectionRoleBitsMasked,
};

// Prototype-only opposite-direction policy for pre-SOCD direction-role masks.
// This does not replace the source-backed core SOCD runtime algorithms.
enum class SenscopePrototypeDirectionOppositePolicy : uint8_t {
    NeutralOnOpposite = 0,
    LeftPriority,
    RightPriority,
    DownPriority,
    UpPriority,
};

struct SenscopePrototypeDirectionRequest {
    SenscopePrototypeDirectionRoleMask pre_socd_direction_roles = 0;
    SenscopePrototypeDirectionOppositePolicy opposite_policy =
        SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite;
};

struct SenscopePrototypeDirectionResult {
    SenscopePrototypeDirectionStatus status = SenscopePrototypeDirectionStatus::Resolved;
    SenscopePrototypeDirectionKey resolved_direction_key = SenscopePrototypeDirectionKey::D5;
    SenscopePrototypeDirectionRoleMask post_socd_direction_roles = 0;
    SenscopePrototypeDirectionDiagnosticCode diagnostic_code =
        SenscopePrototypeDirectionDiagnosticCode::None;
    uint16_t diagnostic_detail = 0;
};

SenscopePrototypeDirectionResult
ResolveSenscopePrototypeDirection(const SenscopePrototypeDirectionRequest &request) noexcept;

} // namespace senscope::prototype

#endif
