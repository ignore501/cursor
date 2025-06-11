from setuptools import setup, find_packages

setup(
    name="ronin_tg_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot>=20.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "jupyter>=1.0.0",
        "nbformat>=5.9.2",
        "nbconvert>=7.14.2",
        "pytest>=7.0.0",
    ],
) 