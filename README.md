# LayoverGuide API

## What it is

LayoverGuide is a community-driven platform where travellers share real layover 
itineraries. Given an airport and a layover duration, users can find exactly what 
other travellers did — how long it took to exit, what transport they used, where 
they went, and whether they made it back in time. The problem it solves: no 
searchable, community-verified resource exists for layover itineraries. Reddit 
threads are scattered, TripAdvisor doesn't filter by duration, and AI-generated 
suggestions aren't verified by real experience.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Database:** PostgreSQL (hosted on Supabase)
- **Authentication:** Supabase Auth (JWT, ES256)
- **Deployment:** Railway
- **Frontend:** Next.js (separate repository)

## Database Schema

| Table | Purpose |
|---|---|
| airports | Stores airport data — IATA code, city, country, timezone |
| profiles | Extends Supabase auth.users — username and display name |
| itineraries | Core table — one row per submitted layover itinerary |
| places | Places visited during a layover — linked to an itinerary |
| tags | Lookup table for itinerary tags (budget_friendly, family_friendly etc.) |
| itinerary_tags | Junction table linking itineraries to tags |
| upvotes | Junction table — one row per user per itinerary upvote |
| bookmarks | Junction table — one row per user per saved itinerary |
| comments | User comments on itineraries, categorised by type |

Foreign keys always live on the "many" side of a relationship. Derived data 
(upvote counts, submission counts) is never stored as a column — always computed 
via SQL queries to prevent stale data.

## Key Technical Decisions

### Composite index on (airport_id, layover_duration_mins)

The core search query filters by both airport and duration range simultaneously. 
A composite index on both columns allows PostgreSQL to satisfy both filters in a 
single index scan rather than scanning every row.

EXPLAIN ANALYZE output confirms this:

Index Scan using itineraries_airport_id_layover_duration_mins_idx on itineraries
(cost=0.15..2.37 rows=1 width=164)
(actual time=0.063..0.064 rows=2 loops=1)
Index Cond: ((airport_id = '...') AND
(layover_duration_mins >= 180) AND
(layover_duration_mins <= 600))
Planning Time: 0.429 ms
Execution Time: 0.136 ms

Without the index, this would be a sequential scan — O(n) across every row. 
With the composite index, it is O(log n) regardless of table size.

### JWT validation via Supabase SDK

Supabase signs tokens with ES256 (Elliptic Curve), not the more common HS256. 
Decoding ES256 locally requires fetching the public key from Supabase's JWKS 
endpoint. Instead, the middleware passes the token directly to 
`supabase.auth.get_user(token)`, letting Supabase's servers handle verification. 
This is simpler, always correct, and automatically handles token expiry.

### Junction tables for upvotes and bookmarks

Both upvotes and bookmarks are modelled as junction tables with a composite 
primary key of (user_id, itinerary_id). The composite PK itself enforces 
uniqueness — a user cannot upvote the same itinerary twice at the database level, 
independent of application logic.

### UUID serialisation fix

Pydantic's model_dump() returns UUID fields as Python UUID objects, not strings. 
Supabase's REST API requires strict JSON, which cannot serialise UUID objects. 
Fixed by using model_dump(mode='json') which converts all fields to 
JSON-compatible types before insertion.

## Analytical SQL Queries

### 1. Top airports by number of itinerary submissions

```sql
SELECT a.airport_name, COUNT(*) as no_of_itineraries
FROM airports AS a
INNER JOIN itineraries AS i ON a.airport_id = i.airport_id
GROUP BY a.airport_name
ORDER BY no_of_itineraries DESC
LIMIT 5;
```

### 2. Average exit time per airport per transport mode

```sql
SELECT a.airport_name, i.exit_transport_mode, 
       ROUND(AVG(i.time_to_exit_mins), 1) as avg_time_to_exit
FROM airports AS a
INNER JOIN itineraries AS i ON a.airport_id = i.airport_id
WHERE i.time_to_exit_mins IS NOT NULL 
AND i.exit_transport_mode IS NOT NULL
GROUP BY a.airport_name, i.exit_transport_mode
ORDER BY a.airport_name;
```

### 3. Itineraries ranked by upvote count within each airport

```sql
WITH upvote_counts AS (
    SELECT itinerary_id, COUNT(*) as upvote_count
    FROM upvotes
    GROUP BY itinerary_id
)
SELECT 
    a.airport_name,
    i.itinerary_id,
    COALESCE(uc.upvote_count, 0) as upvote_count,
    RANK() OVER (PARTITION BY a.airport_id ORDER BY uc.upvote_count DESC) as rank
FROM itineraries i
JOIN airports a ON i.airport_id = a.airport_id
LEFT JOIN upvote_counts uc ON i.itinerary_id = uc.itinerary_id
ORDER BY a.airport_name, rank;
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /airports | No | List all airports for search dropdown |
| GET | /itineraries | No | Search itineraries by airport and duration |
| GET | /itineraries/{id} | No | Fetch single itinerary with upvote count |
| POST | /itineraries | Yes | Submit a new itinerary |
| POST | /itineraries/{id}/upvote | Yes | Toggle upvote on an itinerary |

## Running Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/layoverguide-api.git
cd layoverguide-api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET

# Run the server
uvicorn main:app --reload
```

API documentation available at http://127.0.0.1:8000/docs

## Resume Bullets

- Built and deployed a full-stack layover itinerary platform (Next.js, FastAPI, 
  PostgreSQL) with JWT auth, upvoting, and community submissions
- Designed relational schema with composite indexes, reducing search query cost 
  from O(n) sequential scan to O(log n) index scan — verified via EXPLAIN ANALYZE
- Implemented sliding window rate limiter and duplicate detection in FastAPI, 
  preventing abuse while maintaining sub-150ms API response times
- Wrote window function SQL (RANK() OVER PARTITION BY) for per-airport itinerary 
  ranking — used in platform analytics