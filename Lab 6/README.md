# Lab 6 — Code and Branch Coverage

## About

A Python module (`car_rental_rate.py`) that calculates car rental revenue for a fleet, applies vehicle-type pricing, trip-segment surcharges, young-driver fees, and fleet telematics risk analysis.

## Files

| File | Description |
|------|-------------|
| `car_rental_rate.py` | Module under test |
| `CodeCoverageTest_PES2UG24CS562_application.py` | Test cases targeting 100% **line/statement** coverage |
| `BranchCoverageTest_PES2UG24CS562_application.py` | Test cases targeting 100% **branch** coverage |
| `code_coverage_screenshot.png` | Terminal output – line coverage run |
| `branch_coverage_screenshot.png` | Terminal output – branch coverage run |
| `Coverage_Screenshots_PES2UG24CS562.docx` | Word document containing both screenshots |

## Running Tests

### Line Coverage
```bash
pytest CodeCoverageTest_PES2UG24CS562_application.py -v --cov=car_rental_rate --cov-report=term-missing
```

### Branch Coverage
```bash
pytest BranchCoverageTest_PES2UG24CS562_application.py -v --cov=car_rental_rate --cov-branch --cov-report=term-missing
```

> Install dependencies if needed: `pip install pytest pytest-cov`

Keep all Lab 6 work in this `Lab 6` folder. Lab 7 will be added to this repo later.
