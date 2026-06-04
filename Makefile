.PHONY: install migrate run test lint format superuser shell

install:
	pip install -r requirements/development.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver

test:
	pytest --cov=apps --cov-report=term-missing

lint:
	flake8 .

format:
	black .
	isort .

superuser:
	python manage.py createsuperuser

shell:
	python manage.py shell_plus

collectstatic:
	python manage.py collectstatic --noinput
