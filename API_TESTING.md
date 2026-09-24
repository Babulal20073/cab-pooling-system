# API Testing & Manual Verification

This document contains the manual API verification steps used for the Employee Cab Pooling & Smart Pickup Routing system.

Testing was performed using:

- cURL
- Swagger UI
- PostgreSQL queries

There is currently no automated pytest suite in the repository.

## 1. Prerequisites

Start PostgreSQL and Redis:

```bash
docker compose up -d
```

Verify containers:

```bash
docker compose ps
```

Seed the database:

```bash
uv run python -m scripts.seed
```

Start FastAPI:

```bash
uv run uvicorn app.main:app --reload
```

Base URL:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## 2. Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```text
HTTP 200
```

```json
{
  "status": "ok"
}
```

---

## 3. Register Employee

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "gender": "male",
    "home_lat": 31.25,
    "home_lng": 75.70
  }'
```

Expected:

```text
HTTP 201 Created
```

---

## 4. Duplicate Registration

Repeat the registration request using the same email.

Expected:

```text
HTTP 409 Conflict
```

Example:

```json
{
  "detail": "Email already registered"
}
```

---

## 5. Login

The login endpoint uses OAuth2 password form data.

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!"
```

Expected:

```text
HTTP 200 OK
```

Response:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Set the token locally:

```bash
TOKEN="<JWT>"
```

Do not commit or share real JWT tokens.

---

## 6. Invalid Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=wrongpassword"
```

Expected:

```text
HTTP 401 Unauthorized
```

Example:

```json
{
  "detail": "Invalid email or password"
}
```

---

## 7. Current User

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

Expected:

```text
HTTP 200 OK
```

The response contains the authenticated employee.

---

## 8. Employee Access to Admin Endpoint

An employee should not be able to access admin-only endpoints.

```bash
curl http://127.0.0.1:8000/admin/test \
  -H "Authorization: Bearer $TOKEN"
```

Expected:

```text
HTTP 403 Forbidden
```

Example:

```json
{
  "detail": "Admin access required"
}
```

---

## 9. Admin Access

Login using an account with the `admin` role.

```bash
ADMIN_TOKEN="<admin-jwt>"
```

Then:

```bash
curl http://127.0.0.1:8000/admin/test \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Expected:

```text
HTTP 200 OK
```

---

## 10. Create Booking

```bash
curl -X POST http://127.0.0.1:8000/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shift_id": 1
  }'
```

Expected:

```text
HTTP 201 Created
```

Example response:

```json
{
  "id": 123,
  "employee_id": 10,
  "shift_id": 1,
  "status": "active"
}
```

---

## 11. Duplicate Booking

Repeat the same booking request for the same employee and shift.

Expected:

```text
HTTP 409 Conflict
```

Example:

```json
{
  "detail": "Employee already has a booking for this shift"
}
```

Duplicate bookings are protected by:

1. Service-level validation
2. Database unique constraint

```text
(employee_id, shift_id)
```

---

## 12. Get My Bookings

```bash
curl http://127.0.0.1:8000/bookings \
  -H "Authorization: Bearer $TOKEN"
```

Expected:

```text
HTTP 200 OK
```

---

## 13. Create Office

Admin authentication is required.

```bash
curl -X POST http://127.0.0.1:8000/admin/offices \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Office",
    "lat": 31.2500,
    "lng": 75.7000
  }'
```

Expected:

```text
HTTP 201 Created
```

---

## 14. Create Shift

```bash
curl -X POST http://127.0.0.1:8000/admin/shifts \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "office_id": 1,
    "start_time": "2026-09-24T09:00:00",
    "shift_type": "day"
  }'
```

Expected:

```text
HTTP 201 Created
```

---

## 15. Invalid Shift

Try planning a shift that does not exist:

```bash
curl -X POST \
  http://127.0.0.1:8000/admin/shifts/999/plan \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Expected:

```text
HTTP 404 Not Found
```

Example:

```json
{
  "detail": "Shift not found"
}
```

---

## 16. Plan a Shift

```bash
curl -X POST \
  http://127.0.0.1:8000/admin/shifts/1/plan \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Expected:

```text
HTTP 200 OK
```

The response contains information about:

- Spatial groups
- Nearby employees
- Cab groups
- Routes
- Pickup ETAs

---

## 17. Spatial Grouping Verification

The planning response contains spatial grouping information.

The implementation uses:

```text
GRID_SIZE = 0.005
```

and checks neighboring grid cells before applying the Haversine distance filter.

The candidate threshold is approximately:

```text
2 km
```

This avoids a naive all-pairs employee comparison.

---

## 18. Inspect Cab Stops

After planning a shift, inspect persisted stops using PostgreSQL.

Connect to the database:

```bash
docker exec -it <postgres-container> psql \
  -U cabuser \
  -d cabpooling
```

Then:

```sql
SELECT
    id,
    cab_id,
    employee_id,
    sequence_no,
    eta,
    is_pickup
FROM stops
ORDER BY cab_id, sequence_no;
```

This verifies the persisted pickup order and ETA.

---

## 19. Cancellation

Cancel a booking:

```bash
curl -X DELETE \
  http://127.0.0.1:8000/bookings/<BOOKING_ID> \
  -H "Authorization: Bearer $TOKEN"
```

Expected:

```text
HTTP 200 OK
```

The booking status should become:

```text
cancelled
```

---

## 20. Selective Re-planning

After cancelling an employee:

```text
Cancelled Booking
       │
       ▼
Find Employee's Cab
       │
       ▼
Remove Employee
       │
       ▼
Recalculate Only That Cab
```

The other cabs should not be re-planned.

This was manually verified by comparing stop sequences and ETAs before and after cancellation.

The affected cab changed while an untouched cab remained unchanged.

---

## 21. Night Safety

The seed data contains a night shift with male and female employees.

Plan the night shift:

```bash
curl -X POST \
  http://127.0.0.1:8000/admin/shifts/2/plan \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

For night shifts, the route validator prevents:

```text
First modeled passenger → female
Last modeled passenger  → female
```

A valid route is persisted only when the safety validator accepts the ordering.

### Current limitation

The current model contains pickup stops only.

Therefore, this test verifies the first and last **modeled passenger stops**, not a separate last-drop event.

---

## 22. Maximum Ride-Time Constraint

The routing service uses:

```text
MAX_RIDE_TIME_MINUTES = 90
```

Travel time is estimated using:

```text
distance / average speed × 60
```

Routes exceeding 90 minutes are rejected.

The constraint was manually verified using an artificially distant employee location, where no valid route was found.

Expected error:

```text
No valid route satisfies the planning constraints
```

---

## 23. Late Booking

A booking can be created after a shift already has a cab plan.

```bash
curl -X POST http://127.0.0.1:8000/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shift_id": 2
  }'
```

The planning service evaluates existing cabs.

Checks include:

```text
Available capacity
       +
Geographical compatibility
       +
Route validity
       +
Maximum ride time
       +
Night safety
```

If a valid cab is found:

```text
Existing Cab
     │
     ▼
Add Employee
     │
     ▼
Recalculate Route
     │
     ▼
Recalculate Pickup ETAs
```

The updated route is persisted.

If no suitable cab exists, the booking remains active but unassigned.

---

## 24. Database Uniqueness

The booking table contains:

```text
UNIQUE(employee_id, shift_id)
```

Verify the database constraint using PostgreSQL:

```sql
\d bookings
```

The constraint prevents duplicate bookings even if multiple requests reach the database.

---

## 25. Transaction Behaviour

Booking creation follows:

```text
Create Booking
      │
      ▼
Flush
      │
      ▼
Try Late Assignment
      │
      ▼
Commit
```

If an exception occurs:

```text
Exception
   │
   ▼
Rollback
```

This prevents partial booking and planning changes from being committed.

Cancellation and selective re-planning use the same transaction pattern.

---

## 26. Docker Commands

Check running services:

```bash
docker compose ps
```

Start services:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

Stop services and remove the database volume:

```bash
docker compose down -v
```

Use the last command carefully because it removes persisted PostgreSQL data.

---

## 27. Useful PostgreSQL Queries

### Employees

```sql
SELECT * FROM employees;
```

### Offices

```sql
SELECT * FROM offices;
```

### Shifts

```sql
SELECT * FROM shifts;
```

### Bookings

```sql
SELECT * FROM bookings;
```

### Cabs

```sql
SELECT * FROM cabs;
```

### Stops

```sql
SELECT *
FROM stops
ORDER BY cab_id, sequence_no;
```

### Active bookings for a shift

```sql
SELECT *
FROM bookings
WHERE shift_id = 1
  AND status = 'ACTIVE';
```

---

## 28. Manual Verification Summary

| Feature | Verification |
|---|---|
| Health endpoint | Verified |
| Registration | Verified |
| Duplicate registration | Verified |
| Login | Verified |
| Invalid login | Verified |
| JWT authentication | Verified |
| Employee authorization | Verified |
| Admin authorization | Verified |
| Booking creation | Verified |
| Duplicate booking | Verified |
| Invalid shift | Verified |
| Booking cancellation | Verified |
| Selective re-planning | Verified |
| Spatial grouping | Verified |
| Route generation | Verified |
| Maximum ride time | Verified |
| Night safety | Verified |
| Late booking | Verified |
| Pickup ETA | Verified |
| Database uniqueness | Verified |

