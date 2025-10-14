# 🚀 Quick Error Report Template

Copy and fill this in when you encounter an error:

---

## 🐛 Error Report

**When I:** [what you clicked/selected/typed]

**I got this error:**
```
[paste the exact error message here]
```

**My inputs were:**
- Property Type: 
- Location: 
- Size: 
- Other filters: 

**Console says:** (Press F12)
```
[paste any red errors from browser console]
```

**Terminal says:** (if backend error)
```
[paste any errors from the terminal where Flask runs]
```

**Context:**
- Works for: [list what works]
- Fails for: [what specifically fails]

**Expected:** [what should happen]

---

## 💡 Quick Checklist

Before sending, did I include:
- [ ] Exact error message (copy/paste)
- [ ] What I clicked/selected
- [ ] Console output (F12)
- [ ] Input values
- [ ] What works vs what fails

**4+ checked? → Fast fix!** ⚡
**Less than 4? → Add more info for faster help!**

---

## 🎯 Examples

### ✅ GOOD Report
```
When I selected "Off-Plan" from the Development Status dropdown, I got:

Error: HTTP 500

Console:
Failed to load resource: status 500
(index):2085 Valuation error: Error: HTTP 500

Input:
- Property Type: Unit
- Location: Dubai Hills
- Size: 300
- Bedrooms: 3
- Status: Off-Plan

Context:
- "Ready" works fine
- "Any" works fine
- Only "Off-Plan" fails

Expected: Should show valuation for Off-Plan properties
```
**Result: Fixed in 2 minutes!** 🎉

### ❌ POOR Report
```
It doesn't work
```
**Result: Need 10 minutes of back-and-forth to understand** 😞

---

## 🔍 Where to Find Info

**Browser Console:** F12 → Console tab (red errors)  
**Network Tab:** F12 → Network tab (API responses)  
**Terminal:** Where you run `python app.py` (backend errors)

---

Save this file and use it as your error reporting template! 📋
