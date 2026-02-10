# hevy-cli

Command-line interface for the [Hevy](https://www.hevyapp.com/) fitness app API. Manage workouts, routines, exercise templates, and routine folders from your terminal.

## Requirements

- Python 3.10+
- A Hevy API key (available with [Hevy Pro](https://www.hevyapp.com/))

## Installation

### Homebrew (macOS)

```bash
brew tap sajal2692/tap
brew install hevy-cli
```

### From source

```bash
pip install .
```

Or in editable/dev mode:

```bash
pip install -e .
```

## Authentication

Provide your API key in one of two ways:

```bash
# Option 1: environment variable (recommended)
export HEVY_API_KEY=your-api-key-here
hevy workouts list

# Option 2: CLI flag
hevy --api-key your-api-key-here workouts list
```

## Usage

All commands support a `-j` / `--json-output` flag for raw JSON output instead of formatted tables.

```bash
hevy -j workouts list
```

### Workouts

```bash
# List recent workouts
hevy workouts list
hevy workouts list --page 2 --page-size 10

# Get a specific workout
hevy workouts get <workout-id>

# Get total workout count
hevy workouts count

# Get workout update/delete events
hevy workouts events
hevy workouts events --since 2025-01-01T00:00:00Z

# Create a workout
hevy workouts create \
  --title "Morning Session" \
  --start-time 2025-01-15T08:00:00Z \
  --end-time 2025-01-15T09:00:00Z \
  --exercises-json @exercises.json

# Update a workout
hevy workouts update <workout-id> --title "Updated Title"
```

### Routines

```bash
# List routines
hevy routines list

# Get a specific routine
hevy routines get <routine-id>

# Create a routine
hevy routines create --title "Push Day" --exercises-json @exercises.json

# Update a routine
hevy routines update <routine-id> --title "New Name"
```

### Exercise Templates

```bash
# List exercise templates
hevy exercises list
hevy exercises list --page-size 100

# Get a specific template
hevy exercises get <template-id>

# Get exercise history
hevy exercises history <template-id>
hevy exercises history <template-id> --start-date 2025-01-01 --end-date 2025-02-01

# Create a custom exercise template
hevy exercises create \
  --title "Zercher Squat" \
  --exercise-type weight_reps \
  --equipment barbell \
  --muscle-group quadriceps \
  --other-muscles glutes \
  --other-muscles hamstrings
```

### Routine Folders

```bash
# List folders
hevy folders list

# Get a specific folder
hevy folders get <folder-id>

# Create a folder
hevy folders create --name "Hypertrophy Block"
```

## Exercises JSON Format

The `--exercises-json` flag accepts either an inline JSON string or a file path prefixed with `@`:

```bash
# Inline
hevy workouts create --title "Test" \
  --start-time 2025-01-15T08:00:00Z \
  --end-time 2025-01-15T09:00:00Z \
  --exercises-json '[{"exercise_template_id": "79D0BB3A", "sets": [{"type": "normal", "weight_kg": 60, "reps": 8}]}]'

# From file
hevy workouts create --title "Test" \
  --start-time 2025-01-15T08:00:00Z \
  --end-time 2025-01-15T09:00:00Z \
  --exercises-json @my_exercises.json
```

### Set types

- `normal` -- standard working set
- `warmup` -- warm-up set
- `failure` -- set taken to failure
- `dropset` -- drop set

### Exercise types

`weight_reps`, `reps_only`, `bodyweight_reps`, `bodyweight_assisted_reps`, `duration`, `weight_duration`, `distance_duration`, `short_distance_weight`

### Equipment categories

`none`, `barbell`, `dumbbell`, `kettlebell`, `machine`, `plate`, `resistance_band`, `suspension`, `other`

### Muscle groups

`abdominals`, `shoulders`, `biceps`, `triceps`, `forearms`, `quadriceps`, `hamstrings`, `calves`, `glutes`, `abductors`, `adductors`, `lats`, `upper_back`, `traps`, `lower_back`, `chest`, `cardio`, `neck`, `full_body`, `other`

## License

MIT
