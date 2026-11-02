# Lab 6 — Code and Branch Coverage

**Student:** Thejaswi S  
**SRN:** PES2UG24CS562

## About

A Python module (`car_rental_rate.py`) that calculates car rental revenue for a fleet, applies vehicle-type pricing, trip-segment surcharges, young-driver fees, and fleet telematics risk analysis.

## Files

| File | Description |
|------|-------------|
| `car_rental_rate.py` | Module under test |
| `CodeCoverageTest_PES2UG24CS562_application.py` | Test cases targeting ≥ 90% **line/statement** coverage |
| `BranchCoverageTest_PES2UG24CS562_application.py` | Test cases targeting ≥ 90% **branch** coverage |

## Running Tests

### Line Coverage
```bash
pytest CodeCoverageTest_PES2UG24CS562_application.py -v --cov=car_rental_rate --cov-report=term-missing
```

### Branch Coverage
```bash
pytest BranchCoverageTest_PES2UG24CS562_application.py -v --cov=car_rental_rate --cov-branch --cov-report=term-missing
```

### Both together
```bash
pytest CodeCoverageTest_PES2UG24CS562_application.py BranchCoverageTest_PES2UG24CS562_application.py -v --cov=car_rental_rate --cov-branch --cov-report=term-missing
```

> Install dependencies if needed: `pip install pytest pytest-cov`

## Commits Required

1. **Commit 1** — Add `CodeCoverageTest_PES2UG24CS562_application.py` (code/line coverage test cases)
2. **Commit 2** — Add `BranchCoverageTest_PES2UG24CS562_application.py` (branch coverage test cases)

Keep all Lab 6 work in this `Lab 6` folder. Lab 7 will be added to this repo later.
