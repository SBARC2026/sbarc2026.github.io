# Daily update runbook (followed by the scheduled task)

Repository root = the folder this file's parent sits in (e.g. /home/claude/sbarc2026). Use absolute paths in tool calls.

## 1. Start clean
- `git fetch origin main && git reset --hard origin/main`
- `rm -rf builder/_data && mkdir -p builder/_data`

## 2. Download both dashboards (tools: ArtifactData, Artifact)
For each dashboard:

| id   | url                                              |
|------|--------------------------------------------------|
| exec | https://claude.ai/artifact/UGmYsefN6QhW1Mt17uqpRS |
| p02b | https://claude.ai/artifact/88dbsUWtiu6vG7kdgZB7dK |

1. `ArtifactData` action `list`, collection `datasets`, out_dir `<root>/builder/_data/<id>`
2. `ArtifactData` action `list`, collection `files`, out_dir `<root>/builder/_data/<id>`
3. `ArtifactData` action `list`, collection `dash`, out_dir `<root>/builder/_data/<id>` (may be empty; that is fine)

Then run `python3 builder/build.py --needs`. It prints every data file still missing as JSON, each with
`url`, `path` and `out_dir`. Download each one with the `Artifact` tool: action `read`, `url`, `path` (the id),
out_dir `<root>/<out_dir>`. Repeat `--needs` until it prints `[]` (it can add the site-plan image after the first round).

## 3. Build
`pip install --break-system-packages -q pypdf` (needed for the PDF menu), then
`SBARC_PASSWORD='<password from the task prompt>' SBARC_UPDATE_EMAIL='<email from the task prompt>' python3 builder/build.py`

The build is deterministic: unchanged figures give a byte-identical `docs/`.
It also renders the two full-report PDFs (about a minute) into `docs/pdf/`, encrypted with the portal password,
but only when the figures changed. If it prints `WARNING: PDFs not rebuilt`, the site is still fine: the previous
PDFs stay in place with their own status date. Mention the warning in the report.

## 4. Publish only if something changed
```
git add docs
git diff --cached --quiet && echo "No change in the dashboards; nothing to publish." && exit 0
git commit -m "Update dashboards: $(python3 -c 'import json;v=json.load(open("docs/version.json"));print("status",v["status"],"· data",v["data_updated"])')"
git push origin HEAD:main
```
GitHub Pages republishes https://sbarc2026.github.io/ within a few minutes of the push.

## 5. Report
One or two lines: published or no change, the status date, and any dashboard that failed to download.
Never print the password or any dashboard figures in the report. Never commit builder/_data.

## Weekly Primavera (P6) export
When a new "This Week" P6 export (.xlsx) arrives, convert it before step 3 (build). It replaces the previous week's file:
`SBARC_PASSWORD='<password>' python3 builder/tools/p6_import.py <export.xlsx> --date <data date YYYY-MM-DD> [--week-end <plan Friday>] [--name "<file title>"]`
This writes `builder/p6/p6.bin` (encrypted with the portal password; the repository is public, never commit the readable figures).
The build then (a) sets the earned value of that reporting week in Management Tracking from the export, for all 81 activities, unless the dashboard
already holds a later week, and (b) shows the Primavera tab (overview charts, trade groups, villas and buildings, activity list).
Commit `builder/p6/p6.bin` together with `docs/`. The daily scheduled rebuild keeps using the committed file.

## Weekly P6 schedule (.xer) for the Gantt
`SBARC_PASSWORD='<password>' python3 builder/tools/xer_import.py <schedule.xer>` writes `builder/p6/gantt.bin` (encrypted). The build copies it to
`docs/p6/gantt.bin`, and the Primavera tab's Gantt fetches and decrypts it when opened (WBS tree, activity bars from actual / forecast dates, baseline = target
dates, critical = total float <= 0, % complete from the weekly export's earned units where the activity ID matches). Commit `builder/p6/gantt.bin` with `docs/`.

## Daily Progress Report (DPR) workbook -> Executive Summary data
`python3 builder/tools/dpr_import.py <DPR.xlsx> --src builder/_data/exec/blobs --out <dir> --date DD-MM-YYYY` rewrites the villas,
villa_activities, buildings, manpower, activities (villa rows) and layouts (villa rows, building statuses) blobs from the Villa Status,
Building Status and MP sheets, and cross-checks every count against the workbook's own summary sheets. Upload each result to the exec
dashboard (Artifact `publish` asset:true, then ArtifactData `update` of the dataset doc: source.url, description, updated), because the
daily task re-downloads from there. Landscape rows and the building-only rows are not in the DPR and stay as they were. The villa sheet
may carry a duplicate villa code (R1-03 twice, the second is R1-04); the tool keeps the dashboard's villa list and reports it.
Hard-coded dates in the page (`files/index.html`: site-status chip, buildings note, footer) are edited with ArtifactData str_replace.

## BOQ tab (items and amounts)
`SBARC_PASSWORD=... python3 builder/tools/boq_import.py <"SBARC Rules of Credit" artifact .html or boq.json>` rewrites `builder/boq/boq.bin`
(encrypted with the portal password; the repo is public, so amounts are never committed readable). `build.py` adds the "BOQ items & amounts" tab
when the file exists. Source: artifact https://claude.ai/artifact/Ps17om7Dv51covX5eGw4gz (BOQ 5.3 - IPA 24 B.O.Q. Break R00). Re-run only when the BOQ changes.

## November plan tab
The "November plan" tab (pinned) is computed on every build by `nov_data()` in `build.py` from the latest `villas` and `villa_activities` rows and the settings in `builder/nov_plan.json` (clusters, waves, start/end dates, weeks, villas per crew per week). Nothing to do on a daily update; edit `nov_plan.json` only if the plan itself changes.
