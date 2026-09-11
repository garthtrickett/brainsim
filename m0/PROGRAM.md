# M0 program task list — substrate, fork, toolkit

Home for the option-B program from [PLAN-m0-toolkit.md](../PLAN-m0-toolkit.md).
This file is the persistent master list (session todos mirror it); check off
stages only on merged PRs with green CI. Fork code lives here when it starts
(`m0/` package); v1 slices keep root-level files per repo convention.

Conventions (non-negotiable): register falsifier first → implement → freeze
manifest → confirm → report → PR → merge on green CI. No tuning stages, no
source edits under frozen manifests (subclass/seam only), full reproduction
before every PR.

## Stage 1 — parallel-loops probe [NEXT]

- [ ] Orient: map NM machinery (ADAPTIVE vol scalar, DUALV, VBURST, LR sites)
- [ ] Register `DESIGN-loops-probe.md` (menu, instrument, falsifier)
- [ ] Implement harness (subclass fork, zero v1 source change)
- [ ] Freeze manifest, confirm, report
- [ ] PR, CI, merge — verdict feeds Stage 2 go/no-go

## Stage 2 — substrate slices in v1

- [ ] Seed-generated connectivity (zero-memory fixed synapses; bit-exact gate)
- [ ] Parallel loops, iff Stage 1 passes (parity + replicated win)
- [ ] ebar remainder (Q5-style gate: match reference, no M×H baseline state)

## Stage 3 — toolkit v0 extraction

- [ ] Extract from two instances (brainsim slices + substrate slices)
- [ ] Template repo shape; docs: method in 5 pages

## Stage 4 — M0 fork on toolkit v0

- [ ] Fork registration (constants, ported tasks, per-task parity bars)
- [ ] Continuous-time core; ring buffer L=20; full@200 start
- [ ] M0 parity green (or registered negative)

## Stage 5 — toolkit v1 + paper + M1/M2

- [ ] Toolkit v1 from fork lessons; living report submits
- [ ] External pilot (course practicum + one lab; bar: one non-author slice)
- [ ] M1 throughput; M2 scale demo (H160-gate first)

## Kill lines

- Loops probe fails AND seed-gen disappoints → hold (option C).
- No pilot slice underway within two terms of v0 → toolkit stays v0.
