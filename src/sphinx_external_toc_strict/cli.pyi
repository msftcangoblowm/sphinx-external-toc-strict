from pathlib import Path

def main() -> None: ...
def parse_toc(toc_file: Path) -> None: ...
def create_site(
    toc_file: Path,
    path: Path,
    extension: str,
    overwrite: bool,
) -> None: ...
def create_toc(
    site_dir: Path,
    extension: str,
    index: str,
    skip_match: str,
    guess_titles: bool,
    file_format: str,
) -> None: ...
def migrate_toc(
    toc_file: Path,
    format: str,
    output: Path,
) -> None: ...
