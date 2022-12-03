from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template

import pytest

from last_modified_hook import last_modified_hook
from last_modified_hook.find_and_replace import line_count

file_text = """####################################################
#                                                  #
#     src/snippets/file/find_and_replace.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-30T12:33:25-07:00            #
# Last Modified: $_iso_date_  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryFile
from typing import Callable, Tuple


@dataclass
class ModifiedLine:
    modified: bool
    line: str\n
"""


@pytest.fixture(scope="function")
def test_file_date_slug(test_dir: Path) -> Path:
    file_path = test_dir / "test_slug.py"
    file_path.write_text(file_text, encoding="utf-8")
    return file_path


@pytest.fixture(scope="function")
def test_file_date_now(test_dir: Path) -> Path:
    file_path = test_dir / "test_now.py"
    now = datetime.now(timezone.utc)
    file_path.write_text(
        Template(file_text).safe_substitute(_iso_date_=now.isoformat()),
        encoding="utf-8",
    )
    return file_path


@pytest.fixture(scope="function")
def test_file_date_expired(test_dir: Path) -> Path:
    file_path = test_dir / "test_expired.py"
    expired = datetime.now(timezone.utc) - timedelta(seconds=120)
    file_path.write_text(
        Template(file_text).safe_substitute(_iso_date_=expired.isoformat()),
        encoding="utf-8",
    )
    return file_path


def test_last_modified_slug(test_file_date_slug: Path):
    args = [str(test_file_date_slug)]
    last_modified_hook.cli(argv=args)
    print("Line Count", line_count(test_file_date_slug))
    assert not Path(f"{str(test_file_date_slug)}.bak").exists()
    assert test_file_date_slug.read_text() != file_text


def test_last_modified_now(test_file_date_now: Path):
    original_text = test_file_date_now.read_text()
    args = [str(test_file_date_now)]
    last_modified_hook.cli(argv=args)
    print("Line Count", line_count(test_file_date_now))
    assert not Path(f"{str(test_file_date_now)}.bak").exists()
    assert test_file_date_now.read_text() == original_text


def test_last_modified_expired(test_file_date_expired: Path):
    original_text = test_file_date_expired.read_text()
    args = [str(test_file_date_expired)]
    last_modified_hook.cli(argv=args)
    print("Line Count", line_count(test_file_date_expired))
    assert not Path(f"{str(test_file_date_now)}.bak").exists()
    assert test_file_date_expired.read_text() != original_text
