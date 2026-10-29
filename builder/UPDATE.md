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
GitHub Pages republishes https://asayedhalim91-sudo.github.io/SBARC2026/ within a few minutes of the push.

## 5. Report
One or two lines: published or no change, the status date, and any dashboard that failed to download.
Never print the password or any dashboard figures in the report. Never commit builder/_data.
