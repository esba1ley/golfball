.DEFAULT_GOAL := help

.APP = golfball
.TAG = $(shell git branch | sed -n -e 's/^\* \(.*\)/\1/p')


# User can specify a parallel zip tool (like pigz) for the tarball target.
ifeq ($(ZIP_CMD),)
    ZIP_CMD = gzip
endif

# ---------------------------------------------------------------------------- #
#                                SCRIPTS
# ---------------------------------------------------------------------------- #

# ------------------------ Browser Script -------------------------------------
define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

# ------------------------ Help Script ----------------------------------------
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
  match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
  if match:
	  target, help = match.groups()
	  print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


# ---------------------------------------------------------------------------- #
#                                TARGETS
# ---------------------------------------------------------------------------- #
.PHONY: help
help:  ## Display list of intended targets for user (DEFAULT)
	@echo "-------------------- Makefile Target List --------------------------"
	@echo " Package: $(.APP)"
	@echo " Git branch: $(.TAG)"
	@echo "--------------------------------------------------------------------"
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
	@echo "--------------------------------------------------------------------"

.PHONY: reports
reports:  reports/ruff/ruff_report.txt reports/coverage reports/pytest reports/docs ## check style, coverage, and run tests both locally and in app image
	$(BROWSER) reports/index.html

.PHONY: tests
.coverage: tests
reports/pytest: tests
tests:  ## run tests quickly with the default Python
	@echo -------------------- Running test suite -------------------------------
	pytest -v --cov=golfball --html=reports/pytest/index.html tests/

reports/coverage: .coverage
	@echo ----------------- Computing test coverage -----------------------------
	coverage report -m
	coverage html -d reports/coverage/

.PHONY: ruff
ruff: reports/ruff/ruff_report.txt ## check gball sim code style with pylint
reports/ruff/ruff_report.txt: 
	@echo ------------------- Checking code style -------------------------------
	mkdir -p reports/ruff
	ruff check golfball | tee reports/ruff/ruff_report.txt


golfball.rst: golfball/*.py
modules.rst: golfball/*.py
apidoc: ## generate Sphinx API documentation
	@echo ----------------- Generating Sphinx API documentation -----------------
	sphinx-apidoc -o docs/ golfball

.PHONY: docs
docs:  golfball.rst modules.rst ## generate Sphinx HTML documentation, including API docs
	@echo -------------- Buliding Sphinx HTML documentation ---------------------
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

.PHONY: publish-docs
publish-docs: docs  ## Publish Sphinx HTML docs to GitHub Pages
	@echo ------------- Publishing docs to GitHub Pages -------------------------
	ghp-import -n -p -f docs/_build/html -b gh-pages
	@echo "Docs published at https://esba1ley.github.io/golfball/"

reports/docs: docs
	-cp -r docs/_build/html reports/docs

.PHONY: install
install:  ## install the package to the active Python's site-packages
	@echo !!!------------ Installing into active environment -----------------!!!
	pip install .

.PHONY: install-editable
install-editable:  ## install the package for active development
	@echo !!!------- Installing into active environment for development ------!!!
	pip install -e .

.PHONY: uninstall
uninstall:  ## uninstall the packge from the current environment
	@echo !!! Uninstalling golfball package from active environment !!!
	pip uninstall golfball


# Create a tarball of the test reports
$(.APP)-$(.TAG).tar: reports/coverage reports/pytest reports/docs reports/ruff/ruff_report.txt
	@echo ------------- Archiving test reports to $(.APP)-$(.TAG).tar  ----------
	tar -cvf $(.APP)-$(.TAG).tar reports

reports-archive: ## Create g-zipped tarball of test rports
$(.APP)-$(.TAG).tar.gz:  $(.APP)-$(.TAG).tar  
	@echo --------- Compressing test reports to $(.APP)-$(.TAG).tar.gz  ---------
	${ZIP_CMD} $(.APP)-$(.TAG).tar

clean: clean-build clean-pyc clean-tests clean-archives  ## remove all artifacts

clean-build: ## remove build artifacts
	@echo -------------------- Cleaning build artifacts -------------------------
	-rm -fr build/
	-rm -fr dist/
	-rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python bytecode and object artifacts
	@echo ------------------- Clenaing python artifacts -------------------------
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-tests:  ## remove test reports, caches, and coverage artifacts
	@echo ------------------- Cleaning Test Artifacts ---------------------------
	-rm -f .coverage
	-rm -fr reports/container
	-rm -fr reports/coverage
	-rm -fr reports/ruff
	-rm -fr reports/pytest
	-rm -fr reports/docs
	-rm -fr .pytest_cache

clean-docs: ## remove documentation build
	@echo ----------------- Removing documentation build ------------------------
	-rm -rf docs/_build
	-rm -f docs/golfball.rst docs/modules.rst
	-rm -rf reports/docs

clean-archives:  ## remove tar.gz files
	-rm -rf *.tar.gz