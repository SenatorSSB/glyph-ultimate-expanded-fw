        // Reached by the exact production-LittleFS long-history setup above.
        CheckedStorage::SetFaultHook(read_observer);
        require(!ProfileStoreFaultControls::Current().armed &&
                    !ProfileStoreFaultControls::Current().pending, "no fault state involved");
        const uint32_t ids[] = {1, 3, 4, 22, 5, 20};
        const auto programs_before_reads = block_programs, erases_before_reads = block_erases;
        uint64_t maximum_read_blocks = 0;
        double maximum_read_ms = 0;
        for (unsigned round = 0; round < 1000; ++round) {
            for (uint32_t id : ids) {
                reset_read_observation();
                UltimateProfile out{};
                uint32_t rev = 0;
                const auto before = block_reads;
                const auto started = std::chrono::steady_clock::now();
#if READ_PRODUCTION_TRACE
                { TraceObservation observed;
                  ProfileStoreReadTrace::Scope scope(trace_observer, &observed);
                  require(s.Read(id, out, &rev) == Status::Ok, "actual mounted traced READ");
                  require(observed.next == 19, "all nine production stages complete"); }
#else
                require(s.Read(id, out, &rev) == Status::Ok, "actual mounted READ");
#endif
                maximum_read_ms = std::max(maximum_read_ms,
                    std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now()-started).count());
                maximum_read_blocks = std::max(maximum_read_blocks, block_reads-before);
                require(rev == (id == 22 ? 130u : id == 1 ? 2u : 1u), "READ revision");
                require(observed_storage[unsigned(CheckedStorage::Operation::Stat)] == 2 &&
                    observed_storage[unsigned(CheckedStorage::Operation::OpenRead)] == 1 &&
                    observed_storage[unsigned(CheckedStorage::Operation::Read)] == 1 &&
                    observed_storage[unsigned(CheckedStorage::Operation::Close)] == 1,
                    "stat, open, read, close each completed");
                require(read_phases == 15, "checked read/close, CRC, decode, validation completed");
                no_leaks("full profile READ");
                ProfileStoreResponse response = ProfileStoreResponse_init_default;
                response.protocol_version = 1;
                response.store_generation = s.Generation();
                response.profile_id = id;
                response.profile_revision = rev;
                response.has_profile = true;
                response.profile = out;
                roundtrip_response(response, "stress READ", round == 0);
            }
        }
        require(block_programs == programs_before_reads && block_erases == erases_before_reads,
                "READs never write or erase");
        require(s.Generation() == 160 && s.Count() == 20, "READ authority unchanged");
        require(read_native(record_path(1,2).c_str()) == immutable1 &&
                read_native(record_path(3,1).c_str()) == immutable3 &&
                read_native(record_path(4,1).c_str()) == immutable4, "useful records unchanged");
        std::printf("read_stress=PASS reads=6000 ids=1,3,4,22,5,20 all_phases_completed=true max_block_reads=%llu max_host_ms=%.3f native_handles=0 live_lfs_allocations=%zu live_lfs_bytes=%zu peak_lfs_bytes=%zu gc_enumerations=%llu programs_during_reads=0 erases_during_reads=0 ASAN_UBSAN=true\n",
            (unsigned long long)maximum_read_blocks, maximum_read_ms, live_allocations,
            live_bytes, peak_bytes, (unsigned long long)checked_enumerates);
#if READ_PRODUCTION_TRACE
        check_failed_trace_cleanup(s);
#endif
        check_profile_fixture(argv[2], "maximum_accepted_stage_c");
        check_retained_response(argv[3], "retained_physical_ID1");
        check_retained_response(argv[4], "retained_physical_ID3");
        check_retained_response(argv[5], "retained_physical_ID4");
        check_retained_response(argv[6], "retained_physical_ID22");
        CheckedStorage::SetFaultHook(nullptr);
        require(lfs_unmount(&mounted_fs) == 0 && live_allocations == 0 && live_bytes == 0,
                "unmount releases all LittleFS allocations");
        return 0;
    } catch (const std::exception &e) {
        std::fprintf(stderr, "READ storage FAIL: %s\n", e.what());
        return 1;
    }
}
