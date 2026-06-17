# Przykłady reko

Katalog z realistycznym kodem do refaktoryzacji.

| Katalog | Scenariusz | Komenda |
|---------|------------|---------|
| `01-hardcoded-api/` | URL, timeouty, progi | `reko extract` |
| `02-inline-config/` | duży dict i lista | `reko split` |
| `03-unused-constants/` | martwe stałe | `reko remove` |

## Szybki start

```bash
cd ~/github/semcod/reko
pip install -e .

# skan wszystkich przykładów
reko scan examples/

# pełny workflow na kopii roboczej
python examples/run_all.py
```

Pliki `before.py` pozostają nietknięte — `run_all.py` kopiuje je do `examples/_work/` i stosuje refaktoryzację.
