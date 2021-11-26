"""Setup."""

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

inst_reqs = ["rio-cogeo>=3.0,<4.0"]

extra_reqs = {
    "test": ["pytest", "pytest-cov"],
    "dev": ["pytest", "pytest-cov", "pre-commit"],
}

setup(
    name="rio-chop",
    python_requires=">=3.7",
    description=u"Cloud Optimized GeoTIFF (COGEO) creation plugin for rasterio",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="COGEO CloudOptimized Geotiff rasterio",
    author=u"Vincent Sarago",
    author_email="vincent@developmentseed.com",
    url="https://github.com/cogeotiff/rio-chopcog",
    license="BSD-3",
    packages=find_packages(exclude=["tests"]),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
    entry_points="""
      [rasterio.rio_plugins]
      chop=rio_chop.scripts.cli:chop
      """,
)
