# Recommendation service

Service is responsible for fetching data from Database Service and making recommendations of books based on selected criteria and emotional similarity of books.

**More documentation to be added**

## Installation

Initially, you need `python` 3.5.x or higher and `virtualenv` to be installed on your machine.

```bash
    # to keep the namespace clean
    virtualenv -p python3 .venv

    # to install dependencies
    pip install -r requirements.txt

    # enter the virtual environment
    source .venv/bin/activate
```

## Testing

Currently, for testing purposes are used doctests, eventually unit tests may be added.
To run tests type `./runtests` in the terminal.


## Style Guide

Full PEP8 [here](https://www.python.org/dev/peps/pep-0008/) compliance. You may use PyLint. 1 tab must be 4 spaces wide. Don't use tab character. Configure your editor accordingly. Docstrings must follow NumPy/SciPy style [here](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt).
