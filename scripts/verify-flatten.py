#!/usr/bin/env python3
import pathlib, re, sys
root = pathlib.Path("/www/project2/codex")
def check_file(rel, pattern, desc):
    p = root / rel
    text = p.read_text()
    ok = re.search(pattern, text, re.M)
    print(f"{'✓' if ok else '✗'} {desc}: {'found' if ok else 'MISSING'} ({rel})")
    return bool(ok)
results = []
results.append(check_file("codex-rs/config/src/mcp_types.rs", r"pub flatten_tools:\s*bool", "McpServerConfig.flatten_tools"))
results.append(check_file("codex-rs/config/src/mcp_types.rs", r"pub flatten_tools:\s*Option<bool>", "RawMcpServerConfig.flatten_tools"))
results.append(check_file("codex-rs/codex-mcp/src/mcp/mod.rs", r"flattened_mcp_tool_servers", "McpConfig.flattened"))
results.append(check_file("codex-rs/core/src/config/mod.rs", r"flattened_mcp_tool_servers", "core config收集"))
results.append(check_file("codex-rs/codex-mcp/src/tools.rs", r"normalize_tools_for_model_with_flatten", "tools.rs flatten函数"))
results.append(check_file("codex-rs/codex-mcp/src/tools.rs", r"if flattened_mcp_tool_servers.contains", "tools.rs 空命名空间"))
results.append(check_file("codex-rs/core/src/tools/spec_plan.rs", r"flattened_servers", "spec_plan强制Direct"))
results.append(check_file("codex-rs/codex-mcp/src/connection_manager.rs", r"flattened_mcp_tool_servers", "connection_manager"))
results.append(check_file("codex-rs/codex-mcp/src/connection_manager/tool_catalog.rs", r"normalize_tools_for_model_with_flatten", "tool_catalog"))

print("\n--- 模拟展平行为 ---")
def sanitize(name):
    import re
    return re.sub(r'[^A-Za-z0-9_]', '_', name)
def callable_ns_prefix(ns, prefix):
    LEGACY="mcp__"
    if not prefix or ns.startswith(LEGACY):
        return ns
    return LEGACY+ns
def simulate(server, tool, prefix=True, flattened=[]):
    if server in flattened:
        ns=""
    else:
        ns=callable_ns_prefix(sanitize(server), prefix)
    name=sanitize(tool)
    if ns=="":
        return name, "plain Direct"
    return f"{ns}__{name}", "namespaced"
for s,fl in [("my_server",["my_server"]),("other",["my_server"]),("my_server",[])]:
    out,exp=simulate(s,"search",True,fl)
    print(f"server={s} flattened={s in fl} => {out} {exp}")

print("\n--- 配置示例 ---")
print('[mcp_servers.my_server]\ncommand="npx my-mcp"\nflatten_tools=true')
if all(results):
    print("\n✓ 所有检查通过")
    sys.exit(0)
else:
    print("\n✗ 未通过")
    sys.exit(1)
