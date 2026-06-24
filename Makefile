.PHONY: install test audit reports clean

install:
	python -m pip install --upgrade pip
	python -m pip install -e .[dev]

test:
	python -m unittest discover -s tests

audit:
	python -m devops_toolkit.cli . --config devops-audit.config.json --format text --fail-on-high

reports:
	mkdir -p reports
	python -m devops_toolkit.cli . --config devops-audit.config.json --format markdown --output reports/audit-report.md --fail-on-high
	python -m devops_toolkit.cli . --config devops-audit.config.json --format json --output reports/audit-report.json
	python -m devops_toolkit.cli . --config devops-audit.config.json --format html --output reports/audit-report.html
	python -m devops_toolkit.cli . --config devops-audit.config.json --format sarif --output reports/audit-report.sarif

clean:
	python -c "import shutil; from pathlib import Path; [shutil.rmtree(path, ignore_errors=True) for path in Path('.').rglob('__pycache__')]; shutil.rmtree('reports', ignore_errors=True)"
