.. this will be appended to README.rst

Changelog
=========

..

   Feature request
   .................

   Known regressions
   ..................

   1. Dropped support for hidden document files

   Commit items for NEXT VERSION
   ..............................

.. scriv-start-here

.. _changes_1-1-2:

Version 1.1.2 — 2024-04-18
--------------------------

- ci(test-coverage.yml): bump version codecov/codecov-action
- ci(release.yml): bump version sigstore/gh-action-sigstore-python
- docs(.readthedocs.yml): during pre_build create inv files
- fix(pyproject.toml): tool.black may not contain target_version
- test(test_sphinx.py): ensure do not hardcode extension name
- fix(constants.py): g_app_name should contain underscores not hyphens
- fix(pyproject.toml): tool.mypy turn off warn_unused_ignores

.. _changes_1-1-1:

Version 1.1.1 — 2024-04-18
--------------------------

- docs(Makefile): add targets build_inv and clear_inv
- docs(Makefile): in target htmlall, add prerequisite target build_inv
- docs(conf.py): nitpick_ignore to suppress unfixed warnings
- chore(pre-commit): add hook remove-intersphinx-inventory-files
- chore(igor.py): to quietly command, add arg, cwd
- chore(igor.py): support both branch master and main
- chore(igor.py): readthedocs url hyphenated project name
- docs: convert all .inv --> .txt Do not store any .inv files
- ci(dependabot): weekly --> monthly
- ci(tox.ini): rewrite add targets docs lint mypy test pre-commit cli
- ci: initialize github workflows
- ci: actions/setup-python remove option cache pip
- fix(pep518_read.py): vendor func is_ok
- docs(README.rst): ensure passes check, rst2html.py

.. _changes_1-1-0:

Version 1.1.0 — 2024-04-16
--------------------------

- chore(pre-commit): remove ruff-pre-commit, add mypy, whitespace and file fixer
- chore(.gitignore): hide my dirty laundry
- feat: add Makefile
- chore(ci): add igor.py and howto.txt
- refactor: move source code under src/[app name] folder
- refactor: dynamic requirements
- chore: replace flit --> setuptools
- refactor: remove production dependencies pyyaml
- refactor: add production dependencies strictyaml and myst-parser
- refactor: switch testing dependency pyright --> mypy
- refactor: add testing dependencies isort, black, blackdoc, flake, twine
- feat: add semantic versioning support. setuptools-scm
- chore: add config for mypy, pytest, isort, black, blackdoc, flake, twine, sphinx, coverage
- chore: add config for setuptools_scm and pip-tools
- chore: remove config for flit and ruff.lint.isort
- feat: much smarter file suffix handling
- feat: transition pyyaml --> strictyaml
- feat: can mix markdown and restructuredtext files
- test: super difficult to accomplish test of markdown
- chore(mypy): static type checking. Not perfect
- docs: transition docs from markdown to restructuredtext
- docs: add Makefile
- docs: extensive use of sphinx extension intersphinx
- docs: add code manual
- docs: converted README.md --> README.rst
- test: add for dump_yaml when supplied unsupported type
- docs: comparison between sphinx-external-toc and sphinx-external-toc-strict
- docs: add NOTICE.txt
- docs: add PYVERSIONS sections in both README and docs/index.rst
- chore(igor.py): semantic version parsing enhancements
- chore(igor.py): do not choke if no NOTICE.txt

.. scriv-end-here
