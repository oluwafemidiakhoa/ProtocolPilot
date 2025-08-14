from __future__ import annotations
import json
import click
from pathlib import Path
from slugify import slugify
from .extract import parse_markdown

DEFAULT_ALTS = [
    {"vendor": "Vendor A", "catalog_number": "TBD"},
    {"vendor": "Vendor B", "catalog_number": "TBD"},
]

@click.command()
@click.argument("protocol_md", type=click.Path(exists=True))
@click.option("--out", "out_path", type=click.Path(), help="Output JSON file")
def main(protocol_md, out_path):
    proto = parse_markdown(Path(protocol_md).read_text(encoding="utf-8"))
    items = []
    for r in proto.reagents:
        items.append({
            "name": r.name,
            "amount": r.amount,
            "unit": r.unit,
            "alternatives": DEFAULT_ALTS,
        })
    payload = {"protocol": slugify(proto.title), "items": items}
    if out_path:
        Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
