#ifndef _DISPLAY_DEFAULTCONFIGMENU_HPP
#define _DISPLAY_DEFAULTCONFIGMENU_HPP

#include "display/ConfigMenu.hpp"
#include "core/ProfileSelection.hpp"

class DefaultConfigMenu : public ConfigMenu {
  public:
    DefaultConfigMenu(Config &config, CommunicationBackend **backends, size_t backends_count);
    ~DefaultConfigMenu();

  protected:
    const MenuPage::MenuItem *ResolveItem(MenuPage *page, size_t index) override;
    static void SetStoredProfile(IntegratedDisplay *, ConfigMenu *, Config &, uint8_t);
    profile_selection::Target *_profile_targets = nullptr;
    MenuPage::MenuItem _profile_item{};
    static void SetDefaultMode(
        IntegratedDisplay *instance,
        ConfigMenu *menu,
        Config &config,
        uint8_t mode_config_index
    );
    static void SetUsbBackend(
        IntegratedDisplay *instance,
        ConfigMenu *menu,
        Config &config,
        uint8_t backend_config_index
    );
    static void SetSocdType(
        IntegratedDisplay *instance,
        ConfigMenu *menu,
        Config &config,
        uint8_t socd_type
    );

    MenuPage _usb_backends_page;
    MenuPage _gamemode_options_page;

  private:
    static constexpr uint8_t padding = 2;
    static constexpr uint8_t max_visible_lines = 6;
    static constexpr char highlight_string[] = ">";
};

#endif