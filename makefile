OSFLAG :=
ifeq ($(OS), Linux)
	python = python3
else
	python = python
endif

install:
	@echo $(OSFLAG)
	$(python) -m pip install -r requirements.txt
lint:
	flake8
run:
	$(python) app.py
