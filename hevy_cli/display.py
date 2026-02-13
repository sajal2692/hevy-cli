"""Rich display helpers for Hevy data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


def _parse_ts(ts: str | int | float | None) -> str:
    if ts is None:
        return "-"
    if isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    else:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M")


def _duration(start: str | int | float | None, end: str | int | float | None) -> str:
    if start is None or end is None:
        return "-"

    def _to_epoch(v: str | int | float) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return dt.timestamp()

    secs = _to_epoch(end) - _to_epoch(start)
    if secs < 0:
        return "-"
    mins = int(secs // 60)
    return f"{mins}m"


# -- Workouts ----------------------------------------------------------------


def print_workouts(data: dict) -> None:
    workouts = data.get("workouts", [])
    page = data.get("page", "?")
    page_count = data.get("page_count", "?")

    if not workouts:
        console.print("[dim]No workouts found.[/dim]")
        return

    table = Table(title=f"Workouts (page {page}/{page_count})")
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Title", style="bold")
    table.add_column("Date")
    table.add_column("Duration")
    table.add_column("Exercises", justify="right")

    for w in workouts:
        table.add_row(
            w.get("id", ""),
            w.get("title", "Untitled"),
            _parse_ts(w.get("start_time")),
            _duration(w.get("start_time"), w.get("end_time")),
            str(len(w.get("exercises", []))),
        )
    console.print(table)


def print_workout_detail(data: dict) -> None:
    w = data.get("workout") or data
    title = w.get("title", "Untitled")
    start = _parse_ts(w.get("start_time"))
    dur = _duration(w.get("start_time"), w.get("end_time"))
    desc = w.get("description") or ""

    header = f"[bold]{title}[/bold]  {start}  ({dur})"
    if desc:
        header += f"\n[dim]{desc}[/dim]"
    console.print(Panel(header, title="Workout", expand=False))

    exercises = w.get("exercises", [])
    if not exercises:
        console.print("[dim]No exercises.[/dim]")
        return

    for ex in exercises:
        ex_title = ex.get("title", "Unknown")
        notes = ex.get("notes") or ""
        sets = ex.get("sets", [])
        sets_lines = []
        for s in sets:
            parts = []
            st = s.get("type", "normal")
            if st != "normal":
                parts.append(f"[{st}]")
            if s.get("weight_kg") is not None:
                parts.append(f"{s['weight_kg']}kg")
            if s.get("reps") is not None:
                parts.append(f"x{s['reps']}")
            if s.get("distance_meters") is not None:
                parts.append(f"{s['distance_meters']}m")
            if s.get("duration_seconds") is not None:
                parts.append(f"{s['duration_seconds']}s")
            if s.get("rpe") is not None:
                parts.append(f"RPE {s['rpe']}")
            sets_lines.append(" ".join(parts) if parts else "-")

        body = "\n".join(f"  Set {i+1}: {line}" for i, line in enumerate(sets_lines))
        if notes:
            body = f"  Note: {notes}\n" + body
        console.print(f"\n[bold cyan]{ex_title}[/bold cyan]")
        console.print(body)


def print_workout_count(data: dict) -> None:
    count = data.get("workout_count", data)
    console.print(f"Total workouts: [bold]{count}[/bold]")


def print_workout_events(data: dict) -> None:
    events = data.get("events", [])
    page = data.get("page", "?")
    page_count = data.get("page_count", "?")

    if not events:
        console.print("[dim]No workout events found.[/dim]")
        return

    table = Table(title=f"Workout Events (page {page}/{page_count})")
    table.add_column("Type", style="bold")
    table.add_column("Workout ID", style="dim")
    table.add_column("When")

    for e in events:
        table.add_row(
            e.get("type", "?"),
            e.get("workout_id", ""),
            _parse_ts(e.get("timestamp") or e.get("created_at")),
        )
    console.print(table)


# -- Routines ----------------------------------------------------------------


def print_routines(data: dict) -> None:
    routines = data.get("routines", [])
    page = data.get("page", "?")
    page_count = data.get("page_count", "?")

    if not routines:
        console.print("[dim]No routines found.[/dim]")
        return

    table = Table(title=f"Routines (page {page}/{page_count})")
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Title", style="bold")
    table.add_column("Folder ID")
    table.add_column("Exercises", justify="right")

    for r in routines:
        table.add_row(
            r.get("id", ""),
            r.get("title", "Untitled"),
            str(r.get("folder_id") or "-"),
            str(len(r.get("exercises", []))),
        )
    console.print(table)


def print_routine_detail(data: dict) -> None:
    r = data.get("routine") or data
    if isinstance(r, list):
        if len(r) > 0:
            r = r[0]
        else:
            console.print("[yellow]Warning: Empty list returned from API[/yellow]")
            return
    if not isinstance(r, dict):
        console.print(f"[yellow]Warning: Unexpected data type: {type(r)}[/yellow]")
        console.print(f"Data: {r}")
        return
    title = r.get("title", "Untitled")
    notes = r.get("notes") or ""
    folder_id = r.get("folder_id")

    header = f"[bold]{title}[/bold]"
    if folder_id:
        header += f"  (folder: {folder_id})"
    if notes:
        header += f"\n[dim]{notes}[/dim]"
    console.print(Panel(header, title="Routine", expand=False))

    exercises = r.get("exercises", [])
    for ex in exercises:
        ex_title = ex.get("title", "Unknown")
        ex_notes = ex.get("notes") or ""
        sets = ex.get("sets", [])
        sets_lines = []
        for s in sets:
            parts = []
            st = s.get("type", "normal")
            if st != "normal":
                parts.append(f"[{st}]")
            if s.get("weight_kg") is not None:
                parts.append(f"{s['weight_kg']}kg")
            if s.get("reps") is not None:
                parts.append(f"x{s['reps']}")
            if s.get("distance_meters") is not None:
                parts.append(f"{s['distance_meters']}m")
            if s.get("duration_seconds") is not None:
                parts.append(f"{s['duration_seconds']}s")
            sets_lines.append(" ".join(parts) if parts else "-")
        body = "\n".join(f"  Set {i+1}: {line}" for i, line in enumerate(sets_lines))
        if ex_notes:
            body = f"  Note: {ex_notes}\n" + body
        console.print(f"\n[bold cyan]{ex_title}[/bold cyan]")
        console.print(body)


# -- Exercise Templates ------------------------------------------------------


def print_exercise_templates(data: dict) -> None:
    templates = data.get("exercise_templates", [])
    page = data.get("page", "?")
    page_count = data.get("page_count", "?")

    if not templates:
        console.print("[dim]No exercise templates found.[/dim]")
        return

    table = Table(title=f"Exercise Templates (page {page}/{page_count})")
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Title", style="bold")
    table.add_column("Type")
    table.add_column("Primary Muscle")
    table.add_column("Custom", justify="center")

    for t in templates:
        table.add_row(
            t.get("id", ""),
            t.get("title", ""),
            t.get("type", ""),
            t.get("primary_muscle_group", ""),
            "yes" if t.get("is_custom") else "",
        )
    console.print(table)


def print_exercise_template_detail(data: dict) -> None:
    t = data.get("exercise_template") or data
    lines = [
        f"[bold]{t.get('title', '')}[/bold]",
        f"Type: {t.get('type', '')}",
        f"Primary muscle: {t.get('primary_muscle_group', '')}",
        f"Secondary: {', '.join(t.get('secondary_muscle_groups', [])) or '-'}",
        f"Custom: {'yes' if t.get('is_custom') else 'no'}",
    ]
    console.print(Panel("\n".join(lines), title=f"Template {t.get('id', '')}", expand=False))


def print_exercise_history(data: dict, template_id: str) -> None:
    entries = data.get("exercise_history", [])
    page = data.get("page", "?")
    page_count = data.get("page_count", "?")

    if not entries:
        console.print("[dim]No exercise history found.[/dim]")
        return

    table = Table(title=f"Exercise History for {template_id} (page {page}/{page_count})")
    table.add_column("Workout", style="dim")
    table.add_column("Date")
    table.add_column("Set Type")
    table.add_column("Weight (kg)", justify="right")
    table.add_column("Reps", justify="right")
    table.add_column("RPE", justify="right")

    for e in entries:
        table.add_row(
            e.get("workout_title", ""),
            _parse_ts(e.get("workout_start_time")),
            e.get("set_type", ""),
            str(e.get("weight_kg", "")) if e.get("weight_kg") is not None else "-",
            str(e.get("reps", "")) if e.get("reps") is not None else "-",
            str(e.get("rpe", "")) if e.get("rpe") is not None else "-",
        )
    console.print(table)


# -- Routine Folders ---------------------------------------------------------


def print_routine_folders(data: dict) -> None:
    folders = data.get("routine_folders", [])
    page = data.get("page", "?")
    page_count = data.get("page_count", "?")

    if not folders:
        console.print("[dim]No routine folders found.[/dim]")
        return

    table = Table(title=f"Routine Folders (page {page}/{page_count})")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Created")
    table.add_column("Updated")

    for f in folders:
        table.add_row(
            str(f.get("id", "")),
            f.get("title", ""),
            _parse_ts(f.get("created_at")),
            _parse_ts(f.get("updated_at")),
        )
    console.print(table)


def print_routine_folder_detail(data: dict) -> None:
    f = data.get("routine_folder") or data
    lines = [
        f"[bold]{f.get('title', '')}[/bold]",
        f"ID: {f.get('id', '')}",
        f"Created: {_parse_ts(f.get('created_at'))}",
        f"Updated: {_parse_ts(f.get('updated_at'))}",
    ]
    console.print(Panel("\n".join(lines), title="Routine Folder", expand=False))


# -- Generic JSON fallback ---------------------------------------------------

def print_json(data: Any) -> None:
    """Fallback: pretty-print raw JSON."""
    import json
    console.print_json(json.dumps(data, indent=2, default=str))
