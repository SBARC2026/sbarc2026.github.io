# SBARC Project Portal

The live portal is published by GitHub Pages from the `docs/` folder of `main`: **https://asayedhalim91-sudo.github.io/SBARC2026/**

- Open it, type the project name **SBARC** and the portal password.
- All dashboard figures inside `docs/index.html` are encrypted. Without the password the file only shows the entrance page.

## How it stays up to date
Every morning a scheduled task in Claude:
1. reads the latest **Executive Summary** and **Earned Value Progress Control** dashboards,
2. rebuilds `docs/` with `builder/build.py`,
3. commits here only if the figures changed. Netlify then republishes automatically.

To change the figures, update the dashboards in Claude as usual. The site follows the next morning (or ask Claude to run the update now).

`builder/UPDATE.md` holds the exact steps the scheduled task follows.
