# Xi — Integration Contract v1

## Scope
Offline static web modules (HTML/JS/CSS, Canvas, or tested self-contained web exports). No native executables, online MMORPG backend or nested PWA. Godot Web exports must pass Safari/iPhone compatibility and dependency checks before release; threaded exports that require special headers are not assumed to work on GitHub Pages. HUYỀN ẢNH and MMORPG remain planned. Only trusted, reviewed code may execute on the same origin: save names are a convention, not sandbox isolation.

## Steps for a completed game
1. Copy reviewed, licensed web build to `site/games/<id>/`. Include asset licenses in the module inventory where required. Use only relative, same-module URLs for game resources; test all dynamic assets (including audio/fonts/WASM). Entry is `games/<id>/index.html` and exit destination is `../../`. Save successfully before exiting; test exit during a game and during dialogs. No duplicate service worker registration or manifest. No absolute root path, remote runtime dependency, secrets, server executable, or cross-game storage access. Manual code review is required; the validator cannot infer all dynamically computed paths or storage operations.
2. Add a local cover under `site/assets/`. Released-game covers are automatically included in the hub shell cache. No new module is enabled merely by adding a folder. Draft modules stay outside `site/games/` until approved.
3. Add one record in `integration/games.json` using the example below; `files` includes every regular file inside the module. IDs are stable ASCII lowercase, versions numeric 2/3-part strings. Declare the exact storage keys with prefix `xi:game:<id>:`. Legacy exceptions: `thien-thu-v8`, `thien-thu-v8-recovery`. Preserve save/entry contracts across versions; changing them requires a separately approved migration. Preserve backward save compatibility when a cached older version can launch; do not assume rollback of resources rolls back saves.
4. Run `npm run catalog:build` then `npm test`. Generated `site/catalog-data.js` is the only runtime catalog; never edit it manually. The baseline `integration/release-baseline.json` captures the previous approved release. Do not change it to bypass validation; update it only after approval, retaining old release evidence. Version bumps are required for changed bytes. Hub changes require a new hubVersion and deployment archive. Source validation also rejects unknown module folders, traversal, symlinks, incomplete inventory, collisions, illegal planned launch metadata and unapproved removal of a released game.
5. Run game-specific functional/regression tests, UI at 320/390/844/1280px, real service worker browser acceptance, real Safari/iPhone offline + resume + remove/redownload + update while closed, and two-tab tests. Measure storage and memory on actual devices. Test failed downloads and digest mismatch. Use separate staging origin/scope; do not assume staging shares production saves. Export/restore test saves and test original V9.0 -> current Foundation. Each newly released game needs additional browser acceptance beyond Legacy's existing test.
6. Update baseline on approved release, archive only contents of `site/` for Pages, pin archive SHA-256 in CI and publish on `main` only after all acceptance gates and explicit release approval. Keep full source/fixtures private or as separate backups. Do not overwrite existing stable production until acceptance passes.

## Example (documentation only; not a playable game)
```json
{
  "id": "new-game",
  "title": "Tên trò chơi",
  "subtitle": "Subtitle",
  "genre": "Hành động 2D",
  "description": "Mô tả ngắn",
  "status": "released",
  "version": "1.0",
  "offline": true,
  "runtime": "static-web",
  "contract": 1,
  "entry": "games/new-game/index.html",
  "returnToHub": "../../",
  "cover": "assets/new-game.webp",
  "save": {"namespace": "xi:game:new-game:", "keys": ["xi:game:new-game:save"]},
  "files": ["games/new-game/index.html"]
}
```
The generator calculates integrity; do not supply SHA values manually. For a planned game only use id/title/subtitle/genre/status/description. The same-origin contract does not support untrusted community submissions. Online modules require a separate contract and backend; no credentials are embedded in static files.
