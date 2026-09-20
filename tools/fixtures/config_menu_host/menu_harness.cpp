#include <iostream>
#include <stdexcept>
#include <string>
#include <algorithm>
template <typename A, typename B> constexpr auto min(A a, B b) { return a < b ? a : b; }
template <typename A, typename B> constexpr auto max(A a, B b) { return a > b ? a : b; }

#define private public
#define protected public
#include "../../../HAL/pico/include/display/ConfigMenu.hpp"
#include "../../../HAL/pico/include/display/DefaultConfigMenu.hpp"
#include "../../../config/glyph/common/include/display/GlyphConfigMenu.hpp"
#undef protected
#undef private

// The three following includes are the exact production translation units.
#include "../../../HAL/pico/src/display/ConfigMenu.cpp"
#include "../../../HAL/pico/src/display/DefaultConfigMenu.cpp"
#include "../../../config/glyph/common/src/display/GlyphConfigMenu.cpp"

static void require(bool ok, const char *message) { if (!ok) throw std::runtime_error(message); }

static void null_current_mode() {
    Config config;
    config.communication_backend_configs_count = 1;
    config.communication_backend_configs[0].backend_id = COMMS_BACKEND_XINPUT;
    CommunicationBackend backend(COMMS_BACKEND_XINPUT, nullptr);
    CommunicationBackend *backends[] = {&backend};
    GlyphConfigMenu menu(config, backends, 1);
    require(menu._gamemode_options_page.items_count == 0, "null mode did not preserve empty filtered page");
    std::cout << "case=null_current_mode result=PASS\n";
}

static GlyphConfigMenu empty_filtered_menu(Config &config, CommunicationBackend &backend) {
    CommunicationBackend *backends[] = {&backend};
    GlyphConfigMenu menu(config, backends, 1);
    require(menu._gamemode_options_page.items_count == 0, "filtered page was not empty");
    return menu;
}

static void empty_filtered_pages() {
    Config config;
    config.communication_backend_configs_count = 0;
    config.game_mode_configs_count = 1;
    config.game_mode_configs[0].mode_id = MODE_MELEE;
    config.game_mode_configs[0].applicable_backends_count = 1;
    config.game_mode_configs[0].applicable_backends[0] = COMMS_BACKEND_DINPUT;
    CommunicationBackend backend(COMMS_BACKEND_XINPUT, nullptr);
    auto menu = empty_filtered_menu(config, backend);
    (void)menu;
    std::cout << "case=empty_filtered_pages result=PASS\n";
}

static void empty_child_page_update() {
    Config config;
    config.communication_backend_configs_count = 0;
    config.game_mode_configs_count = 1;
    config.game_mode_configs[0].mode_id = MODE_MELEE;
    config.game_mode_configs[0].applicable_backends_count = 1;
    config.game_mode_configs[0].applicable_backends[0] = COMMS_BACKEND_DINPUT;
    CommunicationBackend backend(COMMS_BACKEND_XINPUT, nullptr);
    auto menu = empty_filtered_menu(config, backend);
    IntegratedDisplay display;
    DisplayControls controls{BTN_MB1, BTN_MB3, BTN_MB2, BTN_MB4};
    menu.HandleControls(&display, controls, BTN_NONE);
    menu.HandleControls(&display, controls, BTN_MB4);
    menu.HandleControls(&display, controls, BTN_MB3);
    menu.HandleControls(&display, controls, BTN_MB2);
    menu.HandleControls(&display, controls, BTN_MB4);
    menu.HandleControls(&display, controls, BTN_MB1);
    Adafruit_GFX graphics;
    menu.UpdateDisplay(&display, graphics);
    std::cout << "case=empty_child_page_update result=PASS\n";
}

static void empty_usb_page_update() {
    Config config;
    config.communication_backend_configs_count = 0;
    config.game_mode_configs_count = 0;
    CommunicationBackend backend(COMMS_BACKEND_XINPUT, nullptr);
    auto menu = empty_filtered_menu(config, backend);
    IntegratedDisplay display;
    DisplayControls controls{BTN_MB1, BTN_MB3, BTN_MB2, BTN_MB4};
    menu.HandleControls(&display, controls, BTN_NONE);
    menu.HandleControls(&display, controls, BTN_MB3);
    menu.HandleControls(&display, controls, BTN_MB4);
    menu.HandleControls(&display, controls, BTN_MB3);
    menu.HandleControls(&display, controls, BTN_MB2);
    menu.HandleControls(&display, controls, BTN_MB1);
    Adafruit_GFX graphics;
    menu.UpdateDisplay(&display, graphics);
    std::cout << "case=empty_usb_page_update result=PASS\n";
}

static void injected_index_equals_count() {
    Config config;
    config.communication_backend_configs_count = 0;
    CommunicationBackend backend(COMMS_BACKEND_XINPUT, nullptr);
    CommunicationBackend *backends[] = {&backend};
    GlyphConfigMenu menu(config, backends, 1);
    MenuPage::MenuItem item{};
    MenuPage page{nullptr, &item, 1};
    menu._top_level_page = &page;
    menu._current_menu_page = &page;
    menu._highlighted_menu_item = 1;
    IntegratedDisplay display;
    DisplayControls controls{BTN_MB1, BTN_MB3, BTN_MB2, BTN_MB4};
    menu.HandleControls(&display, controls, BTN_MB4);
    std::cout << "case=injected_index_equals_count result=PASS\n";
}

int main(int argc, char **argv) {
    try {
        require(argc == 2, "one case argument is required");
        const std::string case_name = argv[1];
        if (case_name == "null_current_mode") null_current_mode();
        else if (case_name == "empty_filtered_pages") empty_filtered_pages();
        else if (case_name == "empty_child_page_update") empty_child_page_update();
        else if (case_name == "empty_usb_page_update") empty_usb_page_update();
        else if (case_name == "injected_index_equals_count") injected_index_equals_count();
        else throw std::runtime_error("unknown case");
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
