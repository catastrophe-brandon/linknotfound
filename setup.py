import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="linknotfound",
    version="0.0.2",
    author="Eduardo Cerqueira",
    author_email="eduardomcerqueira@gmail.com",
    description="cli tool to find broken links in applications source code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eduardocerqueira/linknotfound",
    project_urls={
        "Bug Tracker": "https://github.com/eduardocerqueira/linknotfound/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
    packages=setuptools.find_packages(include=["linknotfound", "linknotfound.*"]),
    install_requires=[
        "requests==2.28.1",
        "GitPython==3.1.27",
        "PyGithub==1.55",
        "click==8.1.3",
    ],
    py_modules=["linknotfound"],
    entry_points={
        "console_scripts": [
            "linknotfound = linknotfound.main:cli",
        ],
    },
)
