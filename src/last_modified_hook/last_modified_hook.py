import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template
from typing import Sequence

from last_modified_hook.find_and_replace import (
    FileLineProtocol,
    LineMatcherProtocol,
    LineReplacerProtocol,
    MatchedLine,
    MatchedLineProtocol,
    ModifiedLine,
    find_and_replace,
)


class LastModifiedMatcher(LineMatcherProtocol):
    def __init__(self, line_limit: int = -1) -> None:
        self.line_limit = line_limit

    def match(self, file_line: FileLineProtocol) -> MatchedLine:
        if self.line_limit == -1 or self.line_limit >= file_line.line_no:
            if file_line.line.startswith("# Last Modified:"):
                values = file_line.line.split()
                try:
                    last_modified = datetime.fromisoformat(values[3])
                    return MatchedLine(
                        is_match=True,
                        file_line=file_line,
                        matched_values={"last_modified": last_modified},
                    )
                except (IndexError, ValueError):
                    return MatchedLine(
                        is_match=True,
                        file_line=file_line,
                        matched_values={"last_modified": None},
                    )
        return MatchedLine(
            is_match=False,
            file_line=file_line,
            matched_values={},
        )


class LastModifiedReplacer(LineReplacerProtocol):
    def __init__(self, seconds: int = 60, line_template: str = "") -> None:

        self.seconds = seconds
        if not line_template:
            self.line_template = Template("# Last Modified: $_iso_date_  #\n")
        else:
            self.line_template = Template(line_template)

    def replace(self, matched_line: MatchedLineProtocol) -> ModifiedLine:
        return self._modify_line(matched_line)

    def _modify_line(self, matched_line: MatchedLineProtocol) -> ModifiedLine:
        if self._check_within_seconds(matched_line):
            return ModifiedLine(
                False, original_line=matched_line, new_line=matched_line.file_line.line
            )
        return ModifiedLine(
            True, original_line=matched_line, new_line=self._generate_line()
        )

    def _check_within_seconds(self, matched_line: MatchedLineProtocol) -> bool:
        last_modified = matched_line.matched_values.get("last_modified", None)
        if last_modified:
            try:
                now = datetime.now(timezone.utc)
                if now - last_modified <= timedelta(seconds=self.seconds):
                    return True
            except ValueError:
                pass
        return False

    def _generate_line(self) -> str:
        now = datetime.now(timezone.utc)
        new_line = self.line_template.safe_substitute(_iso_date_=now.isoformat())
        return new_line


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
    matcher = LastModifiedMatcher()
    retv = 0
    for filename in args.filenames:
        try:
            modified_lines = find_and_replace(
                file_path=Path(filename), replacer=replacer, matcher=matcher
            )
        except Exception as error:
            print(f"{error!r}")
            return 1
        if modified_lines:
            print(f"last_modified_hook updated file: {filename}")
            retv = 1
    return retv


if __name__ == "__main__":
    raise SystemExit(cli())
