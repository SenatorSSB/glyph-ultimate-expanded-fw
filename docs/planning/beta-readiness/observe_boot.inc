// Included only in a disposable copy of the LittleFS host boot probe.
using Clock = std::chrono::steady_clock;
using Op = CheckedStorage::Operation;
struct Observation {
    unsigned stage;
    long long elapsed_us;
    size_t nor_reads, enumerations, opens, seeks, reads;
};
Observation observations[17]{};
size_t sample_count, initial_reads, operation_counts[unsigned(Op::Enumerate) + 1]{};
unsigned fault_stage, fault_hits;
bool inject_read_fault;
Clock::time_point origin;

void observe_stage(boot_diagnostics::Stage stage) {
    const auto code = unsigned(stage);
    test::need(sample_count < 17, "unexpected startup stage count");
    observations[sample_count++] = {
        code, std::chrono::duration_cast<std::chrono::microseconds>(Clock::now() - origin).count(),
        test::reads - initial_reads, operation_counts[unsigned(Op::Enumerate)],
        operation_counts[unsigned(Op::OpenRead)], operation_counts[unsigned(Op::Seek)],
        operation_counts[unsigned(Op::Read)]
    };
    if (code && code == fault_stage) inject_read_fault = true;
}

void start_observing() {
    if (const char *value = std::getenv("BETA_PROBE_FAULT_STAGE")) fault_stage = unsigned(std::atoi(value));
    initial_reads = test::reads;
    CheckedStorage::SetFaultHook([](CheckedStorage::Kind, Op op, CheckedStorage::Phase phase, const char *path) {
        if (phase == CheckedStorage::Phase::Before) {
            ++operation_counts[unsigned(op)];
            if (inject_read_fault && op == Op::Read && path && !std::strcmp(path, "/ultimate-00000002-00000001.bin")) {
                ++fault_hits;
                return CheckedStorage::Fault::Fail;
            }
        }
        return CheckedStorage::Fault::None;
    });
    origin = Clock::now();
}

void finish_observing() {
    observe_stage(static_cast<boot_diagnostics::Stage>(0));
    CheckedStorage::SetFaultHook(nullptr);
    std::ofstream out(test::path("stages.txt"));
    out << fault_hits << '\n';
    for (size_t i = 0; i < sample_count; ++i) {
        const auto &s = observations[i];
        out << s.stage << ' ' << s.elapsed_us << ' ' << s.nor_reads << ' ' << s.enumerations
            << ' ' << s.opens << ' ' << s.seeks << ' ' << s.reads << '\n';
    }
}
