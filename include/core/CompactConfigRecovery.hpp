/* Selection rule for interrupted compact Config rotation recovery. */
#ifndef _CORE_COMPACT_CONFIG_RECOVERY_HPP
#define _CORE_COMPACT_CONFIG_RECOVERY_HPP

class CompactConfigRecovery {
  public:
    enum class Source { Current, PriorCompact, Legacy };

    // A retained compact predecessor always wins over legacy input when the
    // current compact generation is absent. Its validation decides recovery;
    // callers must not silently fall back to legacy on an invalid predecessor.
    static constexpr Source Select(bool has_current, bool has_prior_compact) {
        return has_current ? Source::Current :
               (has_prior_compact ? Source::PriorCompact : Source::Legacy);
    }
};

#endif
