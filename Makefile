IMAGE_NAME = proyecto-rest
CONTAINER_NAME = api-avernia

build:
	docker build -t $(IMAGE_NAME) .

clean:
	docker rm -f $(CONTAINER_NAME) || true

run: clean
	docker run -d -p 8000:8000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

up: build run

curl:
	@curl -X 'POST' \
	  'http://localhost:8000/api/puntaje' \
	  -H 'Content-Type: application/json' \
	  -d '{ "codigo_estudiante": "mPHlIy6JPtw3TbJyu", "codigo_carrera": 10001 }'

test:
	docker run --rm $(IMAGE_NAME) pytest tests/
