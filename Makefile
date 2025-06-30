ifeq (,$(wildcard .env))
$(error .env file is missing at . Please create one based on .env.example)
endif

include .env	
	
build-kubrick:
	docker compose build

start-kubrick:
	docker compose up --build -d

stop-kubrick:
	docker compose stop
