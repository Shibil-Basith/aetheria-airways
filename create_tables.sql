-- Supabase SQL: create flights and bookings tables for Aetheria

create table if not exists flights (
  id uuid primary key default gen_random_uuid(),
  flight_no text not null,
  origin text not null,
  destination text not null,
  price numeric not null,
  departure_date date not null
);

create table if not exists bookings (
  id uuid primary key default gen_random_uuid(),
  user_email text not null,
  flight_id uuid references flights(id) on delete cascade,
  seat_number text not null,
  created_at timestamptz default now()
);
