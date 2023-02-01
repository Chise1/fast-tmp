checkfiles = fast_tmp/ tests/ conftest.py
black_opts = -l 100 -t py38
py_warn = PYTHONDEVMODE=1
test_settings = SETTINGS_MODULE=tests.settings
pytest_opts = -n auto --cov=fast_tmp --tb=native -q

help:
	@echo "fastapi-cli development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up			Updates dev/test dependencies"
	@echo  "    deps		Ensure dev/test dependencies are installed"
	@echo  "    check		Checks that build is sane"
	@echo  "    test		Runs all tests"
	@echo  "    style		Auto-formats the code"

up:
	@poetry update

deps:
	@poetry install --no-root

style: deps
	isort -src $(checkfiles)
	black $(black_opts) $(checkfiles)

check: deps
	black --check $(black_opts) $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
	flake8 $(checkfiles)
	bandit -x test -r $(checkfiles) -c pyproject.toml
	mypy fast_tmp/


test: deps
	$(py_warn) FASTAPI_SETTINGS_MODULE=tests.settings TORTOISE_TEST_DB=sqlite://:memory: pytest  $(pytest_opts)

test_html:
	$(py_warn) FASTAPI_SETTINGS_MODULE=tests.settings TORTOISE_TEST_DB=sqlite://:memory: pytest --cov-report html $(pytest_opts)


cov: deps
	$(py_warn) FASTAPI_SETTINGS_MODULE=tests.settings TORTOISE_TEST_DB=sqlite://:memory: pytest --cov-report xml $(pytest_opts)

build: deps
    @poetry build