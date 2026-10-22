#include "display/DefaultConfigMenu.hpp"
#include "display/ConfigMenuAssets/GlyphMenuBitmaps.h"
#include "core/Persistence.hpp"
#include "core/config_utils.hpp"
#include "core/mode_selection.hpp"
#include "reboot.hpp"
#include "config/glyph/common/include/LEDTemplates.hpp"
#include "comms/NeoPixelBackend.hpp"
#include "img/update.hpp"
#include <new>

DefaultConfigMenu::DefaultConfigMenu(
    Config &config,
    CommunicationBackend **backends,
    size_t backends_count
)
    : ConfigMenu(config, backends, backends_count) {
    /* Build default USB backends page */
    MenuPage::MenuItem *usb_backend_options =
        new MenuPage::MenuItem[config.communication_backend_configs_count];

    size_t usb_backend_options_count = 0;
    for (size_t i = 0; i < config.communication_backend_configs_count; i++) {
        CommunicationBackendConfig &backend_config = config.communication_backend_configs[i];
        MenuPage::MenuItem &current_option = usb_backend_options[usb_backend_options_count];

        if(_backends[0]->CurrentGameMode()->GetConfig()->keyboard_mode_config != 0) {
            if(backend_config.backend_id != COMMS_BACKEND_DINPUT) {
                continue;
            }
        } else if (backend_config.backend_id != COMMS_BACKEND_XINPUT &&
            backend_config.backend_id != COMMS_BACKEND_DINPUT &&
            backend_config.backend_id != COMMS_BACKEND_NINTENDO_SWITCH) {
            continue;
        }

        strlcpy(
            current_option.text,
            backend_name(backend_config.backend_id),
            sizeof(current_option.text)
        );
        current_option.key = i;
        current_option.action = &SetUsbBackend;
        usb_backend_options_count++;
    }

    _usb_backends_page = {
        .items = usb_backend_options,
        .items_count = usb_backend_options_count,
    };

    /* The visible list is unchanged; only its bounded metadata source differs. */
    const auto backend = _backends_count && _backends[0] ? _backends[0]->BackendId() : COMMS_BACKEND_UNSPECIFIED;
    // Configurator is the only live store writer. Its display is the remapper,
    // so it must never enumerate the directory concurrently with that writer.
    const bool browse = backend != COMMS_BACKEND_CONFIGURATOR && backend != COMMS_BACKEND_UNSPECIFIED;
    const size_t capacity = browse && config.game_mode_configs_count <= 30 && profile_store.Count() <= ProfileStore::kMaxEntries
        ? config.game_mode_configs_count + profile_store.Count() : 0;
    _profile_targets = capacity ? new (std::nothrow) profile_selection::Target[capacity] : nullptr;
    _gamemode_options_page = {};
    _gamemode_options_page.items_count = profile_selection::BuildTargets(
        config, profile_store, backend, _profile_targets, capacity);

    /* Build SOCD types page */
    static MenuPage::MenuItem socd_options[_SocdType_MAX] = {};
    for (uint8_t socd_type = SOCD_NEUTRAL; socd_type < _SocdType_ARRAYSIZE; socd_type++) {
        MenuPage::MenuItem &current_option = socd_options[socd_type - 1];
        strlcpy(current_option.text, socd_name((SocdType)socd_type), sizeof(current_option.text));
        current_option.key = socd_type;
        current_option.action = &SetSocdType;
    }

/*
    static MenuPage socd_page = {
        .items = socd_options,
        .items_count = sizeof(socd_options) / sizeof(MenuPage::MenuItem),
    };
*/
    /* Build top-level page */
    // clang-format off
    static MenuPage::MenuItem top_level_items[] = {
        {
            .text = ".Profile",
            .page = &_gamemode_options_page,
            .smallIcon = bitmap_gamemode_small,
            .largeIcon = bitmap_gamemode_large,
            .usb = false,
        },
        {
            .text = ".USB Mode",
            .page = &_usb_backends_page,
            .smallIcon = bitmap_usb_small,
            .largeIcon = bitmap_usb_large,
            .usb = true,
        },
        {
            .text = "RGB.Brightness",
            .action = [](
                IntegratedDisplay *display_backend,
                ConfigMenu *menu,
                Config &config,
                uint8_t key
            ) {
                display_backend->SetDisplayMode(DISPLAY_MODE_RGB_BRIGHTNESS);
            },
            .smallIcon = bitmap_brightness_small,
            .largeIcon = bitmap_brightness_large,
            .usb = false,
        },
        {
            .text = "Input.Viewer",
            .action = [](
                IntegratedDisplay *display_backend,
                ConfigMenu *menu,
                Config &config,
                uint8_t key
            ) {
                // Restore gamemode.
                DefaultConfigMenu *config_menu = (DefaultConfigMenu*)menu; 
                if (config_menu->_backends[0] != nullptr) {
                    config_menu->_backends[0]->SetGameMode(display_backend->CurrentGameMode());
                }
                display_backend->SetDisplayMode(DISPLAY_MODE_VIEWER);
            },
            .smallIcon = bitmap_input_small,
            .largeIcon = bitmap_input_large,
            .usb = false,
        },
        {
            .text = "Connect to.Configurator",
            .action = [](
                IntegratedDisplay *display_backend,
                ConfigMenu *menu,
                Config &config,
                uint8_t key
            ) {
                display_backend->Clear();
                Adafruit_GFX *display = &display_backend->_display;
                display->fillScreen(0);
                display->setCursor(2, 11);
                display->print("Configurator Mode");

                display->setCursor(2, 50);
                display->print("Please visit [URL]");
                display->setCursor(2, 61);
                display->print("to connect");
                //whatever

                for(size_t i = 0; i < config.communication_backend_configs_count; i++) {
                    if(config.communication_backend_configs[i].backend_id == COMMS_BACKEND_CONFIGURATOR) {
                        //TODO: maybe use another byte so I don't have to deal with this
                        //rp2040.idleOtherCore();
                        tud_disconnect();
                        watchdog_hw->scratch[0] = i + 1;
                        display_backend->UpdateDisplay();
                        reboot_firmware();
                    }
                }
            },
            .smallIcon = bitmap_config_small,
            .largeIcon = bitmap_config_large,
            .usb = true,
        },
        {
            .text = "Manual FW.Update",
            .action = [](
                IntegratedDisplay *display_backend,
                ConfigMenu *menu,
                Config &config,
                uint8_t key
            ) {
                display_backend->Clear();
                Adafruit_GFX *display = &display_backend->_display;
                
                // Draw update splash image (128x64 mono)
                display->drawBitmap(0, 0, Bitmap_Update, 128, 64, 1);
                display_backend->UpdateDisplay();

                CRGB *ledArray = FastLED.leds();
                for(int i = 0; i < 76; i++) {
                    ledArray[i] = bootloaderRGB[i];
                }
                FastLED.show();

                reboot_bootloader();
            },
            .smallIcon = bitmap_firmware_small,
            .largeIcon = bitmap_firmware_large,
            .usb = true,
        },
        {
            .text = "Gaming.(coming soon)",
            .action = [](
                IntegratedDisplay *display_backend,
                ConfigMenu *menu,
                Config &config,
                uint8_t key
            ) {
                /*
                display_backend->Clear();
                display_backend->UpdateDisplay();
                display_backend->SetDisplayMode(DISPLAY_MODE_ABOUT);
                */
            },
            .smallIcon = bitmap_gameing_small,
            .largeIcon = bitmap_gameing_large,
            .usb = false,
        },
        {
            .text = "About",
            .action = [](
                IntegratedDisplay *display_backend,
                ConfigMenu *menu,
                Config &config,
                uint8_t key
            ) {
                display_backend->Clear();
                display_backend->UpdateDisplay();
                display_backend->SetDisplayMode(DISPLAY_MODE_ABOUT);
            },

            .smallIcon = bitmap_about_small,
            .largeIcon = bitmap_about_large,
            .usb = false,
        },
    };
    // clang-format on

    static MenuPage top_level_page = {
        .items = top_level_items,
        .items_count = sizeof(top_level_items) / sizeof(MenuPage::MenuItem),
    };
    _top_level_page = &top_level_page;

    _usb_backends_page.parent = _top_level_page;
    _gamemode_options_page.parent = _top_level_page;
    //socd_page.parent = _top_level_page;

    // Set initial page.
    _current_menu_page = _top_level_page;
}

DefaultConfigMenu::~DefaultConfigMenu() {
    delete[] _usb_backends_page.items;
    delete[] _profile_targets;
}

const MenuPage::MenuItem *DefaultConfigMenu::ResolveItem(MenuPage *page, size_t index) {
    if (page != &_gamemode_options_page) return ConfigMenu::ResolveItem(page, index);
    if (!_profile_targets || index >= page->items_count) return nullptr;
    const auto target = _profile_targets[index];
    _profile_item = {};
    _profile_item.key = static_cast<uint8_t>(index);
    if (target.profile_id) {
        const auto *entry = profile_selection::FindEntry(profile_store, target.profile_id);
        if (!entry) return nullptr;
        // Source and destination extents are bounded independently.
        size_t n = 0;
        while (n + 1 < sizeof(_profile_item.text) && n < sizeof(entry->name) && entry->name[n]) {
            _profile_item.text[n] = entry->name[n];
            ++n;
        }
        _profile_item.text[n] = '\0';
        _profile_item.action = &SetStoredProfile;
    } else {
        if (target.mode_index >= _config.game_mode_configs_count) return nullptr;
        const auto &mode = _config.game_mode_configs[target.mode_index];
        const char *name = mode.name[0] ? mode.name : gamemode_name(mode.mode_id);
        size_t n = 0;
        const size_t limit = mode.name[0] ? sizeof(mode.name) : sizeof(_profile_item.text);
        while (n + 1 < sizeof(_profile_item.text) && n < limit && name[n]) {
            _profile_item.text[n] = name[n]; ++n;
        }
        _profile_item.text[n] = '\0';
        _profile_item.key = target.mode_index;
        _profile_item.action = &SetDefaultMode;
    }
    return &_profile_item;
}

void DefaultConfigMenu::SetStoredProfile(IntegratedDisplay *, ConfigMenu *menu, Config &, uint8_t key) {
    auto *self = static_cast<DefaultConfigMenu *>(menu);
    if (self->_profile_targets && key < self->_gamemode_options_page.items_count)
        profile_selection::Request(self->_profile_targets[key].profile_id);
}

void DefaultConfigMenu::SetDefaultMode(
    IntegratedDisplay *display_backend,
    ConfigMenu *menu,
    Config &config,
    uint8_t mode_config_index
) {
    if (mode_config_index < 0 || mode_config_index >= config.game_mode_configs_count) {
        return;
    }

    uint8_t forced_backend_index = 0;
    //dinput is the only valid usb backend for keyboard modes
    if(config.game_mode_configs[mode_config_index].keyboard_mode_config != 0) {
        //find dinput backend
        for(size_t i = 0; i < config.communication_backend_configs_count; i++) {
            if(config.communication_backend_configs[i].backend_id == COMMS_BACKEND_DINPUT) {
                forced_backend_index = i + 1;
                break;
            }
        }
    }

    tud_disconnect();
    //only required in xinput mode...for now
    delay(500);

    watchdog_hw->scratch[0] = forced_backend_index;
    watchdog_hw->scratch[1] = mode_config_index + 1;
    delay(30);
    reboot_firmware();
}

//18 len, as defined in the protobuf
bool sameName(char* name1, char* name2) {
    for(size_t i = 0; i < 18; i++) {
        if(name1[i] != name2[i]) {
            return false;
        }
    }
    return true;
}

void DefaultConfigMenu::SetUsbBackend(
    IntegratedDisplay *display_backend,
    ConfigMenu *menu,
    Config &config,
    uint8_t backend_config_index
) {
    const size_t backend_config_capacity =
        sizeof(config.communication_backend_configs) /
        sizeof(config.communication_backend_configs[0]);
    const size_t game_mode_capacity =
        sizeof(config.game_mode_configs) / sizeof(config.game_mode_configs[0]);
    if (config.communication_backend_configs_count == 0 ||
        config.communication_backend_configs_count > backend_config_capacity ||
        backend_config_index >= config.communication_backend_configs_count ||
        config.game_mode_configs_count == 0 ||
        config.game_mode_configs_count > game_mode_capacity ||
        display_backend == nullptr) {
        return;
    }

    InputMode *current_mode = display_backend->CurrentGameMode();
    if (current_mode == nullptr) {
        return;
    }

    GameModeConfig *current_config = current_mode->GetConfig();
    if (current_config == nullptr) {
        return;
    }

    for(size_t i = 0; i < config.game_mode_configs_count; i++) {
        if(current_config == &config.game_mode_configs[i]) {
            tud_disconnect();
            delay(500);
            watchdog_hw->scratch[1] = i + 1;
            watchdog_hw->scratch[0] = backend_config_index + 1;
            delay(30);
            reboot_firmware();
            return;
        }
    }
}

void DefaultConfigMenu::SetSocdType(
    IntegratedDisplay *display_backend,
    ConfigMenu *menu,
    Config &config,
    uint8_t socd_type
) {
    return;
    /*
    if (socd_type <= SOCD_UNSPECIFIED || socd_type > _SocdType_MAX) {
        return;
    }

    // Overwrite SOCD type for all SOCD pairs of current gamemode's config.
    GameModeConfig *mode_config = display_backend->CurrentGameMode()->GetConfig();
    if (mode_config != nullptr) {
        for (size_t i = 0; i < mode_config->socd_pairs_count; i++) {
            mode_config->socd_pairs[i].socd_type = (SocdType)socd_type;
        }
    }
    */
}
