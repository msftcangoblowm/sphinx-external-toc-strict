Why
====

Primarily didn't want dependency, pyyaml. Also sphinx-external-toc package
appears to be unmaintained.

Removing pyyaml/yaml meant extensive changes. So even if the original
author reemerges, didn't want to trouble him with a package he'll no
longer recognize.

A fork is necessary.

Fixes

- meta field values are scrutinized
- rewrote file name handling issue affecting markdown support
- static type checking
- Extensive unittest coverage
- unittest for mixed markdown and restructuredtext
- the dependencies
- in-code documentation

Enhancements

- Hardened YAML parsing
- Complete **code manual**
- Makefile
- Makefile for docs
- semantic versioning
- github actions
- **mixed** markdown and ReStructuredText support

Dependencies
-------------

Simplier toolchain
^^^^^^^^^^^^^^^^^^^

Switched these dependencies

- pyyaml and yaml --> strictyaml

  Absolutely do not want pyyaml. It's a hard no(rway)!

- pyright --> mypy

- flit --> setuptools

``myst-parser`` is a requirement when running the unittests

Markdown
^^^^^^^^^

Support for both restructuredtext and **markdown**.

Can mix the two.

The only restriction being the root document must be a .rst file


strictyaml
-----------

Advantages:

- Uses a subset of YAML spec

- Removes threat of rogue YAML files. Security issues ... gone!

- YAML flow style is allowed


Uses a schema when parsing yaml files. Since ToC files structure
is dynamic, initial schema is :py:class:`strictyaml.Any`

This treats all field values as str.

All the field keys are known. So the parser uses a map of
:menuselection:`key --> strictyaml Validator` to correct the field values' data type

.. seealso::

   Explains issues faced by yaml parsers

   `Why? <https://hitchdev.com/strictyaml/why/>`_

   `Why not? <https://hitchdev.com/strictyaml/why-not/>`_
