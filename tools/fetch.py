"""Time Kings' asset fetcher: runs on GitHub's machines (see .github/workflows/fetch.yml). Each line of requests.txt
not yet in fetched.log is fetched once:

    polyhaven <id> [1k|2k|4k]        a Poly Haven model (its glTF with textures) or texture set, into polyhaven/<id>/
    catalog models|textures|hdris    Poly Haven's list of them, into catalog/<kind>.json
    url <https://...> <path>         a file from a direct link, to that path in this repository

Poly Haven's assets are CC0 (polyhaven.com/license).
"""
import json
import os
import sys
import urllib.request

HEADERS = {"User-Agent": "TimeKings-asset-fetcher/1.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
        return r.read()


def save(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def polyhaven(asset, res="2k"):
    info = json.loads(get(f"https://api.polyhaven.com/info/{asset}"))
    files = json.loads(get(f"https://api.polyhaven.com/files/{asset}"))
    out = f"polyhaven/{asset}"
    if info.get("type") == 2:  # a model: its glTF with the textures it names
        pick = files["gltf"].get(res) or files["gltf"][sorted(files["gltf"])[0]]
        g = pick["gltf"]
        save(f"{out}/{os.path.basename(g['url'])}", get(g["url"]))
        for rel, inc in g.get("include", {}).items():
            save(f"{out}/{rel}", get(inc["url"]))
    else:  # a texture set: its colour, normal (OpenGL) and roughness maps, as JPG where there is one
        for kind in ("Diffuse", "nor_gl", "Rough"):
            if kind not in files:
                continue
            maps = files[kind].get(res) or files[kind][sorted(files[kind])[0]]
            m = maps.get("jpg") or maps.get("png")
            save(f"{out}/{asset}_{kind}_{res}.{m['url'].rsplit('.', 1)[-1]}", get(m["url"]))
    save(f"{out}/info.json", json.dumps({"id": asset, "name": info.get("name"), "authors": info.get("authors"),
                                         "licence": "CC0 (polyhaven.com/license)", "res": res,
                                         "polycount": info.get("polycount"), "dimensions": info.get("dimensions")},
                                        indent=1).encode())


def main():
    done = set(open("fetched.log").read().splitlines()) if os.path.exists("fetched.log") else set()
    lines = [l.strip() for l in open("requests.txt").read().splitlines() if l.strip() and not l.startswith("#")]
    log = open("fetched.log", "a")
    for line in lines:
        if line in done:
            continue
        w = line.split()
        try:
            if w[0] == "polyhaven":
                polyhaven(w[1], w[2] if len(w) > 2 else "2k")
            elif w[0] == "catalog":
                save(f"catalog/{w[1]}.json", get(f"https://api.polyhaven.com/assets?t={w[1]}"))
            elif w[0] == "url":
                save(w[2], get(w[1]))
            log.write(line + "\n")
            print("fetched", line)
        except Exception as e:  # (one that fails is said and left for next time)
            print("FAILED", line, e, file=sys.stderr)
            log.write(f"# failed: {line}: {e}\n")
    log.close()


if __name__ == "__main__":
    main()
