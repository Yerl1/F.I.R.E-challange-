.PHONY: upd_env install_deps install_full_deps setup_fasttext fix_torch_stack
upd_env:
	@set -a; [ -f .env ] && . ./.env || . ../.env; set +a

install_deps:
	python -m pip install -e '.[dev]'

install_full_deps:
	python -m pip install -e '.[dev,full]'

setup_fasttext:
	mkdir -p models
	curl -L -o models/lid.176.ftz https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz

fix_torch_stack:
	python -m pip uninstall -y torchvision torchaudio
	python -m pip install --upgrade --force-reinstall torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1
	python -m pip check
