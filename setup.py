#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogSentry - Lightweight Log Intelligence Analysis Engine
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="logsentry",
    version="1.0.0",
    author="LogSentry Team",
    author_email="logsentry@example.com",
    description="Lightweight Log Intelligence Analysis Engine CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/logsentry",
    py_modules=["logsentry"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "logsentry=logsentry:main",
        ],
    },
    keywords="log analysis monitoring cli debugging troubleshooting",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/logsentry/issues",
        "Source": "https://github.com/gitstq/logsentry",
    },
)
