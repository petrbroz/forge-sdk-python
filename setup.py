import setuptools

with open("README.md") as f:
    readme = f.read()

setuptools.setup(
    name="autodesk-forge-sdk",
    version="0.1.1",
    author="Petr Broz",
    author_email="petr.broz@autodesk.com",
    description="Unofficial Autodesk Forge SDK for Python.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/petrbroz/forge-sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/petrbroz/forge-sdk-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)