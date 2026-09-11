# Build plan: behaviorally-anchored SNN framework + extracted experiment toolkit

Status: refined in-loop (round 3, converged — no open items remain);
pending owner approval to commit as plan. Neither build is approved
until then. This plan implements option B
of [M0-DECISION.md](M0-DECISION.md) (incremental substrate, then fork);
options A/C are recorded there, not here.

## Background (one paragraph)

Five preregistered slices (404 rows) retired V2.md's pre-fork questions:
per-tick motor sparsity fails at chance, trace-pair eligibility matches the
matrix, replay window L=20 is the measured knee, consume-on-reward at tau
200 stands with the sparse specialist logged, pools are inert and the
capacity cliff was a tie-bug artifact. The verified gap, checked against
Sacred / DVC-class tracking / OSF preregistration / Renku-class provenance
/ Norse-class task suites: nobody combines **preregistration with teeth**
(confirmation physically cannot run before the freeze) **with frozen
behavioral tables as merge gates**. That combination is build #2. Build #1
is its flagship proof: the M0 continuous-time fork, built rigorously from
day one.

## Build 1 — behaviorally-anchored SNN framework (the M0 fork)

**What it is.** A small continuous-time spiking framework whose headline
property is not a mechanism but a guarantee: every release reproduces a
pinned behavioral table exactly, every rule carries its falsifier, every
null publishes through the same pipeline as every win.

**Scope (from the slices, not from ambition).**
- IN: continuous-time core (the one change V2.md says forces a fork),
  ring-buffer replay at L=20, full@200 start rule (proportional@200 in
  the pocket), seed-generated fixed connectivity, parallel NM loops
  *iff* the Stage-1 probe passes, rank-1 credit traces regardless (ebar
  form follows its own slice verdict: matrix stays if the slice fails).
- OUT: local pools (dead-end), event-driven (conditional), same-scale
  constraint (Q3 killed it — the fork may grow units deliberately).
- Borrowed, not rebuilt: task adapters (trial tasks as presentation
  windows), volatility modulation, V(s) critic, reverse-TD replay.

**Milestones.**
- M0 parity: fork matches v1's suite numbers on identical task
  definitions (bit-exact where seeded RNG allows, in-noise otherwise,
  ≥6 seeds). NOTHING else starts until green. This milestone is the
  product's core demo: "watch a rewrite prove it didn't break anything."
- M1 throughput: batched core scales agents/second and units/second to
  10⁴ units (dense-batched; event-driven stays out).
- M2 scale demonstration (reframed; follow-on program, not part of
  build-#1-done): (a) the H160-degradation mechanism identified — fixed,
  or bounded inside a stated operating envelope — as the ENTRY GATE,
  then (b) suite parity at 10x units (H≈1280). Rationale for the split:
  the fork runs at 128 and M1 measures throughput, neither needs
  behavioral parity at scale; M2 is the first milestone that does, so
  the H160 question lives there, explicitly not fork-blocking.

**Rigor properties (non-negotiable, tested in CI).**
- The fork itself opens with a registration: starting constants,
  ported-task definitions, per-task parity bars. M0 parity is a
  confirmatory verdict with a falsifier, not a vibe.
- Frozen behavioral table expands with the suite; any release changing a
  number without a registered falsifier fails the build.
- Every new rule ships as: registration → frozen manifest → confirmation
  → report → review, using build #2's own templates (dogfooding is the
  point).
- Null results publish through the identical pipeline; the report index
  lists negatives alongside positives.

**Fork design sketch (starting point, not the design).**
V2.md's interface stands: `emit(t)` returns spikes at time `t`;
`sense(spikes, t)` delivers input; `reward(r, t)` arrives whenever it
arrives — no decision boundary. Trial tasks port as fixed presentation
windows (a trial task IS a continuous task with a schedule), which is
what makes M0 parity well-defined. Starting constants from the slices:
ring buffer at L=20, consume-on-reward at tau 200, proportional@200 and
none@200 logged for the mixed/sparse cases, rank-1 credit optional.
Open sub-questions for the fork registration (not this plan): reward-
timing semantics at sub-decision granularity; continuous-task
equivalents of lock-style sparsity (the regime Q2 deferred to M0);
rule-vs-regime lockdown with the fork's own instrument; whether the
10x-unit fork keeps k/H proportions or re-derives them (Q3's H160
result forbids assuming either).

**Language posture (decided).** numpy + numba, CPU-first, torch-
intersection ops — V2.md's position, kept for a harder reason than
portability: the headline property (bit-exact ports, frozen tables as
merge gates) depends on determinism, and torch/GPU nondeterminism would
dissolve it. GPU stays deferred under V2.md's arithmetic-intensity
analysis (batch-over-agents restores intensity if M1 ever earns it).
Revisit only with a registered determinism story, not before.

**Costs and risks.** The fork breaks task interface, runner, replay
episode definition, and eligibility consumption at once — the most
expensive step on any roadmap here (estimate: multiples of the five
slices combined). Parallel loops unmeasured is a known unknown inside
  it. Adoption risk is real: researchers may admire the rigor and keep
  their PyTorch. Mitigation: the framework must ALSO be pleasant —
  agent/task API as ergonomic as tasks.py, full suite green in minutes
  on CPU, every failure message citing the frozen number it broke.
  Rigor is the differentiator, not the product.

**Exit criteria.** M0 parity green, or a registered negative (continuous
time loses somewhere — also publishable). Substrate slices stand alone
as v1 improvements either way; no work is fork-contingent except the
fork.

**CI at scale (constraint, not afterthought).** Per-PR workflows keep
the 30-minute budget: fast parity gates + kernel exactness on every PR,
full behavioral suites nightly. A 10⁴-unit suite that cannot fit either
is a design smell in the suite, not a bigger-runner problem — shard by
task, never by lowering the gate. The 26-workflow suite already needs
this split before M1; do it then, not during M2.

## Build 2 — experiment toolkit, extracted (the safe pick)

**What it is.** The harness pattern behind all five slices, packaged so a
small lab gets 80% of the discipline for free: a template repo +
tiny library, not a platform.

**Contents (extracted, not invented).**
- `Evidence`: resumable per-key measurements bound to exact source bytes
  (snapshots), protocol ids, manifest digests; refuses to run
  confirmation against changed sources.
- Registration scaffold: falsifier-first doc template with protocol ids,
  decision procedures, band conventions, explicit non-claims.
- Report/check scaffolds: paired-bootstrap contrasts, band helpers,
  manifest/archive verification, full-reproduction runner with
  rtol/atol comparison.
- CI template: frozen-reference gate + full-reproduce + report-check on
  every PR, with the concurrency/backstop conventions.
- Docs: the method in 5 pages (why each rule exists, which failure it
  prevents), plus the null-corpus paper as a worked example.

**Non-goals.** Not a tracking dashboard (W&B owns that), not a data
versioner (DVC owns that), not a hypothesis registry (OSF owns that).
It does the one thing they don't: make the falsifier-first loop the
path of least resistance in a plain git repo.

**Validation.** Self-hosting (build #1 uses it from its first slice) is
table stakes. Real validation is one external pilot: a computational-
neuroscience course practicum (the model-organism angle doubles as
recruitment) plus one friendly lab, after toolkit v0. Bar: one
non-author registered slice end-to-end — their falsifier, their data,
published null-or-win through the pipeline. No pilot, no v1.0.

**Distribution (decided).** Template repo first: zero install friction,
the whole loop visible in one clone. Extract a micro-lib only when a
second user asks — a premature lib is an API commitment without users
to contradict it.

**Working titles (provisional).** Framework: `m0` (descriptive, matches
the roadmap; rename when it earns one). Toolkit: `register` (it does
what it says). Revisit at toolkit v0, not before.

## Sequencing (one ordering, dependencies honest)

1. **Parallel-loops probe** (one slice, v1, seams only). Gates whether
   loops ride into the substrate phase. Cheapest item, highest decision
   value — start here regardless.
2. **Substrate slices in v1** (seed connectivity; loops iff passed;
   ebar remainder of the Q5 lever, gated like Q5: match on the reference
   with no M×H baseline state). Each parity-checked, each independently
   shippable. V1 gets faster and leaner even if everything after dies.
3. **Toolkit v0 extraction.** The pattern now exists twice (brainsim
   slices + substrate slices) — extract honestly, from two instances.
4. **M0 fork using toolkit v0.** First external-grade consumer; every
   wart found here goes back into the toolkit continuously, not in a
   big-bang v1.
5. **M0 parity → toolkit v1 + paper.** Parity green unlocks both: fork
   lessons harden into toolkit v1, and the living report (running since
   now, venue decided after substrate per decision 6) submits with
   slices + substrate + parity as the worked example.
6. **M1 → reframed M2.** The roadmap resumes, now on measured ground.

Kill lines: if the loops probe fails AND seed-gen disappoints, skip to
C (hold) — the fork loses two passengers and its case weakens. If no
pilot slice is underway within two academic terms of toolkit v0, the
toolkit stays at v0 (used, not published).

Resourcing note: slices run sequentially, single-threaded — the method
(one HEAD, one frozen manifest at a time) is load-bearing, not
ceremony. Parallelize only across independent lanes (pilot outreach,
paper drafting), never across confirmatory evidence.

## Decisions taken in the loop (all nine resolved; rationale in the log)

1. M2's exact bar — RESOLVED in-loop: H160-diagnosis as entry gate,
   then suite parity at 10x units; follow-on program, not build-#1-done.
2. ebar follow-up — RESOLVED in-loop: substrate phase, Q5-style gate.
3. Language/API posture — RESOLVED in-loop: numpy+numba CPU-first
   (determinism is load-bearing), torch-intersection ops, GPU deferred.
4. Distribution shape — RESOLVED in-loop: template-first, lib on
   second user.
5. Pilot strategy — RESOLVED in-loop: course practicum + one friendly
   lab after toolkit v0; bar is one non-author slice end-to-end.
6. Null-corpus paper — RESOLVED in-loop: living tech report now (five
   slices exist today), venue decision after substrate.
7. "Done" — RESOLVED in-loop: build #1 = M0 parity + M1 throughput
   (M2 follow-on); build #2 v1.0 = self-host + one external pilot +
   docs.
8. Working titles — RESOLVED in-loop: `m0` / `register`, provisional.
9. H160 placement — RESOLVED in-loop: M2-blocker, explicitly not
   fork-blocking.

## Decision log (loop round 1)

- M2-as-scale-demo with H160-gate over vaguer framings: Q3 already
  proved scale breaks behavior, so any scale milestone that doesn't
  start from the H160 mechanism is unregistered optimism.
- numpy-first over torch-first: bit-exact gates are the product; torch
  nondeterminism dissolves them. Adoption cost accepted explicitly.
- Template over lib, pilot bar at one non-author slice, paper as living
  report: all bias toward proof-before-packaging, the program's own
  lesson (premises decay; controls are cheap).
- ebar inside substrate (same memory math) rather than dangling: keeps
  the lever whole in one phase.
