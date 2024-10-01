.. this will be appended to README.rst

Changelog
=========

..

   Feature request
   .................

   - migrate docs from rtd --> gh pages

   - https://allcontributors.org/
   - https://shields.io/badges/git-hub-contributors-from-allcontributors-org

   Known regressions
   ..................

   - For an external url, get Sphinx to open in new window
     target="_blank" rel="noopener noreferrer"

   - in cli, create_toc not gracefully handling exceptions

   - In docs, code/user_guide/regressions

   Commit items for NEXT VERSION
   ..............................

.. scriv-start-here

.. _changes_2-0-0p0:

Version 2.0.0.post0 — 2024-10-01
--------------------------------

- chore: remove direct dependency

.. _changes_2-0-0:

Version 2.0.0 — 2024-10-01
--------------------------

- ci: drop PyPy implementation no support by ruamel-yaml
- fix(tox): add setuptools into build environment
- fix(tox): install_command add constraint pip<24.2
- fix: remove myst-parser testing additional dependencies
- chore: add requirements/myst-parser.pins
- fix: myst-parser ruamel-yaml#521 pip#12884 solution pip<24.2
- fix: myst-parser use latest commit
- chore: remove pytest-cov dependency
- ci(test-coverage): remove pytest-cov. coverage > pytest-cov
- chore(tox): build current not tag
- chore(igor): remove commented out code
- ci(test-coverage): fix dependency relative path
- ci(release): python version str needs double quotes
- ci(python-nightly): fix deadsnakes/action actions/setup-python tags
- feat: sphinx drop py39 support, do the same
- feat: add intersphinx support. ref > url
- fix: click.Path parameters receive as pathlib.Path. Previously str
- ci: python base version py39 --> py310
- docs: complete code documentation
- chore: add Makefile targets version-override fix-upgrade

.. _changes_1-2-3:

Version 1.2.3 — 2024-09-19
--------------------------

- fix: gh-action-sigstore-python tag
- ci(python-nightly): update deadsnakes/action
- ci(branch-test-others): limit matrix.os to windows-latest
- chore: all badges
- chore: update gha versions
- chore: update requirement packaging 24.0 --> 24.1

.. _changes_1-2-2p4:

Version 1.2.2.post4 — 2024-08-31
--------------------------------

- test(branch-test-others): os.matrix runners append -latest

.. _changes_1-2-2p3:

Version 1.2.2.post3 — 2024-08-31
--------------------------------

- test(branch-test-others): if condition before matrix
- test(version_semantic): no test version file current version str and tuple

.. _changes_1-2-2p2:

Version 1.2.2.post2 — 2024-08-31
--------------------------------

- ci(branch-test-others: remove surround double quotes in if contains condition

.. _changes_1-2-2p1:

Version 1.2.2.post1 — 2024-08-31
--------------------------------

- ci(branch-test-others): fix if conditions. Mismatched single quotes

.. _changes_1-2-2p0:

Version 1.2.2.post0 — 2024-08-31
--------------------------------

- ci: prevent run on main branch multiple contains

.. _changes_1-2-2:

Version 1.2.2 — 2024-08-31
--------------------------

- ci(python-nightly): fix ubuntu versions
- ci(branch-test-others): add branches test Windows and MacOS
- ci(test-coverage): codecov/codecov-action 4.3.0 --> 4.5.0
- test: coverage omit igor.py and setup.py and vendered packages

.. _changes_1-2-0:

Version 1.2.0 — 2024-08-15
--------------------------

- feat: validate SiteMap.file_format setter only. If unknown use case, do nothing
- fix: upgrade dependencies zipp and typing-extension
- fix(cli): create_site print error msg when existing files and no overwrite flag
- test: add test from toc --> create site
- test: coverage fail from 70% --> 90%

.. _changes_1-1-7:

Version 1.1.7 — 2024-04-19
--------------------------

- docs(_toc.yml): change to correct repo url
- fix(LICENSE): MIT --> Apache 2.0 Was always supposed to be Apache 2.0
- style(pyproject.toml): comment out setuptools-scm option, fallback_version
- docs: add links to pypi, github, issues, chat, changelog
- docs(README.rst): add badge last commit branch main

.. _changes_1-1-6:

Version 1.1.6 — 2024-04-19
--------------------------

- ci(.gitignore): remove ignore of docs/*.inv
- ci(tox): in docs do not build_inv after clean_inv
- ci(pre-commit): remove remove-intersphinx-inventory-files, need docs/*.inv
- docs(Makefile): store *.inv needed by readthedocs
- docs: remove objects-python.txt, excessive file size
- docs: in code manual, add todo list page

.. _changes_1-1-5:

Version 1.1.5 — 2024-04-19
--------------------------

- docs(Makefile): for targets build_inv and clean_inv only use relative paths
- docs(Makefile): for targets doctest and linkcheck require target build_inv

.. _changes_1-1-4:

Version 1.1.4 — 2024-04-19
--------------------------

- ci(.readthedocs.yml): py311 --> py39, do not build pdf, and notes
- docs: defend assertions, links, in comparison table
- fix: sphinx conf option master_doc index --> intro
- docs: in comparison yaml dependency choice why and why not links
- ci(.gitignore): eventhough pre-commit remove, ignore docs/*.inv
- docs: advice on ramification of incorrectly set master_doc value
- docs: add note sphinx extension sphinx-multitoc-numbering not working
- docs: add logo files sphinx-external-toc-strict-logo.*
- docs(credit.txt): document static asset authors and license
- docs(_toc.yml): remove unnecessary captions. Rearrange ToC order
- docs(user_guide/api.rst): in example fix python code
- docs(regressions.rst): add  known regressions page, a markdown file

.. _changes_1-1-3:

Version 1.1.3 — 2024-04-18
--------------------------

- ci(.readthedocs.yml): python.install.requirements list rather than dict
- style(pyproject.toml): configure project.urls
- docs(README.rst): github-ci badge use workflow release
- docs(README.rst): add badges

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
