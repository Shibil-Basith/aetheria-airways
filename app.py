from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("Set SUPABASE_URL and SUPABASE_KEY in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__, static_folder="templates", template_folder="templates")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flights", methods=["POST"])
def api_flights():
    payload = request.get_json() or {}
    origin = (payload.get("origin") or "").strip()
    destination = (payload.get("destination") or "").strip()
    dep_date = payload.get("date") or None

    query = supabase.table("flights").select("*")
    if origin:
        query = query.ilike("origin", f"%{origin}%")
    if destination:
        query = query.ilike("destination", f"%{destination}%")
    if dep_date:
        query = query.eq("departure_date", dep_date)
    query = query.order("departure_date", desc=False).limit(200)

    res = query.execute()
    # Normalize response checking---------------
    data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None)
    err = getattr(res, "error", None) or (res.get("error") if isinstance(res, dict) else None)
    if err:
        return jsonify({"error": str(err)}), 500
    return jsonify({"data": data}), 200

@app.route("/api/book", methods=["POST"])
def api_book():
    payload = request.get_json() or {}
    email = payload.get("user_email")
    flight_id = payload.get("flight_id")
    seat = payload.get("seat_number")
    passenger = payload.get("passenger") or {}
    
    if not (email and flight_id and seat):
        return jsonify({"error": "missing fields"}), 400
    
    # check if seat already booked------------
    check = supabase.table("bookings").select("id").eq("flight_id", flight_id).eq("seat_number", seat).execute()
    check_data = getattr(check, "data", None) or (check.get("data") if isinstance(check, dict) else None)
    if check_data and len(check_data) > 0:
        return jsonify({"error": "seat already booked"}), 409
    
    # insert booking with passenger details
    booking_data = {
        "user_email": email,
        "flight_id": flight_id,
        "seat_number": seat,
        "passenger_name": passenger.get("name", ""),
        "passenger_sex": passenger.get("sex"),
        "passenger_age": passenger.get("age"),
        "passenger_phone": passenger.get("phone")
    }
    res = supabase.table("bookings").insert(booking_data).execute()
    data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None)
    err = getattr(res, "error", None) or (res.get("error") if isinstance(res, dict) else None)
    if err:
        return jsonify({"error": str(err)}), 500
    return jsonify({"data": data}), 201

@app.route("/api/occupied-seats/<flight_id>", methods=["GET"])
def get_occupied_seats(flight_id):
    """Fetch all booked seats for a flight"""
    res = supabase.table("bookings").select("seat_number").eq("flight_id", flight_id).execute()
    data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None)
    err = getattr(res, "error", None) or (res.get("error") if isinstance(res, dict) else None)
    if err:
        return jsonify({"error": str(err)}), 500
    seats = [row["seat_number"] for row in (data or [])]
    return jsonify({"occupied": seats}), 200

@app.route("/seat/<flight_id>")
def seat_page(flight_id):
    # fetch flight
    res = supabase.table("flights").select("*").eq("id", flight_id).execute()
    data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None)
    err = getattr(res, "error", None) or (res.get("error") if isinstance(res, dict) else None)
    if err or not data:
        return "Flight not found", 404
    flight = data[0] if isinstance(data, list) and len(data) else data
    return render_template("seat.html", flight=flight)

@app.route("/passenger")
def passenger_page():
    flight_id = request.args.get("flight_id")
    seat = request.args.get("seat")
    if not flight_id or not seat:
        return redirect(url_for("index"))
    return render_template("passenger.html", flight_id=flight_id, seat=seat)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
