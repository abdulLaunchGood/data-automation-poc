from setuptools import find_packages, setup

setup(
    name="prefect_poc",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "prefect",
        "pandas",
        "requests",
    ],
    extras_require={
        "dev": []
    },
)
