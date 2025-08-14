import os, json, zipfile, pathlib, sys
try:
    import yaml
except ImportError:
    print("Missing PyYAML; install with: pip install pyyaml")
    sys.exit(1)

PACK_YAML = "packs/qpcr-starter/pack.yaml"

def build():
    with open(PACK_YAML, "r", encoding="utf-8") as f:
        pack = yaml.safe_load(f)

    out_dir = pathlib.Path("dist/packs"); out_dir.mkdir(parents=True, exist_ok=True)
    zip_name = f"{pack['id']}-v{pack['version']}.zip"
    zip_path = out_dir / zip_name

    manifest = {
        "id": pack["id"],
        "version": pack["version"],
        "title": pack.get("title"),
        "license": pack.get("license", "RUO"),
        "files": {}
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for entry in pack["files"]:
            src = entry["path"]
            dst = entry.get("as", src)
            if not os.path.exists(src):
                raise FileNotFoundError(f"Missing file for pack: {src}")
            z.write(src, dst)
            manifest["files"][dst] = {"src": src}
        z.writestr("manifest.json", json.dumps(manifest, indent=2))

    print(f"✅ Built {zip_path}")

if __name__ == "__main__":
    build()
