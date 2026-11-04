# Time Kings assets

Models and textures for Time Kings Jurassic. Poly Haven assets (CC0) are fetched by GitHub Actions from requests.txt (tools/fetch.py); models found elsewhere go in incoming/ with their licence.

## How it is used

- `requests.txt`: one request a line (`polyhaven <id> [1k|2k|4k]`, `catalog models|textures|hdris`,
  `url <https://...> <path>`); pushing it starts the fetch (`.github/workflows/fetch.yml`, `tools/fetch.py`), whose
  results are committed back here. `fetched.log` lists what is done.
- `incoming/`: models found by hand (a Sketchfab zip as it comes, with its licence), for Claude to take into the game.
- The game (Time Kings Jurassic) copies what it uses into its own folder: heavy models simplified with gltfpack, the
  machete and hatchet turned to be held (`held_models.py` in the game), and the list of authors in its `CREDITS.txt`.
