# ECET 337 Quick Reference Guide

## Course Overview
**Continuous Systems Analysis and Design**
- Time domain analysis (differential equations)
- Frequency domain analysis (Laplace transforms)
- Active filter design (1st-6th order)
- Closed-loop motor control (PI controllers)

---

## Key Formulas & Concepts

### Time Domain Analysis

#### RC Circuit
- **Time Constant:** τ = RC
- **Charging:** v(t) = V_final(1 - e^(-t/τ))
- **Discharging:** v(t) = V_initial × e^(-t/τ)
- **Differential Equation:** RC(dv/dt) + v = V_in

#### RL Circuit
- **Time Constant:** τ = L/R
- **Current Rise:** i(t) = I_final(1 - e^(-t/τ))
- **Current Fall:** i(t) = I_initial × e^(-t/τ)
- **Differential Equation:** L(di/dt) + Ri = V_in

---

### Laplace Transform Pairs (Common)

| Time Domain f(t) | Laplace F(s) |
|------------------|--------------|
| δ(t) - impulse | 1 |
| u(t) - step | 1/s |
| t | 1/s² |
| e^(-at) | 1/(s+a) |
| te^(-at) | 1/(s+a)² |
| sin(ωt) | ω/(s²+ω²) |
| cos(ωt) | s/(s²+ω²) |
| e^(-at)sin(ωt) | ω/((s+a)²+ω²) |
| e^(-at)cos(ωt) | (s+a)/((s+a)²+ω²) |

#### Laplace Transform Properties
- **Linearity:** L{af(t) + bg(t)} = aF(s) + bG(s)
- **Differentiation:** L{df/dt} = sF(s) - f(0)
- **Integration:** L{∫f(t)dt} = F(s)/s
- **Time Shift:** L{f(t-a)u(t-a)} = e^(-as)F(s)
- **Frequency Shift:** L{e^(-at)f(t)} = F(s+a)
- **Final Value:** lim(t→∞) f(t) = lim(s→0) sF(s)
- **Initial Value:** lim(t→0) f(t) = lim(s→∞) sF(s)

---

### Second Order Systems (RLC)

#### Standard Form
**Transfer Function:** H(s) = ω_n²/(s² + 2ζω_n×s + ω_n²)

Where:
- **ω_n** = natural frequency (rad/s)
- **ζ** = damping ratio (dimensionless)

#### Damping Conditions
- **ζ > 1:** Over-damped (slow, no overshoot)
- **ζ = 1:** Critically damped (fastest without overshoot)
- **0 < ζ < 1:** Under-damped (oscillatory, overshoot)
- **ζ = 0:** Undamped (continuous oscillation)

#### Series RLC Circuit
- **Natural Frequency:** ω_n = 1/√(LC)
- **Damping Ratio:** ζ = R/(2√(L/C)) = R/(2ω_n×L)
- **Quality Factor:** Q = 1/(2ζ) = ω_n×L/R = 1/(ω_n×RC)
- **Resonant Frequency:** f_r = ω_n/(2π)

#### Time Domain Parameters
- **Rise Time:** t_r ≈ 1.8/ω_n (for ζ < 1)
- **Peak Time:** t_p = π/(ω_n√(1-ζ²))
- **Settling Time (2%):** t_s ≈ 4/(ζω_n)
- **Percent Overshoot:** PO% = 100 × e^(-πζ/√(1-ζ²))

---

### Filter Design

#### Filter Types
1. **Butterworth:** Maximally flat passband, -20n dB/decade rolloff
2. **Chebyshev:** Ripple in passband, steeper rolloff
3. **Bessel:** Maximally flat group delay (linear phase)

#### Common Configurations
- **Low Pass (LP):** Passes low frequencies, blocks high
- **High Pass (HP):** Passes high frequencies, blocks low
- **Band Pass (BP):** Passes middle frequencies
- **Band Stop (Notch):** Blocks middle frequencies

#### Sallen-Key Filter (2nd Order LP)
- **Transfer Function:** H(s) = K×ω_c²/(s² + (ω_c/Q)s + ω_c²)
- **Cutoff Frequency:** f_c = 1/(2π√(R₁R₂C₁C₂))
- **Quality Factor:** Q = √(R₁R₂C₁C₂)/(C₂(R₁+R₂))

#### Bode Plot
- **Magnitude:** 20log₁₀|H(jω)| (dB)
- **Phase:** ∠H(jω) (degrees)
- **Corner Frequency:** Where magnitude drops 3dB
- **Slope:** n poles = -20n dB/decade, n zeros = +20n dB/decade

---

### Motor Control

#### DC Motor Model
- **Transfer Function (speed):** Ω(s)/V(s) = K_m/(τ_m×s + 1)
  - K_m = motor gain (rad/s/V)
  - τ_m = motor time constant (s)

#### Closed-Loop Control

**Proportional (P) Controller:**
- **Control Law:** u(t) = K_p × e(t)
- **Transfer Function:** C(s) = K_p
- **Limitations:** Steady-state error

**Proportional-Integral (PI) Controller:**
- **Control Law:** u(t) = K_p × e(t) + K_i × ∫e(t)dt
- **Transfer Function:** C(s) = K_p + K_i/s = (K_p×s + K_i)/s
- **Benefits:** Eliminates steady-state error
- **Tuning:** Increase K_p for faster response, increase K_i to reduce error

**Closed-Loop Transfer Function:**
- T(s) = (C(s)×G(s))/(1 + C(s)×G(s))
  - C(s) = controller
  - G(s) = plant (motor)

---

## MATLAB Quick Commands

### Basic Analysis
```matlab
% Define transfer function
num = [1];           % Numerator coefficients
den = [1 2 1];       % Denominator coefficients
H = tf(num, den);    % Create transfer function

% Step response
step(H);             % Plot step response
stepinfo(H);         % Get step response parameters

% Frequency response
bode(H);             % Bode plot
margin(H);           % Gain/phase margins
```

### Laplace Analysis
```matlab
% Symbolic Laplace
syms t s
f = exp(-2*t);
F = laplace(f, t, s);  % Laplace transform
f_inv = ilaplace(F, s, t);  % Inverse Laplace

% Partial fraction expansion
[r, p, k] = residue(num, den);
```

### Filter Design
```matlab
% Butterworth filter
[b, a] = butter(n, Wn, 'low');  % n=order, Wn=normalized cutoff
H = tf(b, a);

% Frequency response
[mag, phase, w] = bode(H);
```

### Root Locus & Pole Placement
```matlab
rlocus(H);           % Root locus plot
pole(H);             % Find poles
zero(H);             % Find zeros
```

---

## Multisim Quick Tips

### AC Analysis
1. Place AC voltage source
2. Analysis → AC Analysis
3. Set frequency sweep (decade/octave)
4. Add output variables
5. Run → View Bode plot

### Transient Analysis
1. Place voltage/current sources
2. Analysis → Transient Analysis
3. Set end time, max time step
4. Add output variables
5. Run → View waveforms

### Component Values
- **Standard Values:** Use E12/E24 series
- **Tolerances:** 5% typical for resistors
- **Op Amp Models:** TL081, LM741, TL084

---

## Lab Report Format

### Required Sections
1. **Title Page:** Lab name, date, your name, section
2. **Introduction:** Objectives, theory summary
3. **Procedure:** Brief summary (not step-by-step)
4. **Results:** Data tables, graphs, observations
5. **Analysis:** Calculations, comparisons
6. **Conclusion:** Summary of findings, learning outcomes
7. **References:** Textbook, datasheets, etc.

### Formatting Guidelines
- Professional appearance
- Clear figures with captions
- Labeled axes on all graphs
- Units on all numerical values
- Proper significant figures (3-4 typical)

### Grading Criteria (30 points total)
- Technical content: ~20 points
- Presentation/format: ~10 points
- **A/B Grade: 24-30 points** (needed for exemption)

---

## Exam Preparation

### Formula Sheet Strategy
**Exam 1-3:** 1 page front/back
**Final Exam:** 2 pages front/back

**Include:**
- Key formulas (time constants, Laplace pairs)
- Transfer functions
- Step response parameters
- Your worked examples
- **DON'T** just copy - understand!

### Common Exam Topics

**Exam 1:** RC/RL circuits, differential equations, time domain
**Exam 2:** Laplace transforms, RLC circuits, 2nd order response
**Exam 3:** Filters, Bode plots, filter design

### Study Checklist
- [ ] Homework problems (redo without notes)
- [ ] Mock exams (timed practice)
- [ ] Lecture examples
- [ ] Lab theory sections
- [ ] Practice MATLAB/Multisim

---

## Common Mistakes to Avoid

### Analysis Errors
- ❌ Forgetting initial conditions in Laplace
- ❌ Wrong units (rad/s vs Hz)
- ❌ Sign errors in differential equations
- ❌ Incorrect partial fraction expansion
- ❌ Mixing time and frequency domain

### Lab Errors
- ❌ Not completing prelab (delays start)
- ❌ Incorrect component values
- ❌ Poor circuit construction (loose connections)
- ❌ Not measuring actual component values
- ❌ Forgetting to save scope screenshots

### Report Errors
- ❌ Missing units
- ❌ Unlabeled graphs
- ❌ No error analysis
- ❌ Copying text without citation
- ❌ Late submission (50% penalty!)

---

## Calculator Tips (TI-Nspire CX CAS)

### Essential Functions
- Symbolic solve: solve(equation, variable)
- Laplace: laplace(expression, var, s)
- Inverse Laplace: ilaplace(expression, s, t)
- Partial fractions: expand(expression, partfrac)
- Complex numbers: Use i or ∠ for polar

### Graphing
- Function plot for Bode magnitude/phase
- Parametric for root locus
- Store functions for repeated use

---

## Resources

### Course Materials
- **Brightspace:** All lectures, homework, grades
- **Variate:** Online homework system
- **Textbook:** PDF chapters in Textbook folder
- **Office Hours:** See Brightspace (Prof. Jacob, TA Diana)

### External Resources
- MATLAB Documentation: mathworks.com
- Multisim Help: within software (F1)
- TI-Nspire Manual: education.ti.com
- Circuit analysis: All About Circuits, Khan Academy

### Emergency Contacts
- Prof. Jacob: jacobm@purdue.edu, 49-47490
- TA Diana: narvaez@purdue.edu
- ECET Department: Check website for lab hours

---

## Weekly Workflow

### Monday (Lecture Day)
1. Attend class, take quiz (first 5 min!)
2. Take detailed notes
3. Start homework (Variate)

### Tuesday
1. Complete homework
2. Review lecture notes
3. Start prelab for this week

### Wednesday (Lecture + Lab)
1. Attend lecture, take quiz
2. Complete prelab BEFORE lab
3. Attend lab, complete performance

### Thursday/Friday
1. Write lab report (if Wed lab)
2. Review week's material
3. Start next week's reading

### Weekend
1. Submit lab report (Monday 8am)
2. Study for upcoming exams
3. Work on filter project (when applicable)

---

*This reference guide should be used alongside course materials. Always verify formulas and procedures with official sources.*

**Last Updated:** 2026-01-11
