install: 	
	pip install -r requirements.txt  

test: 	
	python -m unittest -v test/data_test.Testing

format: 	
	black . 

lint: 	
	pylint --extension-pkg-whitelist='pydantic' --disable=R,C src/data_scraper.py  

all: install lint test

run: all
