#!/usr/bin/env python3
"""Pack design renders / site photos for the Live 3D tab into an encrypted file.

Usage: SBARC_PASSWORD=... python3 builder/tools/v3d_renders.py <folder with index.json and the .jpg files>
index.json: [["<building codes or villa types, space separated>", "<caption>", "<file.jpg>"], ...]
Writes builder/v3d/renders.bin (encrypted with the portal password; the repo is public, never commit the readable images).
"""
import base64, json, os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(here)
src = sys.argv[1]; pw = os.environ['SBARC_PASSWORD']
items = [{'k': k.split(), 't': t, 'src': 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(src, f), 'rb').read()).decode()} for k, t, f in json.load(open(os.path.join(src, 'index.json')))]
tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump({'items': items}, tmp); tmp.close()
os.makedirs(f'{B}/v3d', exist_ok=True)
subprocess.run(['node', f'{B}/encrypt.js', '--bin', tmp.name, pw, f'{B}/v3d/renders.bin'], check=True); os.remove(tmp.name)
print(len(items), 'images ->', f'{B}/v3d/renders.bin')
