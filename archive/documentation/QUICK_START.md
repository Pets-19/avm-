# 🚀 Quick Start - Your First Rapid Feature

**Time to implement a feature:** 15-20 minutes (vs 60 minutes before)

---

## Step 1: Fill the Template (2 minutes)

Copy this template and fill it out for your next feature:

```markdown
## Feature Request: [YOUR FEATURE NAME]

### 1. CONTEXT
- **Location in UI:** [Where in the UI? e.g., "New card after Price per Sq.M"]
- **Current Behavior:** [What happens now?]
- **Affected Files:** [app.py, templates/index.html, etc.]

### 2. REQUIREMENT
- **What:** [One sentence - what are you building?]
- **Why:** [Business value - why does this matter?]
- **Expected Output:** [What should user see? e.g., "Badge showing 'Modern Property'"]

### 3. SCOPE
- **Approach:** Minimal [unless you want AI to recommend options]
- **Testing:** Yes
- **Documentation:** Minimal

### 4. CONSTRAINTS
- **No Breaking Changes:** Yes
- **Performance:** <50ms
- **Dependencies:** No new libraries

### 5. ACCEPTANCE CRITERIA
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### 6. GO/NO-GO
- **Proceed:** Yes - implement now
```

---

## Step 2: Submit to AI (0 minutes)

Copy and paste this EXACT prompt to AI:

```markdown
I need to implement a new feature quickly. Here's the complete context:

[PASTE YOUR FILLED TEMPLATE FROM STEP 1 HERE]

**IMPLEMENTATION RULES:**
1. ✅ Read .github/instructions/PROJECT_CONTEXT.md first (don't explore)
2. ✅ Create minimal documentation (inline comments only)
3. ✅ Test while implementing (don't wait for end)
4. ✅ Deploy immediately after testing with ./deploy.sh
5. ❌ Don't create separate documentation files
6. ❌ Don't explain every step (just do it)
7. ❌ Don't ask for confirmation (GO approved above)

**DELIVERABLES:**
- [ ] Backend function (if needed)
- [ ] Frontend display (if needed)
- [ ] Unit tests (>90% coverage)
- [ ] Run ./deploy.sh
- [ ] 5-line summary of what changed

**START IMMEDIATELY** - I'll interrupt if needed.
```

---

## Step 3: AI Implements (8-15 minutes)

AI will:
1. Read PROJECT_CONTEXT.md (your project info)
2. Implement backend function
3. Add frontend display
4. Write unit tests
5. Run tests
6. Deploy with `./deploy.sh`
7. Give you 5-line summary

**You do nothing during this phase!**

---

## Step 4: Verify (2-3 minutes)

Once AI says "Done":

1. **Hard refresh browser** (Ctrl+Shift+R)
2. **Test the feature** manually
3. **Check for errors:**
   - Browser console (F12)
   - Flask logs: `tail -20 flask.log`
4. **Verify tests passed:**
   ```bash
   ./test_runner.sh
   ```

---

## Step 5: Log Results (1 minute)

Update `FEATURE_LOG.md`:

```bash
# Add line to the table:
| 2025-10-XX | [Feature Name] | 15 min | XX min | XX/XX | XX% | ✅ | 0 | [Notes] |
```

---

## 🎯 Real Example

### Example Template (filled out in 2 min):

```markdown
## Feature Request: Property Age Badge

### 1. CONTEXT
- **Location in UI:** New card in valuation details, after Price per Sq.M card
- **Current Behavior:** No age information shown
- **Affected Files:** app.py (backend), templates/index.html (frontend)

### 2. REQUIREMENT
- **What:** Show property age category (New/Modern/Established/Legacy)
- **Why:** Users want to know property age for maintenance cost estimates
- **Expected Output:** Badge like "🏗️ Modern (8 years old)"

### 3. SCOPE
- **Approach:** Minimal (use transaction date as proxy)
- **Testing:** Yes
- **Documentation:** Minimal

### 4. CONSTRAINTS
- **No Breaking Changes:** Yes
- **Performance:** <50ms
- **Dependencies:** No new libraries

### 5. ACCEPTANCE CRITERIA
- [ ] Calculate property age from earliest transaction date
- [ ] Classify into 4 categories: New (<5yr), Modern (5-15yr), Established (15-30yr), Legacy (30+yr)
- [ ] Display badge with appropriate icon
- [ ] Test coverage >90%

### 6. GO/NO-GO
- **Proceed:** Yes - implement now
```

**Total Time:** 15 minutes (AI implementation time)

---

## 💡 Pro Tips

### Tip 1: Be Specific in Template
❌ Bad: "Add age feature"
✅ Good: "Show property age category badge in valuation details section"

### Tip 2: Clear Acceptance Criteria
❌ Bad: "Should work"
✅ Good: "Classify into 4 categories with icons"

### Tip 3: Use "START IMMEDIATELY"
This prevents AI from over-analyzing

### Tip 4: Don't Interrupt Unless Error
Let AI complete the full implementation

### Tip 5: Hard Refresh Always
After deployment: Ctrl+Shift+R in browser

---

## 🐛 Troubleshooting

### "Feature not showing in UI"
```bash
# 1. Hard refresh browser
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# 2. Check Flask logs
tail -20 flask.log

# 3. Check browser console
F12 → Console tab
```

### "Tests failing"
```bash
# Run tests with verbose output
./test_runner.sh

# Check specific test
pytest test_[feature].py -v
```

### "Server not starting"
```bash
# Check Flask logs
tail -50 flask.log

# Check if port busy
lsof -i :5000

# Kill existing process
pkill -f "python.*app.py"

# Restart
./deploy.sh
```

---

## 📊 Track Your Progress

After each feature, ask yourself:

1. **How long did it take?** (Target: <20 min)
2. **Did tests pass first time?** (Target: Yes)
3. **Any bugs found?** (Target: 0)
4. **What slowed me down?** (Improve next time)

Update `FEATURE_LOG.md` to track improvement over time.

---

## 🎓 Learning Curve

### Week 1: Learning Phase
- Time: 30-40 minutes per feature
- Focus: Understanding the process
- Goal: Complete 3-5 features

### Week 2: Improvement Phase
- Time: 20-30 minutes per feature
- Focus: Refining templates
- Goal: Complete 8-10 features

### Week 3: Mastery Phase
- Time: 15-20 minutes per feature
- Focus: Batch similar features
- Goal: Complete 10-15 features

### Week 4: Teaching Phase
- Time: <15 minutes per feature
- Focus: Teaching others
- Goal: Document your learnings

---

## 📚 Resources

### Read These (in order):
1. `RAPID_FEATURE_DEVELOPMENT_GUIDE.md` - Complete guide
2. `.github/instructions/PROJECT_CONTEXT.md` - Your project context
3. `.github/FEATURE_TEMPLATE.md` - Template reference
4. `.github/FEATURE_CHECKLIST.md` - Quality checklist

### Use These:
- `./test_runner.sh` - Run all tests
- `./deploy.sh` - Deploy changes
- `FEATURE_LOG.md` - Track progress

---

## 🚀 Ready?

**Your challenge:** Implement your next feature in <20 minutes using this process.

1. Fill template (2 min)
2. Submit to AI with rules (0 min)
3. Let AI implement (8-15 min)
4. Verify (2-3 min)
5. Log results (1 min)

**Total: 15-20 minutes**

Good luck! 🎯

---

**Created:** October 12, 2025  
**Last Updated:** October 12, 2025  
**Next:** Try it with a real feature!
