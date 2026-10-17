"""Cold recovery source pins and functional startup gates; no source rewrite."""
from pathlib import Path
import json
import sys

Import("env")
root = Path(env.subst("$PROJECT_DIR"))
sys.path.insert(0, str(root / "tools"))
from rt2_cold_recovery import COLD_DEFINE, WRAP_FLAGS, verify_installed, validate_graph, write_receipt


def enabled(defines, name):
    return any(isinstance(item, (tuple, list)) and len(item) == 2 and
               item[0] == name and str(item[1]) == "1" for item in defines)


defines = env.ParseFlags(env.get("BUILD_FLAGS", [])).get("CPPDEFINES", [])
if enabled(defines, COLD_DEFINE):
    if env.subst("$PIOENV") != "glyph_mk6" or not enabled(defines, "GLYPH_STRICT_HARDENING_CANDIDATE"):
        raise RuntimeError("cold recovery candidate is restricted to strict glyph_mk6")
    framework = Path(env.PioPlatform().get_package_dir("framework-arduinopico"))
    records = verify_installed(framework)
    env.AppendUnique(LINKFLAGS=list(WRAP_FLAGS))
    receipt = root / "local_backups/cold/source-pin-receipt.json"
    write_receipt(receipt, records, phase="configuration", wrappers=list(WRAP_FLAGS),
                  final_elf_binding="NOT_CHECKED_BY_SOURCE_GATE")

    def require_cold_source_authority(target, source, env):
        current = verify_installed(framework)
        if current != records:
            raise RuntimeError("cold recovery source authority changed during build")
        # Core objects are archived in LIBS rather than passed in the link
        # action's source argument. Traverse actual ELF dependency children,
        # including the archive's object/source children, without globbing
        # unrelated or stale files from the build directory.
        target_children = [child for node in target for child in node.children()]
        library_nodes = [node for node in env.Flatten(env.get("LIBS", []))
                         if hasattr(node, "children") and hasattr(node, "get_abspath")]
        paths, physical_paths, visited, mapped_sources, pending = set(), set(), set(), {}, list(source) + target_children + library_nodes
        while pending:
            node = pending.pop()
            identity = str(node)
            if identity in visited:
                continue
            visited.add(identity)
            node_path = Path(node.get_abspath()).resolve()
            paths.add(node_path)
            physical_paths.add(node_path)
            # FrameworkArduino uses a VariantDir: dependency children name a
            # virtual build-side main.cpp. SCons owns its canonical source
            # mapping; retain both paths, never infer by filesystem glob/name.
            source_node = node.srcnode()
            source_path = Path(source_node.get_abspath()).resolve()
            # Object srcnode() can name a hypothetical source-side .o which
            # is not an object in the link graph. Only canonical source files
            # supplement authority paths; objects remain actual node paths.
            if source_path.suffix != ".o":
                paths.add(source_path)
            if source_path != node_path:
                mapped_sources[str(node_path)] = str(source_path)
            pending.extend(node.children())
        graph_dump = root / "local_backups/cold/prelink-source-graph.json"
        graph_dump.parent.mkdir(parents=True, exist_ok=True)
        graph_dump.write_text(json.dumps(dict(
            status="GRAPH_CAPTURED_BEFORE_VALIDATION",
            source_roots=[str(node) for node in source],
            target_children=[str(node) for node in target_children],
            library_nodes=[str(node) for node in library_nodes],
            library_values=[str(node) for node in env.Flatten(env.get("LIBS", []))],
            scons_source_mappings=mapped_sources,
            physical_node_paths=sorted(map(str, physical_paths)),
            paths=sorted(map(str, paths))), indent=2) + "\n")
        selected = validate_graph(paths, root, framework, env.get("LINKFLAGS", []))
        write_receipt(receipt, current, phase="prelink", wrappers=list(WRAP_FLAGS),
                      selected_objects=selected, graph_nodes=len(paths),
                      final_elf_binding="REQUIRES_SEPARATE_FINAL_ELF_AUDIT")

    env.AddPreAction("$BUILD_DIR/${PROGNAME}.elf", require_cold_source_authority)
