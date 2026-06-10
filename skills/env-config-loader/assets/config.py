"""Load .env, validate required keys, and read typed values - stdlib only.

Scattered os.environ[...] access fails late and silently: a missing key becomes
a KeyError halfway through a run, and "5" vs 5 becomes a type bug. This parses a
simple .env, overlays the real environment (which wins, so prod can override the
file), checks a required-key list once at startup with one clear error, and
exposes typed getters that raise readable errors on bad values. No python-dotenv,
no pydantic. Commit only .env.example with placeholders; gitignore the real .env.
"""
from __future__ import annotations

import os
from pathlib import Path

_TRUE = {"1", "true", "yes", "on", "y", "t"}
_FALSE = {"0", "false", "no", "off", "n", "f", ""}


class ConfigError(ValueError):
    """Raised when config is missing a required key or has a bad typed value."""


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse .env text into a dict. Skips blanks/comments; strips quotes/export."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            raise ConfigError(f"bad .env line (no '='): {raw!r}")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        out[key] = value
    return out


class Config:
    """Validated, typed view over .env values overlaid with the real environment."""

    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    @classmethod
    def load(
        cls,
        dotenv_path: str | Path | None = ".env",
        *,
        required: list[str] | None = None,
        environ: dict[str, str] | None = None,
    ) -> "Config":
        """Read .env (if present), overlay the environment, check required keys."""
        values: dict[str, str] = {}
        if dotenv_path and Path(dotenv_path).is_file():
            values.update(parse_dotenv(Path(dotenv_path).read_text(encoding="utf-8")))
        # The real environment wins over the file.
        env = os.environ if environ is None else environ
        values.update({k: v for k, v in env.items()})

        missing = [k for k in (required or []) if not values.get(k)]
        if missing:
            raise ConfigError(f"missing required keys: {', '.join(sorted(missing))}")
        return cls(values)

    def get(self, key: str, default: str | None = None) -> str:
        value = self._values.get(key, default)
        if value is None:
            raise ConfigError(f"missing required key: {key}")
        return value

    def get_int(self, key: str, default: int | None = None) -> int:
        raw = self._values.get(key)
        if raw is None or raw == "":
            if default is not None:
                return default
            raise ConfigError(f"missing required int key: {key}")
        try:
            return int(raw)
        except ValueError:
            raise ConfigError(f"{key} must be an int, got {raw!r}") from None

    def get_float(self, key: str, default: float | None = None) -> float:
        raw = self._values.get(key)
        if raw is None or raw == "":
            if default is not None:
                return default
            raise ConfigError(f"missing required float key: {key}")
        try:
            return float(raw)
        except ValueError:
            raise ConfigError(f"{key} must be a float, got {raw!r}") from None

    def get_bool(self, key: str, default: bool | None = None) -> bool:
        raw = self._values.get(key)
        if raw is None:
            if default is not None:
                return default
            raise ConfigError(f"missing required bool key: {key}")
        token = raw.strip().lower()
        if token in _TRUE:
            return True
        if token in _FALSE:
            return False
        raise ConfigError(f"{key} must be a boolean, got {raw!r}")

    def get_list(
        self, key: str, default: list[str] | None = None, sep: str = ","
    ) -> list[str]:
        raw = self._values.get(key)
        if raw is None:
            if default is not None:
                return default
            raise ConfigError(f"missing required list key: {key}")
        return [item.strip() for item in raw.split(sep) if item.strip()]


if __name__ == "__main__":
    # Self-test without touching the filesystem or real env.
    fake_env = {
        "API_BASE": "https://api.example.com",
        "RUN_LIMIT": "50",
        "DRY_RUN": "yes",
        "TAGS": "a, b ,c",
    }
    cfg = Config.load(None, required=["API_BASE", "RUN_LIMIT"], environ=fake_env)
    assert cfg.get("API_BASE") == "https://api.example.com"
    assert cfg.get_int("RUN_LIMIT") == 50
    assert cfg.get_bool("DRY_RUN") is True
    assert cfg.get_bool("MISSING", default=False) is False
    assert cfg.get_list("TAGS") == ["a", "b", "c"]

    # Missing required -> clear error listing the key.
    try:
        Config.load(None, required=["NOPE"], environ=fake_env)
    except ConfigError as exc:
        assert "missing required keys: NOPE" in str(exc)

    # Bad int -> clear error, not a silent default.
    try:
        Config({"N": "x"}).get_int("N")
    except ConfigError as exc:
        assert "must be an int" in str(exc)

    print("env-config-loader OK")
