install: 	
	pip install -r requirements.txt  

test_data_scraper: 	
	python -m unittest -v test.data_test.Testing

test_data_test:
	python -m unittest -v test.data_test

format: 	
	black . 

lint_data_scraper: 	
	pylint --extension-pkg-whitelist='pydantic' --disable=R,C src/data_scraper.py

lint_data_test:
	pylint --extension-pkg-whitelist='pydantic' --disable=R,C test/data_test.py

all: install lint_data_scraper lint_data_test test_data_scraper test_data_test

run: all
