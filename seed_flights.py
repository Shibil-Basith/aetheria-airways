import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("Set SUPABASE_URL and SUPABASE_KEY in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

cities = [
    "London", "Tokyo", "New York", "Paris", "Dubai", "Singapore", "Sydney", "Toronto",
    "Los Angeles", "San Francisco", "Berlin", "Rome", "Barcelona", "Hong Kong", "Seoul",
    "Mumbai", "Delhi", "Bangkok", "Istanbul", "Amsterdam", "Copenhagen", "Zurich",
    "Vienna", "Munich", "Chicago", "Dallas", "Atlanta", "Mexico City", "Sao Paulo",
    "Buenos Aires", "Cape Town", "Johannesburg", "Auckland", "Honolulu"
]

airlines = ["AE", "AX", "AH", "AA", "AZ", "BA", "DL", "QF", "SQ", "EK", "JL", "NH"]

def gen_flight_no():
    return f"{random.choice(airlines)}{random.randint(100, 9999)}"

def gen_price():
    return round(random.uniform(250, 4500), 2)

def gen_date():
    return (date.today() + timedelta(days=random.randint(1, 365))).isoformat()

def build_flights(n=120):
    flights = []
    for _ in range(n):
        origin, destination = random.sample(cities, 2)
        flights.append({
            "flight_no": gen_flight_no(),
            "origin": origin,
            "destination": destination,
            "price": gen_price(),
            "departure_date": gen_date()
        })
    return flights

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

def parse_response(res):
    # Normalize different supabase client response shapes
    data = None
    error = None
    status = None
    try:
        if hasattr(res, "data"):
            data = res.data
        elif isinstance(res, dict):
            data = res.get("data")
            error = res.get("error")
            status = res.get("status_code") or res.get("status")
        elif hasattr(res, "json"):
            j = res.json()
            data = j.get("data")
            error = j.get("error")
            status = j.get("status_code") or j.get("status")
    except Exception:
        pass
    # Some clients expose 'error' differently
    if error is None and hasattr(res, "error"):
        try:
            error = getattr(res, "error")
        except Exception:
            error = None
    return data, error, status

def main():
    count = 120
    rows = build_flights(count)
    success = 0
    for chunk in chunked(rows, 50):
        try:
            res = supabase.table("flights").insert(chunk).execute()
        except Exception as e:
            print("Exception during insert:", e)
            continue

        data, error, status = parse_response(res)
        if error:
            print("Error inserting chunk:", error)
        elif status and int(status) >= 400:
            print("HTTP error inserting chunk, status:", status)
        else:
            inserted = len(data) if data else len(chunk)
            success += inserted
            print(f"Inserted {inserted} rows")
    print(f"Done. Attempted: {count}, Inserted: {success}")

if __name__ == "__main__":
    main()