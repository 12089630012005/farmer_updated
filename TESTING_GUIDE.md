# Equipment & Lending Testing Guide

## ✅ All Features Already Implemented

This guide will help you test that all equipment management and lending features are working correctly.

## Prerequisites
1. MySQL database running with tables: `Farmers`, `Equipment`, `LendingRequests`
2. Firebase configured in `index.html` (lines 1326-1334)
3. Flask app running: `python app.py`
4. At least 2 test accounts created in Firebase

---

## Test Scenario 1: User-Specific Equipment Storage

### Steps:
1. **Login as User A** (e.g., `usera@test.com`)
   - Go to Login/Profile section
   - Enter credentials and click Login
   - Check browser console: Should see `✅ Logged in as FarmerID: X`

2. **Add Equipment as User A**
   - Go to Equipment section
   - Fill form:
     - Name: "Tractor A"
     - Type: "Tractor"
     - Condition: "Good"
     - Hourly Rate: 50
     - Availability: "Available"
   - Click "Add Equipment"
   - **Expected**: Equipment appears in "My Equipment" section

3. **Verify Equipment Ownership**
   - Check MySQL database:
     ```sql
     SELECT * FROM Equipment WHERE name = 'Tractor A';
     ```
   - **Expected**: `OwnerID` matches User A's `FarmerID`

4. **Logout and Login as User B** (e.g., `userb@test.com`)
   - Click Logout
   - Login with User B credentials
   - Go to Equipment section
   - **Expected**: 
     - "My Equipment" is empty (or shows only User B's equipment)
     - "Available from Others" shows "Tractor A" (User A's equipment)

✅ **PASS**: Equipment is stored per user and filtered correctly

---

## Test Scenario 2: Request Lending (Auto-fill Borrower/Lender)

### Steps:
1. **Still logged in as User B**
   - In Equipment section, find "Tractor A" in "Available from Others"
   - Click **"Request"** button
   - **Expected**: 
     - Redirects to Lending section
     - Equipment dropdown pre-selected to "Tractor A"
     - Borrower field shows User B (disabled/read-only)

2. **Submit Lending Request**
   - Fill in:
     - Start Date: (any future date)
     - Duration: 3 days
   - Click "Submit Request"
   - **Expected**: Alert "Lending request added successfully"

3. **Verify in Database**
   ```sql
   SELECT lr.*, e.name, f1.name as lender, f2.name as borrower
   FROM LendingRequests lr
   JOIN Equipment e ON lr.EquipmentID = e.EquipmentID
   JOIN Farmers f1 ON lr.LenderID = f1.FarmerID
   JOIN Farmers f2 ON lr.BorrowerID = f2.FarmerID
   WHERE e.name = 'Tractor A';
   ```
   - **Expected**:
     - `BorrowerID` = User B's FarmerID
     - `LenderID` = User A's FarmerID (auto-set by backend)
     - `status` = "Pending"

4. **Check Lending Requests Section**
   - Still as User B, go to Lending section
   - **Expected**: Shows the request for "Tractor A" with status "Pending"

✅ **PASS**: Borrower/Lender auto-assigned correctly

---

## Test Scenario 3: Prevent Self-Lending

### Steps:
1. **Login as User A** (owner of "Tractor A")
   - Go to Equipment section
   - **Expected**: "Tractor A" appears in "My Equipment"
   - **Expected**: NO "Request" button on your own equipment

2. **Try Manual Self-Lending (API Test)**
   - Open browser DevTools Console
   - Run this command:
     ```javascript
     fetch('/add_lending_request', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
         EquipmentID: 1, // Your equipment ID
         BorrowerID: currentFarmerId, // Your ID
         start_date: '2025-10-15',
         duration: 3
       })
     }).then(r => r.json()).then(console.log);
     ```
   - **Expected**: Response `{"message": "Owner cannot borrow own equipment"}`

✅ **PASS**: Self-lending is prevented

---

## Test Scenario 4: Data Persistence After Logout/Reload

### Steps:
1. **Login as User A**
   - Add equipment: "Harvester A"
   - Verify it appears in "My Equipment"

2. **Logout**
   - Click Logout button
   - **Expected**: Redirects to home, equipment sections cleared

3. **Close Browser Tab** (simulate full session end)

4. **Reopen and Login as User A**
   - **Expected**: 
     - Console shows `✅ Restored FarmerID from cache: X`
     - Equipment section automatically loads
     - "Harvester A" still appears in "My Equipment"

5. **Login as User B**
   - **Expected**: 
     - "Harvester A" appears in "Available from Others"
     - User B's equipment (if any) in "My Equipment"

✅ **PASS**: Data persists correctly across sessions

---

## Test Scenario 5: Multiple Users, Multiple Equipment

### Steps:
1. **User A adds**: Tractor, Harvester, Plough
2. **User B adds**: Sprayer, Seeder
3. **User C adds**: Cultivator

**Login as User A:**
- My Equipment: Tractor, Harvester, Plough
- Available from Others: Sprayer, Seeder, Cultivator

**Login as User B:**
- My Equipment: Sprayer, Seeder
- Available from Others: Tractor, Harvester, Plough, Cultivator

**Login as User C:**
- My Equipment: Cultivator
- Available from Others: Tractor, Harvester, Plough, Sprayer, Seeder

✅ **PASS**: Multi-user equipment isolation working

---

## Test Scenario 6: Lending Request Filtering

### Steps:
1. **User B requests**: Tractor (from User A)
2. **User B requests**: Cultivator (from User C)
3. **User C requests**: Sprayer (from User B)

**Login as User B, go to Lending section:**
- **Expected**: Shows only 2 requests (Tractor, Cultivator)
- Does NOT show User C's request for Sprayer

**Login as User C, go to Lending section:**
- **Expected**: Shows only 1 request (Sprayer)

✅ **PASS**: Lending requests filtered by borrower

---

## Backend Validation Checklist

### Equipment Routes
- ✅ `POST /add_equipment` - Requires `OwnerID`
- ✅ `GET /get_equipment` - Returns all equipment
- ✅ Frontend filters by `OwnerID == currentFarmerId`

### Lending Routes
- ✅ `POST /add_lending_request` - Auto-sets `LenderID` from equipment owner
- ✅ `POST /add_lending_request` - Validates borrower ≠ owner
- ✅ `GET /get_lending_requests` - Returns all requests
- ✅ Frontend filters by `BorrowerID == currentFarmerId`

### Auth Routes
- ✅ `GET /get_farmer_by_email` - Fast email lookup
- ✅ Firebase UID → MySQL FarmerID mapping via Firestore

---

## Common Issues & Solutions

### Issue: "My Equipment" shows all equipment
**Cause**: `currentFarmerId` not set  
**Solution**: 
1. Check console for `✅ Logged in as FarmerID: X`
2. Verify Firebase auth is working
3. Refresh page after login

### Issue: Request button appears on own equipment
**Cause**: `isMine` flag not working  
**Solution**: Check `loadEquipment()` function line 2041-2042

### Issue: Can request own equipment via form
**Cause**: Backend validation missing  
**Solution**: Already implemented at line 422-424 in `app.py`

### Issue: Lending requests show all users' requests
**Cause**: Frontend filter not applied  
**Solution**: Check `loadLendingRequestsUI()` line 2191

---

## Database Schema Verification

### Equipment Table
```sql
CREATE TABLE Equipment (
    EquipmentID INT PRIMARY KEY AUTO_INCREMENT,
    OwnerID INT NOT NULL,  -- Links to Farmers.FarmerID
    name VARCHAR(255),
    type VARCHAR(100),
    `condition` VARCHAR(50),
    hourly_rate DECIMAL(10,2),
    availability_status ENUM('Available', 'Unavailable'),
    FOREIGN KEY (OwnerID) REFERENCES Farmers(FarmerID)
);
```

### LendingRequests Table
```sql
CREATE TABLE LendingRequests (
    RequestID INT PRIMARY KEY AUTO_INCREMENT,
    EquipmentID INT NOT NULL,
    LenderID INT NOT NULL,   -- Auto-set to Equipment.OwnerID
    BorrowerID INT NOT NULL, -- Current logged-in user
    start_date DATE,
    duration INT,
    status ENUM('Pending', 'Approved', 'Rejected', 'Completed'),
    FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID),
    FOREIGN KEY (LenderID) REFERENCES Farmers(FarmerID),
    FOREIGN KEY (BorrowerID) REFERENCES Farmers(FarmerID)
);
```

---

## Success Criteria

✅ Each user sees only their own equipment in "My Equipment"  
✅ Each user sees other users' equipment in "Available from Others"  
✅ Request button only appears on others' available equipment  
✅ Borrower auto-set to current user (disabled field)  
✅ Lender auto-set to equipment owner (backend)  
✅ Self-lending prevented with error message  
✅ Lending requests filtered to show only current user's requests  
✅ Data persists after logout and page reload  
✅ Multiple users can have separate equipment lists  
✅ Firebase UID correctly maps to MySQL FarmerID  

---

## Quick Test Commands

### Check Current User
```javascript
// In browser console
console.log('Current Farmer ID:', currentFarmerId);
```

### Check Equipment Ownership
```sql
SELECT e.*, f.name as owner_name 
FROM Equipment e 
JOIN Farmers f ON e.OwnerID = f.FarmerID;
```

### Check Lending Requests
```sql
SELECT 
    lr.RequestID,
    e.name as equipment,
    f1.name as lender,
    f2.name as borrower,
    lr.status
FROM LendingRequests lr
JOIN Equipment e ON lr.EquipmentID = e.EquipmentID
JOIN Farmers f1 ON lr.LenderID = f1.FarmerID
JOIN Farmers f2 ON lr.BorrowerID = f2.FarmerID;
```

---

## All Features Are Implemented! 🎉

Every requirement you listed is already working in the codebase. Follow this testing guide to verify everything is functioning correctly.
