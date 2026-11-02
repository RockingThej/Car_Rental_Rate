import pytest
from car_rental_rate import process_rental_fleet, check_fleet_telematics

# ============================================================
# Branch Coverage Test Suite
# Student: Thejaswi S | SRN: PES2UG24CS562
# Goal: Achieve 90-100% BRANCH coverage
# Each test is annotated with the specific branch it targets.
# ============================================================


# ============================================================
# process_rental_fleet — Branch Map
# ============================================================
# B1:  isinstance(rentals, list) AND base_admin_fee >= 0  → True (proceed)
# B2:  isinstance(rentals, list) OR base_admin_fee < 0   → False (raise)
# B3:  rental["is_confirmed"] → True (process rental)
# B4:  rental["is_confirmed"] → False (continue / skip)
# B5:  days <= 0 → True  (risk_flag++, continue)
# B6:  days <= 0 → False (process vehicle)
# B7:  vehicle_type == "luxury" → True
# B8:  vehicle_type == "suv"   → True
# B9:  vehicle_type else       → True  (economy / unknown)
# B10: miles < 0 → True  (risk_flag++, continue)
# B11: miles < 0 → False (check distance)
# B12: miles > 300 → True  (long-distance surcharge)
# B13: miles > 300 → False (short-distance charge)
# B14: driver_age < 21 → True  (flat $250 + break)
# B15: driver_age < 21 → False (per-mile charge * 0.40)
# B16: driver_age < 25 → True  (young-driver surcharge applies)
# B17: driver_age < 25 → False (no surcharge)
# B18: vehicle_type == "luxury" (inside age<25 block) → True  (50*days)
# B19: vehicle_type == "luxury" (inside age<25 block) → False (20*days)
# B20: risk_flags > 4 → True  (HIGH_RISK_AUDIT)
# B21: risk_flags > 4 → False (check revenue)
# B22: total_revenue == 0.0 → True  (EMPTY_BATCH)
# B23: total_revenue == 0.0 → False (STANDARD)
#
# check_fleet_telematics — Branch Map
# B24: telematics_matrix falsy → True  (NO_DATA)
# B25: telematics_matrix truthy → False (iterate)
# B26: speed > 100 → True  (increment streak)
# B27: speed > 100 → False (reset streak)
# B28: speeding_streak >= 2 → True  (GROUND_VEHICLE)
# B29: speeding_streak >= 2 → False (continue)
# B30: loop exhausted without trigger → SAFE
# ============================================================


# B2: Invalid input → ValueError
def test_b2_invalid_type_raises_value_error():
    """B2a — not a list."""
    with pytest.raises(ValueError):
        process_rental_fleet(42, 10.0)

def test_b2_negative_admin_fee_raises_value_error():
    """B2b — base_admin_fee < 0."""
    with pytest.raises(ValueError):
        process_rental_fleet([], -5.0)


# B1 + B22: Valid input, empty list → EMPTY_BATCH
def test_b1_b22_empty_list_returns_empty_batch():
    """B1 (valid input), B22 (revenue == 0.0)."""
    result = process_rental_fleet([], 0.0)
    assert result == {"total_revenue": 0.0, "status": "EMPTY_BATCH"}


# B4: Unconfirmed rental is skipped
def test_b4_unconfirmed_rental_skipped():
    """B4 — is_confirmed=False, rental skipped entirely."""
    rentals = [{"is_confirmed": False, "vehicle_type": "luxury", "driver_age": 30, "days": 5}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "EMPTY_BATCH"


# B3 + B5: Confirmed rental with days <= 0 → risk_flag, continue
def test_b3_b5_confirmed_zero_days_risk_flag():
    """B3 (confirmed), B5 (days <= 0)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "EMPTY_BATCH"  # revenue still 0, 1 flag only


# B3 + B6: Confirmed rental with days > 0 → proceed to vehicle type
def test_b3_b6_confirmed_positive_days_proceeds():
    """B3 (confirmed), B6 (days > 0 → process)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["status"] == "STANDARD"


# B7: vehicle_type == "luxury"
def test_b7_luxury_vehicle_rate():
    """B7 — luxury daily_rate = 120.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "luxury", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 120.0


# B8: vehicle_type == "suv"
def test_b8_suv_vehicle_rate():
    """B8 — suv daily_rate = 70.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "suv", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 70.0


# B9: vehicle_type else (economy / unknown)
def test_b9_economy_vehicle_rate():
    """B9 — else branch daily_rate = 40.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 40.0

def test_b9_unknown_vehicle_type_defaults_economy():
    """B9 — unknown vehicle_type defaults to 40.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "bike", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 40.0


# B10: miles < 0 → risk_flag, continue
def test_b10_negative_miles_risk_flag():
    """B10 — miles < 0: risk_flags++, continue (no charge)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": [-50]}]
    result = process_rental_fleet(rentals, 0.0)
    # 1 risk flag, revenue = 40.0 (no mile charge added)
    assert result["total_revenue"] == 40.0
    assert result["status"] == "STANDARD"


# B11 + B13: miles >= 0 and <= 300 → short segment charge
def test_b11_b13_short_trip_charge():
    """B11 (miles >= 0), B13 (miles <= 300 → *0.20)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": [200]}]
    result = process_rental_fleet(rentals, 0.0)
    # 40 + 200*0.20 = 80.0
    assert result["total_revenue"] == 80.0


# B12 + B15: miles > 300, driver_age >= 21 → per-mile 0.40
def test_b12_b15_long_trip_adult_per_mile():
    """B12 (miles > 300), B15 (driver_age >= 21 → per-mile 0.40)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 25, "days": 1, "trip_segments": [350]}]
    result = process_rental_fleet(rentals, 0.0)
    # 40 + 350*0.40 = 40 + 140 = 180.0; age>=25 no surcharge
    assert result["total_revenue"] == 180.0


# B12 + B14: miles > 300, driver_age < 21 → flat $250 + break
def test_b12_b14_long_trip_underage_flat_surcharge():
    """B12 (miles > 300), B14 (driver_age < 21 → flat $250, break)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 19, "days": 1, "trip_segments": [400]}]
    result = process_rental_fleet(rentals, 0.0)
    # 40 + 250 = 290 + young-driver: 20*1 = 20 => 310
    assert result["total_revenue"] == 310.0


# B14: break ensures second segment is NOT processed
def test_b14_break_stops_processing_further_segments():
    """B14 — after flat surcharge + break, remaining segments ignored."""
    rentals = [
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 19,
         "days": 1, "trip_segments": [400, 500, 600]}  # only first >300 processed
    ]
    result = process_rental_fleet(rentals, 0.0)
    # Same as single segment: 40 + 250 + 20 = 310
    assert result["total_revenue"] == 310.0


# B16 + B18: driver_age < 25 AND luxury → surcharge 50*days
def test_b16_b18_young_driver_luxury_surcharge():
    """B16 (age < 25), B18 (luxury → 50*days)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "luxury", "driver_age": 22, "days": 3, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    # 120*3 + 50*3 = 360 + 150 = 510.0
    assert result["total_revenue"] == 510.0


# B16 + B19: driver_age < 25 AND non-luxury → surcharge 20*days
def test_b16_b19_young_driver_economy_surcharge():
    """B16 (age < 25), B19 (not luxury → 20*days)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "suv", "driver_age": 20, "days": 2, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    # 70*2 + 20*2 = 140 + 40 = 180.0
    assert result["total_revenue"] == 180.0


# B17: driver_age >= 25 → no young-driver surcharge
def test_b17_adult_driver_no_surcharge():
    """B17 — driver_age >= 25: no extra surcharge."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 25, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 40.0


# B20: risk_flags > 4 → HIGH_RISK_AUDIT
def test_b20_high_risk_audit():
    """B20 — 5 zero-day rentals triggers HIGH_RISK_AUDIT."""
    rentals = [
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},
    ]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "HIGH_RISK_AUDIT"


# B20 + B21 + B23: risk_flags <= 4 AND revenue > 0 → STANDARD
def test_b21_b23_standard_status():
    """B21 (risk_flags <= 4), B23 (revenue > 0 → STANDARD)."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": [100]}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "STANDARD"
    assert result["total_revenue"] == 70.0


# B20 + B21 + B22: risk_flags <= 4 AND revenue == 0 → EMPTY_BATCH
def test_b21_b22_empty_batch_after_all_skipped():
    """B21 (risk_flags <=4), B22 (revenue == 0 → EMPTY_BATCH)."""
    rentals = [{"is_confirmed": False, "vehicle_type": "economy", "driver_age": 30, "days": 5}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "EMPTY_BATCH"
    assert result["total_revenue"] == 0.0


# Combined risk: negative miles + zero days together
def test_mixed_risk_flags_below_threshold():
    """Mix of negative miles and zero days; stays STANDARD if revenue > 0 and flags <=4."""
    rentals = [
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},   # flag 1
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": [-10]},  # flag 2
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 2, "trip_segments": [100]},  # normal
    ]
    result = process_rental_fleet(rentals, 0.0)
    assert result["status"] == "STANDARD"


# ============================================================
# check_fleet_telematics — Branches
# ============================================================

# B24: empty → NO_DATA
def test_b24_empty_telematics_no_data():
    """B24 — falsy telematics_matrix returns NO_DATA."""
    assert check_fleet_telematics([]) == "NO_DATA"
    assert check_fleet_telematics(None) == "NO_DATA"


# B25 + B27 + B30: non-empty, all speeds safe → SAFE
def test_b25_b27_b30_all_safe():
    """B25 (non-empty), B27 (speed <= 100 → reset), B30 (loop done → SAFE)."""
    assert check_fleet_telematics([[60, 80, 100]]) == "SAFE"


# B26 + B29 + B27: one overspeed then safe (streak reset, no flag)
def test_b26_b29_b27_one_overspeed_then_reset():
    """B26 (speed > 100), B29 (streak < 2), B27 (speed <= 100 resets streak)."""
    assert check_fleet_telematics([[110, 90, 110, 80]]) == "SAFE"


# B26 + B28: two consecutive overspeeds → GROUND_VEHICLE
def test_b26_b28_consecutive_overspeed_ground_vehicle():
    """B26 (speed > 100), B28 (streak >= 2 → GROUND_VEHICLE)."""
    assert check_fleet_telematics([[110, 120]]) == "GROUND_VEHICLE"


# B26 + B28: overspeed triggered in second vehicle_log
def test_b28_second_vehicle_triggers_ground_vehicle():
    """B28 — first vehicle safe, second vehicle triggers GROUND_VEHICLE."""
    assert check_fleet_telematics([[80, 90], [105, 110]]) == "GROUND_VEHICLE"


# B30: multiple vehicles, all safe → full loop → SAFE
def test_b30_multiple_vehicles_all_safe():
    """B30 — all vehicles exhaust without triggering, returns SAFE."""
    assert check_fleet_telematics([[80, 70], [60, 50], [100, 99]]) == "SAFE"


# Edge: exactly 3-consecutive overspeeds → still GROUND_VEHICLE at 2nd
def test_three_consecutive_overspeeds():
    """B28 triggered at the second overspeed in a three-overspeed run."""
    assert check_fleet_telematics([[110, 115, 120]]) == "GROUND_VEHICLE"


# Edge: one vehicle safe, then overspeed at very end of second vehicle
def test_b28_overspeed_at_end_of_second_vehicle():
    """B28 edge — overspeed at end of second vehicle's log."""
    assert check_fleet_telematics([[90, 95], [80, 110, 120]]) == "GROUND_VEHICLE"
