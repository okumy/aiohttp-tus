.PHONY: \
	clean \
	coveralls \
	distclean \
	docs \
	install \
	lint \
	lint-only \
	list-outdated \
	open-docs \
	test \
	test-app \
	test-only

# Project constants
PROJECT = aiohttp_tus
DOCS_DIR = ./docs

# Project vars
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
PYTHON ?= $(POETRY) run python
SPHINXBUILD ?= $(POETRY) run sphinx-build
TOX ?= tox

# Example constants
AIOHTTP_PORT ?= 8300

all: install

clean:
	find . \( -name __pycache__ -o -type d -empty \) -exec rm -rf {} + 2> /dev/null

distclean: clean
	rm -rf build/ dist/ *.egg*/ .tox/ .venv/ .install

docs: .install
	$(PYTHON) -m pip install -r docs/requirements.txt
	$(MAKE) -C docs/ SPHINXBUILD="$(SPHINXBUILD)" html

example: .install
ifeq ($(EXAMPLE),)
	# EXAMPLE env var is required, e.g. `make EXAMPLE=uploads example`
	@exit 1
else
	$(PYTHON) -m aiohttp.web --port $(AIOHTTP_PORT) examples.$(EXAMPLE):create_app
endif

install: .install
.install: pyproject.toml poetry.lock
	$(POETRY) config virtualenvs.in-project true
	$(POETRY) install
	touch $@

lint: install lint-only

lint-only:
	SKIP=$(SKIP) $(PRE_COMMIT) run --all $(HOOK)

list-outdated: install
	$(POETRY) show -o

open-docs: docs
	open $(DOCS_DIR)/_build/html/index.html

test: install clean lint test-only

test-only:
	rm -rf tests/test-uploads/
	TOXENV=$(TOXENV) $(TOX) $(TOX_ARGS) -- $(TEST_ARGS)
