from pathlib import Path

import click

from .constants import __version_app
from .parsing_shared import FILE_FORMATS

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version_app)
def main() -> None: ...
@main.command("parse")
@click.argument(
    "toc_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        path_type=Path,
    ),
)
def parse_toc(toc_file: Path) -> None: ...
@main.command("to-project")
@click.argument(
    "toc_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        path_type=Path,
    ),
)
@click.option(
    "-p",
    "--path",
    default=None,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
    help="The root directory [default: ToC file directory].",
)
@click.option(
    "-e",
    "--extension",
    type=click.Choice(["rst", "md"]),
    default="rst",
    show_default=True,
    help="The default file extension to use.",
)
@click.option("-o", "--overwrite", is_flag=True, help="Overwrite existing files.")
def create_site(
    toc_file: Path,
    path: Path,
    extension: str,
    overwrite: bool,
) -> None: ...
@main.command("from-project")
@click.argument(
    "site_dir",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
)
@click.option(
    "-e",
    "--extension",
    multiple=True,
    default=[".rst", ".md"],
    show_default=True,
    help="File extensions to consider as documents (use multiple times)",
)
@click.option(
    "-i",
    "--index",
    default="index",
    show_default=True,
    help="File name (without suffix) considered as the index file in a folder",
)
@click.option(
    "-s",
    "--skip-match",
    multiple=True,
    default=[".*"],
    show_default=True,
    help="File/Folder names which match will be ignored (use multiple times)",
)
@click.option(
    "-t",
    "--guess-titles",
    is_flag=True,
    help="Guess titles of documents from path names",
)
@click.option(
    "-f",
    "--file-format",
    type=click.Choice(list(FILE_FORMATS)),
    default=list(FILE_FORMATS)[0],
    show_default=True,
    help="The key-mappings to use.",
)
def create_toc(
    site_dir: Path,
    extension: str,
    index: str,
    skip_match: str,
    guess_titles: bool,
    file_format: str,
) -> None: ...
@main.command("migrate")
@click.argument(
    "toc_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        path_type=Path,
    ),
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["jb-v0.10"]),
    help="The format to migrate from.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        allow_dash=True,
        exists=False,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
    ),
    help="Write to a file path.",
)
def migrate_toc(
    toc_file: Path,
    format: str,
    output: Path,
) -> None: ...
