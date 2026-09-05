.PHONY: setup run test check docker-test docker-smoke ollama-up ollama-pull package

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install -e '.[dev]'

run:
	.venv/bin/python main.py

test:
	.venv/bin/python -m pytest -q

check:
	.venv/bin/python -m compileall -q main.py legacy_main.py src data learning llm tests
	.venv/bin/python -m pytest -q

docker-test:
	docker compose run --rm test

docker-smoke:
	docker compose run --rm gui-smoke

ollama-up:
	docker compose --profile ai up -d ollama

ollama-pull:
	docker compose --profile ai exec ollama ollama pull qwen3:4b

package:
	.venv/bin/pyinstaller --clean --noconfirm packaging/english-learning.spec
