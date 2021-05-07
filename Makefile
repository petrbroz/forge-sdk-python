init:
	pip3 install -r requirements.txt

init-dev: init
	pip3 install -r requirements-dev.txt

test:
	python3 -m unittest

lint:
	python3 -m pylint src/autodesk_forge_sdk

build:
	python3 -m build

docs:
	python3 -m pdoc --html -o docs src/autodesk_forge_sdk

prepublish-check: build
	python3 -m twine check dist/*

publish: build
	python3 -m twine upload dist/*

clean:
	rm -rf build dist docs