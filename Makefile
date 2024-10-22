.PHONY: all push

all:
	docker build -t diphia/artifactos .

push:
	docker push diphia/artifactos

