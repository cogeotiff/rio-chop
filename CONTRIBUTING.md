# Contributing

Issues and pull requests are more than welcome.

**dev install**

```bash
$ git clone https://github.com/cogeotiff/rio-chop.git
$ cd rio-chop
$ pip install -e .[dev]
```

## pre-commit

This repo is set to use `pre-commit` to run *isort*, *flake8*, *pydocstring*, *black* ("uncompromising Python code formatter") and mypy when committing new code.

```bash
$ pre-commit install
```
