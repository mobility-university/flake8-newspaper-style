#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="flake8-newspaper-style",
    license="MIT",
    version="0.2.7",
    description="Check code for newspaper style",
    author="think",
    author_email="who@knows.me",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Flake8",
    ],
    py_modules=["flake8_newspaper_style"],
    install_requires=["flake8 > 3.0.0"],
    entry_points={
        "flake8.extension": ["NEWS100 = flake8_newspaper_style:Plugin"],
    },
)
