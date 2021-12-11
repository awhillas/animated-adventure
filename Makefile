.PHONY: tests update requirements install

requirements:
	# Compile locked requirements files
	pip-compile --output-file=requirements.txt requirements/base.in
	pip-compile --output-file=requirements.dev.txt requirements/dev.in

install:
	pip install pip-tools wheel setuptools
	pip install -r requirements.dev.txt

update: requirements install

image:
	docker build -t first .

tests:
	python -m pytest --cov=first tests/
