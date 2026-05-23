#include "prototypes/senscope/SenscopePrototypeDirection.hpp"

namespace senscope::prototype {

namespace {

constexpr SenscopePrototypeDirectionRoleMask kKnownDirectionRoleMask =
    kSenscopePrototypeDirectionRoleLeft |
    kSenscopePrototypeDirectionRoleRight |
    kSenscopePrototypeDirectionRoleDown |
    kSenscopePrototypeDirectionRoleUp;

void ResolveHorizontalOpposite(
    bool &left,
    bool &right,
    SenscopePrototypeDirectionOppositePolicy policy
) {
    if (!left || !right) {
        return;
    }

    switch (policy) {
        case SenscopePrototypeDirectionOppositePolicy::LeftPriority:
            right = false;
            return;
        case SenscopePrototypeDirectionOppositePolicy::RightPriority:
            left = false;
            return;
        case SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite:
        case SenscopePrototypeDirectionOppositePolicy::DownPriority:
        case SenscopePrototypeDirectionOppositePolicy::UpPriority:
        default:
            left = false;
            right = false;
            return;
    }
}

void ResolveVerticalOpposite(bool &down, bool &up, SenscopePrototypeDirectionOppositePolicy policy) {
    if (!down || !up) {
        return;
    }

    switch (policy) {
        case SenscopePrototypeDirectionOppositePolicy::DownPriority:
            up = false;
            return;
        case SenscopePrototypeDirectionOppositePolicy::UpPriority:
            down = false;
            return;
        case SenscopePrototypeDirectionOppositePolicy::NeutralOnOpposite:
        case SenscopePrototypeDirectionOppositePolicy::LeftPriority:
        case SenscopePrototypeDirectionOppositePolicy::RightPriority:
        default:
            down = false;
            up = false;
            return;
    }
}

SenscopePrototypeDirectionRoleMask BuildPostSocdDirectionRoleMask(bool left, bool right, bool down, bool up) {
    SenscopePrototypeDirectionRoleMask result = 0;
    if (left) {
        result |= kSenscopePrototypeDirectionRoleLeft;
    }
    if (right) {
        result |= kSenscopePrototypeDirectionRoleRight;
    }
    if (down) {
        result |= kSenscopePrototypeDirectionRoleDown;
    }
    if (up) {
        result |= kSenscopePrototypeDirectionRoleUp;
    }
    return result;
}

SenscopePrototypeDirectionKey
MapPostSocdDirectionToKey(bool left, bool right, bool down, bool up) {
    if (!left && !right && !down && !up) {
        return SenscopePrototypeDirectionKey::D5;
    }
    if (left && down) {
        return SenscopePrototypeDirectionKey::D1;
    }
    if (right && down) {
        return SenscopePrototypeDirectionKey::D3;
    }
    if (left && up) {
        return SenscopePrototypeDirectionKey::D7;
    }
    if (right && up) {
        return SenscopePrototypeDirectionKey::D9;
    }
    if (left) {
        return SenscopePrototypeDirectionKey::D4;
    }
    if (right) {
        return SenscopePrototypeDirectionKey::D6;
    }
    if (down) {
        return SenscopePrototypeDirectionKey::D2;
    }
    return SenscopePrototypeDirectionKey::D8;
}

} // namespace

SenscopePrototypeDirectionResult
ResolveSenscopePrototypeDirection(const SenscopePrototypeDirectionRequest &request) noexcept {
    SenscopePrototypeDirectionResult result = {};

    const SenscopePrototypeDirectionRoleMask unknown_direction_bits =
        request.pre_socd_direction_roles & ~kKnownDirectionRoleMask;

    const SenscopePrototypeDirectionRoleMask sanitized_roles =
        request.pre_socd_direction_roles & kKnownDirectionRoleMask;

    bool left = (sanitized_roles & kSenscopePrototypeDirectionRoleLeft) != 0;
    bool right = (sanitized_roles & kSenscopePrototypeDirectionRoleRight) != 0;
    bool down = (sanitized_roles & kSenscopePrototypeDirectionRoleDown) != 0;
    bool up = (sanitized_roles & kSenscopePrototypeDirectionRoleUp) != 0;

    // Prototype adapter boundary only: this normalizes already OR-composed direction roles.
    // It does not modify or replace source-backed core SOCD runtime behavior.
    ResolveHorizontalOpposite(left, right, request.opposite_policy);
    ResolveVerticalOpposite(down, up, request.opposite_policy);

    result.post_socd_direction_roles = BuildPostSocdDirectionRoleMask(left, right, down, up);
    result.resolved_direction_key = MapPostSocdDirectionToKey(left, right, down, up);

    if (unknown_direction_bits != 0) {
        result.status = SenscopePrototypeDirectionStatus::InvalidDirectionRoleMask;
        result.diagnostic_code = SenscopePrototypeDirectionDiagnosticCode::UnknownDirectionRoleBitsMasked;
        result.diagnostic_detail = unknown_direction_bits;
    }

    return result;
}

} // namespace senscope::prototype
