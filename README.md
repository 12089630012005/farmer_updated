# Farmer Support Pro – README

A full-stack web app to help farmers connect, manage equipment lending, share queries/responses, and post reviews.

## Features

- **[Community]** Browse farmers with search and location filter.
- **[Crops]** Add/list crops; delete per crop card.
- **[Equipment]** Add/list equipment, request lending, and delete own equipment.
- **[Lending]** Borrower can cancel pending requests; two aligned lists for Borrowing vs Lending; quick Review button navigates and pre-fills.
- **[Queries]** Post queries with optional image, view responses inline, respond if not the owner.
- **[Reviews]** 5-star ratings, feedback; From auto-locked to logged-in user; To excludes self.
- **[Auth]** Firebase Authentication for `currentFarmerId` mapping to DB `FarmerID`.

## Tech Stack

- Backend: Flask (`app.py`), MySQL
- Frontend: Vanilla HTML/CSS/JS (`templates/index.html`)
- Auth: Firebase Web SDK (compat)
- Icons/Fonts: Font Awesome, Google Fonts

## Project Structure

- `app.py` – Flask app, DB connection, API routes
- `templates/index.html` – Single-page UI with sections and scripts
- `farmer/index.html` – Secondary HTML (if used by your flow)
- `Testing_Matrix.doc` – Test tables (Word HTML)
- Other assets (icons, placeholders) are inlined or fetched via CDNs

## Prerequisites

- Python 3.9+
- MySQL 5.7+/8.x with a database (e.g., `farmer_support`)
- Internet access for Firebase/Font Awesome CDNs

## Setup (Windows)

1. Create and activate a venv:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install flask mysql-connector-python python-dotenv
   ```

3. Create a `.env` file at project root:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=farmer_support
   ```

4. Initialize MySQL schema (excerpt):
   ```sql
   CREATE DATABASE IF NOT EXISTS farmer_support;
   USE farmer_support;
   -- See full schema in app setup notes or scripts
   ```

5. Firebase config
   - Ensure Firebase SDK scripts are included in `templates/index.html`.
   - Provide your Firebase project config; the app uses `currentFarmerId`.

## Run

```powershell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run
```

Open http://127.0.0.1:5000

## Key UI Behaviors

- `Farmers`: Live search and location filter.
- `Crops`: Each card shows Delete; calls `/delete_crop`.
- `Equipment`: Cards show tractor icon; rate with 2 decimals; Request for non-owners; Delete visible (disabled for others).
- `Lending`: Two columns (Borrowing/Lending), borrower can delete pending, Review button navigates to Reviews and sets target.
- `Reviews`: “From” locked to current user; “To” excludes self; 5-star rating widget.

## API Overview (selected)

- Farmers: `POST /add_farmer`, `GET /get_farmers`, `POST /update_farmer`
- Crops: `POST /add_crop`, `GET /get_crops`, `POST /delete_crop`
- Equipment: `POST /add_equipment`, `GET /get_equipment[?owner_id|exclude_owner_id]`, `POST /delete_equipment`
- Lending: `POST /add_lending_request`, `GET /get_lending_requests[?lender_id|borrower_id]`, `POST /delete_lending_request`
- Queries: `POST /add_query`, `GET /get_queries`, `POST /add_response`, `POST /toggle_like`
- Reviews: `POST /add_review`, `GET /get_reviews`

## Testing

- See `Testing_Matrix.doc` for prepared end‑to‑end test tables.

## Troubleshooting

- If Review button doesn’t navigate: ensure logged in; hard refresh (Ctrl+Shift+R).
- If equipment icon looks hidden: CSS overlay lowered in `.equipment-image::before`.
- DB errors: verify `.env`, schema, and privileges.

## Security Notes

- Delete endpoints validate ownership and pending status.
- Likes constrained with unique key `(ResponseID, FarmerID)`.
- Don’t commit secrets.

## License

Internal academic/project use.
