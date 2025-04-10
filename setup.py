from setuptools import setup, find_packages

setup(
    name="companyfinder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "gunicorn>=20.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "beautifulsoup4>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "companyfinder-api=app:main",
            "companyfinder-worker=worker:main",
        ],
    },
    author="AI Assistant",
    author_email="example@example.com",
    description="A service that analyzes domains to find company information",
    keywords="domain, company, finder, api",
    url="https://github.com/yourusername/companyfinder_py",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/companyfinder_py/issues",
        "Documentation": "https://github.com/yourusername/companyfinder_py/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/companyfinder_py",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)