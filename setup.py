from setuptools import setup, find_packages

setup(
    name="autohedge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "autohedge=autohedge.main:main",
        ],
    },
    python_requires=">=3.8",
)
