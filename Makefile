.PHONY: help clean coverage dev integrate lint package package-install pypi-install test upload uninstall

help:
	@echo "This project assumes that an active Python virtualenv is present."


clean:
	rm -rf dist/*

coverage:
	coverage run --source pytest_jobserver -m py.test
	codecov

dev:
	pip install "pipenv==2018.11.26"
	pipenv install --dev --deploy
	pip install -e .

integrate:
	cd integrate && pytest -p no:jobserver -p no:xdist test_integrate.py

lint:
	black .

package:
	python setup.py sdist
	python setup.py bdist_wheel

package-install:
	pip install dist/*.whl

pypi-install:
	pip install -U --no-cache-dir "pytest-jobserver==${PYTEST_JOBSERVER_VERSION}"

test:
	black --check --diff .
	flake8
	mypy pytest_jobserver
	pytest pytest_jobserver -p no:jobserver

upload:
	twine upload dist/*

uninstall:
	pip uninstall -y pytest-jobserver
