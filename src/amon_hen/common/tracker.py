from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .filesystem import ensure_dir, ensure_file


@dataclass(frozen=True)
class Difference:
    path: tuple
    old: Any
    new: Any


def diff(old: Any, new: Any) -> list[Difference]:
    differences: list[Difference] = []

    _diff(old, new, (), differences)

    return differences


def _diff(old: Any, new: Any, path: tuple, differences: list[Difference]) -> None:
    # Different types
    if type(old) is not type(new):
        differences.append(Difference(path, old, new))
        return

    # Dictionaries
    if isinstance(old, dict):
        keys = set(old) | set(new)

        for key in keys:
            if key not in old:
                differences.append(Difference(path + (key,), None, new[key]))
            elif key not in new:
                differences.append(Difference(path + (key,), old[key], None))
            else:
                _diff(
                    old[key],
                    new[key],
                    path + (key,),
                    differences,
                )

        return

    # Lists
    if isinstance(old, list):
        if old != new:
            differences.append(Difference(path, old, new))

        return

    # Primitive values
    if old != new:
        differences.append(Difference(path, old, new))


@dataclass(frozen=True)
class Track:
    old_hash: str | None
    old_data: dict | None
    new_hash: str | None
    new_data: dict | None

    @property
    def is_new(self) -> bool:
        return self.old_hash is None and self.new_hash is not None

    @property
    def has_changed(self) -> bool:
        return self.old_hash != self.new_hash

    @property
    def is_removed(self) -> bool:
        return self.old_hash is not None and self.new_hash is None

    @property
    def differences(self) -> list[Difference]:
        return diff(self.old_data, self.new_data)


class Tracker:
    def __init__(self):
        self.path = None
        self.versions_path = None
        self.history_path = None

    def _save_version(self, hash_value: str, data: dict) -> None:
        """
        Save the actual content.

        The hash becomes the filename.
        """
        filepath = self.versions_path / f"{hash_value}.json"

        if filepath.exists():
            return

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def _append_history(self, hash_value: str) -> None:
        """
        Append a new entry to the history JSONL file.
        """

        entry = {
            "hash": hash_value,
            "timestamp": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
        }

        with open(self.history_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(entry) + "\n")

    def _get_latest_history_entry(self) -> dict | None:
        """
        Returns the most recent entry from the history JSONL file.
        """

        if not self.history_path.exists():
            return None

        latest = None

        with open(self.history_path, "rb") as file:
            file.seek(0, 2)
            position = file.tell()

            if position == 0:
                return None  # empty file

            # Move back over trailing newlines
            position -= 1
            while position >= 0:
                file.seek(position)
                if file.read(1) != b"\n":
                    break
                position -= 1

            # File contained only newlines
            if position < 0:
                return None

            # Find start of last line
            while position > 0:
                file.seek(position)
                if file.read(1) == b"\n":
                    position += 1
                    break
                position -= 1

            file.seek(position)
            latest = file.readline().decode("utf-8").strip()

        if not latest:
            return None

        return json.loads(latest)

    def _get_old(self) -> tuple[str | None, dict | None]:
        """
        Returns the hash and data from the most recent version.
        """
        if not self.history_path.exists():
            return None, None

        entry = self._get_latest_history_entry()

        if entry is None:
            return None, None

        old_hash = entry["hash"]

        if old_hash is None:
            return None, None

        old_data_path = self.versions_path / f"{old_hash}.json"

        with open(old_data_path, "r", encoding="utf-8") as file:
            old_data = json.load(file)

        return old_hash, old_data

    def _hash_data(self, data: dict | None) -> str | None:
        """
        Create a stable hash.
        """
        if data is None:
            return None

        serialized = json.dumps(data, sort_keys=True)

        return hashlib.sha256(serialized.encode()).hexdigest()

    def set_path(self, path: str | Path) -> None:
        """
        Sets tracked object path.
        """
        self.path = Path(path)

        self.versions_path = self.path / "versions"
        ensure_dir(self.versions_path)

        self.history_path = self.path / "history.jsonl"
        ensure_file(self.history_path)

    def track(self, data: dict | None, path: str | Path) -> Track:
        """
        Initiate the tracking process.
        """
        self.set_path(path)

        old_hash, old_data = self._get_old()
        new_hash = self._hash_data(data)
        new_data = data

        result = Track(
            old_hash=old_hash,
            old_data=old_data,
            new_hash=new_hash,
            new_data=data,
        )

        # First time seeing this object or it changed
        if old_hash != new_hash:
            # Save content only when the object currently exists
            if new_hash is not None:
                self._save_version(new_hash, new_data)

            self._append_history(new_hash)

        return result
