# 🐛 Error Reporting Guide - Quick Reference

## 📋 The Perfect Error Report (30 seconds)

```
When I [ACTION], I got an error:

Input:
   [LIST YOUR INPUT VALUES]

Error:
   [COPY/PASTE EXACT ERROR]

Console (F12):
   [COPY/PASTE CONSOLE ERRORS]

Context:
   - [What works / what doesn't]
   
Expected:
   [What should happen]
```

---

## ⚡ Quick Checklist

Before reporting an error, include:

- [ ] **Exact error message** (copy/paste, don't paraphrase)
- [ ] **What you clicked/selected** (specific action)
- [ ] **Console output** (F12 → Console tab)
- [ ] **Input values** (what you entered in the form)
- [ ] **Context** (does it work for other options?)
- [ ] **Terminal logs** (if backend error)

**4+ checked?** → Fix in minutes! 🚀  
**1-3 checked?** → Might need clarification  
**0 checked?** → Multiple back-and-forth needed

---

## 🎯 Real Examples

### ✅ EXCELLENT (Level 3)
```
When I selected "Off-Plan" filter, I got:
Error: HTTP 500
Console: Failed to load resource: (index):2085
Context: Ready works, Off-Plan fails
Expected: Should show Off-Plan property valuations
```
**Result:** Fixed in 2 minutes!

### ❌ POOR (Level 1)
```
It doesn't work
```
**Result:** Need 5+ follow-up questions

---

## 🔍 Where to Find Error Info

### Browser Console (Frontend Errors)
1. Press **F12** (or right-click → Inspect)
2. Click **Console** tab
3. Look for **red error messages**
4. Copy the entire error including line numbers

### Terminal/Server Logs (Backend Errors)
1. Check the terminal where Flask is running
2. Look for **Traceback**, **Error**, or **Exception**
3. Copy the error message and stack trace

### Network Tab (API Errors)
1. Press **F12** → **Network** tab
2. Click the failed request (shows red)
3. Check **Response** tab for error details

---

## 📝 Templates

### Frontend Error Template
```
I got an error when [selecting/clicking/entering] [specific thing]:

Input:
   Property Type: Unit
   Location: Dubai Hills
   Size: 300
   Filter: Off-Plan

Error:
   HTTP 500: Internal Server Error

Console:
   (index):2085 Valuation error: Error: HTTP 500
   Failed to load resource: status 500

Context:
   - Works for Ready
   - Fails for Off-Plan
   
Expected:
   Should display valuation results for Off-Plan properties
```

### Backend/API Error Template
```
The API endpoint returned an error:

Endpoint: /api/property/valuation
Method: POST
Parameters:
   {
     "property_type": "Unit",
     "area": "Dubai Hills",
     "size_sqm": 300,
     "development_status": "Off Plan"
   }

Error Response:
   HTTP 500

Terminal Log:
   psycopg2.ProgrammingError: column "is_offplan_en" does not match

Expected:
   Should return valuation data
```

### UI/Display Issue Template
```
The [feature name] is not displaying correctly:

What I Did:
   - Filled the form
   - Clicked submit
   - Got results but no comparable properties table

What I Expected:
   Should show a table with 5 comparable properties

What Actually Happened:
   Results show but comparable section is missing

Additional Info:
   - API returns comparables: Yes (checked network tab)
   - Console errors: None
   - Other sections work: Yes
```

---

## 🎓 Error Reporting Levels

### Level 1 - Minimum
> "I got error X"

**Fix time:** 10-15 minutes (need clarification)

### Level 2 - Good
> "I got error X when doing Y. Console: [paste]"

**Fix time:** 5-8 minutes

### Level 3 - Excellent ⭐
> "I got error X when doing Y. Context: A works, B fails. Console: [paste]. Expected: Z"

**Fix time:** 2-3 minutes

### Level 4 - Legendary 🏆
> "Feature X fails for input Y. Error: [exact]. Console: [with lines]. Terminal: [backend error]. Context: Works for [list], fails for [value]. Expected: [outcome]"

**Fix time:** 1-2 minutes (instant diagnosis)

---

## 💡 Pro Tips

### 1. Test in Isolation
✅ "Works for 2BR, 3BR, 4BR but fails for 1BR"  
❌ "The bedroom filter doesn't work"

**Why better?** Tells me it's a specific value issue, not general logic!

### 2. Copy, Don't Describe
✅ `psycopg2.errors.SyntaxError: syntax error at "WHERE"`  
❌ "There's a database syntax error"

**Why better?** Exact errors reveal the root cause immediately!

### 3. Include Line Numbers
✅ `(index):2085 Valuation error`  
❌ "Error in the HTML file"

**Why better?** I can jump straight to the problematic code!

### 4. Show What Works
✅ "Studio, 2BR, 3BR work. 1BR fails"  
❌ "It's broken"

**Why better?** Narrows down the issue to specific edge case!

### 5. Separate Expected vs Actual
```
Expected: Should show 5 comparable properties
Actual: Shows "No data available"
```

**Why better?** Clear gap analysis helps identify the exact failure point!

---

## 🚀 After Implementation Testing

Help me catch issues early by testing:

### 1. Test All Options
- Try "Any" / default option
- Try each specific option
- Try combinations of filters

### 2. Check Edge Cases
- Empty values
- Very large numbers
- Very small numbers
- Special characters

### 3. Verify Data
- Do results make sense?
- Are numbers in reasonable range?
- Do filters actually filter?

### 4. Report Patterns
✅ "Ready works (tested 5 times), Off-Plan fails every time"  
✅ "Works on Chrome, fails on Firefox"  
✅ "Works for Dubai Hills, fails for Business Bay"

---

## 🎯 Quick Decision Tree

**Got an error?**
↓
**Is it red in browser console?** → Frontend issue  
└─ Copy console error + line number

**Is it in terminal/server logs?** → Backend issue  
└─ Copy terminal error + traceback

**No errors but wrong result?** → Logic/data issue  
└─ Describe expected vs actual behavior

**Nothing happens?** → Event/connection issue  
└─ Check network tab + console for clues

---

## 📞 Your Report Template (Copy This)

```markdown
**Issue:** [One-line summary]

**Action:** [What I did step-by-step]

**Input:**
   - Field 1: Value
   - Field 2: Value
   - Field 3: Value

**Error:**
   [Copy/paste exact error message]

**Console Output:**
   [Copy/paste from F12 → Console]

**Terminal Output:** (if backend error)
   [Copy/paste from terminal]

**Context:**
   - What works: [list]
   - What fails: [specific case]
   - When it started: [after X implementation / always]

**Expected:**
   [What should happen]

**Screenshots:** (optional but helpful)
   [Attach if UI issue]
```

---

## 🏆 Hall of Fame Examples

### Your Off-Plan Error (Level 3 - Excellent!)
```
When I selected the filter "Off-plan", it's showing error:
Error getting valuation: HTTP 500
Console:
Failed to load resource: the server responded with a status of 500 ()
(index):2085 Valuation error: Error: HTTP 500
```

**Why excellent?**
- ✅ Specific action ("selected Off-plan")
- ✅ Exact error (HTTP 500)
- ✅ Console output with line number
- ✅ Implied context (other options work)

**Fix time:** 2 minutes!

---

## 🔗 Resources

- **Browser Console:** F12 or Ctrl+Shift+I (Cmd+Opt+I on Mac)
- **Network Tab:** F12 → Network (see API requests/responses)
- **Terminal Logs:** Where you run `python app.py`
- **This Guide:** `/workspaces/avm-retyn/ERROR_REPORTING_GUIDE.md`

---

## 📌 Remember

> "A problem well-stated is a problem half-solved" - Charles Kettering

**The better your error report, the faster I can fix it!**

Your Off-Plan report was **Level 3 (Excellent)** - that's why I fixed it in 2 minutes! 🎉

Keep up the good reporting! 🚀
