checkfiles = fast_tmp/
black_opts = -l 100 -t py38
py_warn = PYTHONDEVMODE=1

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

check:
	black --check $(black_opts) $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
	flake8 $(checkfiles)
	#bandit -x test -r $(checkfiles)
	mypy $(checkfiles)


test:
	pytest tests/ --cov-report=

cov: deps
	coverage run -m pytest tests/
	coverage report --show-missing -m
	coverage xml
	coverage html

publish: check
	poetry publish

docs:
	mkdocs build