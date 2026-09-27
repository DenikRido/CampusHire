.PHONY: install migrate seed run test lint docker-up docker-down collect worker

install:
	python -m pip install -r requirements-dev.txt

migrate:
	python manage.py migrate

seed:
	python manage.py seed_data

run:
	python manage.py runserver 0.0.0.0:8080

collect:
	python manage.py collectstatic --noinput

test:
	pytest -q

worker:
	celery -A config worker -l info

docker-up:
	docker compose up --build

docker-down:
	docker compose down
