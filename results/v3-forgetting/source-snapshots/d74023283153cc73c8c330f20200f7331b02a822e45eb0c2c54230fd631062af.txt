# Registered V3 change-triggered forgetting experiment

Protocol `v3-forgetting-20260909-v1`. The operator authorized a running-average
learner that discards old observations on the fixed detector's alarms, tested
against SGD, fixed windows, ADWIN, perfect-time and random-reset controls.
Register before study data. Preserve all earlier protocols, scientific sources,
evidence and seven CI workflows. No dependency or agent/default change.

## Hypothesis and learner semantics

The previous bounded Adam burst policy lost to SGD even with privileged timing.
This experiment tests a different use of the signal: choosing which observations
to retain. An advantage is a hypothesis, not a consequence of detecting changes.

Use EXACT frozen fixed-reference gates from `v3_burst.reference_gates`, threshold
0.4690234346011377, strict >, first possible nonzero at zero-based t146. No new
calibration, detector search or threshold adjustment. Reset scheduling reuses
`pulse_schedule(q, duration=1, detected=True)`: initially armed; one request on
an alarm; 16 consecutive quiet observations AFTER it before rearming. No repeated
resets during a sustained high signal. The reference is independent of learning.

**forget candidate:** output the previous retained-window mean before seeing y_t
(initial prediction0). Append y_t; evict oldest observations beyond cap W. On a
reset request keep only the newest K observations of the CURRENT retained window,
including y_t. Never resurrect discarded observations, use future samples or
backdate to a true boundary. Average all retained observations with equal weight.
The new estimate is available for prediction at t+1. Window growth between resets
is automatic up to W. No momentum, Adam, burst gain or additional blend parameter.

**window:** identical growing-then-capped arithmetic mean with no alarm resets.
**sgd:** unchanged plain SGD, w_next=w-lr*(w-y). This is an exponentially weighted
tracker, so its memory is not assigned a literal finite sample count.
**noreset_matched:** window with the selected candidate's EXACT W. No separate
search; it measures the benefit of resetting at a matched maximum history.

**oracle:** identical forgetting learner, independently tuned with the same budget.
Evaluator supplies requests at true abrupt target changes ONLY, after the current
observation arrives and its pre-update prediction has been scored. It receives
no true target value, noise level or future samples, and does not respond to drift
or noise transitions. It keeps the newest K samples normally, even if K>1 includes
old-regime samples. This is perfect trigger timing, not perfect segmentation or
a mathematical performance upper bound. **oracle_matched** uses candidate K/W
exactly. Both are privileged diagnostics and cannot authorize candidate advancement.

**random:** candidate K/W with observation-independent Bernoulli reset opportunities
from t146. After each request suppress opportunities for 16 updates. Uniforms use
PCG64 SeedSequence([study_seed,86000+fixture_ordinal,coordinate]), generated per
coordinate to preserve prefix/width invariance. Freeze p from SELECTED candidate
tuning reset count N /S, S=(6000-146)*9*8; f=N/S, p=f/(1-16*f). Validate finite
0<=p<=1; do not clip or match to confirmation. This is expected pooled-frequency
matching, not equal realized counts, forgotten samples or condition-specific age.
Use the duration1 external pulse schedule. Every actual request and discard is
reported. The matched oracle, random and noreset arms receive no extra search.

## ADWIN baseline and scope

Use an independent paper-based ADWIN2 implementation: ordered power-of-two buckets,
at most five per size, merging the two oldest equal-size buckets on overflow.
Keep counts, sums and centered sums of squares. At each selected clock tick, test
bucket boundaries with both subwindows >=5; on a violation remove the oldest
bucket and repeat until no tested cut violates. Predict the prior window mean.

The practical Eq.(3.1) threshold is sqrt(2*r*variance*L)+(2/3)*r*L, with
r=1/n0+1/n1, L=ln(2*ln(n)/delta), population variance of the retained window,
and strict mean-difference > threshold. Check from n>=10. No extra reset of the
surviving window, weight clipping or finite history cap. Centered-variance merge
arithmetic avoids subtracting large raw second moments; clamp roundoff below0.

Source: Bifet and Gavalda, [ADWIN paper, §§3.2–3.3](https://www.cs.upc.edu/~Gavalda/papers/adwin06.pdf).
These Gaussian fixtures violate the paper's bounded-input premise. Apply the
stated practical rule to raw observations identically across policies; claim no
bounded-data false-alarm guarantee and no parity with a particular library release.
A separate slow implementation using explicit bucket contents must agree before
study data. This is established prior art, not a new proposed detector.

## Fixed finite menus and objective

Five searched families, each **12 configurations ×8 paired seeds ×all five
fixtures**. Order below breaks exact objective ties.

- forget and oracle: K in [1,4,16], then W in [32,128,512,6000], Cartesian product.
- window: W in [1,2,4,8,16,32,64,128,256,512,1024,6000].
- sgd: lr in [.0001,.0004,.001,.004,.008,.016,.035743040182210514,
  .064,.128,.256,.512,1], unchanged from the burst comparator menu.
- adwin: delta in [.0001,.001,.01,.1], then clock in [1,8,32], Cartesian product;
  five buckets per size, minimum subwindow5, grace10 remain fixed.

These are finite menus, not global optimization. Report endpoint selections;
no automatic extension or post-result boundary veto. All five receive equal
configuration/seed/fixture budgets, not identical CPU costs. Cache the fixed
causal q only to avoid redundant computation. Record measured execution times.

Reuse the EXACT nine-coordinate fixtures/metrics and selection objective from
the burst registration: 6000 observations, burn1000; ordered core, noise_jump,
drift, exactly_quiet, mixed. P is the equal mean post-200 MSE over core quiet/noisy
switching and both mixed coordinates. R comprises the same 14 cells: core quiet/
noisy excess and quiet/noisy switching post-MSE; three scalar-extra excess errors;
noise-increase/noise-decrease/drift windows; mixed post/stable errors per coordinate.
Select minimum seed-mean (P+mean(R))/2 for every searched family.

A configuration with any non-finite tuning trajectory/metric is ineligible, with
its failure retained. Finish all480 rows. If any family lacks a complete finite
configuration, close tuning_inconclusive and forbid confirmation. Otherwise
freeze all selected configurations, random p, source identity and complete tuning
evidence in a committed manifest BEFORE independent confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | ---: |
| Development only | 80000–80007 | unit/synthetic only |
| Tuning | 81000–81007 | 5×12×8 =480 |
| Independent confirmation | 83000–83031 | 8×32 =256 |
| Bootstrap RNG only | 85000 | 10000 whole-seed resamples |

All seed ranges are fresh, including unused reservations of previous studies.
Do not reopen old studies or substitute seeds. Run all256 confirmation rows if
tuning permits: forget, oracle, window, sgd, adwin, oracle_matched, random,
noreset_matched. Do not stop measuring candidate performance based on oracle
outcomes or alarm diagnostics. The perfect-time diagnostic provides interpretation,
not a route around the fixed full-comparison gate.

Candidate must improve P by >=10% over EACH of window, sgd, adwin, random and
noreset_matched, with paired95% upper candidate-minus-control delta<0. For each
of14 R cells against each control require paired upper delta<=max(.002,.1*control
mean). All **75 comparisons** must pass for learning_positive; otherwise
learning_negative. Non-finite required trajectories fail; missing/malformed evidence
remains incomplete. Controls cannot be dropped because they are strong or fail
other diagnostics. Each oracle is separately tested against window,sgd,adwin with
the same45 criteria (oracle_pass/oracle_negative); neither can repair a candidate
failure. Every final disposition closes this registration with no automatic next
experiment, detector change, default change or agent integration. A positive
would justify only a separately authorized broader supervised benchmark.

Report the fixed detector's SAME12 raw diagnostic cells on candidate confirmation
seeds: eight target direction/condition hit rates>=80% within100; quiet/noisy
stationary block rates<=5%; each noise-transition alarm rate<=5%. They do not veto
or establish learning performance. Also report actual reset hits/delays. Oracle
and detector scheduling differ in false/repeated requests as well as delay; do not
attribute every performance difference to one cause. Failed perfect-time results
limit this finite learner/menu, not all forms of forgetting.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by fixture;
per-coordinate reset/shrink indices and event hit/latency; retained-window width
summaries, discarded observation counts and width at each reset; candidate raw-q
and event prediction-error/recovery diagnostics. Distinguish routine cap evictions
from event flags: fixed windows evict but never issue reset events. SGD has no
literal window. ADWIN flags shrinkage, not the external detector's resets. Always
expose finite-seed counts and expected versus realized random activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific sources;
(3) tune all480/freeze manifest; (4) confirm all256; (5) reproduce every reached row,
manifest, selection and report; (6) publish a draft codex/** PR, monitor all eight
workflows at exact HEAD, mark ready and merge when green and reviews resolved.
Use separate v3_forgetting runtime/policy/study/report/check modules plus a small
ADWIN module and an eighth workflow. Reuse frozen functions without monkeypatching
module globals. Preserve all earlier files except README/PLAN/V3 status pointers.

Before observations verify direct sliced-mean parity (including K=1, W=1, startup,
repeated requests, cap eviction and no resurrection); noreset/window parity and
SGD parity; independent explicit-content ADWIN bucket merges, shrinkage, widths,
variance and estimates; strict threshold/rearm/cooldown; prefix and coordinate
causality, no oracle access in deployable arms, independent random RNG/frequency;
all12 menus, common objective, finite/tie selection; all75 vetoes, all45 oracle
cells, diagnostics/oracle non-authority; missing/invalid/non-finite records,
changed sources, uncommitted manifests and forbidden confirmation. Snapshot all
transitive local code, report/check sources, applicable protocols and pinned
requirements. No source change after observations except a diagnosed, explicitly
reported instrument defect. Registration SHA is immutable.

Reproduce all736 reached rows if eligible, not just aggregates, at rtol1e-11 /
atol1e-13; only execution timing and regenerated input digests are exempt. Old
burst evidence must also reproduce unchanged, and all seven prior workflows
remain intact. Statistical intervals are descriptive; finite menus, small synthetic
fixtures and observed zeros cannot establish population guarantees or general
neural-memory utility. No new dependencies are needed.
