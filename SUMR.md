# reko

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `reko`
- **version**: `0.1.1`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(3), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 27f 2312L | python:23,shell:2,yaml:1,toml:1 | 2026-06-17
# generated in 0.00s
# CC̅=3.7 | critical:2/88 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    extract_constants CC=15 (limit:15)
  🟡 CC    remove_unused_constants CC=16 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[38]:
  [1] Src [main]: main → prepare_workdir
      PURITY: 100% pure
  [2] Src [build_url]: build_url
      PURITY: 100% pure
  [3] Src [fetch_users]: fetch_users
      PURITY: 100% pure
  [4] Src [fetch_orders]: fetch_orders
      PURITY: 100% pure
  [5] Src [scan]: scan → load_config → _load_toml
      PURITY: 100% pure
  [6] Src [extract]: extract → load_config → _load_toml
      PURITY: 100% pure
  [7] Src [split]: split → split_structures → read_module
      PURITY: 100% pure
  [8] Src [move_cmd]: move_cmd → move_constants → read_module
      PURITY: 100% pure
  [9] Src [remove]: remove → remove_unused_constants → read_module
      PURITY: 100% pure
  [10] Src [apply]: apply → apply_plan → extract_constants → _group_target_path
      PURITY: 100% pure
  [11] Src [plan_cmd]: plan_cmd → load_config → _load_toml
      PURITY: 100% pure
  [12] Src [__init__]: __init__
      PURITY: 100% pure
  [13] Src [visit_JoinedStr]: visit_JoinedStr
      PURITY: 100% pure
  [14] Src [visit_Module]: visit_Module
      PURITY: 100% pure
  [15] Src [visit_FunctionDef]: visit_FunctionDef
      PURITY: 100% pure
  [16] Src [visit_AsyncFunctionDef]: visit_AsyncFunctionDef
      PURITY: 100% pure
  [17] Src [visit_ClassDef]: visit_ClassDef
      PURITY: 100% pure
  [18] Src [visit_Constant]: visit_Constant → _is_magic_number
      PURITY: 100% pure
  [19] Src [visit_Dict]: visit_Dict → _literal_size
      PURITY: 100% pure
  [20] Src [visit_List]: visit_List → _literal_size
      PURITY: 100% pure
  [21] Src [_line_offsets]: _line_offsets
      PURITY: 100% pure
  [22] Src [apply_replacements]: apply_replacements → _position_to_index
      PURITY: 100% pure
  [23] Src [_literal_size]: _literal_size
      PURITY: 100% pure
  [24] Src [visit]: visit
      PURITY: 100% pure
  [25] Src [visit_Module]: visit_Module
      PURITY: 100% pure
  [26] Src [visit_FunctionDef]: visit_FunctionDef
      PURITY: 100% pure
  [27] Src [visit_AsyncFunctionDef]: visit_AsyncFunctionDef
      PURITY: 100% pure
  [28] Src [visit_Dict]: visit_Dict
      PURITY: 100% pure
  [29] Src [visit_List]: visit_List
      PURITY: 100% pure
  [30] Src [_insert_at]: _insert_at → _insert_index
      PURITY: 100% pure
  [31] Src [finalize]: finalize → _contains_node
      PURITY: 100% pure
  [32] Src [__init__]: __init__
      PURITY: 100% pure
  [33] Src [visit_JoinedStr]: visit_JoinedStr
      PURITY: 100% pure
  [34] Src [visit_FunctionDef]: visit_FunctionDef
      PURITY: 100% pure
  [35] Src [visit_AsyncFunctionDef]: visit_AsyncFunctionDef
      PURITY: 100% pure
  [36] Src [visit_ClassDef]: visit_ClassDef
      PURITY: 100% pure
  [37] Src [visit_Constant]: visit_Constant → _is_magic_number
      PURITY: 100% pure
  [38] Src [visit_Constant]: visit_Constant
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=3.9    ←in:0  →out:0
  │ detector                   260L  1C   17m  CC=10     ←2
  │ split                      224L  2C   19m  CC=14     ←2
  │ main                       172L  0C    8m  CC=5      ←0
  │ _ast_extract               165L  5C   13m  CC=14     ←1
  │ config                     104L  5C    3m  CC=5      ←5
  │ move                       103L  0C    4m  CC=8      ←2
  │ _utils                     101L  1C   10m  CC=7      ←5
  │ models                      82L  7C    0m  CC=0.0    ←0
  │ !! extract                     75L  0C    2m  CC=15     ←2
  │ !! remove                      70L  0C    1m  CC=16     ←2
  │ engine                      45L  0C    1m  CC=8      ←1
  │ json_reporter               41L  0C    2m  CC=2      ←1
  │ __init__                    39L  0C    0m  CC=0.0    ←0
  │ __main__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.5    ←in:0  →out:0
  │ run_all                     67L  0C    3m  CC=4      ←0
  │ before                      34L  0C    3m  CC=4      ←0
  │ before                      25L  0C    1m  CC=1      ←0
  │ before                      12L  0C    1m  CC=1      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             107L  0C    0m  CC=0.0    ←0
  │ project.sh                  63L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 4 groups | 27f 1693L | 2026-06-17

SUMMARY:
  files_scanned: 27
  total_lines:   1693
  dup_groups:    4
  dup_fragments: 8
  saved_lines:   19
  scan_ms:       3515

HOTSPOTS[3] (files with most duplication):
  src/reko/cli/main.py  dup=14L  groups=1  frags=2  (0.8%)
  src/reko/refactor/_ast_extract.py  dup=12L  groups=3  frags=3  (0.7%)
  src/reko/scanner/detector.py  dup=12L  groups=3  frags=3  (0.7%)

DUPLICATES[4] (ranked by impact):
  [f896f4f707da17b4]   STRU  remove  L=7 N=2 saved=7 sim=1.00
      src/reko/cli/main.py:114-120  (remove)
      src/reko/cli/main.py:124-130  (apply)
  [b96136ca3d8e558b]   EXAC  visit_FunctionDef  L=4 N=2 saved=4 sim=1.00
      src/reko/refactor/_ast_extract.py:45-48  (visit_FunctionDef)
      src/reko/scanner/detector.py:115-118  (visit_FunctionDef)
  [2d39164b839bdf47]   EXAC  visit_AsyncFunctionDef  L=4 N=2 saved=4 sim=1.00
      src/reko/refactor/_ast_extract.py:50-53  (visit_AsyncFunctionDef)
      src/reko/scanner/detector.py:120-123  (visit_AsyncFunctionDef)
  [c9ba3f0f7fdde3c0]   EXAC  visit_ClassDef  L=4 N=2 saved=4 sim=1.00
      src/reko/refactor/_ast_extract.py:55-58  (visit_ClassDef)
      src/reko/scanner/detector.py:125-128  (visit_ClassDef)

REFACTOR[4] (ranked by priority):
  [1] ○ extract_function   → src/reko/cli/utils/remove.py
      WHY: 2 occurrences of 7-line block across 1 files — saves 7 lines
      FILES: src/reko/cli/main.py
  [2] ○ extract_function   → src/reko/utils/visit_FunctionDef.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: src/reko/refactor/_ast_extract.py, src/reko/scanner/detector.py
  [3] ○ extract_function   → src/reko/utils/visit_AsyncFunctionDef.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: src/reko/refactor/_ast_extract.py, src/reko/scanner/detector.py
  [4] ○ extract_function   → src/reko/utils/visit_ClassDef.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: src/reko/refactor/_ast_extract.py, src/reko/scanner/detector.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=7L  → src/reko/cli/utils/remove.py
      FILES: main.py

EFFORT_ESTIMATE (total ≈ 0.6h):
  easy   remove                              saved=7L  ~14min
  easy   visit_FunctionDef                   saved=4L  ~8min
  easy   visit_AsyncFunctionDef              saved=4L  ~8min
  easy   visit_ClassDef                      saved=4L  ~8min

METRICS-TARGET:
  dup_groups:  4 → 0
  saved_lines: 19 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 80 func | 11f | 2026-06-17
# generated in 0.00s

NEXT[3] (ranked by impact):
  [1] !  SPLIT-FUNC      extract_constants  CC=15  fan=16
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 240

  [2] !  SPLIT-FUNC      remove_unused_constants  CC=16  fan=15
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 240

  [3] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.9 → ≤2.7
  max-CC:      16 → ≤8
  god-modules: 1 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  (first run — no previous data)
```

## Intent

Refaktoryzacja hardkodowanych wartości, struktur i kodu w projektach Python
