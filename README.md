# galmask

**galmask** is an open-source package written in Python that provides a simple way to remove unwanted background source detections from galaxy images.
It builds on top of `astropy` and `photutils` astronomical Python libraries and the `opencv` and `skimage` image processing libraries.

The main requirements of `galmask` are:
- `astropy` for handling FITS I/O and general-purpose astronomical routines.
- `photutils` for photometry purposes and deblending detected sources.
- `opencv-python` for connected-component analysis.
- `skimage` for general image processing functionalities.

# Installation

## Via `pip`

`galmask` can be installed from PyPI via `pip` by running::

```
pip install galmask
```

## Alternative method

`galmask` can also be installed by cloning the repository and doing a pip install in the project directory::

```
git clone https://github.com/Yash-10/galmask
cd galmask
pip install .
```

It would be beneficial to create a python virtual environment and install the package within it, to prevent
manipulating your global dependency versions.

# Quick example

# Documentation

The documentation is generated using the [Sphinx](https://www.sphinx-doc.org/) documentation tool and hosted by [Read the Docs](https://readthedocs.org/).
You can find the API reference and also some empirical tips to use galmask there.

# Tests

For running the tests, you would need to install [pytest](https://docs.pytest.org/). You can navigate to the `tests/` directory and run:

```
pytest <name_of_file>
```

# Contribute

Contributions are welcome! Currently, there seem to be a few inefficient ways of handling things within galmask, and we would like you to contribute and improve the package!

Please let us know of any bugs/issues by opening an issue in the [issue tracker](https://github.com/Yash-10/galmask/issues).

# Citing



# License and copyright

galmask is licensed under the [MIT License](LICENSE).

Copyright (c) 2022 Yash Gondhalekar
