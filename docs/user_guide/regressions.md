# Known regressions

In `CHANGES.rst`, has a section of the same name, those issues are intended to be fixed.

These lack that intention.

::: note
**This is a markdown file!**

Proof, in ToC, can mix markdown and RestructuredText files
:::

## Bugs


- Continuous numbering **does not work**

  The sphinx extension
  [sphinx-multitoc-numbering](https://github.com/executablebooks/sphinx-multitoc-numbering)
  which is supposed to fix this issue. However the package is unmaintained and **does not work**

  Package needs to be tested. There is a waiting PR that needs to be looked at too!

## Dropped support

- hidden document files

## Enhancements

These are proposed enhancements

- change theme to [sphinx-book-theme#304](https://github.com/executablebooks/sphinx-book-theme/pull/304)

- CLI command to generate toc from existing documentation ``toctrees`` (and then remove toctree directives)

- document suppressing warnings
