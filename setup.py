# -*- coding: utf-8 -*-

"""The ``setup.py`` file."""

from setuptools import setup, find_packages
from codecs import open
from os import path


# Where are we? Full path.
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(

    # What's the project's name?
    # E.g., when you type ``pip install <name>``.
    name="armyguys",

    # Version should comply with PEP440.
    version="0.0.1dev1",

    # Describe the project.
    description="A tool for working with AWS.",
    long_description=long_description,
    keywords="cli AWS deployment",

    # The project's main homepage.
    url="https://github.com/jtpaasch/armyguys",

    # Author details.
    author="JT Paasch",
    author_email="jt.paasch@gmail.com",

    # Choose a license.
    license="MIT",

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

        # How mature is the project?
        "Development Status :: 3 - Alpha",

        # Who and what is it for?
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        # What's the license (should match the ``license`` param above).
        "License :: OSI Approved :: MIT License",

        # Which languages/versions does this work with?
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",

    ],

    # Which packages should be included in the dist?
    packages=find_packages(
        exclude=[
            "venv",
            "tests",
        ]
    ),

    # What are the run-time dependencies?
    # Pip will install these when you install this package.
    install_requires=[
        "click",
        "boto3"
    ],

    # Are there any extra dependency groups, e.g., for testing?
    extras_require={
        "test": [
            "hypthesis",
            "coverage",
            "flake8",
            "pep257",
        ],
    },

    # This is an executable script, so where is/are the entry point/s?
    entry_points={
        "console_scripts": [

            # Make a script/executable called ``armyguys`` which,
            # when executed, loads and invokes ``armyguys.cli.main.cli()``.
            "armyguys = armyguys.cli.main:cli",

        ],
    },

)
