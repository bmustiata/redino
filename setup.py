from setuptools import setup
from setuptools import find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name="redino",
    version="0.1.master",
    description="redino",
    long_description=readme,
    author="Bogdan Mustiata",
    author_email="bogdan.mustiata@gmail.com",
    license="BSD",
    install_requires=["redis==4.5.3"],
    packages=packages,
    package_data={
        "": ["*.txt", "*.rst"],
        "redino": ["py.typed"],
    },
)
