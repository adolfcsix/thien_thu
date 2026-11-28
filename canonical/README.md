# Xi Universe F1.21 — consolidated source candidate
Run Node 22+ and Python 3.12+.
- npm test — catalog, integrity and unit tests.
- npm start — local web server on port 8000.
- python tools/verify-source.py . — verify snapshot inventory.
- python -m pip install playwright
- python -m playwright install chromium webkit
- python tests/browser.py --engine chromium --site site
- python tests/browser.py --engine webkit --site site

Maintain site/ and integration/ directly. For subsequent releases, increment affected versions, regenerate catalog, worker integrity and offline kit, and refresh the snapshot manifest after testing. Historical V9 and four-game migration suites remain in the parent repository. This candidate requires all browser and deployment gates.
