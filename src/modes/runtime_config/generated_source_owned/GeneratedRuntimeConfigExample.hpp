#pragma once

#include "GeneratedRuntimeConfigSchema.hpp"

namespace glyph::runtime_config::generated_source_owned {

// inert generated-table placeholder: fixture-like metadata shape only.
inline constexpr GeneratedRuntimeConfigTableShape kExampleGeneratedTableShape{
    27u,
    9u,
    2u,
};

inline constexpr GeneratedRuntimeConfigTableId kExampleGeneratedTableId{
    "glyph_mk6",
    "example_source_owned_runtime_config",
    1u,
};

inline constexpr GeneratedRuntimeConfigArtifactMetadata
    kExampleGeneratedArtifactMetadata{
        kGeneratedRuntimeConfigArtifactSchemaVersion,
        kGeneratedRuntimeConfigArtifactKind,
        kExampleGeneratedTableId,
        kExampleGeneratedTableShape,
};

static_assert(MatchesUltimateRuntimeTableShape(kExampleGeneratedTableShape),
              "example generated table shape must match the current runtime table shape");

}  // namespace glyph::runtime_config::generated_source_owned
