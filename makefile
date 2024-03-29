OSFLAG :=
ifeq ($(OS), Windows_NT)
	python = python
else
	python = python3
endif

clean:
	rm -rf find __pycache__
install:
	$(python) -m pip install -r requirements.txt
lint:
	flake8
run:
	$(python) app.py