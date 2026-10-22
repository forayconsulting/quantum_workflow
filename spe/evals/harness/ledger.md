# Credit ledger

Round 1 cap: 25 credits on real QPU jobs (user decision, 2026-10-21). Balances come from the dashboard at `https://resonance.iqm.tech/account/credits`, read with the Playwright Chrome extension. Estimates come from `billed_seconds` times the QPU rate.

## Mock-cost probe (step 0)

| Time (UTC) | Event | Balance | Source |
|---|---|---|---|
| 2026-10-21T15:21:52Z | Before probe | 30.00 | Dashboard, Account page |
| 2026-10-21T15:22:07Z | Probe job `01a15f0e-2d23-7640-890c-786d84d5916f` on `garnet:mock`, 100 shots, completed. The API reported `billed_seconds: 1.0` | | IQM API |
| About 15:23Z | After probe | 30.00 | Dashboard, Account page |
| About 15:30Z | Credit history shows only "+30.00 Monthly Starter plan credits" | 30.00 | Dashboard, Credits page |

**Result:** a mock job cost 0.00 credits, even though the API reports `billed_seconds: 1.0` for it. The halt rule (more than 0.05 credits per mock job) did not trigger. Grading and the helper treat mock jobs as 0 credits.

Other step 0 jobs, all on mock aliases at 0 credits: `01a15f0f-d4cb-7005-9970-e0000d47926d` (GHZ, `sirius:mock`), `01a15f10-a0a6-72f9-aa21-6ce07b45e92b` (Bell, `garnet:mock`), and `01a15f10-cb79-7533-ac8f-ded49f81fdc9` (cancel test, `garnet:mock`).

## Round 1 real-QPU spend

| Time (UTC) | Event | Balance | Source |
|---|---|---|---|
| 15:30:35Z | Round 1 started (run `wf_1a6926f8-f6c`) | 30.00 | Dashboard, before the run |
| 15:31 to 15:46Z | 12 real T6 jobs on `sirius`, 1.0 billed second each. Workflow estimate: 3.60 credits | | IQM API `metrics.billed_seconds` |
| About 15:52Z | Credit history: "- 3.60 IQM Sirius, 12 jobs, Pay-as-you-go" | 26.40 | Dashboard, Credits page |

**Result:** the actual spend was 3.60 credits, the same as the estimate. That is 14% of the 25-credit cap. The credit gate never triggered.

## Job reconciliation (round 1)

The dashboard Jobs page listed 61 jobs on 2026-10-21. These are the 5 jobs from step 0 and the dry run, plus the 56 job IDs that round 1 trials reported. Every job is accounted for, so no trial submitted an unreported job. Of the 56, 12 were real `sirius` jobs (all T6) and 44 were mock jobs.

## Round 2 setup (2026-10-21, before the run)

| Time (UTC) | Job | QPU | Purpose | Credits |
|---|---|---|---|---|
| 16:02Z | `01a15f32-c6e1-72ed-9ea4-5dc2d7e35f31` | garnet:mock | T7 probe. The job failed server-side with "No calibration data for 'cz.crf_crf' at ('QB1', 'QB20')" | 0 |
| 16:02Z | `01a15f32-d229-73a1-af79-a2b734ea30c1` | garnet:mock | T8 oracle, Bell on QB12 and QB17 | 0 |
| 16:02Z | `01a15f32-de09-7462-932e-177f79f9af55` | garnet:mock | T8 negative, Bell on QB8 and QB9 | 0 |
| 16:02Z | `01a15f32-e918-72f4-9000-e31caa84a8fa` | garnet:mock | T9 first try. Failed: `angle` given as integer 0, and the server requires a float | 0 |
| 16:02Z | `01a15f32-ed55-764e-9ced-e703586166be` | garnet:mock | T9 negative, all angles pi/2 | 0 |
| 16:02Z | `01a15f32-f88a-7682-83dd-64c1bc1fda91` | garnet:mock | Negative, not a Bell circuit. The mock still returned only 00 and 11 | 0 |
| 16:03Z | `01a15f33-3f49-73f1-951e-f4b5362a0096` | garnet:mock | T9 oracle, float angles | 0 |
| 16:05Z | `01a15f34-7768-73f4-aeaf-bafe7eb82a04` | sirius | T10 oracle, real GHZ-3. Parity 0.89. Billed 1.0 s | 0.30 (estimate) |

Balance before round 2 setup: 26.40. Expected after setup: 26.10.

## Round 2 real-QPU spend (run `wf_f3caa17a-2c4`, 16:09Z to 16:51Z)

| Item | Value | Source |
|---|---|---|
| Real jobs reported by trials | 24 on `sirius` (12 T6, 12 T10). No T11 trial used real Garnet | Grade files |
| Workflow estimate | 7.20 credits | billed_seconds 1.0 × 0.3 per job |
| Setup oracle (T10) | 0.30 credits | This ledger, round 2 setup |
| Dashboard after the run | Balance 18.90. Credit history: "- 11.10 IQM Sirius, 37 jobs" for the day | Dashboard, Credits page |

**Result:** 37 Sirius jobs (12 in r01, 1 oracle, 24 in r02) at 0.30 each is 11.10, which matches the dashboard exactly. Round 2 spent 7.50 including the oracle, inside the 15 cap. The credit gate never triggered.

## Job reconciliation (round 2)

The dashboard listed 194 jobs. The known set was 192: 61 from r01, 8 from r02 setup, 2 from the r02 dry run, and 121 reported by r02 trials. Matching the 6-character ID suffixes on all 8 dashboard pages found **2 unreported jobs**. Both are `garnet:mock` jobs with 1 circuit and 100 shots, so they cost 0 credits:

| Suffix | Created (UTC) | Likely source |
|---|---|---|
| `a9c744` | about 16:10 | r02-B-T5-1. Its script submitted a job and then crashed on `job.result_counts()` before printing an ID. The agent resubmitted and reported only the second job |
| `7a2293` | about 16:20 | Not attributed. Neither ID appears in any transcript or in the helper's call log, so an SDK script (config A or B) submitted it without printing the ID |

## Round 3 setup (2026-10-21, before the run)

| Job | QPU | Purpose | Credits |
|---|---|---|---|
| `01a15f98-afe1-776d-aa62-817abeb1f8eb` | garnet:mock | T13 oracle, GHZ on QB11-QB12-QB7 | 0 |
| `01a15f98-b828-74a1-8a49-b58c088e36d3` | garnet:mock | T13 negative, wrong triple QB18-QB19-QB20 | 0 |
| `01a15f98-c045-7231-bf45-b467f3b3408e` | garnet:mock | T13 negative, right qubits but not a GHZ circuit | 0 |

Balance before round 3: 18.90.

## Round 3 real-QPU spend (run `wf_3612af23-e49`, 18:00Z to 18:43Z)

| Item | Value | Source |
|---|---|---|
| Real jobs reported | 24 on `sirius` (12 T6, 12 T10). No T11 trial used real Garnet | Grade files |
| Workflow estimate | 7.20 credits | billed_seconds 1.0 × 0.3 per job |
| Dashboard after the run | Balance 11.70. Credit history: "- 18.30 IQM Sirius, 61 jobs" for the day | Dashboard, Credits page |

**Result:** 61 Sirius jobs at 0.30 each is 18.30, which matches the dashboard. Round 3 spent 7.20, inside the 10 cap.

## Job reconciliation (round 3)

The dashboard listed 315 jobs. The known set is 313 reported or setup jobs plus the 2 unreported jobs from round 2. **Round 3 left 0 unreported jobs.** Scrape and attribution output: `evals/results/r03/unreported_jobs.json` (empty).

## Calibration check (round 3)

| QPU | Default before the run | Default after the run (18:45Z) |
|---|---|---|
| garnet | f81c45da (16:42:21Z) | f81c45da |
| sirius | e3e7b570 (08:16:02Z) | e3e7b570 |

## Round 4 setup (2026-10-21, before the run)

Round 4 cap: 6 credits on real QPU jobs, including this probe (user decision, 2026-10-21). Balance before setup: 11.70.

| Task | Jobs | QPU | Purpose | Credits |
|---|---|---|---|---|
| T14 | 2 | garnet:mock | Oracle, and a negative with time scaled by 2 | 0 |
| T15 | 2 | garnet:mock | Oracle, and a negative with a wrong determinant | 0 |
| T16 | 2 | garnet:mock | Oracle with 10 CZ layers, and a negative with 3 | 0 |
| T18 | 2 | garnet:mock | Oracle folded 1x, 3x, 5x, and a negative with no folding | 0 |
| T17 | 1 | sirius:mock | Mock test of the GHZ ladder | 0 |
| T17 | 1 | sirius | Real probe: GHZ on 2, 3, 4, 5 qubits, 4 circuits, 100 shots. Billed 1.0 second. Parities 0.91, 0.85, 0.80, 0.75 | 0.30 (estimate) |

The full job IDs are in `graders/selftest/r04/`. That folder stays untracked until the round ends, so trial worktrees cannot see the oracle payloads (failures.md F14).

**Probe result:** a 4-circuit job billed the same 1.0 second as a 1-circuit job. T17 runs 3 trials per config. The workflow credit cap is 6 minus 0.30, which is 5.70.

Dashboard before the round 4 run (about 20:49Z): balance 11.40. Credit history: "- 18.60 IQM Sirius, 62 jobs" for the day. 62 jobs at 0.30 is 18.60, so the probe cost exactly 0.30.

## Round 4 real-QPU spend (run `wf_664c303a-347`, 20:55Z to 21:41Z)

| Item | Value | Source |
|---|---|---|
| Real jobs reported | 12 on `sirius`, all T17. Each had 4 circuits and 100 shots | Grade files |
| Billed seconds | 1.0 for every real job | IQM API `metrics.billed_seconds` |
| Workflow estimate | 3.60 credits | 12 jobs at 0.30 |
| Dashboard after the run | Balance 7.80. Credit history: "- 22.20 IQM Sirius, 74 jobs" for the day | Dashboard, Credits page |

**Result:** 74 Sirius jobs at 0.30 each is 22.20, which matches the dashboard. Round 4 spent 3.90 including the probe, inside the 6 cap. The credit gate skipped no trial.

## Job reconciliation (round 4)

The dashboard listed 425 jobs. The known set was 422: 315 from earlier rounds, 10 from r04 setup, 3 from the r04 dry run, and 94 reported by r04 trials. Matching suffixes on the first 6 dashboard pages found **3 unreported jobs**. All are `garnet:mock`, so they cost 0 credits:

| Suffix | Created (UTC) | Shape | Likely source |
|---|---|---|---|
| `17706a` | about 21:33 | 3 circuits, 1000 shots, failed | r04-D-T18-5. Its first submission failed with "Circuit contains no measurements". The script crashed before it printed the ID, and the agent did not report the job (failures.md F10) |
| `7364f9` | about 20:58 | 1 circuit, 200 shots | Not attributed. About 20 trials overlap that minute, and no transcript contains the suffix |
| `6f89a9` | about 20:58 | 3 circuits, 1000 shots | Not attributed. The shape fits T18 or a T16 retry |

Output: `evals/results/r04/unreported_jobs.json`.

The print-the-ID line in the preamble did not prevent these. A script that crashes inside the submit call never reaches the print.

## Round 5 setup (2026-10-21)

Balance before setup: 7.80 (round 4 close-out). Cap: 7.5 including the probe.

| Task | Jobs | QPU | Purpose | Credits |
|---|---|---|---|---|
| T19 | `01a16094-1cd7-77de-861f-25df3dc3d73d`, `01a16094-2f1b-7172-8b3b-47d99c414421` | garnet:mock | Oracle, and a negative with time doubled | 0 |
| T20 | `01a16094-4a3c-7513-9790-c9b785b185ba`, `01a16094-5c92-763e-ad5d-a4daeb779226` | garnet:mock | Oracle, and a negative with U labels swapped | 0 |
| T20 | `01a160a1-6d92-7099-8b0c-379cbf1a30c2`, `01a160a1-7e2b-7670-b1df-2d54ffb2c0b1` | garnet:mock | Oracle and negative rerun after the dry-run fix to the double-occupancy definition. They replace the two T20 jobs above as fixtures | 0 |
| T21 | `01a16095-301a-7478-a162-eca33a7b1e0a` | garnet:mock | Mock-only test of the oracle circuits | 0 |
| T21 | `01a16095-bcae-71d0-948b-0fb2af1138a9` | garnet:mock | Mock test inside the real probe | 0 |
| T21 | `01a16095-cb06-7507-8148-8d116616820f` | garnet | **Real probe.** 2 circuits, 42 CZ each, 1000 shots, QB1 to QB10 path, calibration `f81c45da` | 1.00 (billed 2.0 s at 0.5) |

**Probe result.** Real Garnet billed 2.0 seconds for a 2-circuit, 1000-shot job, which is 1.00 credit. The real lane gets floor((7.5 minus 1.0) / (4 times 1.0)) = 1 trial per config. The workflow cap is 6.5 and the reserve is 1.5.

**Physics, first real result (prediction committed at 802b159 before any of this ran).**

| Quantity | Predicted | IQM noise model (IQMFakeGarnet, same 42-CZ circuits, 4000 shots, seed 5) | Real Garnet probe | Ideal (payload) |
|---|---|---|---|---|
| Raw edge, topological | 0.60 ± 0.08 | 0.724 | 0.606 | 0.760 |
| Raw edge, trivial | 0.15 ± 0.06 | 0.210 | 0.339 | 0.145 |
| Post-selected edge, topological | 0.72 ± 0.07 | 0.717 | 0.649 | 0.760 |
| Post-selected edge, trivial | 0.15 ± 0.06 | 0.159 | 0.264 | 0.145 |
| One-excitation share, topological | 0.70 ± 0.10 | 0.502 | 0.524 | 1.000 |
| One-excitation share, trivial | 0.70 ± 0.10 | 0.528 | 0.535 | 1.000 |
| Raw ratio, topological over trivial | 3 or more | 3.45 | 1.79 | 5.24 |

The headline call missed on the probe. The edge state stayed visible (0.606 against 0.339), but the contrast fell to 1.79, below the predicted 3. Agent trials add more real data.

Dry run `wf_dd9c267c-1c6` (r05dry, 3 cells, 12 agents, 5.6 minutes): A-T19 passed. D-T20 failed only on the grader's double-occupancy definition, which was fixed (spec/disagreements.md). C-T21 failed only on the real-QPU checks, as designed, because its real step went to the mock. All 3 judges and all 3 explanation judges returned. 0 credits.

## Round 5 real-QPU spend (run `wf_8040e0a9-69b`, about 22:37Z to 23:13Z)

| Item | Value | Source |
|---|---|---|
| Real jobs reported | 4 on `garnet`, all T21, one per config. Each had 2 circuits and 1000 shots | Grade files |
| Billed seconds | 1.0 for every trial job. The setup probe of the same shape billed 2.0 | IQM API `metrics.billed_seconds` |
| Workflow estimate | 2.00 credits | 4 jobs at 0.50 |
| Dashboard after the run (23:2xZ) | Balance 4.80. Credit history: "- 3.00 IQM Garnet, 5 jobs" for the day | Account page and Credits page |

**Result:** 1.00 for the probe plus 4 jobs at 0.50 is 3.00, which matches the dashboard. Round 5 spent 3.00 of its 7.5 cap. The credit gate skipped no trial.

## Job reconciliation (round 5)

The dashboard Jobs list, paged with its next button, showed 61 jobs created since the first r05 setup job (22:28Z). The known set was 61: 11 from setup, 4 from the dry run, and 46 reported by r05 trials. Every dashboard suffix matched a reported job, and every reported job appeared on the dashboard. **0 unreported jobs.** The `?page=N` URL parameter does not page the list. It always returns page 1.

## Round 5 real physics (SSH edge state, 8 sites, t = 2, 1000 shots, calibration `f81c45da` for all 5 jobs)

| Job | Edge qubit | CZ per circuit | Raw edge, topological | Raw edge, trivial | Ratio | Post-selected, topological | Post-selected, trivial | One-excitation share (topo, triv) |
|---|---|---|---|---|---|---|---|---|
| Setup probe | QB1 | 42 | 0.606 | 0.339 | 1.79 | 0.649 | 0.264 | 0.524, 0.535 |
| r05-A-T21-1 | QB4 | 50 | 0.786 | 0.192 | 4.09 | 0.821 | 0.132 | 0.672, 0.672 |
| r05-B-T21-1 | QB20 | 42 | 0.731 | 0.164 | 4.46 | 0.726 | 0.140 | 0.705, 0.722 |
| r05-C-T21-1 | QB7 | 32 | 0.660 | 0.293 | 2.25 | 0.642 | 0.241 | 0.559, 0.551 |
| r05-D-T21-1 | QB3 | 28 | 0.683 | 0.188 | 3.63 | 0.720 | 0.168 | 0.775, 0.792 |
| Mean of 5 | | | 0.693 | 0.235 | 3.25 (median 3.63) | 0.712 | 0.189 | 0.647, 0.654 |

The edge qubit's T1 and readout error in set `f81c45da` do not explain the spread. QB1 (worst) and QB4 (second best) have similar T1 (24.8 and 22.4 microseconds) and readout fidelity (0.989 and 0.992).

## Round 6 setup (2026-10-22)

Balance before setup: 4.80 (round 5 close-out). Cap: 4.80 including the probe (user decision).

| Task | Jobs | QPU | Purpose | Credits |
|---|---|---|---|---|
| T22 | `01a163db-8bf2-771c-b979-a979f8f76aa2` | emerald:mock | Oracle, 4 circuits of 255 CZ, 250 shots | 0 |
| T22 | `01a163db-a281-70e4-8b60-f33eaab1499a` | emerald:mock | Negative, theta doubled | 0 |
| T22 | `01a163db-b23c-7439-80ba-468af3653dc8` | emerald:mock | Negative, one CZ layer of step 2 dropped | 0 |

Gate 1: selftest 71 of 71 as expected. Gate 2: r05 regraded under the r06 grader gives 42 of 44, the same as the fixed-grader r05 result.

**Calibration-product baseline** (set `3a1a9ad0`, computed after prediction r06 was committed at 18c1292, before the probe). Median IRB CZ fidelity 0.9972, median readout assignment error 0.0121.

| theta / pi | Exact (light cone) | Calibration product |
|---|---|---|
| 0 | 1.000 | 0.972 |
| 0.2 | 0.452 | 0.408 |
| 0.35 | 0.113 | 0.103 |
| 0.5 | 0.000 | 0.000 |

The real Emerald architecture lists 85 couplers. The mock lists 90. The helper's `arch` command shows 83, because QB44-QB50 and QB50-QB51 use the non-default `crf_acstarkcrf` implementation. The grader accepts either the 85 or the 83 list.

**Real probe (gate 5).** Mock test `01a163de-cede-7319-9eee-68d37bd8643d` (emerald:mock, 0 credits), then real job `01a163de-dc2d-7114-b082-68e9ace8ee3b` on `emerald`, created 13:48:32Z. Calibration `3a1a9ad0`. 4 circuits of 255 CZ on all 54 qubits, 250 shots each. Execution took 6.97 s and the API billed **8.0 seconds, an estimated 6.00 credits at 0.75 per second**. That is more than the 4.80 cap and more than the 4.80 balance. The server ran the job anyway. The prediction was 1.0 to 2.0 billed seconds, from Garnet's 1.0 s for 2 circuits of 1000 shots. **HALT:** the probe crossed the round's credit cap. The dashboard balance could not be read, because the Resonance login page appeared. Gate 6 gives 0 real agent trials.

| theta / pi | Exact | Calibration product | Real Emerald raw | Rescaled by theta = 0 |
|---|---|---|---|---|
| 0 | 1.000 | 0.972 | 0.987 | 1.000 |
| 0.2 | 0.452 | 0.408 | 0.476 | 0.482 |
| 0.35 | 0.113 | 0.103 | 0.154 | 0.156 |
| 0.5 | 0.000 | 0.000 | 0.031 | 0.032 |

The raw values sit above exact at every nonzero field. Decay toward 0 (amplitude damping) pushes Z up, so noise did not shrink the signal toward 0 as the prediction assumed.

**Dashboard after the probe (about 13:55Z, user signed in).** Balance **−1.20 credits**. Credit history: "− 6.00 IQM Emerald | 1 jobs, Pay-as-you-go" on 22 Oct. So the 6.00 estimate matched the charge exactly, and Resonance lets a Starter balance go below zero. The page says "Need more credits? Contact your IQM Sales person to top up."
