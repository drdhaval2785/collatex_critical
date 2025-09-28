from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="collatex-critical",
    version="0.1.3",
    description="Critical edition enhancements for CollateX with footnote apparatus and transliterations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dr. Dhaval Patel",
    author_email="drdhaval2785@gmail.com",
    url="https://github.com/drdhaval2785/collatex-critical",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "indic-transliteration",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Intended Audience :: Education",
    ],
)

