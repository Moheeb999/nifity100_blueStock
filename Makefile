load:
	python src/etl/loader.py

test:
	pytest tests/

clean:
	rm -f db/*.db
	rm -f output/*.csv
