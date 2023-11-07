"""This moodule contans setup script for bitwarden2keepass."""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

TEST_REQUIREMENTS = [
    # development & testing tools
    "pytest",
    "coverage[toml]",
    "pytest-cov",
]

REQUIREMENTS = [
    "pykeepass",
]

setuptools.setup(
    name="bitwarden2keepass",
    version="0.0.1",
    author="Anton Bakuteev",
    author_email="bakuteyev@gmail.com",
    description="Convert Bitwarden data to KeePass",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bakuteyev/bitwarden2keepass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=REQUIREMENTS,
    extras_require={"test": TEST_REQUIREMENTS},
    entry_points={
        'console_scripts': [
            'bitwarden2keepass=bitwarden2keepass.convert:main',
        ],
    },
)
