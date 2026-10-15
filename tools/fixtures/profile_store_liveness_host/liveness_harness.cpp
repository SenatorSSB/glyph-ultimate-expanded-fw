// Reuse only the established portable v1 fixture builders and NOR callbacks.
// Its test main is retained under another name and is not executed here.
#define main strict_fixture_unused_main
#include "../profile_store_strict_host/strict_harness.cpp"
#undef main
#include "core/ProfileStoreFaultControls.hpp"

#include <chrono>
#include <cstddef>
#include <cstdlib>

namespace {
    struct alignas(std::max_align_t) Allocation {
        size_t size;
    };

    size_t live_allocations = 0, live_bytes = 0, peak_bytes = 0, total_allocations = 0;
    uint64_t block_reads = 0, block_programs = 0, block_erases = 0, checked_stats = 0,
             checked_enumerates = 0;
    uint64_t capacity_samples = 0, max_capacity_reads = 0, max_capacity_stats = 0;
    double max_capacity_ms = 0;
    uint64_t fault_cycles = 0, fault_triggers = 0, dropped_results = 0, exact_replays = 0;
    size_t mount_allocations = 0, mount_bytes = 0;
    uint64_t next_token = 100;

    int counted_read(const lfs_config *c, lfs_block_t b, lfs_off_t o, void *p, lfs_size_t n) {
        ++block_reads;
        return ram_read(c, b, o, p, n);
    }

    int counted_program(
        const lfs_config *c,
        lfs_block_t b,
        lfs_off_t o,
        const void *p,
        lfs_size_t n
    ) {
        ++block_programs;
        return ram_prog(c, b, o, p, n);
    }

    int counted_erase(const lfs_config *c, lfs_block_t b) {
        ++block_erases;
        return ram_erase(c, b);
    }

    CheckedStorage::Fault observed_hook(
        Kind k,
        CheckedStorage::Operation op,
        CheckedStorage::Phase phase,
        const char *p
    ) {
        if (phase == CheckedStorage::Phase::Before) {
            if (op == CheckedStorage::Operation::Stat)
                ++checked_stats;
            if (op == CheckedStorage::Operation::Enumerate)
                ++checked_enumerates;
        }
        return ProfileStoreFaultControls::Hook(k, op, phase, p);
    }

    void observe() {
        CheckedStorage::SetFaultHook(observed_hook);
    }

    void no_leaks(const char *phase) {
        require(
            mounted_fs.mlist == nullptr,
            std::string(phase) + ": native LittleFS handle retained"
        );
        require(
            live_allocations == mount_allocations && live_bytes == mount_bytes,
            std::string(phase) + ": LittleFS allocation retained"
        );
    }

    ProfileStore::CapacityInfo status_capacity(ProfileStore &s, const char *phase) {
        const auto reads = block_reads, stats = checked_stats, programs = block_programs,
                   erases = block_erases;
        const auto started = std::chrono::steady_clock::now();
        auto c = s.Capacity();
        const double elapsed =
            std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - started)
                .count();
        ++capacity_samples;
        max_capacity_reads = std::max(max_capacity_reads, block_reads - reads);
        max_capacity_stats = std::max(max_capacity_stats, checked_stats - stats);
        max_capacity_ms = std::max(max_capacity_ms, elapsed);
        require(
            c.total_bytes == 524288 && c.reserve_bytes == 16384 && c.admissible_profiles >= 20,
            "capacity geometry and reserve"
        );
        require(c.free_bytes >= c.reserve_bytes + c.staging_bytes, "capacity reserve retained");
        require(
            block_programs == programs && block_erases == erases,
            "STATUS capacity does not write or erase"
        );
        require(block_reads - reads < 100000, "capacity workload guard");
        no_leaks(phase);
        return c;
    }

    Bytes read_native(const char *path) {
        size_t n = 0;
        require(bool(CheckedStorage::Stat(path, &n)), std::string("snapshot stat ") + path);
        Bytes b(n);
        require(
            bool(CheckedStorage::ReadFile(path, b.data(), b.size(), Kind::Root)),
            std::string("snapshot read ") + path
        );
        return b;
    }

    void write_native(const char *path, const Bytes &b, Kind k = Kind::Root) {
        require(
            bool(CheckedStorage::WriteFile(path, b.data(), b.size(), k)),
            std::string("seed write ") + path
        );
    }

    Bytes config_wire(const Config &c) {
        size_t n = 0;
        require(pb_get_encoded_size(&n, Config_fields, &c), "config size");
        Bytes b(n + 8);
        auto stream = pb_ostream_from_buffer(b.data() + 8, n);
        require(pb_encode(&stream, Config_fields, &c), "config encode");
        put32(b.data(), n);
        put32(b.data() + 4, crc(b.data() + 8, n));
        return b;
    }

    uint32_t revision(ProfileStore &s, uint32_t id) {
        for (size_t i = 0; i < s.Count(); ++i)
            if (s.EntryAt(i)->id == id)
                return s.EntryAt(i)->revision;
        throw std::runtime_error("missing revision");
    }

    void clear_rule() {
        require(ProfileStoreFaultControls::Arm(0, 0, 0, 0, 0, 0, true), "clear rule");
        observe();
    }

    void prepare_rule(unsigned operation, bool after) {
        clear_rule();
        require(
            ProfileStoreFaultControls::Arm(1, operation, after ? 2 : 1, after ? 2 : 1, 1, 0, false),
            "prepare fault"
        );
        observe();
    }

    void enter_rule() {
#ifndef LIVENESS_FROZEN_ARM
        require(
            ProfileStoreFaultControls::BeginMutation(ProfileStoreFaultControls::Current().ticket),
            "begin scoped fault"
        );
#endif
        observe();
    }

    void leave_rule() {
#ifndef LIVENESS_FROZEN_ARM
        ProfileStoreFaultControls::EndMutation();
#endif
        observe();
    }

    void fault_row(ProfileStore &s, unsigned operation, bool after) {
        const auto generation = s.Generation();
        const auto rev = revision(s, 22);
        const auto root0 = read_native("/ultimate-v2-0.bin"),
                   root1 = read_native("/ultimate-v2-1.bin"),
                   control = read_native("/ultimate-v2.ctrl");
        status_capacity(s, "preflight");
        prepare_rule(operation, after);
        status_capacity(s, "after prepare before mutation");
        enter_rule();
        const auto tx = identity(next_token++);
        const auto outcome = s.Update(22, legacy.ultimate_profiles[0], rev, tx);
        leave_rule();
        no_leaks("immediately after fault");
        require(
            outcome.status == (after ? Status::UnknownOutcome : Status::IoFailure),
            "fault outcome"
        );
        require(
            ProfileStoreFaultControls::Current().triggered &&
                !ProfileStoreFaultControls::Current().armed,
            "single shot triggered and disarmed"
        );
        ++fault_triggers;
        require(
            s.QueryTransaction(tx).status == Status::NotFound && !s.IsTransactionUncertain(),
            "pre-intent failure reconciles NOT_FOUND and clears fence"
        );
        require(
            s.Generation() == generation && revision(s, 22) == rev && s.Count() == 20,
            "pre-intent failure preserves authority"
        );
        require(
            read_native("/ultimate-v2-0.bin") == root0 &&
                read_native("/ultimate-v2-1.bin") == root1 &&
                read_native("/ultimate-v2.ctrl") == control,
            "fault leaves both roots and control unchanged"
        );
        status_capacity(s, "post fault STATUS");
        no_leaks("post fault return");
        char temporary[32];
        ProfileStorePaths::RecordTemporaryPath(temporary, sizeof(temporary), 22, rev + 1);
        size_t temporary_size = 0;
        const auto temporary_state = CheckedStorage::Stat(temporary, &temporary_size);
        require(
            (operation == static_cast<unsigned>(CheckedStorage::Operation::OpenWrite) && !after)
                ? temporary_state.outcome == Outcome::NotFound
                : bool(temporary_state) && temporary_size == 0,
            "failed publication leaves only expected bounded temporary"
        );
        // Do not clean it here: the next real mutation admission must collect it.
        // Its preceding STATUS and ARM see the exact previous-operation residue.
    }

    void arm_ack_negative() {
        prepare_rule(static_cast<unsigned>(CheckedStorage::Operation::Write), false);
        // Simulate a lost ARM acknowledgement: no ticket is ever supplied by host.
        const uint8_t b[] = { 0x10, 0x20 };
        const auto result = CheckedStorage::WriteFile(
            "/ultimate-000000ff-00000001.tmp",
            b,
            sizeof(b),
            Kind::Record
        );
#ifdef LIVENESS_FROZEN_ARM
        require(
            !result && ProfileStoreFaultControls::Current().triggered,
            "old ARM latent fault must be demonstrated"
        );
        std::puts("old_candidate_lost_arm_ack_negative=DETECTED ordinary_write_triggered=true");
#else
        require(
            bool(result) && !ProfileStoreFaultControls::Current().triggered &&
                !ProfileStoreFaultControls::Current().armed,
            "pending ARM must not affect ordinary write"
        );
        const uint32_t ticket = ProfileStoreFaultControls::Current().ticket;
        require(!ProfileStoreFaultControls::BeginMutation(ticket + 1), "wrong ticket rejected");
        require(
            ProfileStoreFaultControls::BeginMutation(ticket),
            "exact ticket starts bounded mutation"
        );
        ProfileStoreFaultControls::EndMutation();
        require(
            !ProfileStoreFaultControls::BeginMutation(ticket),
            "ticket consumed and cannot be reused"
        );
        std::puts(
            "pending_arm_lost_ack_safety=PASS ordinary_write_unaffected=true wrong_ticket_rejected=true ticket_single_use=true"
        );
#endif
        clear_rule();
        require(
            bool(CheckedStorage::Remove("/ultimate-000000ff-00000001.tmp", Kind::Record)),
            "negative probe cleanup"
        );
        no_leaks("lost arm ack check");
    }
}

extern "C" void *liveness_lfs_malloc(size_t size) {
    auto *p = static_cast<Allocation *>(std::malloc(sizeof(Allocation) + size));
    if (!p)
        return nullptr;
    p->size = size;
    ++live_allocations;
    ++total_allocations;
    live_bytes += size;
    peak_bytes = std::max(peak_bytes, live_bytes);
    return p + 1;
}

extern "C" void liveness_lfs_free(void *pointer) {
    if (!pointer)
        return;
    auto *p = static_cast<Allocation *>(pointer) - 1;
    --live_allocations;
    live_bytes -= p->size;
    std::free(p);
}

int main(int argc, char **argv) {
    try {
        require(argc == 2, "fixture argument");
        std::ifstream input(argv[1], std::ios::binary);
        Bytes encoded((std::istreambuf_iterator<char>(input)), {});
        auto decoded = pb_istream_from_buffer(encoded.data(), encoded.size());
        legacy = Config_init_default;
        require(
            pb_decode(&decoded, Config_fields, &legacy) && !decoded.bytes_left &&
                legacy.ultimate_profiles_count == 2,
            "legacy protobuf fixture"
        );
        mounted_cfg.read = counted_read;
        mounted_cfg.prog = counted_program;
        mounted_cfg.erase = counted_erase;
        mounted_cfg.sync = ram_sync;
        mounted_cfg.read_size = 256;
        mounted_cfg.prog_size = 256;
        mounted_cfg.block_size = 4096;
        mounted_cfg.block_count = 128;
        mounted_cfg.block_cycles = 16;
        mounted_cfg.cache_size = 256;
        mounted_cfg.lookahead_size = 256;
        require(
            lfs_format(&mounted_fs, &mounted_cfg) == 0 && lfs_mount(&mounted_fs, &mounted_cfg) == 0,
            "real pinned LittleFS mount"
        );
        mount_allocations = live_allocations;
        mount_bytes = live_bytes;
        observe();
        const auto v1 = exact_upgrade();
        for (const auto &file : v1.files)
            write_native(file.first.c_str(), file.second);
        write_native("/config.bin", config_wire(legacy), Kind::Config);
        write_native("/ultimate-migration.src", config_wire(legacy), Kind::Config);
        ProfileStore s;
        require(s.Begin(7) && s.Generation() == 8 && s.Count() == 3, "actual v1 to v2 upgrade");
        Config compact = legacy;
        compact.ultimate_profiles_count = 0;
        compact.ultimate_profile_store_format = 1;
        compact.ultimate_profile_store_incarnation = 7;
        for (size_t i = 0; i < compact.game_mode_configs_count; ++i) {
            auto &m = compact.game_mode_configs[i];
            if (m.mode_id == MODE_ULTIMATE) {
                const auto index = m.ultimate_profile_config;
                m.ultimate_profile_id = index == 1 ? 3 : index == 2 ? 4 : 0;
                m.ultimate_profile_config = 0;
            }
        }
        require(
            s.PrepareCompact(compact) && s.ValidateCompactReceipt(compact) &&
                s.CompleteMigration(compact) == Status::Ok,
            "complete compact migration provenance"
        );
        write_native("/config-v2.bin", config_wire(compact), Kind::Config);
        write_native("/config-v2.prev", config_wire(compact), Kind::Config);
        for (unsigned id = 5; id <= 22; ++id) {
            auto t = identity(next_token++);
            auto r = s.Create(legacy.ultimate_profiles[0], "long session", id, t);
            require(r.status == Status::Ok && r.id == id, "twenty plus disposable create");
        }
        require(
            s.Delete(21, s.Generation(), 0, identity(next_token++)).status == Status::Ok &&
                s.Count() == 20,
            "twenty live with highwater22"
        );
        const auto immutable1 = read_native(record_path(1, 2).c_str()),
                   immutable3 = read_native(record_path(3, 1).c_str()),
                   immutable4 = read_native(record_path(4, 1).c_str());
        require(s.Activate(22) != nullptr, "pin older active immutable revision");
        for (unsigned i = 0; i < 129; ++i) {
            const auto expected = revision(s, 22);
            auto tx = identity(next_token++);
            auto r = s.Update(22, legacy.ultimate_profiles[i & 1], expected, tx);
            require(r.status == Status::Ok, "129 real persisted updates");
            if (i % 3 == 0) {
                ++dropped_results;
                auto query = s.QueryTransaction(tx);
                require(
                    query.status == Status::Ok && query.revision == r.revision,
                    "dropped result authoritative query"
                );
                const auto programs = block_programs;
                require(
                    s.Update(22, legacy.ultimate_profiles[i & 1], expected, tx).status ==
                            Status::Ok &&
                        programs == block_programs,
                    "exact replay zero storage writes"
                );
                ++exact_replays;
            }
            status_capacity(s, "long session update");
        }
        while (s.Generation() < 160)
            require(
                s.Reorder(22, s.Generation(), s.Generation(), identity(next_token++)).status ==
                    Status::Ok,
                "generation160 history"
            );
        require(
            s.Generation() == 160 && revision(s, 22) == 130 && s.Count() == 20,
            "physical history shape generation160 ID22 revision130"
        );
        auto capacity = status_capacity(s, "generation160 checkpoint");
        const auto total_erases = block_erases;
        std::printf(
            "history_checkpoint generation=%u count=%zu disposable_id=22 revision=%u highwater=22 successful_updates=129 dropped_results=%llu exact_replays=%llu total=%llu used=%llu free=%llu protected=%llu staging=%llu admissible=%u erases=%llu\n",
            s.Generation(),
            s.Count(),
            revision(s, 22),
            (unsigned long long)dropped_results,
            (unsigned long long)exact_replays,
            (unsigned long long)capacity.total_bytes,
            (unsigned long long)capacity.used_bytes,
            (unsigned long long)capacity.free_bytes,
            (unsigned long long)capacity.protected_bytes,
            (unsigned long long)capacity.staging_bytes,
            capacity.admissible_profiles,
            (unsigned long long)total_erases
        );
        for (unsigned cycle = 0; cycle < 2048; ++cycle) {
            fault_row(s, static_cast<unsigned>(CheckedStorage::Operation::OpenWrite), false);
            fault_row(s, static_cast<unsigned>(CheckedStorage::Operation::OpenWrite), true);
            fault_row(s, static_cast<unsigned>(CheckedStorage::Operation::Write), false);
            clear_rule();
            status_capacity(s, "cycle final status");
            ++fault_cycles;
        }
        require(
            read_native(record_path(1, 2).c_str()) == immutable1 &&
                read_native(record_path(3, 1).c_str()) == immutable3 &&
                read_native(record_path(4, 1).c_str()) == immutable4,
            "useful IDs1 3 4 preserved across all cycles"
        );
        require(
            s.Generation() == 160 && revision(s, 22) == 130 && !s.IsTransactionUncertain(),
            "all faults leave durable authority unchanged"
        );
        require(s.CollectGarbage() == Status::Ok, "final bounded cleanup");
        arm_ack_negative();
        require(
            checked_enumerates > 129 && block_erases > total_erases,
            "real GC and metadata relocation exercised"
        );
        std::printf(
            "fault_campaign_storage_liveness=PASS cycles=%llu triggers=%llu capacity_samples=%llu max_capacity_block_reads=%llu max_capacity_checked_stats=%llu max_capacity_host_ms=%.3f native_handles=0 live_lfs_allocations=%zu live_lfs_bytes=%zu peak_lfs_bytes=%zu total_lfs_allocations=%zu checked_enumerates=%llu block_reads=%llu block_programs=%llu block_erases=%llu ASAN_UBSAN=true hardware_liveness=NOT_PROVEN\n",
            (unsigned long long)fault_cycles,
            (unsigned long long)fault_triggers,
            (unsigned long long)capacity_samples,
            (unsigned long long)max_capacity_reads,
            (unsigned long long)max_capacity_stats,
            max_capacity_ms,
            live_allocations,
            live_bytes,
            peak_bytes,
            total_allocations,
            (unsigned long long)checked_enumerates,
            (unsigned long long)block_reads,
            (unsigned long long)block_programs,
            (unsigned long long)block_erases
        );
        clear_rule();
        require(
            lfs_unmount(&mounted_fs) == 0 && live_allocations == 0 && live_bytes == 0,
            "unmount releases all LittleFS allocations"
        );
        return 0;
    } catch (const std::exception &e) {
        std::fprintf(stderr, "liveness FAIL: %s\n", e.what());
        return 1;
    }
}
