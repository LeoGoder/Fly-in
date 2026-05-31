install:
	uv sync

run:
	uv run src/main.py

debug:
	uv run python3 -m pdb src/main.py

clean:
	rm -fr __pycache__
	rm -fr src/__pycache__
	rm -fr src/gui/__pycache__
	rm -fr .venv
	rm -fr .mypy_cache

lint:
	flake8 --exclude=.venv,.mypy_cache,llm_sdk .
# 	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

