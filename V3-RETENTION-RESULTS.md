# Oracle-schedule retention closes learning-negative on drift

The registered candidate passed **68/75 independent comparisons** and closes as
**learning-negative**. Its primary post-switch MSE was **0.082702**, versus
**0.119466 for SGD**, **0.128206 for the tuned fixed window**, **0.197654 for
ADWIN2**, **0.197029 for random-schedule fallback**, and **0.086763 for the
matched no-fallback ablation** (preserved within bounds). All five primary
comparisons pass.

This is not the failure its predecessors recorded. Every stable and noise cell
against ADWIN passes — both mixed-fixture `stable_mse` cells among them — so
the adaptation/stability tradeoff that killed the burst, forgetting and
discovery studies was **held**, not repeated. The experiment closes on six
drift cells, which neither the fast window nor ADWIN tracks, plus one
strict-veto cell that failed on a 0.000000-vs-0.000000 tie on the noiseless
fixture. Drift is now isolated as a distinct regime rather than confounded
with the tradeoff.

All **384 tuning and 192 confirmation rows** were completed and finite. No new
default, broader benchmark, search extension or agent integration is activated.

## What was implemented

The [registration](DESIGN-v3-retention.md) grants true abrupt-target times and
varies only what is kept after a change: a fast post-change window (K_fast=4,
W_fast=32, the forgetting matched-oracle base) plus an ADWIN2 accumulator
behind a fallback horizon H. At most 32 observations after a request the policy
predicts from the fast mean; otherwise from the ADWIN prior-window mean. The
ADWIN instance is untouched by requests and manages its own shrinkage. There is
no detector arm and no diagnostic screen.

Controls: y-only window/SGD/ADWIN2 (unchanged menus), the matched
no-fallback ablation (fast base without slow state, same true schedule), and
random-schedule fallback (selected delta/H on Bernoulli requests from t0 with
16-update suppression, frozen expected frequency). The granted schedule is the
experiment's premise, not a deployable claim; window, SGD and ADWIN receive no
schedule of any kind.

The registration was refined twice before any study observation, with rationale
recorded in the document: the H grid traded H=128 for H=2048 (one full regime,
read from the stream generator rather than assumed), and the slow state became
an ADWIN2 instance instead of a plain long mean. No scientific source changed
after tuning began.

## Equal-budget finite tuning

Four families each received **12 configurations × 8 paired seeds × all five
fixtures**, selected on the same objective as burst/forgetting/discovery (half
primary post-switch MSE, half mean of 14 retention metrics). Matched arms
received no additional search.

| Policy | Selected setting |
| --- | --- |
| Retention | delta=0.1, H=32 |
| Fixed window | W=8 |
| SGD | lr=.128 |
| ADWIN2 | delta=.1, clock=1 |
| Matched no-fallback | K=4, W=32 |
| Random fallback | delta=0.1, H=32 |

All three y-only controls selected the identical settings as the forgetting and
discovery studies (W=8, lr=.128, delta=.1/clock=1) — instrument stability
across three registrations. The retain selection sits on two endpoints
(delta high, H low); these were explicitly reportable outcomes with no
automatic search extension.

Random-request probability was frozen at **0.0001485001485001485**, from **64
candidate tuning requests / 432000 coordinate-updates** (S=6000·9·8,
opportunities from t0), with 16-update suppression. Expected pooled frequency
is matched, not confirmation counts or per-condition memory age. The complete
tuning evidence and manifest were committed before any confirmation
observation.

## Independent performance

Each of six policies ran on the same **32 fresh confirmation seeds** and all
five inherited fixtures: core, noise_jump, drift, exactly_quiet and mixed.
Primary MSE averages the four switching coordinates equally over 200
pre-update predictions following each target change. Lower is better.

| Policy | Primary MSE | Role |
| --- | ---: | --- |
| Detector-controlled retention | **0.082702** | Registered candidate |
| Matched no-fallback | 0.086763 | Mechanism ablation |
| SGD | 0.119466 | Deployable control |
| Fixed window, W=8 | 0.128206 | Deployable control |
| Random fallback | 0.197029 | Timing control |
| ADWIN2 | 0.197654 | Adaptive-window control |

Candidate-minus-control paired 95% intervals (primary): SGD
**[-0.039927, -0.033676]** (30.77% lower mean); fixed window **[-0.049688,
-0.041408]** (35.49% lower); ADWIN2 **[-0.118086, -0.111738]** (58.16% lower);
random fallback **[-0.117380, -0.111218]** (58.02% lower); no-fallback
preservation **[-0.005675, -0.002360]**, inside the retention bound. All five
primary comparisons pass.

## The tradeoff was held; drift closed the experiment

Against ADWIN, every stable/noise cell passes with identical values on both
sides — the candidate in slow-regime segments *is* ADWIN2 (same delta, clock,
kernel and inputs), so mixed stable MSE is 0.000691 vs 0.000691
(increase-first) and 0.000926 vs 0.000926 (decrease-first), stationary noisy
0.001187 vs 0.001187, noise_jump 0.000732 vs 0.000732. These were the
registered veto cells that killed the last three experiments, and they passed
here while the candidate simultaneously beat ADWIN 0.082702 to 0.197654 on
primary. For abrupt changes, the carried-forward claim — "even granted true
timing, no single policy beats both the fast tracker and the stable
accumulator" — is contradicted. The barrier for abrupt changes was trigger
quality all along.

The six closing cells are all drift: candidate drift-window MSE **0.003148**
versus **0.000195 for SGD**, **0.000322 for W=8**, **0.000184 for no-fallback**;
drift-fixture MSE **0.007562** versus **0.000229**, **0.000334**, **0.000339**.
The candidate receives no requests on drift (true abrupt-target times only),
so on drift fixtures it reduces to ADWIN2 exactly — candidate and ADWIN drift
cells are identical (0.003148 vs 0.003148, passing) — and ADWIN loses drift
tracking to the fast exponential and window trackers. Drift is a regime
neither component of this composition tracks. It is now isolated as its own
question rather than confounded with the adaptation/stability tradeoff, and
nothing in this result claims otherwise.

## The strict-veto tie is a defect in the rule, not the candidate

Seven of eight strict stable/noise cells against no-fallback pass, most by
large margins: noisy 0.001187 vs 0.031134 (paired interval [-0.030737,
-0.029088]), mixed decrease-first stable 0.000926 vs 0.018795, noise-increase
window 0.006020 vs 0.029683. The fallback decisively beats having no fallback
exactly where it was built to help.

The eighth, `exactly_quiet`, reads candidate **0.000000** versus control
**0.000000** with interval **[0.000000, 0.000000]** — both arms predict the
noiseless fixture perfectly — and strict improvement (paired upper < 0) is
unsatisfiable on a perfect tie. This is a flaw in the gate as specified: the
rule demands improvement where no improvement is possible, so it fired on a
tie, not a regression. It was **not decisive**: the six drift cells close the
experiment independently, and the cell is retained in the record rather than
dropped or given weight it has not earned.

## The ~1% that carries everything

Post-burn fast-regime share of the selected config (32 confirmation seeds):

| Fixture | Mean fast share | Max over coordinates |
| --- | ---: | ---: |
| core | 0.0064 | 0.0128 |
| mixed | 0.0128 | 0.0128 |
| noise_jump | 0.0000 | 0.0000 |
| drift | 0.0000 | 0.0000 |
| exactly_quiet | 0.0000 | 0.0000 |

Outside the fast regime the candidate's predictions are bit-identical to the
ADWIN control (same delta=.1, clock=1, kernel and inputs), so the two arms
differ on 0.6–1.3% of switching-fixture updates and never elsewhere — yet
primary MSE is 0.082702 against 0.197654. Near-indistinguishable predictions,
very different adaptation: the ~1% after a true change carries the entire gap.
Stationary passes are by construction and are not reported as discoveries.

## Briefest-fast wins everywhere: a finding about composition

Retain tuning objectives by configuration (lower is better, selected marked):

| Index | delta | H | Objective |
| --- | ---: | ---: | ---: |
| 0 | .001 | 32 | 0.080686 |
| 1 | .001 | 512 | 0.056349 |
| 2 | .001 | 2048 | 0.056946 |
| 3 | .001 | 6000 | 0.056911 |
| 4 | .01 | 32 | 0.064099 |
| 5 | .01 | 512 | 0.056178 |
| 6 | .01 | 2048 | 0.056764 |
| 7 | .01 | 6000 | 0.056721 |
| 8 | .1 | 32 | **0.055560 selected** |
| 9 | .1 | 512 | 0.056149 |
| 10 | .1 | 2048 | 0.056682 |
| 11 | .1 | 6000 | 0.056634 |

At every delta, H=32 beats H=512 beats H=2048 and the always-fast endpoint:
longer fast regimes cost stability without buying adaptation. The H=2048
interior the refinement added to cover the regime scale was beaten decisively
enough to select against at all three deltas — against the expectation that
motivated adding it. Composition helps only briefly after a change; past ~32
observations the ADWIN state alone does better.

## Privilege caveat

The candidate runs on granted true change times it could not recover itself —
no deployable timing was tested, and the primary win in particular is a win
under privilege. The registration limits what any positive authorizes, and
that limit binds just as hard on this partial positive: no default change, no
agent integration, no broader claim without a separately authorized benchmark
with rediscovered timing.

## Evidence, phases and changed files

| Phase | Evidence | Status |
| --- | --- | --- |
| Registration/refinement | `5c07122fb9a047730121791d737f2ac6c3cda027` | Before study observations |
| Implementation/checks | `caeed27` | Before tuning |
| Tuning / manifest freeze | `8ad5c3f` | 384 rows; before confirmation |
| Confirmation | seeds 103000–103031, six policies | 192 rows; learning-negative |
| Reproduction/publication | All 576 reached rows; ten workflows | See validation below |

Protocol SHA-256:
`8efd8adfeda13a3fc1079b94f69b26b4e9091ad1c1729a3a8cd4c129dd056309`.
Development 100000–100007, tuning 101000–101007, confirmation 103000–103031
and bootstrap 105000 are separate and disjoint from all previous studies.
Source snapshots cover all transitive local runtime/report/check dependencies
and inherited threshold manifests. Snapshots preserve provenance after squash
merge.

New files: `v3_retention.py`, `v3_retention_policy.py`,
`study_v3_retention.py`, `report_v3_retention.py`, `check_v3_retention.py`,
`.github/workflows/v3-retention-checks.yml`, the registration, this results
file and `results/v3-retention/`. README and PLAN/V3 status pointers report
the outcome. Earlier scientific sources, evidence, protocols, all nine
previous workflows, dependencies and agent defaults remain unchanged. No
capability or registry row is promoted.

The [generated report](results/v3-retention/report.md) includes all 75
candidate comparisons with their improve/preserve/strict modes, per-fixture
absolute errors, dual-state memory and regime shares, and execution times. Raw
records retain request indices, fast/ADWIN widths, discarded counts and regime
at each prediction.

## Validation and limits

All commands below passed locally, including reproduction of all 576 new rows.
Python commands use the project's existing `.venv`:

```sh
python check_v3_retention.py --evidence results/v3-retention --reproduce
python report_v3_retention.py --check
python check_evidence.py
git diff --check
```

Checks cover dual-state composition and H boundaries, frozen forgetting/ADWIN
parity, the from-t0 request schedule against `pulse_schedule`, causal
prefixes, coordinate isolation, privilege isolation of the granted schedule,
all 75 vetoes including the asymmetric primary rule and the strict ablation
cells, immutable sources/manifests/stages, missing/invalid/non-finite
evidence, and dual memory accounting. Every reached row, manifest, selection,
probability, decision and scientific summary is reproduced at
rtol1e-11/atol1e-13, excluding only timing and regenerated input digests. CI
must pass all ten workflows before merge.

Intervals use 10000 whole-seed resamples (seed 105000). Small Gaussian
supervised fixtures, finite parameter menus, approximate random matching and
the granted schedule cannot establish population guarantees, global rankings,
or neural-memory utility. The authoritative outcome is the candidate's
independent learning-negative result on drift.
