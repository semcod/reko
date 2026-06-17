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
project_file('src/reko/cli/main.py', 194, 'python').
project_file('src/reko/config.py', 105, 'python').
project_file('src/reko/models.py', 83, 'python').
project_file('src/reko/refactor/__init__.py', 2, 'python').
project_file('src/reko/refactor/_ast_extract.py', 166, 'python').
project_file('src/reko/refactor/_utils.py', 118, 'python').
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
project_file('tests/test_cli.py', 28, 'python').
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
python_function('src/reko/cli/main.py', 'extract', 3, 2, 8).
python_function('src/reko/cli/main.py', 'split', 2, 2, 7).
python_function('src/reko/cli/main.py', 'move_cmd', 4, 3, 9).
python_function('src/reko/cli/main.py', 'remove', 2, 1, 7).
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
python_function('tests/test_cli.py', 'test_cli_remove_missing_file', 0, 6, 5).
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
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-api-smoke.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').

