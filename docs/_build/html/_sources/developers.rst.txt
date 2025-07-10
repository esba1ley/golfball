For Developers
==============

This page is a "how to" for developers.

Repo Structure
--------------

This repository is structured as follows:

.. code-block:: text

   .
    ├── AUTHORS.rst . . . . . . . . Authors who contributed to code
    ├── CHANGELOG.rst . . . . . . . Tagged/Released Version Change Log
    ├── CONTRIBUTING.rst  . . . . . How to contribute to the project
    ├── Dockerfile  . . . . . . . . Creates golfball app Docker image (portable)
    ├── Jenkinsfile . . . . . . . . Jenkins pipeline definition to test golfball
    ├── LICENSE . . . . . . . . . . license
    ├── Makefile  . . . . . . . . . Developer shortcuts (with help!)
    ├── README.rst  . . . . . . . . Repository top-level README
    ├── container_test.sh . . . . . script to test golfball with Jenkins
    ├── data  . . . . . . . . . . . DRAG MODEL SOURCE DATA
    │   ├── cd_table.h5 . . . . . . HDF5 table used by golfball
    │   ├── dimpledSpheresDragData/ directory with source drag data in it
    │   └── write_cd_h5.py  . . . . script to generate HDF5 table for golfball
    ├── docs  . . . . . . . . . . . PACKAGE DOCUMENTATION
    │   ├── Makefile  . . . . . . . Build Targets for documentation
    │   ├── _static/  . . . . . . . directory w/ static content
    │   ├── authors.rst . . . . . . include ../AUTHORS.rst
    │   ├── changelog.rst . . . . . include ../CHANGELOG.rst
    │   ├── conf.py . . . . . . . . Documentation Configuration
    │   ├── contributing.rst  . . . include ../CONTRIBUTING.rst
    │   ├── developers.rst  . . . . Documentation for Developers (this file)
    │   ├── examples.rst  . . . . . How to use golfball package
    │   ├── figures/  . . . . . . . Documentation Figures
    │   ├── index.html  . . . . . . Redirect to _build/html/index.html
    │   ├── index.rst . . . . . . . Top-level Documentation File
    │   ├── install.rst . . . . . . Installation Documentation
    │   ├── kudos.rst   . . . . . . "Thanks" recognition
    │   ├── license.rst . . . . . . include ../LICENSE
    │   ├── modules.rst . . . . . . code modules (extracts docstrings from code)
    │   ├── quickstart.rst  . . . . How to get started quickly
    │   └── requirements.txt  . . . sphinx build requirements
    ├── golfball  . . . . . . . . . GOLFBALL PYTHON PACKAGE
    │   ├── __init__.py . . . . . . Python package init file
    │   ├── __version__.py  . . . . current tag/release
    │   ├── cd_table.h5 . . . . . . data that gets installed by pip
    │   ├── sim.py  . . . . . . . . Golfball Simulation
    │   ├── stdAtm76.py . . . . . . Standard 1976 Atmosphere model
    │   ├── utils.py  . . . . . . . utilities for testing
    │   └── yaml2results.py . . . . convert sim output to Dakota results format
    ├── setup.py  . . . . . . . . . PyPA/PyPI setuptools configuration
    └── test  . . . . . . . . . . . AUTOMATED TESTS FOR PYTEST
        ├── sim/  . . . . . . . . . golfball sim tests
        ├── stdAtm76/ . . . . . . . atmosphere model tests
        └── uq_dakota/  . . . . . . Dakota execution tests


The above list was made by taking the output of:

.. code-block:: text

   $ tree -L 2 .

at the top level of this repository, and then annotating the descriptions
manually in this file.

Using Makefiles
---------------

The bulk of development tasks are automated by Make targets in makefiles.  All
makefiles have a built-in "help" target, that is also the default.  For example,
in the top directory of this repository:

.. code-block:: text

    $ make
    -------------------- Makefile Target List --------------------------
    Package: golfball
    Git branch: main
    --------------------------------------------------------------------
    help                 Display list of intended targets for user (DEFAULT)
    test-all             check style, coverage, and run tests.
    test                 run tests quickly with the default Python
    coverage-report      generate code coverage report with pytest
    pylint-report        check style with pylint
    install              install the package to the active Python's site-packages
    install-dev          install the package for active development
    uninstall            uninstall the packge from the current environment
    docs                 generate Sphinx HTML documentation, including API docs
    clean                remove all artifacts
    clean-build          remove build artifacts
    clean-pyc            remove Python bytecode and object artifacts
    clean-test           remove test reports, caches, and coverage artifacts
    clean-docs           remove documentation build
    clean-dakota         clean dakota run outputs
    docker-build         Build docker image, using cached layers
    docker-build-nc      Build docker image, WITHOUT cached layers
    docker-run           run golfball in container as one-shot
    docker-run-it        run docker image interactively
    docker-test          test golfball inside the container
    docker-pull          pull branch image from registry
    docker-push          push branch image to registry
    docker-archive       Create g-zipped tarball of image
    --------------------------------------------------------------------

The list above are the makefile targets the developer can do in that directory,
with a short description of what they do.  For the specific commands, look in
the **Makefile** itself.

Local Development
-----------------

The golfball sim is written to be completely generic with no platform-dependent
libraries.  Therefore, if you have a local Python environment, you can use
**pip** to install this module as an editable module as instructed by the
installation documentation.  If you want to not have pip auto-install the
dependencies that golfball needs, see the installation instructions for which
python packages you'll need to install with your other package manager (e.g.
conda).

Local Testing
-------------

Using the "test" make target will first ensure that the golfball package is
installed as an editable package (you can make changes without needing to re-
install) and then executes the full pytest suite, capturing data for a coverage
report, and produces an HTML pytest report at **reports/pytest/index.html**.  In
general, all targets involved in testing the code put their human-readable
outputs into the **reports/** directory.

To get the coverage report, run the "coverage_report" make target, and it will
produce an HTML report at **reports/coverage/index.html**.

To get a pylint report, run the "pylint_report" make target, and it will produce
a pylint report as a text file at **reports/pylint/pylint_report.txt**.

Note that you may see skipped tests for the dakota tests if dakota is not
installed in your system path.  This is by design.  If you want the dakota tests
to execute, check your dakota installation and make sure the executable is
available in your system path.

Building Documentation
----------------------

To build the documentation for this project, just use the "docs" target of the
makefile.  The documentation is posted on GitHub Pages, and it hosts from the master branch.


Building the Docker App
-----------------------

To build an executable image of the golfball package and its required
environment for portability across platforms, use the "docker-build" makefile
target.  This will first build the "environment" image, then the "application"
image.  The use cases for the two different images are as follows:

   1. The *environment* image is used to build the environment once and speed up
   repeated building of the application image as Python code changes are made.
   It is also the image used by the Jenkins CI/CD workflow to automatically test
   the golfball code when changes are made in GitHub.

   2. The *application* image is the environment image with golfball installed
   in it.  This is the portable "batteries included" application that can be
   used in parallel computing.


Testing the Docker App
----------------------

Use the "docker-test" make target to execute pytest *inside* the container to
run the automated test suite in the container environment.  The test result will
be an HTML report written at **reports/container/pytest/index.html**.
