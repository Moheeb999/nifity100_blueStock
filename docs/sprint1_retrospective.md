# Sprint 1 Retrospective — Data Foundation

## Sprint Summary

Sprint 1 focused on building the complete data foundation for the Nifty100 analytics platform. The goal was to ingest 12 Excel datasets, validate them using data quality rules, and load clean structured data into a relational SQLite database.

**Sprint Duration:** Day 01 – Day 07
**Story Points:** 34
**Status:** Completed

---

## What Went Well

* Successfully built a complete ETL pipeline using Python and Pandas.
* Loaded 12 source datasets into SQLite.
* Designed relational schema with primary and foreign keys.
* Implemented 16 Data Quality (DQ) validation rules.
* Resolved critical data issues before production loading.
* Achieved full ETL test success (**35/35 tests passed**).

---

## Challenges Faced

### Duplicate Source Rows (DQ-02)

Several company-year rows appeared multiple times in raw Excel files, causing composite key violations.

### Foreign Key Failures (DQ-03)

Some companies existed in financial tables but were missing in the master company dataset.

### Schema Mismatch

Supplementary datasets had inconsistent column naming:

* `Annual_Report` vs `annual_report`
* `operating_activity` missing in schema
* header mismatch (`header=0` vs `header=1`)

### Validator Complexity

The validator evolved from 6 rules to 16 rules, increasing debugging complexity.

---

## Key Learnings

* Real-world data is messy and requires extensive cleaning.
* Strong schema design reduces downstream issues.
* Primary and foreign key constraints are essential for data integrity.
* Validation pipelines should be modular and reusable.
* Automated tests significantly reduce regression risk.

---

## Metrics

* Companies Loaded: **92**
* Profit & Loss Rows: **1070**
* Balance Sheet Rows: **1058**
* Cash Flow Rows: **1056**
* Unit Tests Passed: **35**
* Foreign Key Violations in Final DB: **0**

---

## Improvements for Sprint 2

* Add structured logging
* Improve code modularity
* Increase test coverage
* Add richer audit reporting
* Reduce manual validation steps

---

## Final Sprint Outcome

Sprint 1 successfully delivered a production-ready data foundation for the Nifty100 project.

### Deliverables

* `nifty100.db`
* `db/schema.sql`
* `src/etl/loader.py`
* `src/etl/validator.py`
* `output/load_audit.csv`
* `output/validation_failures.csv`
* `tests/etl/`
* `notebooks/exploratory_queries.sql`

**Sprint Status:** DONE
**Completion:** 34 / 34 Story Points
