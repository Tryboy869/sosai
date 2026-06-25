# Contributing to SOSAI

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Submit a PR

## Adding a new domain to Benchmark Resolver

Edit `sosai/benchmarks/resolver.py` and add your domain to `CATALOG`:

```python
"your_domain": [
    {"name": "BenchmarkName", "url": "https://...", "measures": "what it measures"},
    ...
]
```

## Adding a new provider to IR Engine

Edit `sosai/ir/engine.py` and add to `ENDPOINTS`:

```python
"your_provider": ("https://api.your-provider.com/v1/chat/completions", "Bearer"),
```

## Code style

- Python 3.10+
- Black formatting
- Type hints where possible
- Docstrings for public functions

## Questions

Open an issue or start a Discussion on GitHub.
