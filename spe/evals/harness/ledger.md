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
