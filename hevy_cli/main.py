"""Hevy CLI -- interact with the Hevy fitness app from your terminal."""

from __future__ import annotations

import json
import os
import sys

import click
import httpx
from rich.console import Console

from hevy_cli.client import HevyClient
from hevy_cli import display

console = Console(stderr=True)

# Shared enum values (match the Hevy API spec)
EXERCISE_TYPES = [
    "weight_reps", "reps_only", "bodyweight_reps", "bodyweight_assisted_reps",
    "duration", "weight_duration", "distance_duration", "short_distance_weight",
]
EQUIPMENT_CATEGORIES = [
    "none", "barbell", "dumbbell", "kettlebell", "machine",
    "plate", "resistance_band", "suspension", "other",
]
MUSCLE_GROUPS = [
    "abdominals", "shoulders", "biceps", "triceps", "forearms",
    "quadriceps", "hamstrings", "calves", "glutes", "abductors",
    "adductors", "lats", "upper_back", "traps", "lower_back",
    "chest", "cardio", "neck", "full_body", "other",
]
SET_TYPES = ["warmup", "normal", "failure", "dropset"]


def _get_client(ctx: click.Context) -> HevyClient:
    return ctx.obj["client"]


def _handle_api_error(e: httpx.HTTPStatusError) -> None:
    try:
        body = e.response.json()
    except Exception:
        body = e.response.text
    console.print(f"[red]API error {e.response.status_code}:[/red] {body}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Top-level group
# ---------------------------------------------------------------------------


@click.group()
@click.option(
    "--api-key",
    envvar="HEVY_API_KEY",
    required=True,
    help="Hevy API key (or set HEVY_API_KEY env var).",
)
@click.option("--json-output", "-j", is_flag=True, help="Print raw JSON instead of tables.")
@click.pass_context
def cli(ctx: click.Context, api_key: str, json_output: bool) -> None:
    """CLI for the Hevy fitness app API."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = HevyClient(api_key)
    ctx.obj["json"] = json_output


# ---------------------------------------------------------------------------
# Workouts
# ---------------------------------------------------------------------------


@cli.group()
def workouts() -> None:
    """Manage workouts."""


@workouts.command("list")
@click.option("--page", default=1, type=int, help="Page number (default 1).")
@click.option("--page-size", default=5, type=click.IntRange(1, 10), help="Items per page (1-10, default 5).")
@click.pass_context
def workouts_list(ctx: click.Context, page: int, page_size: int) -> None:
    """List workouts (newest first)."""
    try:
        data = _get_client(ctx).get_workouts(page, page_size)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_workouts(data)


@workouts.command("get")
@click.argument("workout_id")
@click.pass_context
def workouts_get(ctx: click.Context, workout_id: str) -> None:
    """Get a single workout by ID."""
    try:
        data = _get_client(ctx).get_workout(workout_id)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_workout_detail(data)


@workouts.command("count")
@click.pass_context
def workouts_count(ctx: click.Context) -> None:
    """Get total workout count."""
    try:
        data = _get_client(ctx).get_workout_count()
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_workout_count(data)


@workouts.command("events")
@click.option("--page", default=1, type=int)
@click.option("--page-size", default=5, type=click.IntRange(1, 10))
@click.option("--since", default="1970-01-01T00:00:00Z", help="ISO-8601 datetime to filter from.")
@click.pass_context
def workouts_events(ctx: click.Context, page: int, page_size: int, since: str) -> None:
    """Get workout update/delete events."""
    try:
        data = _get_client(ctx).get_workout_events(page, page_size, since)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_workout_events(data)


@workouts.command("create")
@click.option("--title", required=True)
@click.option("--description", default=None)
@click.option("--start-time", required=True, help="ISO-8601 start time.")
@click.option("--end-time", required=True, help="ISO-8601 end time.")
@click.option("--is-private", is_flag=True, default=False)
@click.option("--exercises-json", default=None, help="JSON string or @file path for exercises array.")
@click.pass_context
def workouts_create(
    ctx: click.Context,
    title: str,
    description: str | None,
    start_time: str,
    end_time: str,
    is_private: bool,
    exercises_json: str | None,
) -> None:
    """Create a new workout."""
    workout: dict = {
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "is_private": is_private,
    }
    if description:
        workout["description"] = description
    if exercises_json:
        workout["exercises"] = _load_json_arg(exercises_json)
    try:
        data = _get_client(ctx).create_workout(workout)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        console.print("[green]Workout created.[/green]")
        display.print_workout_detail(data)


@workouts.command("update")
@click.argument("workout_id")
@click.option("--title", default=None)
@click.option("--description", default=None)
@click.option("--start-time", default=None, help="ISO-8601 start time.")
@click.option("--end-time", default=None, help="ISO-8601 end time.")
@click.option("--is-private", type=bool, default=None)
@click.option("--exercises-json", default=None, help="JSON string or @file path for exercises array.")
@click.pass_context
def workouts_update(
    ctx: click.Context,
    workout_id: str,
    title: str | None,
    description: str | None,
    start_time: str | None,
    end_time: str | None,
    is_private: bool | None,
    exercises_json: str | None,
) -> None:
    """Update an existing workout."""
    workout: dict = {}
    if title is not None:
        workout["title"] = title
    if description is not None:
        workout["description"] = description
    if start_time is not None:
        workout["start_time"] = start_time
    if end_time is not None:
        workout["end_time"] = end_time
    if is_private is not None:
        workout["is_private"] = is_private
    if exercises_json:
        workout["exercises"] = _load_json_arg(exercises_json)

    if not workout:
        console.print("[yellow]Nothing to update -- provide at least one option.[/yellow]")
        sys.exit(1)

    try:
        data = _get_client(ctx).update_workout(workout_id, workout)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        console.print("[green]Workout updated.[/green]")
        display.print_workout_detail(data)


# ---------------------------------------------------------------------------
# Routines
# ---------------------------------------------------------------------------


@cli.group()
def routines() -> None:
    """Manage routines."""


@routines.command("list")
@click.option("--page", default=1, type=int)
@click.option("--page-size", default=5, type=click.IntRange(1, 10))
@click.pass_context
def routines_list(ctx: click.Context, page: int, page_size: int) -> None:
    """List routines."""
    try:
        data = _get_client(ctx).get_routines(page, page_size)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_routines(data)


@routines.command("get")
@click.argument("routine_id")
@click.pass_context
def routines_get(ctx: click.Context, routine_id: str) -> None:
    """Get a single routine by ID."""
    try:
        data = _get_client(ctx).get_routine(routine_id)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_routine_detail(data)


@routines.command("create")
@click.option("--title", required=True)
@click.option("--folder-id", default=None, type=int)
@click.option("--notes", default=None)
@click.option("--exercises-json", default=None, help="JSON string or @file path for exercises array.")
@click.pass_context
def routines_create(
    ctx: click.Context,
    title: str,
    folder_id: int | None,
    notes: str | None,
    exercises_json: str | None,
) -> None:
    """Create a new routine."""
    routine: dict = {"title": title}
    if folder_id is not None:
        routine["folder_id"] = folder_id
    if notes:
        routine["notes"] = notes
    if exercises_json:
        routine["exercises"] = _load_json_arg(exercises_json)
    try:
        data = _get_client(ctx).create_routine(routine)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        console.print("[green]Routine created.[/green]")
        display.print_routine_detail(data)


@routines.command("update")
@click.argument("routine_id")
@click.option("--title", default=None)
@click.option("--notes", default=None)
@click.option("--exercises-json", default=None, help="JSON string or @file path for exercises array.")
@click.pass_context
def routines_update(
    ctx: click.Context,
    routine_id: str,
    title: str | None,
    notes: str | None,
    exercises_json: str | None,
) -> None:
    """Update an existing routine."""
    routine: dict = {}
    if title is not None:
        routine["title"] = title
    if notes is not None:
        routine["notes"] = notes
    if exercises_json:
        routine["exercises"] = _load_json_arg(exercises_json)

    if not routine:
        console.print("[yellow]Nothing to update -- provide at least one option.[/yellow]")
        sys.exit(1)

    try:
        data = _get_client(ctx).update_routine(routine_id, routine)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        console.print("[green]Routine updated.[/green]")
        display.print_routine_detail(data)


# ---------------------------------------------------------------------------
# Exercise Templates
# ---------------------------------------------------------------------------


@cli.group()
def exercises() -> None:
    """Manage exercise templates."""


@exercises.command("list")
@click.option("--page", default=1, type=int)
@click.option("--page-size", default=5, type=click.IntRange(1, 100))
@click.pass_context
def exercises_list(ctx: click.Context, page: int, page_size: int) -> None:
    """List exercise templates."""
    try:
        data = _get_client(ctx).get_exercise_templates(page, page_size)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_exercise_templates(data)


@exercises.command("get")
@click.argument("template_id")
@click.pass_context
def exercises_get(ctx: click.Context, template_id: str) -> None:
    """Get an exercise template by ID."""
    try:
        data = _get_client(ctx).get_exercise_template(template_id)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_exercise_template_detail(data)


@exercises.command("history")
@click.argument("template_id")
@click.option("--start-date", default=None, help="ISO-8601 start date filter.")
@click.option("--end-date", default=None, help="ISO-8601 end date filter.")
@click.pass_context
def exercises_history(
    ctx: click.Context, template_id: str, start_date: str | None, end_date: str | None
) -> None:
    """Get exercise history for a template."""
    try:
        data = _get_client(ctx).get_exercise_history(template_id, start_date, end_date)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_exercise_history(data, template_id)


@exercises.command("create")
@click.option("--title", required=True)
@click.option("--exercise-type", required=True, type=click.Choice(EXERCISE_TYPES))
@click.option("--equipment", required=True, type=click.Choice(EQUIPMENT_CATEGORIES))
@click.option("--muscle-group", required=True, type=click.Choice(MUSCLE_GROUPS))
@click.option("--other-muscles", multiple=True, type=click.Choice(MUSCLE_GROUPS), help="Secondary muscles (repeatable).")
@click.pass_context
def exercises_create(
    ctx: click.Context,
    title: str,
    exercise_type: str,
    equipment: str,
    muscle_group: str,
    other_muscles: tuple[str, ...],
) -> None:
    """Create a custom exercise template."""
    template = {
        "title": title,
        "type": exercise_type,
        "equipment_category": equipment,
        "primary_muscle_group": muscle_group,
    }
    if other_muscles:
        template["secondary_muscle_groups"] = list(other_muscles)
    try:
        data = _get_client(ctx).create_exercise_template(template)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        console.print("[green]Exercise template created.[/green]")
        display.print_exercise_template_detail(data)


# ---------------------------------------------------------------------------
# Routine Folders
# ---------------------------------------------------------------------------


@cli.group()
def folders() -> None:
    """Manage routine folders."""


@folders.command("list")
@click.option("--page", default=1, type=int)
@click.option("--page-size", default=5, type=click.IntRange(1, 10))
@click.pass_context
def folders_list(ctx: click.Context, page: int, page_size: int) -> None:
    """List routine folders."""
    try:
        data = _get_client(ctx).get_routine_folders(page, page_size)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_routine_folders(data)


@folders.command("get")
@click.argument("folder_id")
@click.pass_context
def folders_get(ctx: click.Context, folder_id: str) -> None:
    """Get a routine folder by ID."""
    try:
        data = _get_client(ctx).get_routine_folder(folder_id)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        display.print_routine_folder_detail(data)


@folders.command("create")
@click.option("--name", required=True, help="Folder name.")
@click.pass_context
def folders_create(ctx: click.Context, name: str) -> None:
    """Create a routine folder."""
    try:
        data = _get_client(ctx).create_routine_folder(name)
    except httpx.HTTPStatusError as e:
        _handle_api_error(e)
    if ctx.obj["json"]:
        display.print_json(data)
    else:
        console.print("[green]Folder created.[/green]")
        display.print_routine_folder_detail(data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_json_arg(value: str) -> list | dict:
    """Parse a JSON string or read from a file prefixed with @."""
    if value.startswith("@"):
        path = value[1:]
        with open(path) as f:
            return json.load(f)
    return json.loads(value)


if __name__ == "__main__":
    cli()
