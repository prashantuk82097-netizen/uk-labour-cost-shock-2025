.PHONY: install test analysis clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

analysis:
	python -m labour_cost_shock.pipeline

clean:
	rm -f results/tables/*.csv results/tables/*.json
	rm -f results/figures/*.svg
	rm -rf data/processed
