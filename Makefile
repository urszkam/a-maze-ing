SCRIPT	= a_maze_ing.py
CONFIG	= config.txt
UV	= uv run

install:
	pip install uv
	uv sync
run:
	${UV} python3 ${SCRIPT} ${CONFIG}
debug:
	${UV} python3 -m pdb ${SCRIPT} ${CONFIG}
test:

clean:
	find . -name '*cache*' -type d -exec rm -rf {} +
lint:
	${UV} flake8 .
	${UV} mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
lint-strict:
	${UV} flake8 .
	${UV} mypy . --strict

.PHONY: install run debug test clean lint lint-strict
