install:
	uv sync

run:
	uv run src/main.py

debug:

clean:
	rm -fr __pycache__
	rm -fr src/__pycache__
	rm -fr src/gui/__pycache__
	rm -fr .venv
	rm -fr .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict



