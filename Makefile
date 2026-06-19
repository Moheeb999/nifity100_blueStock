load:
	python src/etl/loader.py

ratios:
	python src/analytics/ratios.py

test:
	pytest tests/

report:
	python src/reporting/report.py

dashboard:
	python dashboard/app.py

api:
	python src/api/main.py

clean:
	rm -f db/*.db
	rm -f output/*.csv