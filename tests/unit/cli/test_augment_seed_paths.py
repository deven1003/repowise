"""Working-set and Glob-rescue paths keep their leading dot.

``str.lstrip("./")`` strips a run of *characters*, not the ``./`` prefix, so
``.github/workflows/ci.yml`` became ``github/workflows/ci.yml``: no graph node
or decision link has that spelling, so decisions governing any dot-directory
(``.github/``, ``.claude/``, ``.devcontainer/``, ...) scored zero and were
never injected. The Glob rescue mangled patterns the same way.
"""

from __future__ import annotations

from pathlib import Path

from repowise.cli.commands.augment_cmd import decision_inject, glob_rescue


def test_collect_seeds_keeps_dot_directory_paths(tmp_path: Path, monkeypatch) -> None:
    dirty = [
        ".github/workflows/ci.yml",
        "./src/core/auth.py",
        ".claude\\settings.json",
        "./.devcontainer/devcontainer.json",
    ]
    monkeypatch.setattr(decision_inject, "_dirty_files_and_branch", lambda p: (dirty, "main"))
    monkeypatch.setattr(decision_inject, "_branch_changed_files", lambda p, b: [])

    seeds, branch = decision_inject._collect_seeds(tmp_path)

    assert branch == "main"
    assert seeds == [
        ".github/workflows/ci.yml",
        "src/core/auth.py",
        ".claude/settings.json",
        ".devcontainer/devcontainer.json",
    ]


def test_matching_paths_keeps_dot_directory_pattern(tmp_path: Path, monkeypatch) -> None:
    seen: list[str] = []

    def capture(pattern: str):
        seen.append(pattern)
        return None  # ``matching_paths`` answers ([], 0) before touching the store

    monkeypatch.setattr(glob_rescue, "_translate", capture)

    assert glob_rescue.matching_paths(tmp_path, "./.github/workflows/*.yml") == ([], 0)
    assert glob_rescue.matching_paths(tmp_path, ".claude\\**\\*.md") == ([], 0)

    assert seen == [".github/workflows/*.yml", ".claude/**/*.md"]
