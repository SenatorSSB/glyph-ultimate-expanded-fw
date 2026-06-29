#pragma once

#include <cstddef>
#include <cstdint>

namespace glyph::runtime_config::generated_source_owned {

// inert generated-table placeholder: schema metadata only, not wired into runtime selection.
inline constexpr std::uint32_t kGeneratedRuntimeConfigArtifactSchemaVersion = 1;
inline constexpr char kGeneratedRuntimeConfigArtifactKind[] =
    "generated_source_owned_runtime_config_table";
inline constexpr char kGeneratedRuntimeConfigArtifactNamePrefix[] =
    "generated_source_owned_runtime_config_";

struct GeneratedRuntimeConfigTableId {
  const char* controller_family;
  const char* profile_name;
  std::uint32_t revision;
};

struct GeneratedRuntimeConfigTableShape {
  std::uint8_t table_count;
  std::uint8_t points_per_table;
  std::uint8_t axes_per_point;
};

struct GeneratedRuntimeConfigArtifactMetadata {
  std::uint32_t schema_version;
  const char* artifact_kind;
  GeneratedRuntimeConfigTableId table_id;
  GeneratedRuntimeConfigTableShape table_shape;
};

constexpr bool MatchesUltimateRuntimeTableShape(
    GeneratedRuntimeConfigTableShape shape) {
  return shape.table_count == 27u && shape.points_per_table == 9u &&
         shape.axes_per_point == 2u;
}

}  // namespace glyph::runtime_config::generated_source_owned
