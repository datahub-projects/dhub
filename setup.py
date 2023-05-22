from setuptools import setup, find_packages
setup(
    name="dhub",
    version="0.2.0",
    packages=find_packages(),
    python_requires='>=3',
    scripts=['bin/dhub'],
    install_requires=[
        "requests == 2.31.0",
        "blessings == 1.7",
        "python_dateutil == 2.8.1",
    ],
    include_package_data=True
)
