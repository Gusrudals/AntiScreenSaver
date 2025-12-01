"""
Setup script for Anti-Screensaver Mouse Mover
Supports Windows packaging and distribution
"""

from setuptools import setup, find_packages

setup(
    name="anti-screensaver",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "anti-screensaver=main:main",
        ],
        "gui_scripts": [
            "anti-screensaver-gui=main:main",
        ],
    },
)
