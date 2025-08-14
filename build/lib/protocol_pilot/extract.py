from __future__ import annotations
import re
import json
import click
from pathlib import Path
from markdown_it import MarkdownIt
from .schema import Protocol, Step, Reagent, validate_protocol

md = MarkdownIt()

RUO_PREFIX = "Research Use Only (RUO)."

def parse_markdown(md_text: str) -> Protocol:
    # Very light parser for the example template
    title_match = re.search(r"^#\s+(.+)$", md_text, re.M)
    title = title_match.group(1).strip() if title_match else "Untitled Protocol"

    sources = re.findall(r"^\*\*Sources\*\*:([^\n]+)$", md_text, re.M)
    sources = [s.strip() for s in ",".join(sources).split(",") if s.strip()] or []

    equipment_section = re.search(r"## Equipment\n([\s\S]*?)\n##", md_text)
    equipment = []
    if equipment_section:
        equipment = [l.strip("- ") for l in equipment_section.group(1).splitlines() if l.strip().startswith("-")]

    reagents_section = re.search(r"## Reagents[\s\S]*?\n([\s\S]*?)\n##", md_text)
    reagents = []
    if reagents_section:
        for l in reagents_section.group(1).splitlines():
            if l.strip().startswith("-"):
                name = l.strip("- ").strip()
                reagents.append(Reagent(name=name))

    # Steps
    steps = []
    for i, m in enumerate(re.finditer(r"^\d+\.\s+(.+)$", md_text, re.M), start=1):
        steps.append(Step(number=i, description=m.group(1).strip()))

    # Safety
    safety = []
    safety_sec = re.search(r"## Safety notes\n([\s\S]*?)\n##|$", md_text)
    if safety_sec:
        for l in safety_sec.group(1).splitlines():
            if l.strip().startswith("-"):
                safety.append(l.strip("- ").strip())

    disclaimer = "Research Use Only (RUO). Not for use in diagnostic procedures or patient care."

    return Protocol(
        title=title,
        sources=sources,
        equipment=equipment,
        reagents=reagents,
        steps=steps,
        safety_notes=safety,
        ruo_disclaimer=disclaimer,
    )

@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--validate", "do_validate", is_flag=True, help="Validate after parsing")
@click.option("--json-out", "json_out", is_flag=True, help="Print JSON to stdout")
def main(path, do_validate, json_out):
    text = Path(path).read_text(encoding="utf-8")
    proto = parse_markdown(text)
    if do_validate:
        validate_protocol(proto)
    if json_out:
        click.echo(proto.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
