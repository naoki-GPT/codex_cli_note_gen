VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: venv deps auto

venv:
	python3 -m venv $(VENV)

deps: venv
	$(PIP) install 'openai>=1.0.0' pyyaml Pillow

# Example:
# make auto TITLE="タイトル" SUMMARY="要約" AUDIENCE="想定読者" KEYWORDS="kw1,kw2"
auto:
	. $(VENV)/bin/activate; \
	$(PY) scripts/auto_pipeline.py \
	  --title "$(TITLE)" \
	  --summary "$(SUMMARY)" \
	  --audience "$(AUDIENCE)" \
	  --keywords "$(KEYWORDS)" \
	  --brand-name "$(BRAND)" \
	  --brand-color "$(COLOR)" \
	  --theme "$(THEME)"

