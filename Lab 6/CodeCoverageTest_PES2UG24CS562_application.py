import pytest
from car_rental_rate import process_rental_fleet, check_fleet_telematics

# ============================================================
# Code Coverage Test Suite
# Student: Thejaswi S | SRN: PES2UG24CS562
# Goal: Achieve 90-100% LINE (statement) coverage
# ============================================================


# --- process_rental_fleet: ValueError branch ---
def test_invalid_rentals_type_raises():
    """Covers: line 2-3 — invalid list input raises ValueError."""
    with pytest.raises(ValueError):
        process_rental_fleet("not_a_list", 10.0)


def test_negative_admin_fee_raises():
    """Covers: line 2-3 — negative base_admin_fee raises ValueError."""
    with pytest.raises(ValueError):
        process_rental_fleet([], -1.0)


# --- process_rental_fleet: unconfirmed rental skip ---
def test_unconfirmed_rental_is_skipped():
    """Covers: line 9-10 — is_confirmed=False causes continue."""
    rentals = [{"is_confirmed": False, "vehicle_type": "economy", "driver_age": 30, "days": 2}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "EMPTY_BATCH"
    assert result["total_revenue"] == 0.0


# --- process_rental_fleet: days <= 0 increments risk_flags ---
def test_zero_days_increments_risk_flag():
    """Covers: lines 16-18 — days <= 0 triggers risk_flags increment and continue."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "EMPTY_BATCH"


# --- vehicle_type: luxury ---
def test_luxury_vehicle_daily_rate():
    """Covers: lines 20-21 — luxury vehicle type daily_rate = 120.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "luxury", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 120.0
    assert result["status"] == "STANDARD"


# --- vehicle_type: suv ---
def test_suv_vehicle_daily_rate():
    """Covers: lines 22-23 — suv vehicle type daily_rate = 70.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "suv", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 70.0
    assert result["status"] == "STANDARD"


# --- vehicle_type: economy (default) ---
def test_economy_vehicle_daily_rate():
    """Covers: lines 24-25 — else branch sets daily_rate = 40.0."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    assert result["total_revenue"] == 40.0
    assert result["status"] == "STANDARD"


# --- trip_segments: negative miles ---
def test_negative_miles_increments_risk_flag():
    """Covers: lines 30-32 — negative miles triggers risk_flags and continue."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": [-10]}]
    result = process_rental_fleet(rentals, 0.0)
    # risk_flag=1, revenue=40.0 => STANDARD
    assert result["status"] == "STANDARD"
    assert result["total_revenue"] == 40.0


# --- trip_segments: miles > 300, driver_age >= 21 ---
def test_long_trip_adult_driver_surcharge():
    """Covers: lines 33-34, 38 — miles > 300, driver_age >= 21: per-mile charge."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 25, "days": 1, "trip_segments": [400]}]
    result = process_rental_fleet(rentals, 0.0)
    # 40 + 400*0.40 = 40 + 160 = 200.0
    assert result["total_revenue"] == 200.0
    assert result["status"] == "STANDARD"


# --- trip_segments: miles > 300, driver_age < 21 (flat $250 + break) ---
def test_long_trip_underage_driver_flat_surcharge():
    """Covers: lines 35-37 — miles > 300 AND driver_age < 21: flat 250 + break."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 19, "days": 1, "trip_segments": [400, 500]}]
    result = process_rental_fleet(rentals, 0.0)
    # 40 + 250 (break after first segment) + young-driver fee: 20*1 = 20 => 310
    assert result["total_revenue"] == 310.0
    assert result["status"] == "STANDARD"


# --- trip_segments: miles <= 300 ---
def test_short_trip_per_mile_charge():
    """Covers: line 40 — miles <= 300: miles * 0.20."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 1, "trip_segments": [100]}]
    result = process_rental_fleet(rentals, 10.0)
    # 40 + 10 + 100*0.20 = 70.0
    assert result["total_revenue"] == 70.0
    assert result["status"] == "STANDARD"


# --- driver_age < 25, luxury ---
def test_young_driver_luxury_surcharge():
    """Covers: line 43 — driver_age < 25 + luxury: 50*days surcharge."""
    rentals = [{"is_confirmed": True, "vehicle_type": "luxury", "driver_age": 22, "days": 2, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    # 120*2 + 50*2 = 240 + 100 = 340.0
    assert result["total_revenue"] == 340.0
    assert result["status"] == "STANDARD"


# --- driver_age < 25, non-luxury ---
def test_young_driver_non_luxury_surcharge():
    """Covers: line 43 — driver_age < 25 + economy: 20*days surcharge."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 20, "days": 3, "trip_segments": []}]
    result = process_rental_fleet(rentals, 0.0)
    # 40*3 + 20*3 = 120 + 60 = 180.0
    assert result["total_revenue"] == 180.0
    assert result["status"] == "STANDARD"


# --- HIGH_RISK_AUDIT: risk_flags > 4 ---
def test_high_risk_audit_status():
    """Covers: lines 47-48 — risk_flags > 4 returns HIGH_RISK_AUDIT."""
    rentals = [
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},  # flag 1
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},  # flag 2
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},  # flag 3
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},  # flag 4
        {"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 0},  # flag 5
    ]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "HIGH_RISK_AUDIT"


# --- EMPTY_BATCH: total_revenue == 0.0 ---
def test_empty_batch_status():
    """Covers: lines 49-50 — total_revenue == 0.0 returns EMPTY_BATCH."""
    result = process_rental_fleet([], 10.0)
    assert result["status"] == "EMPTY_BATCH"
    assert result["total_revenue"] == 0.0


# --- STANDARD return ---
def test_standard_status_return():
    """Covers: line 51 — normal path returns STANDARD."""
    rentals = [{"is_confirmed": True, "vehicle_type": "economy", "driver_age": 30, "days": 2, "trip_segments": [100]}]
    result = process_rental_fleet(rentals, 10.0)
    assert result["status"] == "STANDARD"
    # 40*2 + 10 + 100*0.20 = 110.0
    assert result["total_revenue"] == 110.0


# ============================================================
# check_fleet_telematics coverage
# ============================================================

def test_telematics_no_data():
    """Covers: lines 55-56 — empty list returns NO_DATA."""
    assert check_fleet_telematics([]) == "NO_DATA"


def test_telematics_safe():
    """Covers: lines 58-66 — all speeds <= 100, returns SAFE."""
    assert check_fleet_telematics([[80, 90, 70]]) == "SAFE"


def test_telematics_single_overspeed_not_consecutive():
    """Covers: lines 61-66 — one overspeed then back to normal, streak reset."""
    assert check_fleet_telematics([[110, 90, 110, 80]]) == "SAFE"


def test_telematics_consecutive_overspeed_ground_vehicle():
    """Covers: lines 63-64 — speeding_streak >= 2 returns GROUND_VEHICLE."""
    assert check_fleet_telematics([[110, 115]]) == "GROUND_VEHICLE"


def test_telematics_multiple_vehicles_one_flagged():
    """Covers: loop over multiple vehicle_logs, one triggers GROUND_VEHICLE."""
    assert check_fleet_telematics([[80, 90], [110, 120]]) == "GROUND_VEHICLE"


def test_telematics_multiple_vehicles_all_safe():
    """Covers: all vehicles safe returns SAFE after full loop."""
    assert check_fleet_telematics([[80, 90], [70, 100]]) == "SAFE"
