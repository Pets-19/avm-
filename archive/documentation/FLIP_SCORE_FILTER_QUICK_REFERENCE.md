# Flip Score Filter - Quick Reference Card

## 🎯 What It Does
Filters property valuations to only include comparables with minimum flip investment score.

## 📊 Current Data
- **Total Properties:** 153,573
- **With Flip Scores:** 10
- **Score Range:** 30 - 88
- **Average Score:** 73.2

## 🔢 Score Distribution
| Score | Count | Areas | Investment Level |
|-------|-------|-------|------------------|
| 88 | 2 | Madinat Al Mataar | Excellent |
| 82 | 3 | Palm Deira | Good |
| 70 | 4 | Dubai Production City | Moderate |
| 30 | 1 | Wadi Al Safa | Low Potential |

## 🎛️ Filter Options
- **Any Score** - No filter (default)
- **30+** - Low Potential or better (10 properties)
- **50+** - Moderate or better (9 properties)
- **70+** - Good or better (6 properties)
- **80+** - Excellent only (5 properties)

## 📍 Where to Find It
1. Navigate to **Property Valuation** tab
2. Scroll to optional filters section
3. Find **📈 Flip Score (Investment)** dropdown
4. Located after ESG Score filter

## 🔗 Combine with Other Filters
```
ESG 40+ AND Flip 70+ = Sustainable properties with good investment potential
```

## 🔍 How It Works
1. User selects minimum flip score
2. Frontend sends `flip_score_min` parameter
3. Backend adds SQL condition: `AND flip_score >= X`
4. Only properties meeting threshold used for valuation
5. Reduces comparable count, increases relevance

## 🚨 Important Notes
- Filter applies to **comparables search only**
- Does **NOT** add premium/discount to final price
- Works with existing filters (bedrooms, status, ESG)
- Gracefully handles missing data
- No performance impact (indexed column)

## 📈 Expected Impact
| Filter | Comparables Found | Use Case |
|--------|-------------------|----------|
| None | All available | General valuation |
| 30+ | 10 (current sample) | Any flip potential |
| 70+ | 6 (current sample) | Strong flip potential |
| 80+ | 5 (current sample) | Premium flip targets |

## 🔧 Technical Details
- **Column:** `flip_score INTEGER (0-100)`
- **Index:** `idx_flip_score` (btree, conditional)
- **Backend:** Dynamic column mapping via `find_column_name()`
- **Pattern:** Exact replica of ESG filter

## ✅ Testing
```bash
# Run unit tests
PYTHONPATH=/workspaces/avm- pytest tests/test_flip_score_filter.py::TestFlipScoreDatabase -v

# Expected: 5 passed in ~19s
```

## 🐛 Troubleshooting
**No results?**
- Area may not have properties with flip scores
- Try lower threshold or remove filter

**Filter not working?**
- Check browser console for `flip_score_min` in request
- Check Flask logs for `📈 [DB] Filtering for Flip score >= X`

**See errors?**
- Verify Flask restarted after migration
- Check flip_score column exists: `\d properties` in psql

## 📝 Files Changed
| File | Lines | Type |
|------|-------|------|
| templates/index.html | +18 | Dropdown + JS |
| app.py | +16 | Backend logic |
| tests/test_flip_score_filter.py | +187 | Tests (NEW) |
| migrations/*.sql | +140 | Migration (NEW) |

## 🚀 Future Enhancements
- **Approach #2:** Display flip scores in results
- **Approach #3:** Apply price premium based on flip score
- **Real-time:** Calculate flip score for all 153K properties
- **Dashboard:** Add flip score to trending analytics

## 📚 Related Docs
- Implementation: `FLIP_SCORE_FILTER_IMPLEMENTATION.md`
- Prompt: `FLIP_SCORE_FILTER_PROMPT.md`
- Flip Score Calc: `FLIP_SCORE_IMPLEMENTATION_SUMMARY.md`
- ESG Filter: `ESG_FILTER_IMPLEMENTATION.md`

---

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Date:** October 16, 2025  
**Time to Implement:** 30 minutes
