=================
trending-homebrew
=================

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |github-actions| |travis| |appveyor| 
        |coveralls| |codecov|
        |scrutinizer| |codacy| |codeclimate| |code-style| |pre-commit|
    * - security
      - |security-bandit| |security-pyup|
    * - package
      - |version| |wheel| |supported-versions| |supported-implementations|
        |commits-since| |dependencies-status| |semantic-versions| |license|

.. |docs| image:: https://readthedocs.org/projects/trending-homebrew/badge/?style=flat
    :target: https://trending-homebrew.readthedocs.io/
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/johnpatrickroach/trending-homebrew.svg?branch=main
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/johnpatrickroach/trending-homebrew

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/johnpatrickroach/trending-homebrew?branch=main&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/johnpatrickroach/trending-homebrew

.. |github-actions| image:: https://github.com/johnpatrickroach/trending-homebrew/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/johnpatrickroach/trending-homebrew/actions

.. |requires| image:: https://requires.io/github/johnpatrickroach/trending-homebrew/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/johnpatrickroach/trending-homebrew/requirements/?branch=main

.. |coveralls| image:: https://coveralls.io/repos/johnpatrickroach/trending-homebrew/badge.svg?branch=main&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/johnpatrickroach/trending-homebrew

.. |codecov| image:: https://codecov.io/gh/johnpatrickroach/trending-homebrew/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/johnpatrickroach/trending-homebrew

.. |codacy| image:: https://img.shields.io/codacy/grade/cf46c1370f5247a4985e2b37f7315664.svg
    :target: https://www.codacy.com/app/johnpatrickroach/trending-homebrew
    :alt: Codacy Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/johnpatrickroach/trending-homebrew/badges/gpa.svg
   :target: https://codeclimate.com/github/johnpatrickroach/trending-homebrew
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/trending-homebrew.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/trending-homebrew

.. |wheel| image:: https://img.shields.io/pypi/wheel/trending-homebrew.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/trending-homebrew

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/trending-homebrew.svg
    :alt: Supported versions
    :target: https://pypi.org/project/trending-homebrew

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/trending-homebrew.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/trending-homebrew

.. |commits-since| image:: https://img.shields.io/github/commits-since/johnpatrickroach/trending-homebrew/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/johnpatrickroach/trending-homebrew/compare/v0.1.0...main

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/quality/g/johnpatrickroach/trending-homebrew/main.svg
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/johnpatrickroach/trending-homebrew/

.. |security-pyup| image:: https://pyup.io/repos/github/johnpatrickroach/trending_homebrew/shield.svg
    :target: https://pyup.io/repos/github/johnpatrickroach/trending_homebrew/
    :alt: Updates

.. |dependencies-status| image:: https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg
   :target: https://github.com/johnpatrickroach/trending-homebrew/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot

.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. |security-bandit| image:: https://img.shields.io/badge/security-bandit-green.svg
   :target: https://github.com/PyCQA/bandit

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/johnpatrickroach/trending-homebrew/blob/master/.pre-commit-config.yaml

.. |semantic-versions| image:: https://img.shields.io/badge/%C2%90%F0%9F%93%A6%F0%9F%9A%80%C2%90-semantic--versions-e10079.svg
   :target: https://github.com/johnpatrickroach/trending-homebrew/releases

.. |license| image:: https://img.shields.io/github/license/johnpatrickroach/trending-homebrew
   :target: https://github.com/johnpatrickroach/trending-homebrew/blob/master/LICENSE

.. end-badges

Tool for identifying trending Homebrew formulae, casks, and build errors.

* Free software: MIT license

Installation
============

::

    pip install trending-homebrew

You can also install the in-development version with::

    pip install https://github.com/johnpatrickroach/trending-homebrew/archive/main.zip


Documentation
=============


https://trending-homebrew.readthedocs.io/


Features
========

* TODO


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

Credits
=======

* TODO

