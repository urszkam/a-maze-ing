from __future__ import annotations

from typing import Any


class MazeGenerator:
    _instance: MazeGenerator | None = None
    _initialized: bool = False

    def __new__(cls, config: dict[str, Any]) -> MazeGenerator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, config: dict[str, Any]) -> None:
        if self._initialized:
            return

        self._config = config
        self._initialized = True

    def update_config(self, config: dict[str, Any]) -> None:
        self._config = config
