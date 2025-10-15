# Authentication & Data Persistence Flow

## Overview
This system uses **Firebase Authentication** for user login and **MySQL** for storing farmer data. The two systems are linked via email and a persistent `currentFarmerId` mapping.

## How It Works

### 1. User Login (Firebase)
- User logs in with email/password via Firebase Auth
- Firebase returns a `user.uid` and `user.email`

### 2. Farmer ID Mapping
When a user logs in, the system:

1. **Checks Firestore cache** first:
   - Looks for `profiles/{uid}/farmerID`
   - If found, immediately sets `currentFarmerId` (fastest)

2. **Queries MySQL by email**:
   - Calls `/get_farmer_by_email?email={user.email}`
   - Finds the matching `Farmers` row where `contact_info = email`

3. **Creates farmer if not found**:
   - Inserts new row into `Farmers` table
   - Uses email as `contact_info` for linking

4. **Stores mapping in Firestore**:
   - Saves `farmerID` to `profiles/{uid}` for future sessions
   - This enables instant restoration on page reload

### 3. Data Persistence

#### Firebase Firestore (profiles collection)
```javascript
{
  uid: "firebase_user_id",
  email: "user@example.com",
  farmerID: 123,  // ← MySQL Farmers.FarmerID
  name: "John Doe",
  location: "Punjab",
  phone: "1234567890",
  language: "Hindi",
  field_size: 10
}
```

#### MySQL (Farmers table)
```sql
FarmerID | name      | location | language | field_size | contact_info
---------|-----------|----------|----------|------------|------------------
123      | John Doe  | Punjab   | Hindi    | 10         | user@example.com
```

### 4. Session Restoration
When user returns to the site:
1. Firebase `onAuthStateChanged` fires automatically
2. System calls `ensureFarmerExistsAndSetDefaults()`
3. Restores `currentFarmerId` from Firestore cache
4. All forms auto-populate with user's ID

## Key Features

### ✅ Equipment Section
- **My Equipment**: Shows equipment where `OwnerID == currentFarmerId`
- **Others' Equipment**: Shows all other equipment
- **Request Button**: Only appears on others' available equipment
- Clicking "Request" opens lending form with:
  - Equipment pre-selected
  - Borrower auto-set to current user (disabled field)
  - Lender auto-determined by backend from equipment owner

### ✅ Lending Requests
- Shows only requests where `BorrowerID == currentFarmerId`
- Displays: equipment name, status, start date, duration, lender name

### ✅ Auto-filled Forms
All forms automatically use `currentFarmerId`:
- Add Equipment → `OwnerID`
- Add Query → `FarmerID`
- Add Response → `ResponderID`
- Request Equipment → `BorrowerID`
- Add Review → `FromFarmerID`

## Backend Routes

### New Route: `/get_farmer_by_email`
```python
GET /get_farmer_by_email?email=user@example.com
```
Returns the farmer record matching the email (faster than fetching all farmers).

### Existing Routes
- `POST /add_farmer` - Create new farmer
- `POST /update_farmer` - Update farmer details
- `GET /get_farmers` - Get all farmers
- `GET /get_equipment` - Get all equipment
- `POST /add_lending_request` - Create lending request (auto-sets LenderID)
- `GET /get_lending_requests` - Get all lending requests

## Flow Diagram

```
User Login (Firebase)
    ↓
Check Firestore cache
    ↓ (if not cached)
Query MySQL by email
    ↓ (if not found)
Create new Farmer row
    ↓
Store farmerID in Firestore
    ↓
Set currentFarmerId globally
    ↓
Update all dropdowns & forms
    ↓
Load user-specific data:
  - My Equipment
  - My Lending Requests
  - Pre-fill forms
```

## Console Logs
Watch browser console for:
- ✅ `Logged in as FarmerID: 123 (John Doe)` - Login successful
- ✅ `Restored FarmerID from cache: 123` - Fast cache restore
- ✅ `Restored FarmerID from Firestore: 123` - Profile loaded

## Troubleshooting

### Issue: currentFarmerId is null
**Solution**: 
1. Check browser console for errors
2. Verify Firebase is configured (check `firebaseConfig`)
3. Ensure user is logged in (`auth.currentUser` should exist)
4. Check MySQL `Farmers` table has matching `contact_info`

### Issue: Equipment not showing "My Equipment"
**Solution**:
1. Verify `currentFarmerId` is set (check console)
2. Check `Equipment.OwnerID` matches your `FarmerID`
3. Refresh the page after login

### Issue: Lending form not auto-filling
**Solution**:
1. Ensure you're logged in
2. Check `#lendingBorrower` dropdown is populated
3. Verify `currentFarmerId` is set before opening form

## Security Notes
- Firebase handles authentication securely
- MySQL stores farmer data
- Email is the linking key between systems
- `currentFarmerId` is client-side only (for UI convenience)
- Backend validates all requests (e.g., LenderID is always derived from equipment owner)
