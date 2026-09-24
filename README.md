# 🚕 Employee Cab Pooling & Smart Pickup Routing

A backend system for employee cab pooling and smart pickup routing, built for the **MoveInSync Backend Case Study 2026**.

The system groups employees travelling to the same office and shift into shared cabs while considering:

- Cab capacity
- Employee geographical proximity
- Pickup route distance
- Maximum ride time
- Night-time safety
- Duplicate booking prevention
- Booking cancellation and selective re-planning
- Late bookings
- Pickup ETAs
- Authentication and role-based authorization

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM |
| PostgreSQL | Relational database |
| Psycopg 3 | PostgreSQL driver |
| Pydantic | Request/response validation |
| Pydantic Settings | Environment configuration |
| JWT | Authentication |
| pwdlib + Argon2 | Password hashing |
| Docker Compose | Local infrastructure |
| uv | Python dependency management |

Redis is included in Docker for possible future use, but the current application does not depend on it.

## 🏗️ Architecture

```text
                    Client
               (Swagger / cURL)
                       │
                       ▼
              ┌─────────────────┐
              │  FastAPI Router │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Service Layer  │
              ├─────────────────┤
              │ AuthService      │
              │ BookingService   │
              │ PlanningService  │
              │ RoutingService   │
              │ SafetyValidator  │
              │ OfficeService    │
              │ ShiftService     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   SQLAlchemy    │
              │      ORM        │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   PostgreSQL    │
              └─────────────────┘
```

Business logic is kept inside the service layer rather than directly inside API routers.

The application uses FastAPI's **lifespan mechanism** for startup initialization.

## 📁 Project Structure

```text
cab-pooling-system/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── employee.py
│   │   ├── office.py
│   │   ├── shift.py
│   │   ├── booking.py
│   │   ├── cab.py
│   │   ├── stop.py
│   │   └── enums.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── booking.py
│   │   ├── office.py
│   │   ├── shift.py
│   │   └── planning.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── bookings.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── booking_service.py
│   │   ├── planning_service.py
│   │   ├── routing_service.py
│   │   ├── safety_service.py
│   │   ├── spatial_service.py
│   │   ├── office_service.py
│   │   └── shift_service.py
│   │
│   ├── exceptions.py
│   ├── exception_handlers.py
│   └── main.py
│
├── docs/
│   └── API_TESTING.md
│
├── scripts/
│   ├── __init__.py
│   └── seed.py
│
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

## 🚀 Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/Babulal20073/cab-pooling-system.git
cd cab-pooling-system
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://cabuser:cabpass@localhost:5433/cabpooling
REDIS_URL=redis://localhost:6379
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Never commit `.env` or production secrets.

### 4. Start the infrastructure

```bash
docker compose up -d
```

Check the services:

```bash
docker compose ps
```

PostgreSQL:

```text
localhost:5433
```

Redis:

```text
localhost:6379
```

### 5. Seed demonstration data

```bash
uv run python -m scripts.seed
```

The seed script creates demonstration employees, an office, shifts, and bookings.

### 6. Start FastAPI

```bash
uv run uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## 📚 Main API Endpoints

### Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Bookings

```text
POST   /bookings
GET    /bookings
DELETE /bookings/{booking_id}
```

### Admin

```text
POST /admin/offices
POST /admin/shifts
POST /admin/shifts/{shift_id}/plan
```

### Health

```text
GET /health
```

## 🗄️ Database Design

The system uses PostgreSQL because the domain is strongly relational.

```text
Employee
   │
   └──< Booking >── Shift >── Office
                       │
                       └──< Cab >──< Stop
```

### Employee

```text
Employee
---------
id
name
email
password_hash
gender
role
home_lat
home_lng
```

### Office

```text
Office
------
id
name
lat
lng
```

### Shift

```text
Shift
-----
id
office_id
start_time
shift_type
```

### Booking

```text
Booking
-------
id
employee_id
shift_id
status
created_at
```

A database uniqueness constraint ensures:

```text
(employee_id, shift_id)
```

is unique, preventing duplicate bookings for the same employee and shift.

### Cab

```text
Cab
---
id
shift_id
capacity
guard_assigned
```

### Stop

```text
Stop
----
id
cab_id
employee_id
sequence_no
eta
is_pickup
```

Keeping `Stop` separate from `Cab` allows an individual cab's route to be re-planned without recreating unrelated cab plans.

## 🚕 Cab Planning

Planning follows this pipeline:

```text
Active Bookings
       │
       ▼
Spatial Index
       │
       ▼
Nearby Employees
       │
       ▼
Cab Grouping
       │
       ▼
Route Optimization
       │
       ▼
Night Safety Validation
       │
       ▼
Pickup ETA Calculation
       │
       ▼
Persist Cab + Stops
```

## 📍 Spatial Indexing

A naive implementation would compare every employee with every other employee:

```text
O(n²)
```

Instead, employees are first assigned to geographical grid cells.

```text
Employee
   │
   ▼
Grid Cell
   │
   ▼
Current + Neighboring Cells
   │
   ▼
Haversine Distance
   │
   ▼
Nearby Candidates
```

The current implementation uses a fixed grid and considers candidates within approximately **2 km**.

This avoids unnecessary global employee-to-employee comparisons.

## 👥 Cab Grouping

Cab grouping is a heuristic rather than an exact optimization algorithm.

The system:

1. Builds a spatial index.
2. Finds nearby candidates.
3. Selects the most constrained unassigned employee.
4. Adds nearby employees to the group.
5. Stops when the cab reaches its capacity.
6. Repeats until all active bookings are assigned.

The most constrained employee is processed first because employees with fewer nearby candidates have fewer possible grouping choices.

This is a practical heuristic rather than a globally optimal clustering solution.

## 🗺️ Route Optimization

Once a cab group is created, the system evaluates possible pickup orders.

For a cab containing `k` employees:

```text
O(k!)
```

The current implementation supports cab groups of up to 6 employees:

```text
6! = 720
```

possible pickup permutations in the worst case.

Each candidate route is checked against the planning constraints, and the shortest valid route is selected.

The office is treated as the final destination.

## ⏱️ Route Constraints

A route must satisfy:

- Maximum ride time of **90 minutes**
- Valid pickup ordering
- Night safety constraints
- Arrival at the office before the shift start

Travel time is currently estimated using an average speed and Haversine distance.

## 🌙 Night Safety

For night shifts, the route validator prevents a female employee from being:

- The first modeled pickup
- The last modeled passenger stop

The current `Stop` model represents pickup events rather than separate pickup and drop-off events.

Therefore, the current implementation validates the first and last **modeled passenger stops**, rather than a complete real-world last-drop condition.

Explicit pickup/drop-off modeling can be added in a future version.

## 🔄 Cancellation & Re-planning

When an employee cancels:

```text
Cancellation
     │
     ▼
Find affected cab
     │
     ▼
Remove employee
     │
     ▼
Recalculate affected cab
     │
     ▼
Persist updated route
```

Only the affected cab is re-planned.

Untouched cabs are not reshuffled.

The booking cancellation and re-planning operation is handled within a database transaction so that failures can roll back the changes.

## ➕ Late Bookings

A late booking can be evaluated against existing cabs.

The system checks:

- Available capacity
- Geographic compatibility
- Route validity
- Maximum ride time
- Night safety

If a valid cab is found, its route and pickup ETAs are recalculated.

If no existing cab can accept the employee while satisfying the constraints, the booking remains active but unassigned.

## 🔐 Authentication & Authorization

The application uses:

- JWT authentication
- OAuth2 bearer tokens
- Argon2 password hashing
- Role-based authorization

Supported roles:

```text
employee
admin
```

Employees can manage their own bookings.

Admins can additionally:

- Create offices
- Create shifts
- Trigger cab planning
- Access admin-only endpoints

## ⚠️ Error Handling

Business-level exceptions are handled centrally and converted into appropriate HTTP responses.

Examples include:

```text
InvalidCredentialsError
OfficeAlreadyExistsError
OfficeNotFoundError
ShiftNotFoundError
DuplicateBookingError
BookingNotFoundError
NoValidRouteError
```

Typical responses include:

```text
401 → Invalid credentials
403 → Insufficient permissions
404 → Resource not found
409 → Duplicate/conflicting resource
422 → No valid route
```

## 📏 Distance Calculation

The current implementation uses the **Haversine formula**.

Advantages:

- No external API key
- No external network dependency
- Fast
- Simple
- Suitable for this case study

Haversine calculates straight-line geographical distance rather than actual road distance.

A production implementation could use a road-routing service such as OSRM, Mapbox, or Google Maps.

That would provide more realistic travel times but introduce external dependencies, latency, cost, rate limits, and availability concerns.

## 🧠 Complexity

### Spatial Search

Naive approach:

```text
O(n²)
```

Current approach:

```text
Grid indexing
+
Neighboring-cell search
+
Distance filtering
```

The exact complexity depends on employee distribution and grid density, but the approach avoids globally comparing every employee with every other employee.

### Route Optimization

For `k` employees in a cab:

```text
O(k!)
```

With:

```text
k <= 6
```

the maximum is:

```text
720 permutations
```

This is reasonable for the current case-study constraints.

## 🧪 Testing & Verification

The application was manually verified using:

- Swagger UI
- cURL
- PostgreSQL queries

Verified scenarios include:

- Health check
- Employee registration
- Duplicate registration
- Valid login
- Invalid login
- JWT authentication
- Employee/admin authorization
- Booking creation
- Duplicate booking prevention
- Invalid shift handling
- Booking cancellation
- Selective cab re-planning
- Spatial grouping
- Route generation
- Maximum ride-time validation
- Night safety validation
- Late booking assignment
- Pickup ETA generation
- Database uniqueness constraints

Detailed manual API testing steps are documented in:

```text
docs/API_TESTING.md
```

There is currently **no automated pytest test suite** in the repository.

## ⚖️ Design Trade-offs

### Haversine vs Road Routing

Haversine was chosen because it is fast, dependency-free, and sufficient for demonstrating the planning logic.

Road routing would provide more realistic results but introduces external API dependencies and cost.

### Brute Force vs Advanced VRP

Brute-force route evaluation is practical because each cab contains at most a small number of employees.

For larger groups, a VRP solver or more advanced optimization technique would be more appropriate.

### PostgreSQL vs NoSQL

PostgreSQL was selected because the system contains strong relationships between:

```text
Employee
Booking
Shift
Cab
Stop
Office
```

and requires transactional consistency.


## 🔮 Future Improvements

Possible production improvements include:

- Road-network routing
- PostGIS spatial indexing
- Advanced VRP optimization
- Explicit pickup/drop-off modeling
- More sophisticated night safety rules
- Automatic new-cab creation
- Redis caching where useful
- Alembic database migrations
- Automated test suite
- Monitoring and metrics
- CI/CD

## 📄 API Testing

Detailed manual API requests and verification steps are available in:

```text
docs/API_TESTING.md
```
