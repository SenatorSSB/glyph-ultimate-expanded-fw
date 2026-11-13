// Production menu and controls, with the same display/metadata doubles as the
// historical selector proof. Package-capable builds have dedicated row choices.
#define main historical_menu_main
#include "metadata_menu.cpp"
#undef main

int main() {
    Config config{};
    config.ultimate_profile_store_format = 1;
    config.game_mode_configs_count = 3;
    config.communication_backend_configs_count = 3;
    const CommunicationBackendId routes[] = {COMMS_BACKEND_GAMECUBE, COMMS_BACKEND_XINPUT,
                                             COMMS_BACKEND_NINTENDO_SWITCH};
    entries.clear();
    for (size_t i = 0; i < 3; ++i) {
        config.communication_backend_configs[i].backend_id = routes[i];
        auto &row = config.game_mode_configs[i];
        row.mode_id = MODE_ULTIMATE;
        row.ultimate_profile_engine = 1;
        row.ultimate_profile_id = 71 + i;
        row.managed_format = i ? 1 : 0;
        row.layout_plate = i == 1 ? LAYOUT_PLATE_SPLIT_FGC : LAYOUT_PLATE_PLATFORM_FIGHTER;
        row.applicable_backends_count = 1;
        row.applicable_backends[0] = routes[i];
        if (i == 2) row.applicable_backends[row.applicable_backends_count++] = routes[0];
        ProfileStore::Entry entry{};
        entry.id = row.ultimate_profile_id;
        entry.rank = 3 - i;
        entry.payload_version = 5;
        entry.managed_format = row.managed_format;
        entry.owned_row1 = i ? i + 1 : 0;
        std::snprintf(entry.name, sizeof(entry.name), "Profile%zu", i);
        entries.push_back(entry);
    }
    auto orphan = entries[1];
    orphan.id = 123456;
    entries.push_back(orphan);
    const DisplayControls controls{BTN_MB1, BTN_MB3, BTN_MB2, BTN_MB4};
    for (size_t i = 0; i < 3; ++i) {
        auto &row = config.game_mode_configs[i];
        InputMode current(&row);
        CommunicationBackend backend(routes[i], &current);
        CommunicationBackend *backends[] = {&backend};
        GlyphConfigMenu menu(config, backends, 1);
        IntegratedDisplay display;
        auto *page = &menu._gamemode_options_page;
        check(page->items_count == (i ? 1 : 2), "filtered bound pairs only");
        const size_t selected = i ? i : 2;
        check(menu._profile_targets[0].mode_index == selected, "rank orders exact pair");
        check(!std::strcmp(menu.ResolveItem(page, 0)->text, entries[selected].name), "directory display name");
        menu._current_menu_page = page;
        menu.UpdateDisplay(&display, display._display);
        check(display._display.plate == dashboard_plate_label(config.game_mode_configs[selected].layout_plate),
              "rendered plate of highlighted pair");
        check(display._display.name == entries[selected].name, "rendered complete highlighted name");
        menu.HandleControls(&display, controls, controls.enter);
        check(profile_selection::Pending() == entries[selected].id, "menu action carries stable logical ID");
        profile_selection::Complete();
        if (i) {
            check(menu._usb_backends_page.items_count == 1, "managed USB menu filtered by applicability");
            menu.SetUsbBackend(&display, &menu, config, i);
            check(profile_selection::RequestedBackend() == routes[i] && profile_selection::Pending() == entries[i].id,
                  "USB action carries exact destination");
            profile_selection::Complete();
        }
    }
    CommunicationBackend no_default(routes[0], nullptr);
    CommunicationBackend *no_default_backends[] = {&no_default};
    GlyphConfigMenu unselected(config, no_default_backends, 1);
    check(unselected._gamemode_options_page.items_count == 2, "missing active mode can choose eligible pairs");
    std::puts("PASS production managed Profile menu, bound legacy pair, ordering, eligibility, plate, name and USB action");
}
