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
