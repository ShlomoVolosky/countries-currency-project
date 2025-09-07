"""
Setup script for the Countries Currency Project.

This module provides the setup configuration for the package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="countries-currency-project",
    version="1.0.0",
    author="Countries Currency Project Team",
    author_email="team@countries-currency.com",
    description="A production-grade system for processing country and currency data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/countries-currency-project",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.12.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "grafana-api>=1.0.3",
        ],
        "airflow": [
            "apache-airflow>=2.7.3",
            "apache-airflow-providers-postgres>=5.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "countries-currency=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.sql", "*.yml", "*.yaml", "*.json"],
    },
    zip_safe=False,
    keywords="countries currency exchange rates data processing api",
    project_urls={
        "Bug Reports": "https://github.com/your-org/countries-currency-project/issues",
        "Source": "https://github.com/your-org/countries-currency-project",
        "Documentation": "https://countries-currency-project.readthedocs.io/",
    },
)
