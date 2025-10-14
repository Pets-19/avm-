# Bug Report: Rental Yield Not Showing

**Subject:** Rental Yield feature not displaying on valuation results

**Error Description:**
When I perform a property valuation, the rental yield card does not appear even though the valuation completes successfully.

**Console/Terminal Output:**
```
⚠️ [RENTAL] Could not fetch rental data: (psycopg2.errors.UndefinedFunction) operator does not exist: text > integer
LINE 11:                 AND "actual_area" > 0
                                           ^
HINT:  No operator matches the given name and argument types. You might need to add explicit type casts.
```

**Input:**
- Property Type: Unit
- Location: Dubai Hills
- Size: 300 sqm
- Bedrooms: Any
- Status: Any

**Expected Behavior:**
- Should show rental yield card (4th card) with percentage
- Should display color-coded yield (Green/Orange/Red)
- Should show comparables count or city average

**Actual Behavior:**
- Rental yield card is hidden
- Valuation works fine: 4,750,917 AED (97% confidence)
- Console shows: "⚠️ Rental data not available for this property"

**Root Cause:**
The `actual_area` column in the `rentals` table is TEXT type, not numeric. The query tries to compare TEXT > INTEGER which causes a PostgreSQL type error.

**Fix Required:**
Cast `actual_area` to NUMERIC in the rental query SQL.

**Files Affected:**
- `/workspaces/avm-retyn/app.py` (lines 1103-1203)
  - Rental query section needs type casting

**Priority:** 🔴 HIGH - Feature is completely non-functional

**Status:** 🛠️ IDENTIFIED - Ready to fix
