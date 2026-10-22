#include "display/GlyphConfigMenu.hpp"

#include "core/Persistence.hpp"
#include "core/config_utils.hpp"
#include "core/mode_selection.hpp"
#include "reboot.hpp"

GlyphConfigMenu::GlyphConfigMenu(
    Config &config,
    CommunicationBackend **backends,
    size_t backends_count
)
    : DefaultConfigMenu(config, backends, backends_count) {
    // Profile data/eligibility is shared with DefaultConfigMenu.

    /* Add new page for dashboard option */
    // clang-format off
    size_t dashboard_options_count = 2;
    static MenuPage::MenuItem dashboard_options[] = {
        {
            .text = "Dashboard Menu",
            .key = DASHBOARD_MENU_BUTTON_HINTS,
            .action = &SetDashboardOption,
        },
        {
            .text = "Input Viewer",
            .key = DASHBOARD_INPUT_VIEWER,
            .action = &SetDashboardOption,
        },
    };
    // clang-format on

    static MenuPage dashboard_options_page = {
        .parent = _top_level_page,
        .items = dashboard_options,
        .items_count = sizeof(dashboard_options) / sizeof(MenuPage::MenuItem),
    };

    /* Overrides for top-level page */
    /*
    strlcpy(_top_level_page->items[2].text, "SOCD Option", sizeof(_top_level_page->items[2].text));
    _top_level_page->items[4] = {
        .text = "Dashboard Option",
        .page = &dashboard_options_page,
    };
    */
}

void GlyphConfigMenu::ReturnToDashboard(IntegratedDisplay *instance) {
    instance->SetDisplayMode(
        _config.default_dashboard_option == DASHBOARD_INPUT_VIEWER ? DISPLAY_MODE_VIEWER
                                                                   : DISPLAY_MODE_BUTTON_HINTS
    );
}

void GlyphConfigMenu::SetDashboardOption(
    IntegratedDisplay *display_backend,
    ConfigMenu *menu,
    Config &config,
    uint8_t dashboard_option
) {
    // Restore gamemode.
    GlyphConfigMenu *config_menu = (GlyphConfigMenu *)menu;
    if (config_menu->_backends[0] != nullptr) {
        config_menu->_backends[0]->SetGameMode(display_backend->CurrentGameMode());
    }

    config.default_dashboard_option = (DashboardOption)dashboard_option;
    config_menu->ReturnToDashboard(display_backend);
}