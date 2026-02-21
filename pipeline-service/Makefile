.PHONY: upd_env install_deps setup_fasttext
upd_env:
	@set -a; [ -f .env ] && . ./.env || . ../.env; set +a

install_deps:
	python -m pip install -e '.[dev]'

setup_fasttext:
	mkdir -p models
	curl -L -o models/lid.176.ftz https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
