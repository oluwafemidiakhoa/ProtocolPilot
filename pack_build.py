import json, yaml, shutil, hashlib, os, pathlib, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
DIST  = ROOT / "dist" / "packs"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def build_one(pack_dir: pathlib.Path):
    meta = yaml.safe_load((pack_dir/"pack.yaml").read_text())
    slug = meta["slug"]; version = meta["version"]
    outdir = DIST; outdir.mkdir(parents=True, exist_ok=True)
    zip_path = outdir / f"{slug}-v{version}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in ["pack.yaml","RUO_LICENSE.txt"]:
            z.write(pack_dir/rel, rel)
        for sub in ["protocols","bom","prompts"]:
            for p in (pack_dir/sub).rglob("*"):
                if p.is_file():
                    z.write(p, str(p.relative_to(pack_dir)))
        # generated manifest for buyers
        manifest = {
            "name": meta["name"], "slug": slug, "version": version,
            "files": [str(p) for p in z.namelist()]
        }
        z.writestr("manifest.json", json.dumps(manifest, indent=2))

    (outdir / "checksums.txt").write_text(
        f"{sha256(zip_path)}  {zip_path.name}\n", encoding="utf-8"
    )
    print(f"Built {zip_path}")

def main():
    for p in PACKS.iterdir():
        if (p/"pack.yaml").exists():
            build_one(p)

if __name__ == "__main__":
    main()
