.PHONY: install run clean

install:
	pip install -r requirements.txt

run:
	python gui_main.py

clean:
	rm -rf src/__pycache__ tests/__pycache__ __pycache__
	rm -rf build dist *.spec
	rm -rf *.pyc *.pyo
