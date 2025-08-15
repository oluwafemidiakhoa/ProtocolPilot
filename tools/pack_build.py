#!/usr/bin/env python3
import os
import sys
import json
import glob
import hashlib
import zipfile
import pathlib
from typing import Dict, List, Tuple

try:
    import yaml  # PyYAML
except ImportError:
    print("Missing PyYAML; install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------- helpers ----------

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo/ (tools/ is under repo/)
DIST_DIR = REPO_ROOT / "dist" / "packs"
DEFAULT_DISCOVERY = str(REPO_ROOT / "packs" / "*" / "pack.yaml")


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_arcname(s: str) -> str:
    """Ensure forward slashes inside zip (Windows-safe)."""
    return s.replace("\\", "/")


def load_pack_yaml(pack_yaml_path: pathlib.Path) -> Dict:
    with open(pack_yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{pack_yaml_path}: pack.yaml must be a mapping")
    return data


def resolve_files(pack_yaml_path: pathlib.Path, pack_cfg: Dict) -> List[Tuple[pathlib.Path, str]]:
    """
    Return list of (src_path, arcname) tuples to include in the zip.
    Supports either:
      - files:
          - path: ...
            as: optional_name
      - or:
        source_dir: subfolder
        include:
          - file1
          - dir/file2
    """
    base_dir = pack_yaml_path.parent  # packs/<name>/
    items: List[Tuple[pathlib.Path, str]] = []

    if "files" in pack_cfg:
        files = pack_cfg["files"] or []
        if not isinstance(files, list):
            raise ValueError(f"{pack_yaml_path}: 'files' must be a list")
        for entry in files:
            if not isinstance(entry, dict) or "path" not in entry:
                raise ValueError(f"{pack_yaml_path}: each files[] needs 'path'")
            src = (base_dir / entry["path"]).resolve()
            if not src.exists():
                raise FileNotFoundError(f"Missing file: {src}")
            arc = entry.get("as", entry["path"])
            items.append((src, norm_arcname(arc)))
        return items

    # source_dir + include
    source_dir = pack_cfg.get("source_dir")
    include = pack_cfg.get("include", [])
    if source_dir is None or not include:
        raise ValueError(
            f"{pack_yaml_path}: provide either 'files' or both 'source_dir' and 'include'"
        )
    src_root = (base_dir / source_dir).resolve()
    if not src_root.exists():
        raise FileNotFoundError(f"source_dir not found: {src_root}")

    if not isinstance(include, list):
        raise ValueError(f"{pack_yaml_path}: 'include' must be a list of paths")
    for rel in include:
        src = (src_root / rel).resolve()
        if not src.exists():
            raise FileNotFoundError(f"Missing file listed in include: {src}")
        # arcname should be relative to source_dir root
        arc = norm_arcname(rel)
        items.append((src, arc))

    return items


def infer_id(pack_yaml_path: pathlib.Path, cfg: Dict) -> str:
    # Priority: id -> slug -> name -> folder name
    for key in ("id", "slug", "name"):
        val = cfg.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().replace(" ", "-")
    return pack_yaml_path.parent.name  # packs/<folder>/


def infer_version(cfg: Dict) -> str:
    v = cfg.get("version", "1.0.0")
    if not isinstance(v, str) or not v.strip():
        raise ValueError("version must be a non-empty string")
    return v.strip()


def infer_output_path(cfg: Dict, pack_id: str, version: str) -> pathlib.Path:
    out = cfg.get("output")
    if out:
        return (REPO_ROOT / out).resolve()
    return DIST_DIR / f"{pack_id}-v{version}.zip"


# ---------- build ----------

def build_one(pack_yaml: pathlib.Path) -> pathlib.Path:
    cfg = load_pack_yaml(pack_yaml)
    pack_id = infer_id(pack_yaml, cfg)
    version = infer_version(cfg)
    title = cfg.get("title", pack_id)
    license_text = cfg.get("license", "RUO")

    files = resolve_files(pack_yaml, cfg)

    out_zip = infer_output_path(cfg, pack_id, version)
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "id": pack_id,
        "version": version,
        "title": title,
        "license": license_text,
        "source_pack_yaml": str(pack_yaml.relative_to(REPO_ROOT)),
        "files": {}  # arcname -> {src,size,sha256}
    }

    # Create zip
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Write files (keep stable order)
        for src, arc in sorted(files, key=lambda t: t[1].lower()):
            info = {
                "src": str(src.relative_to(REPO_ROOT)),
                "size": src.stat().st_size,
                "sha256": sha256_of(src),
            }
            z.write(src, arcname=arc)
            manifest["files"][arc] = info

        # Write manifest.json last
        z.writestr("manifest.json", json.dumps(manifest, indent=2))

    print(f"Built {out_zip}")
    return out_zip


def build_many(paths: List[str]) -> int:
    # Expand globs; default discover packs/*/pack.yaml
    if not paths:
        paths = [DEFAULT_DISCOVERY]
    pack_files: List[pathlib.Path] = []
    for pat in paths:
        pack_files.extend(pathlib.Path(p) for p in glob.glob(pat, recursive=True))

    if not pack_files:
        print("No pack.yaml found. Try: python tools/pack_build.py packs/*/pack.yaml", file=sys.stderr)
        return 1

    rc = 0
    for pack_yaml in pack_files:
        try:
            build_one(pack_yaml)
        except Exception as e:
            rc = 2
            print(f"[ERROR] {pack_yaml}: {e}", file=sys.stderr)
    return rc


# ---------- main ----------

if __name__ == "__main__":
    # Run from repo root or tools/; normalize CWD to repo root
    os.chdir(REPO_ROOT)
    sys.exit(build_many(sys.argv[1:]))
