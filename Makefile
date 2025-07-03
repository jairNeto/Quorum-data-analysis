IMAGE_NAME = quorum-legislative-analysis
DATA_DIR = $(PWD)

.PHONY: build
build:
	docker build -t $(IMAGE_NAME) .

.PHONY: run
run: build
	docker run --rm -v $(DATA_DIR):/app $(IMAGE_NAME) python src/main.py

.PHONY: test
test: build
	docker run --rm -v $(DATA_DIR):/app $(IMAGE_NAME) python -m pytest src/test_data_processor.py -v
