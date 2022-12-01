import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template
from typing import Sequence, Tuple

from last_modified_hook.find_and_replace import ModifiedLine, find_and_replace


class LastModifiedReplacer:
    def __init__(
        self, seconds: int = 60, line_limit: int = -1, line_template: str = ""
    ) -> None:
        self.line_limit = line_limit
        self.seconds = seconds
        if not line_template:
            self.line_template = Template("# Last Modified: $_iso_date_         #")
        else:
            self.line_template = Template(line_template)

    def __call__(self, filename: str, line_no: int, line: str) -> ModifiedLine:
        if self.line_limit == -1 or self.line_limit >= line_no:
            if line.startswith("# Last Modified:"):
                return self._modify_line(line)
            else:
                return ModifiedLine(False, line)
        else:
            return ModifiedLine(False, line)

    def _modify_line(self, line) -> ModifiedLine:
        if self._check_within_seconds(line):
            return ModifiedLine(False, line)
        return ModifiedLine(True, self._generate_line())

    def _check_within_seconds(self, line: str) -> bool:
        values = line.split()
        try:
            last_modified = datetime.fromisoformat(values[2])
            now = datetime.now(timezone.utc)
            if now - last_modified <= timedelta(seconds=self.seconds):
                return True
        except:
            pass
        return False

    def _generate_line(self) -> str:
        now = datetime.now(timezone.utc)
        return self.line_template.safe_substitute(_iso_date_=now.isoformat())


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to check for last_modified.",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=60,
        help="Max age of a valid last_modified date in seconds.",
    )
    parser.add_argument(
        "--line_limit",
        type=int,
        default=-1,
        help="Max number of lines to search for last_modified. -1 for no limit.",
    )
    parser.add_argument(
        "--line_template",
        type=str,
        default="",
        help="Template string for a -new- last_modified line.",
    )
    args = parser.parse_args(argv)
    replacer = LastModifiedReplacer()
    retv = 0
    for filename in args.filenames:
        try:
            dirty = find_and_replace(file=Path(filename), replacer=replacer)
        except Exception as error:
            print(f"{error!r}")
            return 1
        if dirty:
            print(f"last_modified_hook updated file: {filename}")
            retv = 1
    return retv


if __name__ == "__main__":
    raise SystemExit(cli())
