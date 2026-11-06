# Lab 7 — Fuzz Testing for Input Validation Bugs

## Student Details
- **Name**: Thejaswi S
- **SRN**: `PES2UG24CS562`
- **Course**: Software Engineering
- **Lab**: Lab 7 — Property-Based Fuzz Testing with Hypothesis

---

## About

This lab explores **property-based fuzz testing** using the Python **Hypothesis** library to detect and fix input validation bugs, crashes, and edge cases in car rental record processing routines (`PES2UG24CS562_processor.py`).

By describing invariants and properties (such as *the function must not crash on arbitrary Unicode text or `None`*), Hypothesis automatically generates hundreds of randomized edge-case inputs and minimizes failing inputs to isolate root causes.

---

## Files

| File | Description |
|------|-------------|
| `PES2UG24CS562_processor.py` | Hardened application module containing `sanitize_license_plate`, `parse_trip_mileage`, and `format_rental_invoice` |
| `PES2UG24CS562_test_processor.py` | Property-based fuzz test suite using `@given(st.text() \| st.none())` |
| `PES2UG24CS562_Lab7_Fuzzing_Report.pdf` | Final submission report with student details and terminal output screenshots |
| `ss1_buggy_processor_output.png` | Terminal output screenshot — Step 2: Running the initial application |
| `ss2_buggy_hypothesis_tests.png` | Terminal output screenshot — Step 4: Hypothesis uncovering edge-case crashes |
| `ss3_fixed_processor_output.png` | Terminal output screenshot — Step 5: Running the fixed application |
| `ss4_fixed_hypothesis_tests.png` | Terminal output screenshot — Step 6: All property-based fuzz tests passing |

---

## Edge Cases Uncovered by Hypothesis Fuzzing

1. **`sanitize_license_plate(plate)`**:
   - **Crash**: Passing `None` raised `AttributeError: 'NoneType' object has no attribute 'strip'`.
   - **Fix**: Added `isinstance(plate, str)` type checking; returns `""` for `None` or non-string inputs.

2. **`parse_trip_mileage(mileage_csv)`**:
   - **Crash 1**: Passing empty string `""` or invalid tokens raised `ValueError: could not convert string to float: ''`.
   - **Crash 2**: Passing `None` raised `AttributeError: 'NoneType' object has no attribute 'split'`.
   - **Fix**: Safely validates string type, splits elements, strips whitespace, ignores empty/non-numeric tokens, and filters out non-finite (`NaN`/`Inf`) and negative numbers using `math.isfinite()`.

3. **`format_rental_invoice(record)`**:
   - **Crash 1**: Passing `""` or strings with fewer than 2 colons raised `IndexError: list index out of range`.
   - **Crash 2**: Passing non-integer or empty days (e.g. `":"`) raised `ValueError: invalid literal for int()`.
   - **Crash 3**: Passing `None` raised `AttributeError: 'NoneType' object has no attribute 'split'`.
   - **Fix**: Enforces `len(parts) >= 3`, safely converts days to integer with fallback and non-negative check, defaults missing driver/category, and returns structured descriptive error messages for malformed records without raising uncaught exceptions.

---

## Instructions to Run

### 1. Install Dependencies
```bash
pip install hypothesis pytest
```

### 2. Run the Application Interactively
```bash
python PES2UG24CS562_processor.py
```

### 3. Run the Property-Based Fuzz Tests
```bash
pytest PES2UG24CS562_test_processor.py -v
```
All tests run with 100+ randomized iterations each and pass with zero failures.
