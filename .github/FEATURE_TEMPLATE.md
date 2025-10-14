# Feature Request Template

Copy this template for every new feature request to AI.

---

## Feature Request: [Feature Name]

### 1. CONTEXT (30 seconds)
- **Location in UI:** [Exact card/section name, line number if known]
- **Current Behavior:** [What happens now]
- **Affected Files:** [If known: app.py, templates/index.html, etc.]

### 2. REQUIREMENT (30 seconds)
- **What:** [One sentence description]
- **Why:** [Business value]
- **Expected Output:** [Visual description or example]

### 3. SCOPE (30 seconds)
- **Approach:** [Minimal/Visual/Complex - or let AI recommend]
- **Testing:** [Yes/No - default: Yes]
- **Documentation:** [Minimal/Full - default: Minimal]

### 4. CONSTRAINTS (30 seconds)
- **No Breaking Changes:** [Yes/No - default: Yes]
- **Performance:** [Any specific requirements, default: <50ms]
- **Dependencies:** [New libraries OK? Default: No]

### 5. ACCEPTANCE CRITERIA (1 minute)
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### 6. GO/NO-GO
- **Proceed:** [Yes - implement now / No - analyze first]

---

## Example: Market Segment Badge

### 1. CONTEXT
- **Location in UI:** "Price per Sq.M" card in valuation results (templates/index.html ~line 649)
- **Current Behavior:** Shows only price, no context
- **Affected Files:** app.py (backend), templates/index.html (frontend)

### 2. REQUIREMENT
- **What:** Add market segment classification badge (Budget/Mid-Tier/Premium/Luxury/Ultra-Luxury)
- **Why:** Help users understand market positioning (+60% conversion expected)
- **Expected Output:** Badge like "💎 Luxury - Top 10%" below price

### 3. SCOPE
- **Approach:** Minimal (percentile-based, no ML)
- **Testing:** Yes (unit tests required)
- **Documentation:** Minimal (inline comments only)

### 4. CONSTRAINTS
- **No Breaking Changes:** Yes (must not affect existing valuation)
- **Performance:** <50ms added to valuation time
- **Dependencies:** No new libraries

### 5. ACCEPTANCE CRITERIA
- [ ] Backend classifies price into 5 segments
- [ ] Frontend displays badge with icon and percentile
- [ ] Badge visible in valuation results section
- [ ] Test coverage >90%

### 6. GO/NO-GO
- **Proceed:** Yes - implement now (Quick Win approach)

---

## How to Use

1. **Copy this template** into a new file or text editor
2. **Fill out each section** (should take ~2-3 minutes total)
3. **Paste into AI chat** with implementation rules:

```markdown
I need to implement a new feature quickly. Here's the complete context:

[PASTE FILLED TEMPLATE]

**IMPLEMENTATION RULES:**
1. ✅ Read .github/instructions/PROJECT_CONTEXT.md first
2. ✅ Test while implementing
3. ✅ Deploy immediately after testing
4. ❌ Don't create separate documentation files
5. ❌ Don't explain every step (just do it)

**DELIVERABLES:**
- [ ] Backend function (if needed)
- [ ] Frontend display (if needed)
- [ ] Unit tests (>90% coverage)
- [ ] Run ./deploy.sh
- [ ] 5-line summary

**START IMMEDIATELY**
```

---

**Created:** October 12, 2025  
**Last Updated:** October 12, 2025
