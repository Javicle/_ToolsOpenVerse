from setuptools import find_packages, setup

setup(
    name="Tools",
    version="0.0.1",
    description="Tools for OpenVerseProject",
    author="Javicle",
    author_email="qubackx@gmail.com",
    packages=find_packages(where="src"),
    package_data={"tools_openverse.common": ["py.typed"]},
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "fastapi",
        "redis",
        "pydantic",
        "pydantic-settings",
        "setuptools",
    ],
)
