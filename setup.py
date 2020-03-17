from setuptools import setup, find_packages
import os

XRAY_SETUP_DIR = os.path.abspath(os.path.dirname(__file__))


def long_description():
    filepath = os.path.join(XRAY_SETUP_DIR, "README.md")
    with open(filepath) as f:
        return f.read()


PKG_INSTALL_REQS = ["pytest==4.3.1", "requests==2.21.0"]


setup(
    name="pytest_xrayjira",
    author="Inbar Rose",
    author_email="inbar.rose1@gmail.com",
    version="1.0",
    python_requires=">=3.7.4",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",)),
    #  download_url="MISSING",  # TODO: add download_url
    install_requires=PKG_INSTALL_REQS,
    summary="py.test Xray Jira integration plugin, using markers",
    entry_points={"pytest11": ["pytest_xrayjira = pytest_xrayjira.plugin"]},
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)

