from io import open
from os import environ

from setuptools import setup


def read(filename):
    with open(filename, encoding="utf-8") as file:
        return file.read()


def requirements():
    with open("requirements.txt", "r") as req:
        return [r for r in req.read().split("\n") if r]


setup(
    name="tochka_api",
    version=environ.get("TAG_VERSION").replace("v", ""),
    packages=[
        "tochka_api",
        "tochka_api.exceptions",
        "tochka_api.models",
        "tochka_api.models.responses",
    ],
    url="https://github.com/WhiteApfel/tochka_api",
    license="Mozilla Public License 2.0",
    author="WhiteApfel",
    author_email="white@pfel.ru",
    description="Simple Tochka Bank Open API client",
    install_requires=requirements(),
    project_urls={
        "Source code": "https://github.com/WhiteApfel/tochka-api",
        "Write me": "https://t.me/whiteapfel",
    },
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords="tochka openapi api bank",
)
