# Registered V3 oracle-schedule retention experiment

Protocol `v3-retention-20260909-v1`. The operator authorized a retention-mechanism
test with true abrupt-target times granted for free, no detector arm, a fixed
finite fallback menu, equal small tuning budgets, fresh confirmation, and
adaptation plus retention criteria. Register before study observations. Preserve
all earlier protocols, scientific sources, evidence and nine CI workflows. No
dependency or agent/default change.

## Hypothesis and why this follows discovery

The bounded-burst study showed perfect trigger timing does not buy adaptation in
that controller family (tuned oracle primary 0.146911 vs SGD 0.119910). The
change-triggered forgetting and interference-as-discovery studies showed the
other shape: privileged scheduling buys large primary wins (forgetting tuned
oracle 0.034957 vs SGD 0.116201; discovery tuned oracle 0.047243 vs SGD
0.114924) but no tested single-memory policy keeps ADWIN's stable-noise
accuracy. No single (K, W, schedule) beats both specialists.

This experiment grants the schedule and varies only what is kept after a
change: a fast post-change window plus an ADWIN2 accumulator behind an
oracle-gated fallback. An advantage is a hypothesis, not a consequence of being
given true times.

Falsifier, stated in advance: a retention mechanism that cannot hold the
stable-noise cells against ADWIN while preserving its primary win over the fast
trackers has not solved the tradeoff — even with perfect timing. The registered
veto cells of interest are the mixed-fixture stable_mse cells against ADWIN,
where changes and stable segments coexist; any veto in the full gate closes
negative regardless.

In purely stationary fixtures the oracle schedule never fires, so the candidate
reduces to ADWIN2 exactly and passes those stable cells by construction. That
is not a discovery and must not be reported as one. Because of that reduction,
this design cannot fail for an uninteresting reason, and both outcomes are
informative: a pass means the barrier was trigger quality all along and
contradicts the narrower claim carried forward from burst, forgetting and
discovery; a failure means the adaptation/stability tradeoff is real even when
the two specialists are composed with perfect timing.

Re-searching (K, W) alone is explicitly out of scope: the independently tuned
forgetting oracle already covered that menu at K=1, W=128 (primary 0.034957,
still failing five stable/noise cells against ADWIN and drift against SGD).
This registration tests only whether adding an ADWIN2-backed fallback to a fixed
fast base rescues retention. The fast base is fixed at the forgetting
matched-oracle parameters K_fast=4, W_fast=32, which already pass everything
against SGD and W=8 (39/45, primary 0.083220), so the experiment isolates the
ADWIN veto rather than re-litigating adaptation. A failure limits this finite
fallback family and objective, not all forms of retention.

## Learner semantics

Reuse the EXACT y/target/events generation of the forgetting study (five
fixtures `core, noise_jump, drift, exactly_quiet, mixed`, nine coordinates,
6000 observations, burn 1000, same `v3_persistent.fixture` process). Seeds are
fresh so y bytes differ; the process is unchanged so the y-only controls remain
comparable in kind. There is no cue and no hidden context in this study. All
arms see history of y alone.

All policies predict each coordinate's y[t,j] before seeing it (initial
prediction 0), then update. Causal, per-coordinate, no resurrection of
discarded information, no cross-coordinate leakage.

**retain candidate (fast window + ADWIN2 fallback), per coordinate:** state is a
fast retained window (cap W_fast=32) and an ADWIN2 instance (delta from the
menu; clock 1, five buckets per size, minimum subwindow 5, grace 10, same
implementation and Eq.(3.1) rule as the baseline below). The fast window starts
empty and grows by appending y_t with oldest-first eviction beyond its cap,
averaging retained observations with equal weight.

- Predict: let d be the number of observations since the most recent request
  index at prediction time; before any request d is infinite. If d <= H predict
  the fast mean, else the ADWIN prior-window mean. The request observation's
  own pre-update prediction uses the pre-request regime; the new estimates are
  available at t+1.
- Observe y. Append y_t to the fast window with routine cap eviction, and feed
  y_t to the ADWIN instance through its ordinary clocked update and shrinkage.
  On a request, the fast window keeps only the newest K_fast=4 observations of
  its CURRENT retained window, including y_t; the ADWIN instance is untouched
  by requests and manages its own shrinkage. Never resurrect discarded
  observations, use future samples or backdate to a true boundary. No momentum,
  Adam, burst gain or additional blend parameter.

**oracle_nofallback:** the forgetting learner with K=4, W=32 on the same true
schedule, always predicting its single window. This is the mechanism ablation:
it measures what the fallback adds at matched schedule and matched fast memory.
No separate search; it is the candidate's fast base without slow state.

**random_fallback:** the full dual-state candidate with its SELECTED (delta, H)
and observation-independent Bernoulli reset opportunities from t0. After each
request suppress opportunities for 16 updates. Uniforms use PCG64
SeedSequence([study_seed,106000+fixture_ordinal,coordinate]), generated per
coordinate to preserve prefix/width invariance, using the fixed fixture order
core, noise_jump, drift, exactly_quiet, mixed. This tests schedule timing vs
the retention mechanism at matched capacity.

**window:** identical growing-then-capped arithmetic mean with no requests.
**sgd:** unchanged plain SGD, w_next=w-lr*(w-y). This is an exponentially
weighted tracker, so its memory is not assigned a literal finite sample count.
**adwin:** the paper-based ADWIN2 from the forgetting study, unchanged (same
module and fixed bucket/minimum/grace settings).

**Schedule ownership.** The evaluator supplies requests at true abrupt target
changes ONLY, after the current observation arrives and its pre-update
prediction has been scored. Requesting arms receive no true target value, noise
level or future samples, and no requests on drift or noise transitions. Keeping
K_fast=4 at a true boundary can retain old-regime samples; perfect timing is
not perfect segmentation or a mathematical performance upper bound. The granted
schedule is the experiment's premise, not a deployable claim: a pass authorizes
only a separately authorized broader benchmark of retention mechanisms with
rediscovered timing, never agent integration and never a claim that the schedule
is deployable. Random-request arms receive no true indices. Window, SGD and
ADWIN receive no schedule of any kind.

## ADWIN baseline and scope

Use the independent paper-based ADWIN2 implementation from the forgetting study:
ordered power-of-two buckets, at most five per size, merging the two oldest
equal-size buckets on overflow. Keep counts, sums and centered sums of squares.
At each selected clock tick, test bucket boundaries with both subwindows >=5;
on a violation remove the oldest bucket and repeat until no tested cut violates.
Predict the prior window mean.

The practical Eq.(3.1) threshold is sqrt(2*r*variance*L)+(2/3)*r*L, with
r=1/n0+1/n1, L=ln(2*ln(n)/delta), population variance of the retained window,
and strict mean-difference > threshold. Check from n>=10. No extra reset of the
surviving window, weight clipping or finite history cap. Centered-variance merge
arithmetic avoids subtracting large raw second moments; clamp roundoff below 0.

Source: Bifet and Gavaldà, [ADWIN paper, §§3.2–3.3](https://www.cs.upc.edu/~Gavalda/papers/adwin06.pdf).
These Gaussian fixtures violate the paper's bounded-input premise. Apply the
stated practical rule to raw observations identically across policies; claim no
bounded-data false-alarm guarantee and no parity with a particular library
release. A separate slow implementation using explicit bucket contents must
agree before study data. This is established prior art, not a new proposed
detector.

## Fixed finite menus and objective

Four searched families, each **12 configurations × 8 paired seeds × all five
fixtures** (384 tuning rows). The count differs from prior studies because no
separately tuned oracle family is searched here: the fast base is fixed and the
ablations receive no search, per the out-of-scope rule above. Order below
breaks exact objective ties.

- retain: delta in [.001,.01,.1], then H in [32,512,2048,6000], Cartesian
  product (12). K_fast=4, W_fast=32 fixed; slow-state clock 1, five buckets per
  size, minimum subwindow 5, grace 10 fixed. H=6000 is the always-fast endpoint
  after the first request; delta=.1 is the previously selected ADWIN endpoint.
  Refinement before any study observation: H was first registered as
  [32,128,512,6000], which jumps from a quarter-regime straight to the
  always-fast endpoint and leaves the regime scale itself untested. Switch
  spacing was read from the stream generator (`v3_slice1_streams.py:29-33`:
  first switch uniform 1800–2200, second 3800–4200, so ~2000-step regimes
  ~1800–2200 apart) rather than assumed. H=128 is traded for H=2048 — one full
  regime — holding the 12-configuration budget and both endpoints; the cost is
  short-horizon granularity, with H=32 still anchoring the brief end. Adding
  1024 as well would force a 15-configuration menu or a second dropped value
  and is not taken.
  Refinement before any study observation (slow state): the slow state was
  first registered as a plain growing-then-capped mean over a W_slow menu
  [512,2048,6000]. A plain long mean is structurally weaker than the ADWIN
  control it must match on stable cells, so a negative result would indict the
  fallback family rather than answer the question. The slow state is an ADWIN2
  instance and the W_slow axis is replaced by its delta, holding the
  12-configuration budget at 3 deltas × 4 H. The cost is one fewer ADWIN
  setting than the 12-configuration control menu; the previously selected
  delta=.1 endpoint is retained.
- window: W in [1,2,4,8,16,32,64,128,256,512,1024,6000] (unchanged).
- sgd: lr in [.0001,.0004,.001,.004,.008,.016,.035743040182210514,
  .064,.128,.256,.512,1] (unchanged).
- adwin: delta in [.0001,.001,.01,.1], then clock in [1,8,32], Cartesian product
  (unchanged); five buckets per size, minimum subwindow 5, grace 10 fixed.

These are finite menus, not global optimization. Report endpoint selections; no
automatic extension or post-result boundary veto. All four receive equal
configuration/seed/fixture budgets, not identical CPU costs. Record measured
execution times.

Freeze random-request probability from SELECTED retain tuning rows only. Pool
request counts N and observed coordinate-time S=6000*9*8 across all five
fixtures/eight seeds. Let f=N/S and p=f/(1-16*f); p=0 if N=0. Require finite
0<=p<=1, no clipping. This is expected pooled-frequency matching, NOT exact
per-condition counts, forgotten-sample counts or confirmation duty cycle.
Report those differences; no post-confirmation matching or retrospective
correction.

Reuse the EXACT nine-coordinate fixtures/metrics and selection objective of the
burst/forgetting/discovery registrations: 6000 observations, burn 1000; ordered
core, noise_jump, drift, exactly_quiet, mixed. P is the equal mean post-200 MSE
over core quiet/noisy switching and both mixed coordinates. R comprises the
same 14 cells: core quiet/noisy excess and quiet/noisy switching post-MSE;
three scalar-extra excess errors; noise-increase/noise-decrease/drift windows;
mixed post/stable errors per coordinate. Select minimum seed-mean (P+mean(R))/2
for every searched family.

A configuration with any non-finite tuning trajectory/metric is ineligible, with
its failure retained. Finish all 384 rows. If any family lacks a complete
finite configuration, close tuning_inconclusive and forbid confirmation.
Otherwise freeze all selected configurations, random p, source identity and
complete tuning evidence in a committed manifest BEFORE independent
confirmation.

## Partitions, confirmation and disposition

| Partition | Seeds | Rows |
| --- | --- | ---: |
| Development only | 100000–100007 | unit/synthetic only |
| Tuning | 101000–101007 | 4×12×8 = 384 |
| Independent confirmation | 103000–103031 | 6×32 = 192 |
| Bootstrap RNG only | 105000 | 10000 whole-seed resamples |

All seed ranges are fresh, including unused reservations of previous studies. Do
not reopen old studies or substitute seeds. Run all 192 confirmation rows if
tuning permits: retain, window, sgd, adwin, oracle_nofallback, random_fallback.
There is no detector in this study and no diagnostic screen is re-run; the 12
raw detector cells of prior studies are provenance, not evidence here. Do not
stop measuring candidate performance based on ablation outcomes.

Candidate must improve P by >=10% over EACH of window, sgd, adwin and
random_fallback, with paired 95% upper candidate-minus-control delta < 0.
Against oracle_nofallback the candidate must PRESERVE P within the retention
bound (paired upper delta <= max(.002,.1*control mean)): the fallback is a
stability addition, not an adaptation claim, and this deliberate asymmetry is
part of the registration. For each of 14 R cells against each of the five
controls require paired upper delta <= max(.002,.1*control mean), with one
stricter set: on the 8 stable/noise R cells against oracle_nofallback — core
quiet/noisy excess-MSE, whole noise_jump and exactly_quiet excess-MSE, the
noise-increase and noise-decrease windows, and mixed stable-MSE for each of
its two coordinates — the bound is replaced by a strict improvement
requirement (paired upper delta < 0). A fallback that cannot beat having no
fallback on the exact cells it was built for closes the experiment negative,
even if every other comparison passes; a do-nothing fallback passes the
preservation arm trivially and dies on this veto. Refinement before any study
observation (two-sided ablation): the ablation arm was first registered as
preservation-only, which a no-op fallback satisfies for free. All **75
comparisons** must pass for learning_positive; otherwise learning_negative.
Non-finite required trajectories fail; missing/malformed evidence remains
incomplete. Controls cannot be dropped because they are strong or fail other
diagnostics. Every final disposition closes this registration with no automatic
next experiment, mechanism change, default change or agent integration. A
positive would justify only a separately authorized broader supervised
benchmark of retention mechanisms with rediscovered timing.

Report regime use rates (fast vs ADWIN prediction share per condition), fast
retained-window widths at each request, ADWIN window widths and shrinkage
records, discarded observation counts, and actual update
norms per policy/seed/fixture. Distinguish routine cap evictions from request
flags: fixed windows evict but never issue requests. SGD has no literal window.
ADWIN flags shrinkage, not requests. Oracle and random scheduling differ in
false/repeated requests as well as delay; do not attribute every performance
difference to one cause. A failed result limits this finite (delta, H) fallback
family, not all forms of retention.

## Evidence, implementation phases and refinement

Archive every policy/seed's learning metrics and actual update norms by fixture;
per-coordinate request indices, event hit/latency against true target changes,
retained-window width summaries and ADWIN width/shrinkage summaries, discarded
observation counts, regime (fast/ADWIN) at each prediction, and realized versus
expected random activity. Always expose finite-seed counts and expected versus
realized random activity.

Phases: (1) register/refine; (2) implement/test and commit all scientific
sources; (3) tune all 384/freeze manifest; (4) confirm all 192; (5) reproduce
every reached row, manifest, selection and report; (6) publish a draft codex/**
PR, monitor all ten workflows at exact HEAD, mark ready and merge when green
and reviews resolved. Use separate v3_retention runtime/policy/study/report/
check modules plus a tenth workflow. Reuse frozen functions without
monkeypatching module globals. Preserve all earlier files except README/PLAN/V3
status pointers.

Before observations verify direct sliced-mean parity on hand-worked traces
(including startup, repeated requests, fast-window cap eviction, no
resurrection, H-boundary regime selection including the always-ADWIN
pre-request regime and the H=6000 always-fast endpoint, and K_fast=4 boundary
retention of old-regime samples); slow-state parity against a slow explicit
ADWIN implementation at matched delta (including bucket merges, shrinkage,
widths and estimates) and fast parity against the frozen forgetting
single-window learner at matched parameters; strict request-timing ownership (requests applied after scoring,
new estimates at t+1); prefix and coordinate causality, no true-index access in
the random arm, independent random RNG/frequency; all menus, common objective,
finite/tie selection; all 75 vetoes including the asymmetric primary rule and
the strict stable/noise improvement rule against oracle_nofallback; missing/invalid/non-finite records, changed sources,
uncommitted manifests and forbidden confirmation. Snapshot all transitive local
code, report/check sources, applicable protocols and pinned requirements. No
source change after observations except a diagnosed, explicitly reported
instrument defect. Registration SHA is immutable.

Reproduce all reached rows if eligible at rtol1e-11/atol1e-13; only execution
timing and regenerated input digests are exempt. Old discovery+forgetting+burst
evidence must also reproduce unchanged, and all nine prior workflows remain
intact. Statistical intervals are descriptive; finite menus, small synthetic
fixtures and observed zeros cannot establish population guarantees or general
neural-memory utility. No new dependencies are needed.
