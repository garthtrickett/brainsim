# Change-triggered forgetting closes learning-negative

The registered candidate passed **58/75 independent learning comparisons** and
closes as **learning-negative**. Its primary post-switch MSE was **0.191012**,
versus **0.116201 for SGD** and **0.124435 for the tuned fixed window**.
It passed all comparisons against random resets and the matched no-reset policy,
but did not clear the stronger controls and every retention requirement.

Perfect-time forgetting produced a substantial adaptation benefit: the separately
tuned oracle reached primary MSE **0.034957**, and the oracle using the candidate's
exact parameters reached **0.083220**. Both nevertheless failed their full criteria,
with stable/noise-condition failures against ADWIN; the separately tuned oracle
also failed drift checks. These privileged diagnostics cannot override the
candidate's independent negative result.

All **480 tuning and 256 confirmation rows** were completed and finite. The fixed
detector passed all **12 diagnostic cells**. No new default, broader benchmark,
search extension or agent integration is activated.

## What was implemented

The [registration](DESIGN-v3-forgetting.md) tests a new use of the existing signal:
selecting which observations to retain. The detector, its reference predictor,
windows, persistence and calibrated threshold remain exactly unchanged.

The learner predicts from its existing arithmetic mean before observing y_t.
After receiving y_t, it appends that sample and enforces a maximum window W.
On a detector reset, it keeps the most recent K samples in its CURRENT retained
window, including y_t, and rebuilds the mean. It never resurrects discarded data,
backdates a boundary or sees a target value. A sustained high signal triggers once;
16 quiet observations are required before rearming.

Controls include an independently tuned fixed window, unchanged SGD, ADWIN2,
random resets at a frozen expected frequency, and the candidate's exact maximum
window with resets disabled. The two oracle arms receive only true abrupt target
change times, after pre-update prediction. They never receive target values or
noise labels and do not trigger on gradual drift. Keeping K>1 at a true boundary
can retain old-regime samples; perfect timing is not perfect segmentation or a
mathematical performance upper bound.

The ADWIN2 baseline is an independent implementation of the paper's practical
variance-aware test and bucket compression, checked against a slow implementation
with explicit bucket contents. It uses the unchanged Gaussian observations.
The bounded-input formal guarantees therefore do not apply; no particular
library-release parity or universal ADWIN ranking is claimed. Algorithm and
source attribution are fixed in the registration.

## Equal-budget finite tuning

Five families each received **12 configurations ×8 paired seeds ×all five
fixtures**. All used the same selection objective: equal weight on primary
post-switch MSE and the mean of 14 retention metrics. The matched arms received
no additional search.

| Policy | Selected setting |
| --- | --- |
| Detector-controlled forgetting | K=4, W=32 |
| Independently tuned oracle | K=1, W=128 |
| Fixed window | W=8 |
| SGD | lr=.128 |
| ADWIN2 | delta=.1, clock=1; five buckets/size, minimum subwindow5 |
| Matched oracle | K=4, W=32 |
| Random resets | K=4, W=32 |
| Matched no-reset window | W=32 |

Several settings lie on finite-menu endpoints: candidate W, oracle K, and
ADWIN delta/clock. These were explicitly reportable outcomes, with no automatic
search expansion. The results describe these menus, not globally optimal methods.

Random-reset probability was frozen at **0.00048054854257516646**, from **201
candidate tuning requests /421,488 coordinate-updates**, corrected for the
16-update cooldown. Expected pooled frequency is matched, not confirmation counts,
forgotten-sample counts or per-condition memory age. The complete tuning evidence
and manifest were committed before any confirmation observation.

## Independent performance

Each of eight policies ran on the same **32 fresh confirmation seeds** and all
five inherited fixtures: core, noise_jump, drift, exactly_quiet and mixed.
Primary MSE averages the four core/mixed switching coordinates equally over
200 pre-update predictions following each target change. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Independently tuned oracle | **0.034957** | Privileged diagnostic |
| Matched oracle | 0.083220 | Privileged diagnostic |
| SGD | 0.116201 | Deployable control |
| Fixed window, W=8 | 0.124435 | Deployable control |
| Detector-controlled forgetting | 0.191012 | Registered candidate |
| ADWIN2 | 0.195223 | Adaptive-window control |
| Random resets | 0.236991 | Matched timing control |
| Matched no-reset window, W=32 | 0.237095 | Matched memory-cap control |

Candidate-minus-control paired 95% intervals:

- SGD: **[0.072612, 0.077225]**, worse;
- fixed window: **[0.063882, 0.069347]**, worse;
- ADWIN2: **[-0.010073, 0.001481]**, failing the required benefit;
- random resets: **[-0.047700, -0.044194]**, **19.40%** lower mean primary error;
- matched no-reset: **[-0.047887, -0.044239]**, **19.44%** lower mean primary error.

The candidate passed all 15 comparisons against EACH matched random/no-reset
control. Its **17 failures** comprise three primary checks and 14 retention /
per-condition checks. Eight are switching-condition regressions against SGD or
W=8; six are stable/noise-condition failures against ADWIN. For example, noisy
switching MSE is **0.228658 versus 0.153912 for SGD**, while stationary noisy MSE
is **0.030309 versus 0.001224 for ADWIN**. Strong matched-control results do not
erase those failures.

## What the oracle and memory records show

The independently tuned oracle passes **38/45** comparisons. It beats all three
strong controls on the primary metric, but fails five stable/noise checks against
ADWIN and the drift-window check against both SGD and the fixed window. Its drift
MSE is **0.004052**, versus **0.000232 for SGD** and **0.000336 for W=8**.
The oracle has no privileged drift boundaries and must track drift through its
ordinary W=128 average.

The matched oracle passes **39/45** comparisons, including ALL comparisons against
SGD and W=8. Its six failures are stable/noise checks against ADWIN. At fixed K=4,
W=32, replacing detector scheduling with true-change scheduling reduces primary
MSE from **0.191012 to 0.083220**. That diagnoses the schedule's consequences,
including timing and false/repeated resets; it does not isolate delay alone.

The memory records make the stable-noise tradeoff visible:

| Policy, stationary noisy core | Mean retained observations | MSE |
| --- | ---: | ---: |
| Candidate | 31.97 | 0.030309 |
| Matched no-reset / matched oracle | 32.00 | 0.030225 |
| Independently tuned oracle | 128.00 | 0.007796 |
| ADWIN2 | 2366.73 | 0.001224 |

SGD has exponential weights and no literal finite window; its memory is not
reported as zero. Width counts represented observations, not ADWIN's physical
bucket storage. Discarded totals include routine cap evictions; fixed windows
have zero reset flags while still evicting samples.

The fixed detector catches **32/32** events in each of eight target cells. Mean
delays range **10.03–13.59 observations**, and actual candidate reset hits/delays
match those first raw alarms in these cells. Stationary block alarms are **9/1600
quiet** and **11/1600 noisy**; both noise-transition windows have **0/32** alarms.
These 12 passing diagnostics do not establish learning advancement.

Confirmation contains **728 candidate resets**, **802 random resets**, **256
requests in each oracle arm**, and **4465 ADWIN shrink updates**. These event types
have different meanings and discard different amounts of history. Random frequency
matching is approximate and pooled; no retrospective correction was applied.
The generated report exposes every coordinate's memory, errors and event counts.

This test establishes benefits over matched controls and an adaptation benefit
under privileged scheduling. It does not establish one deployable policy that
beats the fast fixed trackers while preserving ADWIN's stable-condition accuracy.
Both the candidate and oracle full-comparison decisions remain negative. This
closes the tested finite forgetting family without claiming all forgetting fails.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | `cd86be570c5f8f0c4c19c49f4561fa165f2fca34` | Before study data |
| Implementation/checks | `a4abc9a4a44a557786859ae403996a5d48d8c6ce` | Before tuning |
| Tuning / manifest freeze | `918b22c7115dcf6c3b5b5e7cf29e7c546a1d485c` | 480 rows; before confirmation |
| Confirmation | seeds 83000–83031, eight policies | 256 rows; learning-negative |
| Reproduction/publication | All 736 reached rows; eight workflows | See validation below |

Protocol SHA-256:
`d74023283153cc73c8c330f20200f7331b02a822e45eb0c2c54230fd631062af`.
Development 80000–80007, tuning 81000–81007, confirmation 83000–83031 and bootstrap 85000
are separate. Thirty source snapshots include applicable protocols and every
transitive local runtime/report/check dependency. No scientific source changed
after observations began. Snapshots preserve identities after squash merge.

New files: `v3_adwin.py`, `v3_forgetting.py`, `v3_forgetting_policy.py`,
`study_v3_forgetting.py`, `report_v3_forgetting.py`, `check_v3_forgetting.py`,
`.github/workflows/v3-forgetting-checks.yml`, the registration, this results
file and `results/v3-forgetting/`. README and PLAN/V3 status pointers report the
outcome. Earlier scientific sources, protocols, evidence, all seven previous
workflows, dependencies and agent defaults remain unchanged. No capability or
registry row is promoted.

The [generated report](results/v3-forgetting/report.md) includes all 75 candidate
and both 45 oracle comparisons, the 12 raw detector cells, memory and update-norm
summaries and execution times. The [summary](results/v3-forgetting/summary.json)
also includes intervals. Raw records retain reset indices/widths, discarded counts
and candidate prediction-error/recovery diagnostics alongside alarms.

## Validation and limits

All commands below passed locally, including reproduction of all 736 new rows
and all 704 previous burst rows. Python commands use the existing project `.venv`:

```sh
python check_v3_forgetting.py --evidence results/v3-forgetting --reproduce
python report_v3_forgetting.py --check
python check_evidence.py
python check_v3_burst.py --evidence results/v3-burst --reproduce
python report_v3_burst.py --check
git diff --check
```

Checks cover direct sliced-mean parity, startup/cap/reset boundaries, no data
resurrection, independent explicit-content ADWIN bucket/variance/width parity,
causal prefixes, coordinate isolation, oracle metadata restrictions, random RNG /
frequency, every 75 veto, all 45 oracle cells, immutable sources/manifests/stages,
missing/invalid/non-finite evidence and memory conservation. Every reached row,
manifest, selection, probability, decision and scientific summary is reproduced at
rtol1e-11/atol1e-13, excluding only timing and regenerated input digests. CI must
pass all eight workflows before merge.

Intervals use 10000 whole-seed resamples. Small Gaussian supervised fixtures,
finite parameter menus, approximate random matching and privileged oracles cannot
establish population guarantees, global rankings, or neural-memory utility.
ADWIN's bounded-input theorem is not invoked on these unbounded observations.
The authoritative outcome is the candidate's independent learning-negative result.
