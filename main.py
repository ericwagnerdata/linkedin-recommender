import sys
from pathlib import Path

import click

from pipeline import add_person, get_person, list_people, mark_completed, update_people_file
from recommender import ask_questions, generate_recommendation


@click.group()
def cli():
    """LinkedIn Recommendation Writer — track your pipeline and generate recommendations."""
    pass


@cli.command()
@click.argument("name")
@click.option("--url", default="", help="LinkedIn profile URL (optional, can be added later).")
def add(name, url):
    """Add a person to your recommendation pipeline."""
    person, error = add_person(name, url)
    if error:
        click.echo(f"Error: {error}")
        sys.exit(1)
    click.echo(f"Added {person['name']} to the pipeline.")


@cli.command("batch-add")
def batch_add():
    """Add multiple people at once.

    Enter one per line as either:
      Full Name
      Full Name | LinkedIn URL

    Press Enter on a blank line when done.
    """
    click.echo("Enter one person per line:  Full Name  or  Full Name | LinkedIn URL")
    click.echo("Press Enter on a blank line when done.\n")

    added = []
    skipped = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        if "|" in line:
            parts = [p.strip() for p in line.split("|", 1)]
            name, url = parts[0], parts[1] if len(parts) > 1 else ""
        else:
            name, url = line, ""

        if not name:
            continue

        person, error = add_person(name, url)
        if error:
            click.echo(f"  Skipped {name}: {error}")
            skipped.append(name)
        else:
            click.echo(f"  Added: {name}")
            added.append(name)

    click.echo(f"\nDone. Added {len(added)}, skipped {len(skipped)}.")
    click.echo("PIPELINE.md has been updated.")


@cli.command()
@click.argument("name")
@click.option(
    "--profile",
    default=None,
    help="Path to a LinkedIn screenshot (.png/.jpg) or text file for this session only.",
)
def write(name, profile):
    """Write a recommendation for someone in your pipeline."""
    person = get_person(name)
    if not person:
        click.echo(f"'{name}' not found in pipeline. Use 'add' to add them first.")
        sys.exit(1)

    if person["status"] == "completed":
        click.echo(f"A recommendation for {person['name']} already exists.")
        click.echo(f"File: {person['people_file']}")
        if not click.confirm("Generate a new one and overwrite?", default=False):
            return

    click.echo(f"\nWriting recommendation for: {person['name']}")
    if person.get("linkedin_url"):
        click.echo(f"LinkedIn: {person['linkedin_url']}\n")

    profile_input = profile
    if not profile_input:
        click.echo(
            "Paste profile text below (press Enter twice when done), "
            "or just press Enter to skip:"
        )
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        pasted = "\n".join(lines).strip()
        profile_input = pasted if pasted else None

    answers = ask_questions()

    click.echo("Generating recommendation...")
    recommendation = generate_recommendation(
        person["name"],
        person.get("linkedin_url", ""),
        profile_input,
        answers,
    )

    update_people_file(person, answers, recommendation)
    mark_completed(person["id"])

    click.echo(f"\n{'─' * 60}\n")
    click.echo(recommendation)
    click.echo(f"\n{'─' * 60}")
    click.echo(f"\nSaved to: {person['people_file']}")


@cli.command("list")
def list_cmd():
    """Show your full recommendation pipeline."""
    people = list_people()
    if not people:
        click.echo("Your pipeline is empty. Use 'add' to add someone.")
        return

    pending   = [p for p in people if p["status"] == "pending"]
    completed = [p for p in people if p["status"] == "completed"]

    if pending:
        click.echo(f"\nPending ({len(pending)}):")
        for p in pending:
            url_note = f"  [{p['linkedin_url']}]" if p.get("linkedin_url") else "  [no URL yet]"
            click.echo(f"  - {p['name']}{url_note}  (added {p['added_date']})")

    if completed:
        click.echo(f"\nCompleted ({len(completed)}):")
        for p in completed:
            click.echo(f"  - {p['name']}  (done {p['completed_date']})")

    click.echo()


@cli.command()
@click.argument("name")
def show(name):
    """Print everything saved for a person."""
    person = get_person(name)
    if not person:
        click.echo(f"'{name}' not found in pipeline.")
        sys.exit(1)

    people_path = Path(person["people_file"])
    if not people_path.exists():
        click.echo(f"No file found for {person['name']}.")
        sys.exit(1)

    click.echo(people_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    cli()
