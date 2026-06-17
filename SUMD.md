# reko

Refaktoryzacja hardkodowanych wartości, struktur i kodu w projektach Python

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `reko`
- **version**: `0.1.1`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(3), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: reko;
  version: 0.1.1;
}

dependencies {
  runtime: "typer>=0.12.0, rich>=13.0, pydantic>=2.0, pyyaml>=6.0, tomli>=2.0; python_version<'3.11'";
  apply: libcst>=1.0;
  dev: "reko[apply], pytest>=7.0, pytest-cov>=4.0, ruff>=0.4, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

entity[name="Finding"] {
  kind: FindingKind!;
  file: Path!;
  line: int!;
  col: int!;
  end_line: int | None;
  end_col: int | None;
  value_repr: string!;
  message: string!;
  suggested_name: str | None;
  severity: string!;
  context: str | None;
  metadata: dict[str, Any]!;
}

entity[name="ScanReport"] {
  root: Path!;
  findings: list[Finding]!;
  files_scanned: int!;
  counts: dict[str, int]!;
}

entity[name="RefactorChange"] {
  action: RefactorAction!;
  file: Path!;
  description: string!;
  line: int | None;
  metadata: dict[str, Any]!;
}

entity[name="RefactorPlan"] {
  root: Path!;
  changes: list[RefactorChange]!;
  dry_run: bool!;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="reko"] {
  entry: reko.cli.main:app;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, PIP_DISABLE_PIP_VERSION_CHECK;
}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES, PIP_DISABLE_PIP_VERSION_CHECK;
  runtime_llm: OPENROUTER_API_KEY;
  runtime_pfix: PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
}
```

## Interfaces

### CLI Entry Points

- `reko`

### testql Scenarios

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-smoke.testql.toon.yaml
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true
# DETECTORS: ConfigEndpointDetector

CONFIG[5]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 10000
  retry_count, 3
  retry_backoff_ms, 1000
  detected_frameworks, ConfigEndpointDetector

# Wait for service to be ready
WAIT 1000

# Health check
API GET /api/health 200
ASSERT_STATUS 200

# REST API Endpoints (1 unique)
API[1]{method, endpoint, expected_status}:
  GET, /, 200

# Capture useful values from responses for subsequent tests
# CAPTURE request_id FROM 'headers.x-request-id'
# CAPTURE session_token FROM 'body.token'

ASSERT[2]{field, operator, expected}:
  _status, <, 500
  _status, >=, 200

# Conditional flow for error handling
FLOW[2]{condition, action}:
  _status >= 500, LOG 'Server error detected'
  _status == 429, WAIT 2000  # Rate limit - wait and retry


# Summary by Framework:
#   env: 1 endpoints
```

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m reko
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m reko --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m reko --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m reko --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 2 assertions from pytest
ASSERT[2]{field, operator, expected}:
  result.returncode, ==, 0
  result.returncode, ==, 0
```

## Configuration

```yaml
project:
  name: reko
  version: 0.1.1
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
typer>=0.12.0
rich>=13.0
pydantic>=2.0
pyyaml>=6.0
tomli>=2.0; python_version<'3.11'
```

### Development

```text markpact:deps python scope=dev
reko[apply]
pytest>=7.0
pytest-cov>=4.0
ruff>=0.4
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Deployment

```bash markpact:run
pip install reko

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PIP_DISABLE_PIP_VERSION_CHECK` | `1` | Quiet pip in venv/scripts (suppress "new release of pip" notices) |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`reko`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `pyproject.toml:version`, `.venv/lib/python3.13/site-packages/markdown_it/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# reko | 31f 1989L | python:28,shell:2,less:1 | 2026-06-17
# stats: 77 func | 21 cls | 31 mod | CC̄=4.1 | critical:6 | cycles:0
# alerts[5]: CC remove_unused_constants=16; CC extract_constants=15; CC insert_import=14; CC split_structures=14; CC test_examples_workflow_produces_valid_python=12
# hotspots[5]: split_structures fan=27; move_constants fan=19; plan_cmd fan=17; extract_constants fan=16; remove_unused_constants fan=15
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[31]:
  app.doql.less,74
  examples/01-hardcoded-api/before.py,35
  examples/02-inline-config/before.py,26
  examples/03-unused-constants/before.py,13
  examples/run_all.py,68
  project.sh,63
  src/reko/__init__.py,40
  src/reko/__main__.py,7
  src/reko/cli/__init__.py,2
  src/reko/cli/main.py,173
  src/reko/config.py,105
  src/reko/models.py,83
  src/reko/refactor/__init__.py,2
  src/reko/refactor/_ast_extract.py,166
  src/reko/refactor/_utils.py,102
  src/reko/refactor/engine.py,46
  src/reko/refactor/extract.py,76
  src/reko/refactor/move.py,104
  src/reko/refactor/remove.py,71
  src/reko/refactor/split.py,225
  src/reko/reporters/__init__.py,2
  src/reko/reporters/json_reporter.py,42
  src/reko/scanner/__init__.py,2
  src/reko/scanner/detector.py,261
  src/reko/writers/__init__.py,2
  tests/fixtures/sample.py,24
  tests/test_cli.py,25
  tests/test_detector.py,29
  tests/test_examples_e2e.py,54
  tests/test_refactor.py,65
  tree.sh,2
D:
  examples/01-hardcoded-api/before.py:
    e: fetch_users,fetch_orders,is_premium
    fetch_users(page)
    fetch_orders(user_id)
    is_premium(total)
  examples/02-inline-config/before.py:
    e: get_settings
    get_settings()
  examples/03-unused-constants/before.py:
    e: build_url
    build_url(path)
  examples/run_all.py:
    e: run,prepare_workdir,main
    run(cmd)
    prepare_workdir()
    main()
  src/reko/__init__.py:
  src/reko/__main__.py:
  src/reko/cli/__init__.py:
  src/reko/cli/main.py:
    e: _print_findings,scan,extract,split,move_cmd,remove,apply,plan_cmd
    _print_findings(report)
    scan(path;format;output)
    extract(path;target;dry_run)
    split(path;dry_run)
    move_cmd(source;target;names;dry_run)
    remove(path;dry_run)
    apply(plan;dry_run)
    plan_cmd(path;output)
  src/reko/config.py:
    e: _load_yaml,_load_toml,load_config,ScanConfig,ExtractConfig,SplitConfig,MoveConfig,RekoConfig
    ScanConfig:
    ExtractConfig:
    SplitConfig:
    MoveConfig:
    RekoConfig:
    _load_yaml(path)
    _load_toml(path)
    load_config(root)
  src/reko/models.py:
    e: FindingKind,RefactorAction,Finding,ScanReport,RefactorChange,RefactorPlan,RefactorResult
    FindingKind:
    RefactorAction:
    Finding:
    ScanReport: by_kind(0)
    RefactorChange:
    RefactorPlan:
    RefactorResult:
  src/reko/refactor/__init__.py:
  src/reko/refactor/_ast_extract.py:
    e: build_extraction_plan,transform_module,transform_source,insert_import,ExtractableNode,ExtractionPlan,_InsideJoinedStr,_ExtractCollector,_ExtractTransformer
    ExtractableNode:
    ExtractionPlan:
    _InsideJoinedStr: __init__(0),visit_JoinedStr(1)
    _ExtractCollector: __init__(2),visit_FunctionDef(1),visit_AsyncFunctionDef(1),visit_ClassDef(1),visit_Constant(1)
    _ExtractTransformer: __init__(1),visit_Constant(1)
    build_extraction_plan(tree;config)
    transform_module(tree;plan)
    transform_source(source;plan;tree)
    insert_import(source;module;names)
  src/reko/refactor/_utils.py:
    e: _line_offsets,_position_to_index,apply_replacements,unique_name,to_upper_snake,ensure_trailing_newline,read_module,write_module,module_level_names,collect_name_usages,Replacement
    Replacement:
    _line_offsets(source)
    _position_to_index(source;line;col)
    apply_replacements(source;replacements)
    unique_name(base;existing)
    to_upper_snake(name)
    ensure_trailing_newline(text)
    read_module(path)
    write_module(path;source;dry_run)
    module_level_names(tree)
    collect_name_usages(tree;names)
  src/reko/refactor/engine.py:
    e: apply_plan
    apply_plan(plan_path)
  src/reko/refactor/extract.py:
    e: _group_target_path,extract_constants
    _group_target_path(source;target;config)
    extract_constants(source)
  src/reko/refactor/move.py:
    e: _assignment_lines,_remove_assignments,_ensure_import,move_constants
    _assignment_lines(source;tree;names)
    _remove_assignments(source;tree;names)
    _ensure_import(source;module;names)
    move_constants(source;target)
  src/reko/refactor/remove.py:
    e: remove_unused_constants
    remove_unused_constants(source)
  src/reko/refactor/split.py:
    e: _parent_map,_contains_node,_literal_size,_key_name,_make_assign,_split_dict_node,_split_list_node,_insert_index,split_structures,_iter_scopes,_SplitTarget,_SplitFinder
    _SplitTarget:
    _SplitFinder: __init__(1),visit(1),visit_Module(1),visit_FunctionDef(1),visit_AsyncFunctionDef(1),visit_Dict(1),visit_List(1),_insert_at(1),finalize(0)
    _parent_map(tree)
    _contains_node(parent;child)
    _literal_size(node)
    _key_name(key;index)
    _make_assign(name;value)
    _split_dict_node(node;prefix;used)
    _split_list_node(node;prefix;used)
    _insert_index(scope)
    split_structures(source)
    _iter_scopes(tree)
  src/reko/reporters/__init__.py:
  src/reko/reporters/json_reporter.py:
    e: report_to_dict,write_report
    report_to_dict(report)
    write_report(report;output;fmt)
  src/reko/scanner/__init__.py:
  src/reko/scanner/detector.py:
    e: _should_exclude,_is_magic_number,_suggest_constant_name,_literal_size,_get_source_segment,scan_file,_collect_literal_hashes,scan_project,_HardcodeVisitor
    _HardcodeVisitor: __init__(3),visit_JoinedStr(1),visit_Module(1),visit_FunctionDef(1),visit_AsyncFunctionDef(1),visit_ClassDef(1),visit_Constant(1),visit_Dict(1),visit_List(1)
    _should_exclude(path;root;patterns)
    _is_magic_number(value;config)
    _suggest_constant_name(value;kind)
    _literal_size(node)
    _get_source_segment(source;node)
    scan_file(path;config)
    _collect_literal_hashes(findings)
    scan_project(root;config)
  src/reko/writers/__init__.py:
  tests/fixtures/sample.py:
    e: process,greet
    process(value)
    greet()
  tests/test_cli.py:
    e: test_cli_scan_table,test_cli_plan
    test_cli_scan_table()
    test_cli_plan(tmp_path)
  tests/test_detector.py:
    e: test_scan_file_detects_magic_number_and_string,test_scan_file_detects_inline_dict_and_list,test_scan_project_returns_report
    test_scan_file_detects_magic_number_and_string()
    test_scan_file_detects_inline_dict_and_list()
    test_scan_project_returns_report()
  tests/test_examples_e2e.py:
    e: _run,setup_module,test_examples_workflow_produces_valid_python
    _run(cmd)
    setup_module()
    test_examples_workflow_produces_valid_python()
  tests/test_refactor.py:
    e: _copy_fixture,test_extract_constants_dry_run,test_extract_constants_apply,test_split_structures_apply,test_remove_unused_constants,test_move_constants
    _copy_fixture(tmp_path;name)
    test_extract_constants_dry_run(tmp_path)
    test_extract_constants_apply(tmp_path)
    test_split_structures_apply(tmp_path)
    test_remove_unused_constants(tmp_path)
    test_move_constants(tmp_path)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('reko', '0.1.1', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 74, 'less').
project_file('examples/01-hardcoded-api/before.py', 35, 'python').
project_file('examples/02-inline-config/before.py', 26, 'python').
project_file('examples/03-unused-constants/before.py', 13, 'python').
project_file('examples/run_all.py', 68, 'python').
project_file('project.sh', 63, 'shell').
project_file('src/reko/__init__.py', 40, 'python').
project_file('src/reko/__main__.py', 7, 'python').
project_file('src/reko/cli/__init__.py', 2, 'python').
project_file('src/reko/cli/main.py', 173, 'python').
project_file('src/reko/config.py', 105, 'python').
project_file('src/reko/models.py', 83, 'python').
project_file('src/reko/refactor/__init__.py', 2, 'python').
project_file('src/reko/refactor/_ast_extract.py', 166, 'python').
project_file('src/reko/refactor/_utils.py', 102, 'python').
project_file('src/reko/refactor/engine.py', 46, 'python').
project_file('src/reko/refactor/extract.py', 76, 'python').
project_file('src/reko/refactor/move.py', 104, 'python').
project_file('src/reko/refactor/remove.py', 71, 'python').
project_file('src/reko/refactor/split.py', 225, 'python').
project_file('src/reko/reporters/__init__.py', 2, 'python').
project_file('src/reko/reporters/json_reporter.py', 42, 'python').
project_file('src/reko/scanner/__init__.py', 2, 'python').
project_file('src/reko/scanner/detector.py', 261, 'python').
project_file('src/reko/writers/__init__.py', 2, 'python').
project_file('tests/fixtures/sample.py', 24, 'python').
project_file('tests/test_cli.py', 25, 'python').
project_file('tests/test_detector.py', 29, 'python').
project_file('tests/test_examples_e2e.py', 54, 'python').
project_file('tests/test_refactor.py', 65, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('examples/01-hardcoded-api/before.py', 'fetch_users', 1, 2, 5).
python_function('examples/01-hardcoded-api/before.py', 'fetch_orders', 1, 4, 4).
python_function('examples/01-hardcoded-api/before.py', 'is_premium', 1, 1, 0).
python_function('examples/02-inline-config/before.py', 'get_settings', 0, 1, 0).
python_function('examples/03-unused-constants/before.py', 'build_url', 1, 1, 1).
python_function('examples/run_all.py', 'run', 1, 4, 4).
python_function('examples/run_all.py', 'prepare_workdir', 0, 3, 4).
python_function('examples/run_all.py', 'main', 0, 4, 9).
python_function('src/reko/cli/main.py', '_require_python_file', 1, 3, 3).
python_function('src/reko/cli/main.py', '_print_findings', 1, 5, 7).
python_function('src/reko/cli/main.py', 'scan', 3, 5, 13).
python_function('src/reko/cli/main.py', 'extract', 3, 2, 7).
python_function('src/reko/cli/main.py', 'split', 2, 2, 6).
python_function('src/reko/cli/main.py', 'move_cmd', 4, 3, 8).
python_function('src/reko/cli/main.py', 'remove', 2, 1, 6).
python_function('src/reko/cli/main.py', 'apply', 2, 1, 6).
python_function('src/reko/cli/main.py', 'plan_cmd', 2, 5, 17).
python_function('src/reko/config.py', '_load_yaml', 1, 3, 3).
python_function('src/reko/config.py', '_load_toml', 1, 3, 4).
python_function('src/reko/config.py', 'load_config', 1, 5, 6).
python_function('src/reko/refactor/_ast_extract.py', 'build_extraction_plan', 2, 6, 12).
python_function('src/reko/refactor/_ast_extract.py', 'transform_module', 2, 1, 4).
python_function('src/reko/refactor/_ast_extract.py', 'transform_source', 3, 2, 2).
python_function('src/reko/refactor/_ast_extract.py', 'insert_import', 3, 14, 9).
python_function('src/reko/refactor/_utils.py', '_line_offsets', 1, 2, 3).
python_function('src/reko/refactor/_utils.py', '_position_to_index', 3, 4, 4).
python_function('src/reko/refactor/_utils.py', 'apply_replacements', 2, 2, 2).
python_function('src/reko/refactor/_utils.py', 'unique_name', 2, 3, 0).
python_function('src/reko/refactor/_utils.py', 'to_upper_snake', 1, 2, 3).
python_function('src/reko/refactor/_utils.py', 'ensure_trailing_newline', 1, 2, 1).
python_function('src/reko/refactor/_utils.py', 'require_python_file', 1, 4, 7).
python_function('src/reko/refactor/_utils.py', 'read_module', 1, 1, 3).
python_function('src/reko/refactor/_utils.py', 'write_module', 3, 2, 3).
python_function('src/reko/refactor/_utils.py', 'module_level_names', 1, 7, 3).
python_function('src/reko/refactor/_utils.py', 'collect_name_usages', 2, 1, 5).
python_function('src/reko/refactor/engine.py', 'apply_plan', 1, 8, 14).
python_function('src/reko/refactor/extract.py', '_group_target_path', 3, 2, 0).
python_function('src/reko/refactor/extract.py', 'extract_constants', 1, 15, 16).
python_function('src/reko/refactor/move.py', '_assignment_lines', 3, 7, 3).
python_function('src/reko/refactor/move.py', '_remove_assignments', 3, 8, 5).
python_function('src/reko/refactor/move.py', '_ensure_import', 3, 4, 6).
python_function('src/reko/refactor/move.py', 'move_constants', 2, 8, 19).
python_function('src/reko/refactor/remove.py', 'remove_unused_constants', 1, 16, 15).
python_function('src/reko/refactor/split.py', '_parent_map', 1, 3, 2).
python_function('src/reko/refactor/split.py', '_contains_node', 2, 3, 1).
python_function('src/reko/refactor/split.py', '_literal_size', 1, 3, 2).
python_function('src/reko/refactor/split.py', '_key_name', 2, 3, 1).
python_function('src/reko/refactor/split.py', '_make_assign', 2, 1, 3).
python_function('src/reko/refactor/split.py', '_split_dict_node', 3, 3, 11).
python_function('src/reko/refactor/split.py', '_split_list_node', 3, 2, 9).
python_function('src/reko/refactor/split.py', '_insert_index', 1, 3, 3).
python_function('src/reko/refactor/split.py', 'split_structures', 1, 14, 27).
python_function('src/reko/refactor/split.py', '_iter_scopes', 1, 3, 3).
python_function('src/reko/reporters/json_reporter.py', 'report_to_dict', 1, 2, 2).
python_function('src/reko/reporters/json_reporter.py', 'write_report', 3, 2, 5).
python_function('src/reko/scanner/detector.py', '_should_exclude', 3, 4, 4).
python_function('src/reko/scanner/detector.py', '_is_magic_number', 2, 7, 2).
python_function('src/reko/scanner/detector.py', '_suggest_constant_name', 2, 9, 8).
python_function('src/reko/scanner/detector.py', '_literal_size', 1, 3, 2).
python_function('src/reko/scanner/detector.py', '_get_source_segment', 2, 7, 5).
python_function('src/reko/scanner/detector.py', 'scan_file', 2, 3, 5).
python_function('src/reko/scanner/detector.py', '_collect_literal_hashes', 1, 3, 5).
python_function('src/reko/scanner/detector.py', 'scan_project', 2, 10, 14).
python_function('tests/fixtures/sample.py', 'process', 1, 2, 0).
python_function('tests/fixtures/sample.py', 'greet', 0, 1, 0).
python_function('tests/test_cli.py', 'test_cli_scan_table', 0, 3, 2).
python_function('tests/test_cli.py', 'test_cli_plan', 1, 4, 5).
python_function('tests/test_detector.py', 'test_scan_file_detects_magic_number_and_string', 0, 4, 1).
python_function('tests/test_detector.py', 'test_scan_file_detects_inline_dict_and_list', 0, 4, 1).
python_function('tests/test_detector.py', 'test_scan_project_returns_report', 0, 4, 2).
python_function('tests/test_examples_e2e.py', '_run', 1, 1, 1).
python_function('tests/test_examples_e2e.py', 'setup_module', 0, 3, 4).
python_function('tests/test_examples_e2e.py', 'test_examples_workflow_produces_valid_python', 0, 12, 6).
python_function('tests/test_refactor.py', '_copy_fixture', 2, 1, 3).
python_function('tests/test_refactor.py', 'test_extract_constants_dry_run', 1, 3, 4).
python_function('tests/test_refactor.py', 'test_extract_constants_apply', 1, 3, 4).
python_function('tests/test_refactor.py', 'test_split_structures_apply', 1, 3, 3).
python_function('tests/test_refactor.py', 'test_remove_unused_constants', 1, 4, 3).
python_function('tests/test_refactor.py', 'test_move_constants', 1, 5, 4).

% ── Python Classes ───────────────────────────────────────
python_class('src/reko/config.py', 'ScanConfig').
python_class('src/reko/config.py', 'ExtractConfig').
python_class('src/reko/config.py', 'SplitConfig').
python_class('src/reko/config.py', 'MoveConfig').
python_class('src/reko/config.py', 'RekoConfig').
python_class('src/reko/models.py', 'FindingKind').
python_class('src/reko/models.py', 'RefactorAction').
python_class('src/reko/models.py', 'Finding').
python_class('src/reko/models.py', 'ScanReport').
python_method('ScanReport', 'by_kind', 0, 2, 1).
python_class('src/reko/models.py', 'RefactorChange').
python_class('src/reko/models.py', 'RefactorPlan').
python_class('src/reko/models.py', 'RefactorResult').
python_class('src/reko/refactor/_ast_extract.py', 'ExtractableNode').
python_class('src/reko/refactor/_ast_extract.py', 'ExtractionPlan').
python_class('src/reko/refactor/_ast_extract.py', '_InsideJoinedStr').
python_method('_InsideJoinedStr', '__init__', 0, 1, 1).
python_method('_InsideJoinedStr', 'visit_JoinedStr', 1, 3, 4).
python_class('src/reko/refactor/_ast_extract.py', '_ExtractCollector').
python_method('_ExtractCollector', '__init__', 2, 1, 0).
python_method('_ExtractCollector', 'visit_FunctionDef', 1, 1, 1).
python_method('_ExtractCollector', 'visit_AsyncFunctionDef', 1, 1, 1).
python_method('_ExtractCollector', 'visit_ClassDef', 1, 1, 1).
python_method('_ExtractCollector', 'visit_Constant', 1, 2, 7).
python_class('src/reko/refactor/_ast_extract.py', '_ExtractTransformer').
python_method('_ExtractTransformer', '__init__', 1, 1, 0).
python_method('_ExtractTransformer', 'visit_Constant', 1, 2, 4).
python_class('src/reko/refactor/_utils.py', 'Replacement').
python_class('src/reko/refactor/split.py', '_SplitTarget').
python_class('src/reko/refactor/split.py', '_SplitFinder').
python_method('_SplitFinder', '__init__', 1, 1, 0).
python_method('_SplitFinder', 'visit', 1, 2, 3).
python_method('_SplitFinder', 'visit_Module', 1, 1, 1).
python_method('_SplitFinder', 'visit_FunctionDef', 1, 1, 1).
python_method('_SplitFinder', 'visit_AsyncFunctionDef', 1, 1, 1).
python_method('_SplitFinder', 'visit_Dict', 1, 2, 5).
python_method('_SplitFinder', 'visit_List', 1, 2, 5).
python_method('_SplitFinder', '_insert_at', 1, 5, 4).
python_method('_SplitFinder', 'finalize', 0, 7, 4).
python_class('src/reko/scanner/detector.py', '_HardcodeVisitor').
python_method('_HardcodeVisitor', '__init__', 3, 1, 1).
python_method('_HardcodeVisitor', 'visit_JoinedStr', 1, 3, 4).
python_method('_HardcodeVisitor', 'visit_Module', 1, 5, 3).
python_method('_HardcodeVisitor', 'visit_FunctionDef', 1, 1, 1).
python_method('_HardcodeVisitor', 'visit_AsyncFunctionDef', 1, 1, 1).
python_method('_HardcodeVisitor', 'visit_ClassDef', 1, 1, 1).
python_method('_HardcodeVisitor', 'visit_Constant', 1, 9, 11).
python_method('_HardcodeVisitor', 'visit_Dict', 1, 4, 7).
python_method('_HardcodeVisitor', 'visit_List', 1, 2, 5).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PIP_DISABLE_PIP_VERSION_CHECK', '1', 'Quiet pip in venv/scripts (suppress "new release of pip" notices)').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-api-smoke.testql.toon.yaml', 'api').
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
```

## Call Graph

*54 nodes · 56 edges · 12 modules · CC̄=3.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `split_structures` *(in src.reko.refactor.split)* | 14 ⚠ | 2 | 33 | **35** |
| `move_constants` *(in src.reko.refactor.move)* | 8 | 2 | 28 | **30** |
| `remove_unused_constants` *(in src.reko.refactor.remove)* | 16 ⚠ | 2 | 27 | **29** |
| `extract_constants` *(in src.reko.refactor.extract)* | 15 ⚠ | 2 | 22 | **24** |
| `_suggest_constant_name` *(in src.reko.scanner.detector)* | 9 | 3 | 18 | **21** |
| `apply_plan` *(in src.reko.refactor.engine)* | 8 | 1 | 20 | **21** |
| `plan_cmd` *(in src.reko.cli.main)* | 5 | 0 | 21 | **21** |
| `visit_Constant` *(in src.reko.scanner.detector._HardcodeVisitor)* | 9 | 0 | 20 | **20** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/reko
# generated in 0.03s
# nodes: 54 | edges: 56 | modules: 12
# CC̄=3.7

HUBS[20]:
  src.reko.refactor.split.split_structures
    CC=14  in:2  out:33  total:35
  src.reko.refactor.move.move_constants
    CC=8  in:2  out:28  total:30
  src.reko.refactor.remove.remove_unused_constants
    CC=16  in:2  out:27  total:29
  src.reko.refactor.extract.extract_constants
    CC=15  in:2  out:22  total:24
  src.reko.scanner.detector._suggest_constant_name
    CC=9  in:3  out:18  total:21
  src.reko.refactor.engine.apply_plan
    CC=8  in:1  out:20  total:21
  src.reko.cli.main.plan_cmd
    CC=5  in:0  out:21  total:21
  src.reko.scanner.detector._HardcodeVisitor.visit_Constant
    CC=9  in:0  out:20  total:20
  examples.run_all.main
    CC=4  in:0  out:19  total:19
  src.reko.scanner.detector.scan_project
    CC=10  in:2  out:16  total:18
  src.reko.refactor._ast_extract.build_extraction_plan
    CC=6  in:1  out:14  total:15
  src.reko.refactor.split._split_dict_node
    CC=3  in:1  out:13  total:14
  src.reko.cli.main.scan
    CC=5  in:0  out:14  total:14
  src.reko.config.load_config
    CC=5  in:7  out:7  total:14
  src.reko.scanner.detector._get_source_segment
    CC=7  in:2  out:11  total:13
  src.reko.refactor.split._split_list_node
    CC=2  in:1  out:11  total:12
  src.reko.refactor._ast_extract._ExtractCollector.visit_Constant
    CC=9  in:0  out:12  total:12
  src.reko.cli.main.move_cmd
    CC=3  in:0  out:11  total:11
  src.reko.refactor._utils.write_module
    CC=2  in:6  out:3  total:9
  src.reko.cli.main.extract
    CC=2  in:0  out:9  total:9

MODULES:
  examples.run_all  [3 funcs]
    main  CC=4  out:19
    prepare_workdir  CC=3  out:4
    run  CC=4  out:7
  src.reko.cli.main  [7 funcs]
    apply  CC=1  out:6
    extract  CC=2  out:9
    move_cmd  CC=3  out:11
    plan_cmd  CC=5  out:21
    remove  CC=1  out:6
    scan  CC=5  out:14
    split  CC=2  out:7
  src.reko.config  [3 funcs]
    _load_toml  CC=3  out:6
    _load_yaml  CC=3  out:3
    load_config  CC=5  out:7
  src.reko.refactor._ast_extract  [4 funcs]
    visit_Constant  CC=9  out:12
    build_extraction_plan  CC=6  out:14
    transform_module  CC=1  out:4
    transform_source  CC=2  out:2
  src.reko.refactor._utils  [9 funcs]
    _position_to_index  CC=4  out:6
    apply_replacements  CC=2  out:3
    collect_name_usages  CC=1  out:5
    ensure_trailing_newline  CC=2  out:1
    module_level_names  CC=7  out:7
    read_module  CC=1  out:2
    to_upper_snake  CC=2  out:5
    unique_name  CC=3  out:0
    write_module  CC=2  out:3
  src.reko.refactor.engine  [1 funcs]
    apply_plan  CC=8  out:20
  src.reko.refactor.extract  [2 funcs]
    _group_target_path  CC=2  out:0
    extract_constants  CC=15  out:22
  src.reko.refactor.move  [3 funcs]
    _assignment_lines  CC=7  out:4
    _remove_assignments  CC=8  out:6
    move_constants  CC=8  out:28
  src.reko.refactor.remove  [1 funcs]
    remove_unused_constants  CC=16  out:27
  src.reko.refactor.split  [9 funcs]
    _insert_at  CC=5  out:4
    finalize  CC=7  out:5
    _contains_node  CC=3  out:1
    _insert_index  CC=3  out:3
    _iter_scopes  CC=3  out:3
    _make_assign  CC=1  out:3
    _split_dict_node  CC=3  out:13
    _split_list_node  CC=2  out:11
    split_structures  CC=14  out:33
  src.reko.reporters.json_reporter  [2 funcs]
    report_to_dict  CC=2  out:3
    write_report  CC=2  out:6
  src.reko.scanner.detector  [10 funcs]
    visit_Constant  CC=9  out:20
    visit_Dict  CC=4  out:8
    visit_List  CC=2  out:6
    _get_source_segment  CC=7  out:11
    _is_magic_number  CC=7  out:2
    _literal_size  CC=3  out:4
    _should_exclude  CC=4  out:5
    _suggest_constant_name  CC=9  out:18
    scan_file  CC=3  out:5
    scan_project  CC=10  out:16

EDGES:
  examples.run_all.main → examples.run_all.prepare_workdir
  examples.run_all.main → examples.run_all.run
  src.reko.config.load_config → src.reko.config._load_toml
  src.reko.config.load_config → src.reko.config._load_yaml
  src.reko.cli.main.scan → src.reko.config.load_config
  src.reko.cli.main.scan → src.reko.scanner.detector.scan_project
  src.reko.cli.main.scan → src.reko.reporters.json_reporter.write_report
  src.reko.cli.main.extract → src.reko.config.load_config
  src.reko.cli.main.extract → src.reko.refactor.extract.extract_constants
  src.reko.cli.main.split → src.reko.refactor.split.split_structures
  src.reko.cli.main.move_cmd → src.reko.refactor.move.move_constants
  src.reko.cli.main.remove → src.reko.refactor.remove.remove_unused_constants
  src.reko.cli.main.apply → src.reko.refactor.engine.apply_plan
  src.reko.cli.main.plan_cmd → src.reko.config.load_config
  src.reko.cli.main.plan_cmd → src.reko.scanner.detector.scan_project
  src.reko.scanner.detector._HardcodeVisitor.visit_Constant → src.reko.scanner.detector._is_magic_number
  src.reko.scanner.detector._HardcodeVisitor.visit_Dict → src.reko.scanner.detector._literal_size
  src.reko.scanner.detector._HardcodeVisitor.visit_Dict → src.reko.scanner.detector._get_source_segment
  src.reko.scanner.detector._HardcodeVisitor.visit_List → src.reko.scanner.detector._literal_size
  src.reko.scanner.detector.scan_project → src.reko.config.load_config
  src.reko.scanner.detector.scan_project → src.reko.scanner.detector._should_exclude
  src.reko.scanner.detector.scan_project → src.reko.scanner.detector.scan_file
  src.reko.reporters.json_reporter.write_report → src.reko.reporters.json_reporter.report_to_dict
  src.reko.refactor.extract.extract_constants → src.reko.refactor.extract._group_target_path
  src.reko.refactor.extract.extract_constants → src.reko.refactor._utils.read_module
  src.reko.refactor.extract.extract_constants → src.reko.refactor._ast_extract.build_extraction_plan
  src.reko.refactor.extract.extract_constants → src.reko.refactor._ast_extract.transform_source
  src.reko.refactor.extract.extract_constants → src.reko.refactor._utils.ensure_trailing_newline
  src.reko.refactor.extract.extract_constants → src.reko.refactor._utils.write_module
  src.reko.refactor._utils.apply_replacements → src.reko.refactor._utils._position_to_index
  src.reko.refactor._utils.write_module → src.reko.refactor._utils.ensure_trailing_newline
  src.reko.refactor.move.move_constants → src.reko.refactor._utils.read_module
  src.reko.refactor.move.move_constants → src.reko.refactor.move._assignment_lines
  src.reko.refactor.move.move_constants → src.reko.refactor._utils.ensure_trailing_newline
  src.reko.refactor.move.move_constants → src.reko.refactor.move._remove_assignments
  src.reko.refactor.move.move_constants → src.reko.refactor._utils.write_module
  src.reko.refactor.move.move_constants → src.reko.config.load_config
  src.reko.refactor.remove.remove_unused_constants → src.reko.refactor._utils.read_module
  src.reko.refactor.remove.remove_unused_constants → src.reko.refactor._utils.module_level_names
  src.reko.refactor.remove.remove_unused_constants → src.reko.refactor._utils.collect_name_usages
  src.reko.refactor.remove.remove_unused_constants → src.reko.refactor._utils.write_module
  src.reko.refactor.split._SplitFinder._insert_at → src.reko.refactor.split._insert_index
  src.reko.refactor.split._SplitFinder.finalize → src.reko.refactor.split._contains_node
  src.reko.refactor.split._split_dict_node → src.reko.refactor._utils.unique_name
  src.reko.refactor.split._split_dict_node → src.reko.refactor._utils.to_upper_snake
  src.reko.refactor.split._split_dict_node → src.reko.refactor.split._make_assign
  src.reko.refactor.split._split_list_node → src.reko.refactor._utils.unique_name
  src.reko.refactor.split._split_list_node → src.reko.refactor._utils.to_upper_snake
  src.reko.refactor.split._split_list_node → src.reko.refactor.split._make_assign
  src.reko.refactor.split.split_structures → src.reko.refactor._utils.read_module
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (1)

**`Auto-generated API Smoke Tests`**
- assert `_status < 500`
- assert `_status >= 200`
- detectors: ConfigEndpointDetector

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

Refaktoryzacja hardkodowanych wartości, struktur i kodu w projektach Python
