"""Ordia.

Usage:
  ordia

Description:
  Ordia is a Python package and a webservice for the lexical data in Wikidata.

  The webservice can be started with `python app.py`.

"""

from docopt import docopt


def main():
    """Handle command-line interface."""
    docopt(__doc__)


if __name__ == '__main__':
    main()
