// Compile this translation unit with the selected target flags as an object.
// Host executables also call its descriptor guard before decoding wire data.
#include <pb_common.h>
#include "config.pb.h"

#include <climits>
#include <cstddef>
#include <limits>
#include <type_traits>

#ifdef GP_C020_PROBE_MAIN
#include <cstdio>
#endif

using ButtonStorage = std::underlying_type<Button>::type;
static_assert(CHAR_BIT == 8, "Button probe requires eight-bit bytes");
static_assert(std::is_unsigned<ButtonStorage>::value, "Button storage must be unsigned");
static_assert(std::numeric_limits<ButtonStorage>::digits == sizeof(Button) * CHAR_BIT,
              "Button storage has padding bits");
static_assert(sizeof(Button) == 1 || sizeof(Button) == 4, "unsupported Button ABI");
#ifdef GP_C020_TARGET_ABI
static_assert(sizeof(Button) == 1, "selected Mk6 Button ABI must be one byte");
#define CHECK_BUTTON_FIELD(type, field, htype) \
    static_assert(PB_DATA_SIZE_STATIC(htype, type, field) == sizeof(Button), \
                  "target descriptor item width differs from Button"); \
    static_assert(PB_DATA_OFFSET_STATIC(htype, type, field) == offsetof(type, field), \
                  "target descriptor offset differs from C++ layout")
CHECK_BUTTON_FIELD(GameModeConfig, activation_binding, _PB_HTYPE_REPEATED);
CHECK_BUTTON_FIELD(ButtonRemap, physical_button, _PB_HTYPE_SINGULAR);
CHECK_BUTTON_FIELD(ButtonRemap, activates, _PB_HTYPE_SINGULAR);
CHECK_BUTTON_FIELD(SocdPair, button_dir1, _PB_HTYPE_SINGULAR);
CHECK_BUTTON_FIELD(SocdPair, button_dir2, _PB_HTYPE_SINGULAR);
CHECK_BUTTON_FIELD(CommunicationBackendConfig, activation_binding, _PB_HTYPE_REPEATED);
CHECK_BUTTON_FIELD(AnalogModifier, buttons, _PB_HTYPE_REPEATED);
CHECK_BUTTON_FIELD(ButtonComboMapping, buttons, _PB_HTYPE_REPEATED);
CHECK_BUTTON_FIELD(CustomModeConfig, digital_button_mappings, _PB_HTYPE_REPEATED);
CHECK_BUTTON_FIELD(CustomModeConfig, stick_direction_mappings, _PB_HTYPE_REPEATED);
CHECK_BUTTON_FIELD(AnalogTriggerMapping, button, _PB_HTYPE_SINGULAR);
CHECK_BUTTON_FIELD(ButtonToKeycodeMapping, button, _PB_HTYPE_SINGULAR);
#undef CHECK_BUTTON_FIELD
#endif

namespace {

struct Field {
    const char *name;
    const pb_msgdesc_t *descriptor;
    void *message;
    unsigned tag;
    size_t offset;
    size_t item_size;
    size_t capacity;
};

// Each descriptor is checked against the actual C++ layout compiled with the
// same ABI flags as the decoder's generated C and Nanopb C translation units.
GameModeConfig game{};
ButtonRemap remap{};
SocdPair socd{};
CommunicationBackendConfig backend{};
AnalogModifier modifier{};
ButtonComboMapping combo{};
CustomModeConfig custom{};
AnalogTriggerMapping trigger{};
ButtonToKeycodeMapping keyboard_entry{};

#define ARRAY_FIELD(label, type, object, member, number) \
    {label, type##_fields, &object, number, offsetof(type, member), \
     sizeof(object.member[0]), sizeof(object.member) / sizeof(object.member[0])}
#define SINGLE_FIELD(label, type, object, member, number) \
    {label, type##_fields, &object, number, offsetof(type, member), sizeof(object.member), 1}

Field fields[] = {
    ARRAY_FIELD("game_activation", GameModeConfig, game, activation_binding, 5),
    SINGLE_FIELD("remap_physical", ButtonRemap, remap, physical_button, 1),
    SINGLE_FIELD("remap_activates", ButtonRemap, remap, activates, 2),
    SINGLE_FIELD("socd_dir1", SocdPair, socd, button_dir1, 1),
    SINGLE_FIELD("socd_dir2", SocdPair, socd, button_dir2, 2),
    ARRAY_FIELD("backend_activation", CommunicationBackendConfig, backend, activation_binding, 3),
    ARRAY_FIELD("modifier_button", AnalogModifier, modifier, buttons, 1),
    ARRAY_FIELD("combo_button", ButtonComboMapping, combo, buttons, 1),
    ARRAY_FIELD("digital_button", CustomModeConfig, custom, digital_button_mappings, 2),
    ARRAY_FIELD("stick_button", CustomModeConfig, custom, stick_direction_mappings, 3),
    SINGLE_FIELD("trigger_button", AnalogTriggerMapping, trigger, button, 1),
    SINGLE_FIELD("keyboard_button", ButtonToKeycodeMapping, keyboard_entry, button, 1),
};

bool matches(const Field &field, pb_field_iter_t &iter) {
    if (!pb_field_iter_begin(&iter, field.descriptor, field.message) ||
        !pb_field_iter_find(&iter, field.tag)) return false;
    const auto *base = static_cast<const unsigned char *>(field.message);
    const auto *data = static_cast<const unsigned char *>(iter.pField);
    return iter.data_size == field.item_size &&
           static_cast<size_t>(data - base) == field.offset &&
           iter.array_size == field.capacity &&
           field.item_size == sizeof(Button);
}

} // namespace

extern "C" int gp_config020_abi_probe() {
    int failures = 0;
    for (const Field &field : fields) {
        pb_field_iter_t iter{};
        if (!matches(field, iter)) ++failures;
    }
    return failures;
}

#ifdef GP_C020_PROBE_MAIN
int main() {
    std::printf("button_size=%zu button_align=%zu storage_digits=%d config_size=%zu config_align=%zu\n",
                sizeof(Button), alignof(Button), std::numeric_limits<ButtonStorage>::digits,
                sizeof(Config), alignof(Config));
    int failures = 0;
    for (const Field &field : fields) {
        pb_field_iter_t iter{};
        const bool valid = matches(field, iter);
        std::printf("class=%s data_size=%u offset=%zu stride=%zu capacity=%u expected_offset=%zu result=%s\n",
                    field.name, static_cast<unsigned>(iter.data_size),
                    iter.pField ? static_cast<size_t>(static_cast<const unsigned char *>(iter.pField) -
                                                     static_cast<const unsigned char *>(field.message)) : 0,
                    field.item_size, static_cast<unsigned>(iter.array_size), field.offset,
                    valid ? "PASS" : "FAIL");
        if (!valid) ++failures;
    }
    return failures == 0 ? 0 : 1;
}
#endif
