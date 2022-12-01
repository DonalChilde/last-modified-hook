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
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryFile
from typing import Callable, Tuple


@dataclass
class ModifiedLine:
    modified: bool
    line: str


def find_and_replace(
    file: Path,
    replacer: Callable[[str, int, str], ModifiedLine],
    backup: str = "",
    encoding="utf-8",
) -> bool:
    """Find and replace in a text file, by lines.

    Iterate over the lines in a text file, with the option to replace the line.
    Lines are saved to a temporary file, and the original file is changed only if a line
    was modified. A backup file of the original is made before the temp file is copied
    back over the original file, and by default the backup is erased after the process
    is complete. If a file suffix is supplied with the `backup` argument, then the
    backup file will be preserved.
    """
    dirty = False
    remove_backup = False
    backup_suffix = backup
    if not backup:
        remove_backup = True
        backup_suffix = ".bak"
    with TemporaryFile(mode="w", encoding=encoding) as temp_file:
        with file.open(mode="r", encoding=encoding) as input_file:
            for line_no, input_line in enumerate(input_file, start=1):
                modified_line = replacer(str(file), line_no, input_line)
                if modified_line.modified:
                    dirty = True
                temp_file.write(modified_line.line)
        temp_file.flush()
        if dirty:
            backup_path = Path(f"{str(file)}{backup_suffix}")
            shutil.copy2(file, backup_path)
            temp_file.seek(0)
            with file.open(mode="w", encoding=encoding) as output_file:
                shutil.copyfileobj(temp_file, output_file)
            if remove_backup:
                backup_path.unlink()
    return dirty


def noop_replacer(file_name: str, line_no: int, line: str) -> ModifiedLine:
    """
    This replacer does nothing.

    _extended_summary_

    Args:
        file_name: _description_
        line_no: _description_
        line: _description_

    Returns:
        _description_
    """
    _ = file_name, line_no
    modified = False
    return ModifiedLine(modified, line)
