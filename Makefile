.PHONY: docker
docker:
	docker build . -t transcriptor

.PHONY: docker-run
docker-run: docker
	docker run -p 5001:5001 -v ~/.cache:/home/transcriptor/.cache/ transcriptor

.PHONY: fmt
fmt:
	black src/*.py
	isort src/*.py

.PHONY: lint
lint:
	flake8 --ignore=E501 src/*.py

.PHONY: run
run:
	FLASK_DEBUG=true python3 src/app.py
