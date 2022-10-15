#!/usr/bin/env python3
import setuptools

with open('README.md', 'r', encoding='utf-8') as file:
    README = file.read()

setuptools.setup(
    name="flake8-newspaper-style",
    license="MIT",
    version="0.4.3",
    description="Check code for newspaper style",
    long_description=README,
    long_description_content_type='text/markdown',
    author="think",
    author_email="who@knows.me",
    url='https://github.com/mobility-university/flake8-newspaper-style',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Flake8",
    ],
    py_modules=["flake8_newspaper_style"],
    install_requires=["flake8 > 3.0.0"],
    entry_points={
        "flake8.extension": ["NEW100 = flake8_newspaper_style:Plugin"],
    },
)
