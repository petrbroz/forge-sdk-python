init:
	pip3 install -r requirements.txt

init-dev: init
	pip3 install -r requirements-dev.txt

test:
	python3 -m unittest

build:
	python3 -m build

docs:
	python3 -m pdoc --html -o docs src/autodesk_forge_sdk

prepublish-check: build
	python3 -m twine check dist/*

publish-test: test build
	python3 -m twine upload --repository testpypi dist/*