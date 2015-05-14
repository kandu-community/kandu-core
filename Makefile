serve:
	python manage.py runserver 0.0.0.0:8000

sudo-serve:
	sudo $(HOME)/.virtualenvs/kandu/bin/python manage.py runserver 0.0.0.0:80

clean-python:
	find . -name '*.pyc' -delete

.PHONY: serve
