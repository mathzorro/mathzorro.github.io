#!/usr/bin/env python3
"""Create (or fetch existing) Dropbox share links for files under Dropbox/webfiles
and record them as direct, inline-rendering URLs in webfiles.json.

Usage:
  tools/dropbox_links.py check                 # verify the token works
  tools/dropbox_links.py link <path> [...]     # e.g. research/talks/AxiDraw-slides.pdf
  tools/dropbox_links.py link-dir <dir>        # every file under webfiles/<dir>

Paths are relative to the webfiles folder and mirror the repo layout.
The token is read from ~/.config/dropbox/token (never from the repo).
"""
import json, os, sys, urllib.request, urllib.error

TOKEN_FILE = os.path.expanduser("~/.config/dropbox/token")
WEBFILES_LOCAL = os.path.expanduser("~/Library/CloudStorage/Dropbox/webfiles")
WEBFILES_REMOTE = "/webfiles"
MANIFEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webfiles.json")


def token():
    try:
        return open(TOKEN_FILE).read().strip()
    except FileNotFoundError:
        sys.exit(f"No token at {TOKEN_FILE}. See setup notes.")


def api(endpoint, body):
    req = urllib.request.Request(
        f"https://api.dropboxapi.com/2/{endpoint}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{endpoint} failed ({e.code}): {e.read().decode()}")


def to_raw(url):
    """Turn a share link into one that renders inline (no preview page)."""
    url = url.replace("&dl=0", "").replace("?dl=0", "")
    return url + ("&" if "?" in url else "?") + "raw=1"


def share_link(rel_path):
    remote = f"{WEBFILES_REMOTE}/{rel_path}"
    existing = api("sharing/list_shared_links", {"path": remote, "direct_only": True})
    if existing["links"]:
        return existing["links"][0]["url"]
    created = api("sharing/create_shared_link_with_settings",
                  {"path": remote, "settings": {"requested_visibility": "public"}})
    return created["url"]


def load_manifest():
    return json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}


def save_manifest(m):
    json.dump(dict(sorted(m.items())), open(MANIFEST, "w"), indent=2)
    print(f"wrote {len(m)} entries to {MANIFEST}")


def main(argv):
    if not argv or argv[0] not in ("check", "link", "link-dir"):
        sys.exit(__doc__)
    if argv[0] == "check":
        me = api("users/get_current_account", {})
        print("token OK for", me["email"])
        return
    if argv[0] == "link":
        paths = argv[1:]
    else:
        root = os.path.join(WEBFILES_LOCAL, argv[1])
        paths = sorted(
            os.path.relpath(os.path.join(d, f), WEBFILES_LOCAL)
            for d, _, fs in os.walk(root) for f in fs if not f.startswith(".")
        )
    manifest = load_manifest()
    for p in paths:
        if p in manifest:
            print(f"have  {p}")
            continue
        manifest[p] = to_raw(share_link(p))
        print(f"link  {p}")
    save_manifest(manifest)


if __name__ == "__main__":
    main(sys.argv[1:])
