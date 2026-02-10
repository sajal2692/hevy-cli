"""Hevy API client."""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.hevyapp.com"


class HevyClient:
    """HTTP client for the Hevy API."""

    def __init__(self, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"api-key": api_key},
            timeout=30.0,
        )

    # -- low-level helpers ---------------------------------------------------

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        resp = self._client.post(path, json=json)
        resp.raise_for_status()
        return resp.json()

    def _put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        resp = self._client.put(path, json=json)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> int:
        resp = self._client.delete(path)
        resp.raise_for_status()
        return resp.status_code

    # -- workouts ------------------------------------------------------------

    def get_workouts(self, page: int = 1, page_size: int = 5) -> dict:
        return self._get("/v1/workouts", params={"page": page, "pageSize": page_size})

    def get_workout(self, workout_id: str) -> dict:
        return self._get(f"/v1/workouts/{workout_id}")

    def get_workout_count(self) -> dict:
        return self._get("/v1/workouts/count")

    def get_workout_events(
        self, page: int = 1, page_size: int = 5, since: str = "1970-01-01T00:00:00Z"
    ) -> dict:
        return self._get(
            "/v1/workouts/events",
            params={"page": page, "pageSize": page_size, "since": since},
        )

    def create_workout(self, workout: dict) -> dict:
        return self._post("/v1/workouts", json={"workout": workout})

    def update_workout(self, workout_id: str, workout: dict) -> dict:
        return self._put(f"/v1/workouts/{workout_id}", json={"workout": workout})

    # -- routines ------------------------------------------------------------

    def get_routines(self, page: int = 1, page_size: int = 5) -> dict:
        return self._get("/v1/routines", params={"page": page, "pageSize": page_size})

    def get_routine(self, routine_id: str) -> dict:
        return self._get(f"/v1/routines/{routine_id}")

    def create_routine(self, routine: dict) -> dict:
        return self._post("/v1/routines", json={"routine": routine})

    def update_routine(self, routine_id: str, routine: dict) -> dict:
        return self._put(f"/v1/routines/{routine_id}", json={"routine": routine})

    # -- exercise templates --------------------------------------------------

    def get_exercise_templates(self, page: int = 1, page_size: int = 5) -> dict:
        return self._get(
            "/v1/exercise_templates", params={"page": page, "pageSize": page_size}
        )

    def get_exercise_template(self, template_id: str) -> dict:
        return self._get(f"/v1/exercise_templates/{template_id}")

    def get_exercise_history(
        self,
        template_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        params: dict[str, Any] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self._get(f"/v1/exercise_history/{template_id}", params=params or None)

    def create_exercise_template(self, template: dict) -> dict:
        return self._post(
            "/v1/exercise_templates", json={"exercise_template": template}
        )

    # -- routine folders -----------------------------------------------------

    def get_routine_folders(self, page: int = 1, page_size: int = 5) -> dict:
        return self._get(
            "/v1/routine_folders", params={"page": page, "pageSize": page_size}
        )

    def get_routine_folder(self, folder_id: str) -> dict:
        return self._get(f"/v1/routine_folders/{folder_id}")

    def create_routine_folder(self, name: str) -> dict:
        return self._post("/v1/routine_folders", json={"routine_folder": {"title": name}})
