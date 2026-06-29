# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-06-29

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.1.3] - 2026-06-29

### Docs
- Update CHANGELOG.md
- Update README.md

### Test
- Update tests/test_cli.py
- Update tests/test_detector.py
- Update tests/test_examples_e2e.py
- Update tests/test_refactor.py

### Other
- Update prefact.yaml

## [0.1.11] - 2026-06-17

### Fixed
- Naprawiono fałszywe wpisy CHANGELOG z wersji 0.1.10 (tickety planfile nie były wtedy wykonane)
- Usunięto `from __future__ import annotations` powodujące fałszywe alarmy prefact
- Zamieniono konkatenacje stringów na f-stringi w modułach refactor/
- Dodano `_MAX_TABLE_ROWS` w CLI zamiast magic number 200
- Dodano adnotacje `-> None` w testach
- Lepszy komunikat błędu gdy plik nie istnieje (`reko remove`)

### Changed
- Zaktualizowano `prefact.yaml`: wykluczenie `examples/`, `tests/fixtures/`, reguł ai-boilerplate

## [0.1.10] - 2026-06-17

### Docs
- Wygenerowano planfile.yaml i artefakty analizy (prefact/code2llm) — refaktoryzacja kodu wykonana dopiero w 0.1.11

## [0.1.2] - 2026-06-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-api-smoke.testql.toon.yaml
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml
- Update tests/test_cli.py

### Other
- Update app.doql.less
- Update planfile.yaml
- Update prefact.yaml
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 11 more files

## [0.1.1] - 2026-06-17

### Docs
- Update README.md

### Other
- Update project.sh
- Update tree.sh
- Update uv.lock

