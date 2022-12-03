####################################################
#                                                  #
#     src/snippets/file/find_and_replace.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-30T12:33:25-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Protocol


class FileLineProtocol(Protocol):
    file_name: str
    line_no: int
    line: str


class MatchedLineProtocol(Protocol):
    is_match: bool
    file_line: FileLineProtocol
    matched_values: dict[str, Any]


class ModifiedLineProtocol(Protocol):
    is_modified: bool
    original_line: MatchedLineProtocol
    new_line: str


class LineReplacerProtocol(Protocol):
    def replace(self, matched_line: MatchedLineProtocol) -> ModifiedLineProtocol:
        ...


class LineMatcherProtocol(Protocol):
    def match(self, file_line: FileLineProtocol) -> MatchedLineProtocol:
        ...


@dataclass
class FileLine:
    file_name: str
    line_no: int
    line: str


def find_and_replace(
    file_path: Path,
    matcher: LineMatcherProtocol,
    replacer: LineReplacerProtocol,
    backup: str = "",
    encoding="utf-8",
    dry_run: bool = False,
) -> list[ModifiedLineProtocol]:
    """
    Find and replace in a text file, by lines.

    Iterate over the lines in a text file, testing for a match, with the option to
    replace the line.

    Lines are saved to a temporary file, and if there has been a change, the original
    file will be overwritten with the temp file.

    A backup file of the original is made before the temp file is copied back over the
    original file, and by default the backup is erased after the process is complete.

    If a file suffix is supplied with the `backup` argument, then the backup file will
    be preserved.

    If dry_run is True, all operations take place except altering the original file.

    Args:
        file_path: The file to be used.
        matcher: A line matcher used to determine if the line might be a valid replace
            target.
        replacer: A replacer that may or may not replace the line with a new line.
        backup: The file suffix to be used for the backup file. If no value is provided,
            the suffix is '.bak', and the backup file will be automaticly deleted if the
            are no errors. If a suffix is provided, the backup file will not be deleted.
            Defaults to "".
        encoding: The encoding to be used for file input and output. Defaults to "utf-8".
        dry_run: If `True`, all operations take place except chnaging the original file.
            Defaults to False.

    Returns:
        A list of modified lines.
    """

    remove_backup = False
    backup_suffix = backup
    if not backup:
        remove_backup = True
        backup_suffix = ".bak"
    modified_lines: list[ModifiedLineProtocol] = []
    with NamedTemporaryFile(mode="w", encoding=encoding) as temp_file:
        with file_path.open(mode="r", encoding=encoding) as input_file:
            file_name_string = str(file_path)
            for line_no, input_line in enumerate(input_file, start=1):
                line_match = matcher.match(
                    FileLine(file_name_string, line_no, input_line)
                )
                if line_match.is_match:
                    modified_line = replacer.replace(matched_line=line_match)
                    if modified_line.is_modified:
                        modified_lines.append(modified_line)
                    temp_file.write(modified_line.new_line)
                else:
                    temp_file.write(input_line)
        temp_file.flush()
        if modified_lines:
            backup_path = Path(f"{str(file_path)}{backup_suffix}")
            # This assertion makes no sense if the replace changes the line count.
            assert line_count(Path(temp_file.name)) == line_count(file_path), (
                f"Line count of potential modified file does not match "
                f"original file {file_path}."
            )
            shutil.copy2(file_path, backup_path)
            if not dry_run:
                shutil.copy2(temp_file.name, file_path)
            if remove_backup:
                backup_path.unlink()
    return modified_lines


def line_count(file_name: Path) -> int:
    total = 0
    with file_name.open(mode="rt", encoding="utf-8") as file_in:
        for count, _ in enumerate(file_in, start=1):
            total = count
    return total


@dataclass
class MatchedLine:
    is_match: bool
    file_line: FileLineProtocol
    matched_values: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModifiedLine:
    is_modified: bool
    original_line: MatchedLineProtocol
    new_line: str


class NoOpReplacer(LineReplacerProtocol):
    def replace(self, matched_line: MatchedLineProtocol) -> ModifiedLine:
        return ModifiedLine(
            is_modified=False,
            original_line=matched_line,
            new_line=matched_line.file_line.line,
        )


class NoOpMatcher(LineMatcherProtocol):
    def match(self, file_line: FileLineProtocol) -> MatchedLineProtocol:
        return MatchedLine(
            is_match=False,
            file_line=file_line,
            matched_values={},
        )
