from pathlib import Path


def user_zpp_root(home: Path) -> Path:
    return home / ".zpp"
