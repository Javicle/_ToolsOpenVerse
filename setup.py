from setuptools import setup, find_packages

setup(
    name="Tools",
    version="0.0.1",
    description="Tools for OpenVerseProject",
    author="Javicle",
    author_email="qubackx@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi" ,
        "redis" ,
        "pydantic" ,
        "pydantic-settings" ,
        "setuptools" ,
    ]
)