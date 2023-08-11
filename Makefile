version := $(shell cat VERSION)

REGISTRY := registry.fke.fptcloud.com/xplat-fke

all: 
	docker build -f Dockerfile . -t be-hackathon:$(version)
	docker tag be-hackathon:$(version) $(REGISTRY)/be-hackathon:$(version)
	docker push $(REGISTRY)/be-hackathon:$(version)
