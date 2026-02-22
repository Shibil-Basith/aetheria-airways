# Aetheria Airways — Flask + Supabase

Small full-stack demo app for Aetheria Airways.

Quick start:

1. Create a Python virtualenv and install deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set Supabase credentials in `.env` (SUPABASE_URL and SUPABASE_KEY).

3. Run the app:

```powershell
python app.py
```

4. In Supabase SQL editor run `create_tables.sql` to create `flights` and `bookings`.

Notes:
- `GET /` serves the UI.
- `POST /api/flights` accepts JSON { origin, destination, date }.
- `POST /api/book` accepts JSON { user_email, flight_id, seat_number }.
