"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Command line functions

Usage

sphinx-etoc-strict [command] [options]

Help

sphinx-etoc-strict --help

sphinx-etoc-strict [command] --help

commands:

- create_site

- create_toc

- migrate_toc

- parse_toc

"""

from __future__ import annotations

from pathlib import Path

import click

from .constants import __version_app
from .parsing_shared import FILE_FORMATS
from .parsing_strictyaml import (
    dump_yaml,
    load_yaml,
    parse_toc_yaml,
)
from .tools_strictyaml import (
    create_site_from_toc,
    create_site_map_from_path,
    migrate_jupyter_book,
    site_map_guess_titles,
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version_app)
def main():
    """Command-line for sphinx-external-toc-strict. Prints usage"""


@main.command("parse")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
def parse_toc(toc_file):
    """Parse a ToC file to a site-map YAML

    :param toc_file: Absolute path to toc file. File name convention: ``_toc.yml ``
    :type toc_file: pathlib.Path
    """
    yml = load_yaml(toc_file)
    site_map = parse_toc_yaml(yml)
    # out_json = site_map.as_json()
    yml_2 = dump_yaml(site_map)
    # click.echo(yaml.dump(data, sort_keys=False, default_flow_style=False))
    click.echo(yml_2)


@main.command("to-project")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
@click.option(
    "-p",
    "--path",
    default=None,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
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
def create_site(toc_file, path, extension, overwrite):
    """Create a project directory from a ToC file

    :param toc_file: Absolute path to toc file. File name convention: ``_toc.yml ``
    :type toc_file: pathlib.Path
    :param path:

       root index file absolute path. Sphinx file stem convention:
       ``index``. Possible suffixes: ``.rst`` or ``.md``

    :type path: pathlib.Path
    :param extension:

       Default documentation file format extension. Either "rst" or "md"

    :type extension: str
    :param overwrite:

       Whether to overwrite docs/ folder tree. A default would be really
       nice here, ey?

    :type overwrite: bool

    .. todo:: conf.py

       Option to add basic conf.py?

    """
    if not extension.startswith("."):
        default_ext = f".{extension}"
    else:  # pragma: no cover
        default_ext = extension

    try:
        create_site_from_toc(
            toc_file,
            root_path=path,
            default_ext=default_ext,
            overwrite=overwrite,
        )
    except IOError:
        msg_err = "Existing file found. Overwrite permission not granted"
        click.secho(msg_err, fg="green")
    else:
        click.secho("SUCCESS!", fg="green")


@main.command("from-project")
@click.argument(
    "site_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
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
def create_toc(site_dir, extension, index, skip_match, guess_titles, file_format):
    """Create a ToC file from a project directory

    :param site_dir: Base folder documentation. Coding convention ``docs/`` or ``doc/``
    :type site_dir: pathlib.Path
    :param extension:

       Documentation file format extensions. Default both ".rst" or ".md". Take
       the opportunity to specify one rather than both

    :type extension: str
    :param index: File stem of root file. Coding convention is ``index``
    :type index: str
    :param skip_match:

       Default ``(".*",)``. Can provide option multiple times. Glob of
       relative path files to skip

    :type skip_match: str
    :param guess_titles:

       Default True. ``True`` to pull title from each document

    :type guess_titles: bool
    :param file_format:

       Supported use cases: ``default``, ``jb-book``, or ``jb-article``

    :type file_format: str
    """
    site_map = create_site_map_from_path(
        site_dir,
        suffixes=extension,
        default_index=index,
        ignore_matches=skip_match,
        file_format=file_format,
    )
    # May raise NotADirectoryError or FileNotFoundError
    site_map_guess_titles(site_map, index, is_guess=guess_titles)

    # yaml.dump(data, sort_keys=False, default_flow_style=False)
    yml_2 = dump_yaml(site_map)
    click.echo(yml_2)


@main.command("migrate")
@click.argument("toc_file", type=click.Path(exists=True, file_okay=True))
@click.option(
    "-f",
    "--format",
    type=click.Choice(["jb-v0.10"]),
    help="The format to migrate from.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(allow_dash=True, exists=False, file_okay=True, dir_okay=False),
    help="Write to a file path.",
)
def migrate_toc(toc_file, format, output):
    """Migrate a ToC from a previous revision

    :param toc_file: Table of contents file absolute path
    :type toc_file: pathlib.Path
    :param format: Ignored. Only possible value is ``jb-v0.10``
    :type format: str
    :param output: Output file absolute path
    :type output: pathlib.Path
    """

    toc = migrate_jupyter_book(Path(toc_file))
    # content = yaml.dump(toc, sort_keys=False, default_flow_style=False)
    content = dump_yaml(toc)

    if output:
        path = Path(output)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(content, encoding="utf8")
        click.secho(f"Written to: {path}", fg="green")
    else:
        click.echo(content)
