SCRIPT	= a_maze_ing.py
CONFIG	= config.txt
UV		= uv run
LIB		= ./mazegen-0.1.0-py3-none-any.whl

install:
	pip install -r requirements.txt
	uv sync --locked
run:
	${UV} python3 ${SCRIPT} ${CONFIG}
debug:
	${UV} python3 -m pdb ${SCRIPT} ${CONFIG}
test:
	${UV} python3 -m pytest -v ./tests
clean:
	find . -name '*cache*' -type d -exec rm -rf {} +
lint:
	${UV} flake8 .
	${UV} mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
lint-strict:
	${UV} flake8 .
	${UV} mypy . --strict
package:
	uv build --wheel ./mazegen -o .
	uv pip install ${LIB}

.PHONY: install run debug test clean lint lint-strict package
