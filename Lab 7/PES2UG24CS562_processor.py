import math

def sanitize_license_plate(plate):
    """
    Sanitizes license plate by stripping whitespace, removing delimiters
    (-, ' ', _, #), and returning in uppercase. Handles invalid/None inputs safely.
    """
    if not isinstance(plate, str):
        return ""
    plate = plate.strip()
    for ch in ['-', ' ', '_', '#']:
        plate = plate.replace(ch, '')
    return plate.upper()

def parse_trip_mileage(mileage_csv):
    """
    Parses a comma-separated string of mileages into a list of non-negative floats.
    Safely ignores invalid, empty, negative, or non-finite entries.
    """
    if not isinstance(mileage_csv, str):
        return []
    parts = mileage_csv.split(',')
    mileages = []
    for m in parts:
        m = m.strip()
        if not m:
            continue
        try:
            val = float(m)
            if math.isfinite(val) and val >= 0:
                mileages.append(val)
        except (ValueError, TypeError):
            continue
    return mileages

def format_rental_invoice(record):
    """
    Parses and formats rental record string formatted as 'Driver:Days:Category'.
    Safely validates input types, delimiters, integer days, and defaults missing values.
    """
    if not isinstance(record, str):
        return "Invalid rental record: input must be a string"
    parts = record.split(':')
    if len(parts) < 3:
        return "Invalid rental record: expected format 'Driver:Days:Category'"
    driver = parts[0].strip() or "Unknown"
    try:
        days = int(parts[1].strip())
        if days < 0:
            return "Invalid rental record: days cannot be negative"
    except (ValueError, TypeError):
        return "Invalid rental record: invalid days value"
    category = parts[2].strip() or "Standard"
    daily_rate = 50.0 if category.lower() == "suv" else 30.0
    total = days * daily_rate
    return f"Driver {driver} booked {category} for {days} days: Total ${total:.2f}"

def main():
    print("==== Running sanitize_license_plate ====")
    raw_plate = input("Enter license plate with delimiters (-, _, #): ")
    clean_plate = sanitize_license_plate(raw_plate)
    print("Sanitized Plate:", clean_plate)

    print("\n==== Running parse_trip_mileage ====")
    csv_input = input("Enter CSV of mileages (e.g. 100.5, 45.2, 80.0): ")
    mileage_list = parse_trip_mileage(csv_input)
    print("Parsed Mileage List:", mileage_list)

    print("\n==== Running format_rental_invoice ====")
    record_input = input("Enter rental record (Driver:Days:Category): ")
    invoice = format_rental_invoice(record_input)
    print("Rental Invoice:", invoice)

if __name__ == "__main__":
    main()
