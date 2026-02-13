---
name: hevy-cli
description: Interact with the Hevy fitness app via the hevy-cli command-line tool. Use when the user wants to view, create, or update workouts, routines, exercise templates, or routine folders in their Hevy account. Triggers on requests involving workout tracking, exercise history, routine management, or any Hevy-related data operations.
---

# Hevy CLI

Use the `hevy` CLI to interact with Hevy fitness app data. Requires `HEVY_API_KEY` env var to be set.

Always use `-j` for JSON output -- it provides exact IDs and complete data for parsing.

## Quick Start

```bash
# Verify access
hevy -j workouts count

# List recent workouts
hevy -j workouts list --page-size 10
```

## Common Tasks

### View workout history

```bash
hevy -j workouts list --page 1 --page-size 10
hevy -j workouts get <workout-id>
```

### Check exercise progress

```bash
# Find the exercise template ID first
hevy -j exercises list --page-size 100

# Then get history for that exercise
hevy -j exercises history <template-id>
hevy -j exercises history <template-id> --start-date 2025-01-01 --end-date 2025-02-01
```

### Create a workout

```bash
hevy -j workouts create \
  --title "Push Day" \
  --start-time 2025-01-15T08:00:00Z \
  --end-time 2025-01-15T09:00:00Z \
  --exercises-json '[{"exercise_template_id":"79D0BB3A","sets":[{"type":"normal","weight_kg":60,"reps":8}]}]'
```

For complex exercises, use a file: `--exercises-json @exercises.json`

### Manage routines

```bash
hevy -j routines list
hevy -j folders list  # Get folder ID first
hevy -j routines create --title "Upper Body" --folder-id <folder-id> --exercises-json @routine.json
hevy -j routines update <routine-id> --title "Updated Name"
```

**Important**: The Hevy API requires a `--folder-id` when creating routines. Use `hevy folders list` to find folder IDs, or create a new folder with `hevy folders create --name "Folder Name"`.

### Organize with folders

```bash
hevy -j folders list
hevy -j folders create --name "Hypertrophy Block"
```

## Key Patterns

- Always use `hevy -j` for JSON output to get structured, parseable data.
- All list commands accept `--page` and `--page-size` for pagination.
- Exercise data for create/update uses `--exercises-json` accepting inline JSON or `@filepath`.
- Set types: `normal`, `warmup`, `failure`, `dropset`.

## Full Command Reference

See [references/commands.md](references/commands.md) for complete command syntax, all flag options, enum values for exercise types/equipment/muscle groups, and the exercises JSON schema.
