#ifndef _PROTOTYPES_SENSCOPE_PROTOTYPE_BUILD_FLAGS_HPP
#define _PROTOTYPES_SENSCOPE_PROTOTYPE_BUILD_FLAGS_HPP

#ifndef SENSCOPE_PROTOTYPE_ENABLE_MANUAL_SELECTION
#define SENSCOPE_PROTOTYPE_ENABLE_MANUAL_SELECTION 0
#endif

namespace senscope::prototype {

constexpr bool kEnableSenscopePrototypeManualSelection =
    SENSCOPE_PROTOTYPE_ENABLE_MANUAL_SELECTION != 0;

} // namespace senscope::prototype

#endif
