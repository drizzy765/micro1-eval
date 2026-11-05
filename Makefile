.PHONY: setup generate test baseline assets

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

generate:
	python -m generator.write_assets

assets: generate

test:
	python -m pytest -q

baseline:
	python -m runner.run --backend baseline --runs 1
