PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TRACE_PYTHON ?= /usr/bin/python3

.PHONY: all build test validate trace site clean install

all: build

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

validate:
	$(PYTHON) scripts/validate_ontology.py
	$(PYTHON) scripts/generate_glyphs.py
	$(PYTHON) scripts/validate_glyphs.py

trace:
	$(TRACE_PYTHON) scripts/trace_gray_bones.py

build: validate
	$(PYTHON) scripts/generate_registry.py
	$(PYTHON) scripts/build_font.py
	$(PYTHON) scripts/subset_webfonts.py
	$(PYTHON) scripts/validate_fonts.py
	$(PYTHON) scripts/export_png.py
	$(PYTHON) scripts/build_docs.py

test: site
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

site: build
	$(PYTHON) scripts/build_site.py

clean:
	rm -rf dist/png glyphs/png
	rm -f font/sources/*.fea font/sources/*.json
	rm -rf _site
