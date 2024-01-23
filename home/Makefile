.PHONY: install migrate runserver test lint clean

install:
	pip install -r requirements.txt

run:
	python3 manage.py runserver

docker:
	docker build -t dockerbackend

up:
	docker-compose up

down:
	docker-compose down
