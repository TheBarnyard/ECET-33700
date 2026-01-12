# ECET 337 System Usage Guide

## ✅ What's AUTOMATED

### 1. **Navigation & Organization**
- **Scripts are ready to use** - Just run them:
  - `ecet337` - Interactive navigation menu
  - `matlab337` - MATLAB file manager
  - `ecethw`, `ecetlab`, `ecetlec` - Jump to folders instantly
  - `ecettrack`, `ecetref`, `ecethelp` - View documentation

- **File Discovery** - Scripts automatically:
  - Find all MATLAB files (.m)
  - Find all Multisim files (.ms14, .ms12)
  - Find lectures by keyword
  - Find labs by number
  - List files by category (RC/RL, filters, motors)

### 2. **Templates & Structure**
- **MATLAB script templates** are pre-built:
  - Basic analysis
  - Transfer function analysis
  - Bode plots
  - Step response
  - Filter design
  - Just run `matlab337` → option 5

### 3. **Backup System**
- **MATLAB backup** - Run `matlab337` → option 8
  - Creates timestamped backup automatically
  - Stores in `MATLAB_Backups/` folder

### 4. **Documentation**
- **All reference materials created:**
  - Complete assignment tracker (all 15 weeks)
  - Quick reference guide (formulas, tips)
  - Study schedules (all 3 exams + final)
  - Weekly workflow guide
  - Exam prep checklists

---

## 📝 What You NEED TO DO MANUALLY

### **Weekly Maintenance**

#### 1. **Update Assignment Tracker** (5-10 min/week)
**File:** `assignment-tracker.md`

**What to update:**
```markdown
### Week X - Status
- **Status:** ⬜ Not Started | ✅ In Progress | ✓ Complete

### Lab Report Tracking
| Lab # | Prelab | Performance | Report Score | Status |
|-------|--------|-------------|--------------|--------|
| 1     | ✓      | ✓           | 28/30        | A      |
```

**When:**
- After completing homework → Mark complete
- After lab → Mark prelab/performance complete
- After lab report graded → Record score
- End of week → Update status

#### 2. **Track Your Grades** (2-3 min per graded item)
**File:** `assignment-tracker.md` (Grade Breakdown section)

**Update:**
```markdown
| Component | Weight | Current | Notes |
|-----------|--------|---------|-------|
| Hour Tests (3) | 30% | 85% | Exam 1: 88%, Exam 2: 82% |
| Homework | 20% | 92% | All completed on time |
```

#### 3. **Add Personal Notes** (ongoing)
**File:** `assignment-tracker.md` (Notes Section at bottom)

**Use for:**
- Questions to ask in office hours
- Topics you found difficult
- Reminders for yourself
- Study group meeting notes

---

### **Before Each Exam**

#### 1. **Create Formula Sheet** (1-2 hours)
**Manual task** - The system provides content, you organize:

**Where to find content:**
- `quick-reference.md` - All formulas
- Your lecture notes
- Homework problems you struggled with

**What to do:**
1. Open blank document
2. Copy relevant formulas from quick-reference
3. Add your own worked examples
4. Organize clearly with headers
5. Print and bring to exam

#### 2. **Take Mock Exams** (1 hour each)
**Location:** `Mock Exams/` folder

**What to do:**
1. Set timer (1 hour for regular exams)
2. Take mock exam under test conditions
3. Grade yourself using solutions
4. Record score in study schedule
5. Review mistakes thoroughly

#### 3. **Update Study Progress** (5 min)
**File:** `study-schedule.md`

**Mark off completed items:**
```markdown
### Exam 1 - Week of Jan 26-30:
- [x] Review all lecture notes weeks 1-3
- [x] Redo homework problems
- [ ] Practice problems from textbook
- [x] Work through Lab 1-3 theory
- [x] Take Mock Exam 1 (timed)
```

---

### **Lab Work**

#### 1. **Complete Prelab** (30-60 min before each lab)
**Location:** Lab procedure PDFs in `Lab Exercises/`

**What to do:**
- Read entire lab procedure
- Answer prelab questions
- Calculate expected values
- Prepare data tables
- **Submit to instructor at lab start**

#### 2. **Write Lab Reports** (2-3 hours per report)
**Manual writing** - System provides templates/guidelines

**Resources:**
- `Lab Exercises/Lab Report Grading.docx`
- `Lab Exercises/Report Writing Guidelines.docx`
- `Lab Exercises/00c4-Sample Report-2026.pdf`

**What to do:**
1. Gather lab data and photos
2. Perform calculations
3. Create graphs
4. Write sections (Intro, Procedure, Results, Analysis, Conclusion)
5. Format professionally
6. Export to PDF
7. Submit via Brightspace by 8am deadline

#### 3. **Track Lab Report Exemption** (ongoing)
**File:** `assignment-tracker.md` (Lab Report Tracking table)

**Goal:** 3 consecutive A/B grades (24-30/30)

**Update after each report:**
```markdown
| Lab # | Report Score | Status |
|-------|--------------|--------|
| 1     | 28/30        | A ✓    |
| 2     | 26/30        | B ✓    |
| 3     | 29/30        | A ✓    | ← EXEMPTION ACHIEVED!
```

---

### **Homework**

#### 1. **Complete Homework on Variate** (1-2 hours/week)
**NOT automated** - You must do the work!

**Access:**
- Go to Brightspace
- Click homework link (goes to Variate)
- Complete problems
- Submit before deadline

**Tip:** Use `quick-reference.md` for formulas while working

#### 2. **MATLAB/Multisim Homework** (varies)
**Some homework requires simulations**

**Workflow:**
1. Use `matlab337` to find relevant example files
2. Copy to working directory
3. Modify for your specific problem
4. Run simulation
5. Export results (plots, data)
6. Submit PDF via Brightspace

---

### **Study & Practice**

#### 1. **Daily Review** (15-30 min/day)
**Your responsibility:**
- Review today's lecture notes
- Preview tomorrow's topics
- Work practice problems

**Resources in system:**
- `quick-reference.md` - Formula lookup
- `study-schedule.md` - What to study when
- Lecture files in `Lectures/`

#### 2. **MATLAB Practice** (30 min/week recommended)
**Use the templates:**
```bash
matlab337  # Launch helper
# → Option 5: Create new script from template
# → Practice with transfer functions, Bode plots, etc.
```

#### 3. **Form Study Group** (your social coordination)
**System helps with content, but you organize:**
- Find classmates
- Schedule meetings
- Share responsibilities
- Quiz each other
- Compare notes

---

### **File Management**

#### 1. **Backup Your Work** (weekly recommended)
**Partially automated:**

**Automated:**
```bash
matlab337  # → Option 8: Backup MATLAB work
```

**Manual (still needed):**
- Lab report drafts → Copy to cloud storage
- Your homework solutions → Save copies
- Personal notes → Backup regularly

**Remember syllabus requirement:**
> "Save file to three separate locations: USB drive, Purdue account, and cloud"

#### 2. **Organize New Materials** (as instructor releases)
**When instructor posts new files:**
1. Download from Brightspace
2. Move to appropriate folder:
   - Homework → `Homework/`
   - Lab procedures → `Lab Exercises/`
   - Lecture slides → `Lectures/`
   - Textbook chapters → `Textbook/`

---

## 🔄 Weekly Workflow Summary

### **What System Does:**
✅ Provides navigation to all materials
✅ Organizes existing files
✅ Gives templates for MATLAB scripts
✅ Lists all assignments (pre-populated)
✅ Provides formula references
✅ Gives study timeline templates

### **What You Do:**
📝 Complete homework on Variate
📝 Do prelab exercises
📝 Attend class and take quizzes
📝 Perform lab work
📝 Write lab reports
📝 Update trackers with your progress
📝 Study using the guides
📝 Take practice exams
📝 Make formula sheets
📝 Back up your work files

---

## 📊 Time Estimates

### **Using the System:**
- Navigate to files: **Instant** (with aliases)
- Find MATLAB examples: **30 seconds**
- Check assignment tracker: **1 minute**
- Look up formula: **30 seconds**
- Create MATLAB template: **2 minutes**

### **Your Work:**
- Homework: **1-2 hours/week**
- Prelab: **30-60 min/week**
- Lab report: **2-3 hours/week** (until exemption!)
- Study/review: **1-2 hours/week**
- Exam prep: **10-15 hours/exam**

---

## 🎯 Quick Start Checklist

### **One-Time Setup** (Already Done!)
- [x] Navigation scripts created
- [x] MATLAB helper created
- [x] Assignment tracker created
- [x] Reference guides created
- [x] Aliases added to .bashrc

### **Your First Steps** (Do Now!)
- [ ] Open and read `README.md`
- [ ] Review `assignment-tracker.md` Week 1
- [ ] Check syllabus in `Course Info/`
- [ ] Verify you have required parts
- [ ] Install MATLAB and Multisim
- [ ] Try running `ecet337` command

### **Before Class Starts** (Jan 12)
- [ ] Print syllabus or have it accessible
- [ ] Check Brightspace access
- [ ] Prepare for Week 1 quiz (review analog basics)
- [ ] Have calculator ready

---

## 💡 Pro Tips

### **Maximize Automation:**
1. **Use aliases constantly** - faster than clicking
2. **Use MATLAB templates** - don't start from scratch
3. **Reference quick-guide** - faster than searching textbook
4. **Check tracker daily** - stay ahead of deadlines

### **What NOT to Expect Automation For:**
- ❌ Doing homework problems (you must learn!)
- ❌ Writing lab reports (your analysis required)
- ❌ Studying for exams (active learning needed)
- ❌ Attending class (in-person quiz!)
- ❌ Understanding concepts (engage with material)

### **Best Practices:**
1. **Update tracker Friday afternoon** - Review week's completion
2. **Sunday evening** - Preview next week in tracker
3. **After each grade** - Update grade table
4. **Before each exam** - Check study schedule

---

## 🆘 Troubleshooting

### **"Aliases don't work"**
**Solution:**
```bash
source ~/.bashrc
# Or restart your terminal
```

### **"Can't find a file"**
**Solution:**
```bash
ecet337  # Use navigation menu
# Or
ecetfindpdf  # Search for PDFs
```

### **"Forgot what to do this week"**
**Solution:**
```bash
ecettrack  # View assignment tracker
```

### **"Need a formula quickly"**
**Solution:**
```bash
ecetref  # View quick reference
# Or search: grep -i "laplace" /path/to/quick-reference.md
```

---

## 📈 Success Metrics

### **Track Your Efficiency:**
- **Time to find materials:** Should be < 30 seconds with aliases
- **Time to start MATLAB work:** Should be < 2 minutes with templates
- **Lab report exemption:** Target by Week 7
- **Homework completion:** Every assignment on time
- **Grade trend:** Monitor in tracker

### **Adjust as Needed:**
- Not using a tool? Figure out why or remove it
- Tool saving time? Use it more!
- Tracker getting stale? Set reminder to update
- System not helping? Customize it!

---

## 🎓 Remember

**The system ORGANIZES and GUIDES.**
**You still need to DO THE WORK.**

But now you can:
- ✅ Find everything instantly
- ✅ Know what's due when
- ✅ Have formulas at your fingertips
- ✅ Follow proven study plans
- ✅ Track your progress clearly

**The system removes friction so you can focus on LEARNING.**

---

*Questions? Add them to the Notes section in assignment-tracker.md!*
*Working well? Great! Keep using it consistently.*
*Not working? Customize it to fit your style!*

**Last Updated:** 2026-01-11
