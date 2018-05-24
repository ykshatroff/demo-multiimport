PROJECT = multiimport

PYTHON_VERSION = 3.6
REQUIREMENTS = requirements.txt
VIRTUAL_ENV = $(shell realpath venv)
PYTHON = $(VIRTUAL_ENV)/bin/python
PYTEST = $(VIRTUAL_ENV)/bin/pytest
PACKAGE_DIR = lib-demo

venv_init:
	if [ ! -d $(VIRTUAL_ENV) ]; then \
		python$(PYTHON_VERSION) -m venv --prompt="($(PROJECT):$(PYTHON_VERSION)) " $(VIRTUAL_ENV); \
	fi

venv:  venv_init
	$(VIRTUAL_ENV)/bin/pip install -r $(REQUIREMENTS)

test:
	cd $(PACKAGE_DIR) && $(PYTHON) setup.py test

migrate:
	$(PYTHON) manage.py migrate --noinput

loaddata:
	$(PYTHON) manage.py loaddata demo/fixtures/initial.json

add_admin:
	$(PYTHON) manage.py createsuperuser --username=admin --email=admin@localhost

init: venv migrate loaddata add_admin

package: venv
	cd $(PACKAGE_DIR) && \
	$(PYTHON) setup.py test sdist && \
	$(VIRTUAL_ENV)/bin/pip install dist/demo-mapper-1.0.tar.gz

runserver: init
	$(PYTHON) manage.py runserver 8000

rss_aggregator:
	$(PYTHON) manage.py aggregator_worker

rss_generator:
	$(PYTHON) -m demo.rssgenerator.app
