# reko


## AI Cost Tracking

![AI Cost](https://img.shields.io/badge/AI%20Cost-$2.46-green) ![AI Model](https://img.shields.io/badge/AI%20Model-openrouter%2Fqwen%2Fqwen3-coder-next-lightgrey)

This project uses AI-generated code. Total cost: **$2.4632** with **3** AI commits.

Generated on 2026-06-29 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/models/openrouter/qwen/qwen3-coder-next)

---

Narzędzie do wykrywania i refaktoryzacji hardkodowanych wartości, struktur danych i kodu w projektach Python.

## Co robi

- **scan** — wykrywa magic numbers, długie stringi, osadzone słowniki/listy, powtarzające się literały
- **extract** — wyciąga hardkod do modułu stałych (`constants.py` lub wskazany plik)
- **split** — rozbija duże struktury (dict/list) na mniejsze nazwane fragmenty
- **move** — przenosi stałe między modułami i aktualizuje importy
- **remove** — usuwa nieużywane stałe modułowe
- **apply** — stosuje plan refaktoryzacji (YAML/JSON)

## Instalacja

```bash
cd ~/github/semcod/reko
pip install -e ".[apply,dev]"
```

## Użycie

```bash
# skan projektu
reko scan .

# skan z raportem JSON
reko scan src/ --format json -o report.json

# wyciągnij hardkod do constants.py (dry-run)
reko extract src/ --target src/myapp/constants.py --dry-run

# rozbij dużą strukturę w pliku
reko split src/config.py --min-keys 5

# przenieś stałe
reko move src/old.py src/new_constants.py --names TIMEOUT,API_URL

# usuń nieużywane stałe
reko remove src/constants.py --dry-run

# zastosuj plan
reko apply plan.yaml
```

## Konfiguracja

Plik `reko.yaml` w katalogu projektu:

```yaml
scan:
  extensions: [".py"]
  exclude:
    - "**/tests/**"
    - "**/__pycache__/**"
  min_string_length: 8
  min_dict_keys: 4
  allowed_numbers: [0, 1, -1, 2, 10, 100, 1000]

extract:
  target: "constants.py"
  naming: "upper_snake"
  group_by: "file"  # file | kind | none
```

## API

```python
from pathlib import Path
from reko import scan_project, extract_constants, apply_plan

findings = scan_project(Path("src/"))
result = extract_constants(Path("src/app.py"), target=Path("src/constants.py"))
```

## Licencja

Apache-2.0
