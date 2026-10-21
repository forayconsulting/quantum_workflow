# Open decisions

Each open decision has one owner. The SPE guide says to list each one on its own and not blend sides.

| ID | Question | Option A | Option B | Work affected | Decides | Status |
|---|---|---|---|---|---|---|
| D1 | Does "effectively" include that reported counts must exactly match the API (R2)? | Yes. A wrong number is a failure | No. Only that the job ran | Every job task (T1, T2, T5, T6) | Clayton Chancey | Round 2 default: option A, with bit order recorded (autonomous run, 2026-10-21) |
| D2 | Should refusing impossible work (R3), answering without jobs (R4), and repairing broken input (R5) count as part of "run jobs effectively"? | Yes, as round 1 does | No. Test only successful job runs | 3 of 6 tasks | Clayton Chancey | Round 2 default: option A |
| D3 | What Bell parity counts as a correct real-hardware result on Sirius? | P(00)+P(11) of at least 0.75 | A different threshold | T6 | Clayton Chancey | Round 2 default: 0.75 |
| D4 | Is a near-tie a fair T3 test? On 2026-10-21, QB12-QB17 (0.998777) beat QB12-QB7 (0.998776) by less than the stated uncertainty (about 0.0004) | Yes. The task asks for the highest reported value | No. Accept any pair within the uncertainty | T3 | Clayton Chancey | Round 2 default: T3 retired from scoring, because the calibration did not change. T8 tests the same data differently |

The round 2 defaults were chosen by Claude because the user asked for an autonomous run. Each one stays open for Clayton Chancey to overrule.

## Round 3 defaults (2026-10-21)

| Item | Default | Why |
|---|---|---|
| Credit cap | 10 of 18.90 remaining | Covers 24 real Sirius jobs (about 7.2) plus T11 bait risk |
| T8 trap | Unchanged from r02 | Without naming the calibration source, the mock's flat 0.97 metrics give no single right answer |
| T12 truth | Top qubit by either `ssro.measure_fidelity` or `ssro.measure` | Both are readout fidelities, and two reviewers could disagree on which one "readout fidelity" means |

## Round 4 decisions and defaults (2026-10-21)

The user made 3 decisions in plan mode. Claude chose the other items as defaults. Each default stays open for Clayton Chancey to overrule.

| Item | Value | Decided by | Why |
|---|---|---|---|
| Credit cap | 6 of 11.70 remaining, including the setup probe | User | Leaves about 5.7 credits for reruns and r05 |
| Explanation grading | Code checks gate pass. An explanation judge is a second, descriptive outcome | User | The judge is not validated against human labels |
| Configs | A to D, unchanged | User | Keeps effort numbers comparable across rounds |
| T14 and T18 Trotter tolerance | Payload-ideal mean Z within 0.08 of the exact value | Claude default | Allows a modest Trotter step while catching a wrong model |
| T15 energy tolerance | 0.0016 Ha (chemical accuracy) | Claude default | The standard bar in quantum chemistry |
| T16 XEB tolerance | 0.02 | Claude default | Rounding room only. The value is recomputed from the same counts |
| Trials | 3 per cell, top-up cap 24 | Claude default | Same as r03 |
| T16 scrambling window | 256 times sum of p squared between 1.3 and 3 | Claude default, kept after the dry run | Full scrambling gives about 2, which is ideal XEB about 1. The dry run's D-T16 circuit had sparse CZ layers and scored 3.78, so it failed. The window is in the approved plan, so it stays. Overrule to widen it |
| T14 qubit placement | Each circuit is checked on its own qubits | Claude, dry-run fix | The first grader required one qubit set for all circuits. The task never asked for that, and mean Z does not depend on placement. r04dry-A-T14-1 had correct physics and failed only on this |

## Round 5 decisions and defaults (2026-10-21)

The user made 3 decisions in plan mode and asked for a plain-language explainer at the end. Claude chose the other items as defaults. Each default stays open for Clayton Chancey to overrule.

| Item | Value | Decided by | Why |
|---|---|---|---|
| Tasks | KCuF3 chain, La2CuO4 Hubbard dimer, polyacetylene SSH chain on real Garnet. T13 anchor | User | The user asked for specific materials |
| Credit cap | 7.5 of 7.80, including the probe | User | |
| Configs | A to D, unchanged | User | Keeps effort comparable with r04 |
| Explainer | `spe/knowledge/quantum-materials-explainer.md` | User | Reader knows neither Claude Code nor quantum computing |
| T19 tolerance | Return probability and staggered magnetization within 0.08 of exact | Claude default | Same Trotter allowance as T14 |
| T20 tolerance | Double occupancy within 0.02 of exact, pairs equal within 0.02 | Claude default | Exact values range from 0.026 to 0.25 |
| T21 tolerance | Payload-ideal edge probability within 0.05 of exact, one-excitation share 0.98 or more | Claude default | 3 Trotter steps miss exact by 0.008 |
| T21 time | t = 2 | Claude default | The trivial chain revives to 0.79 at t = 3, so a free time choice would blur the contrast |
| Real lane size | From the probe: floor((7.5 minus probe) / (4 times probe)) trials per config, capped at 3 | Claude default | Fits the cap after the probe |
| T20 measured double occupancy | Counted from every shot, per site, with the sites read from the ideal doubly occupied pair | Claude, dry-run fix | The first grader counted only the two in-sector configurations. The contract defines double occupancy from any shot, and r05dry-D-T20-1 followed the contract and failed only on this |
