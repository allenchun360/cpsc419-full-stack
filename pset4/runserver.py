#! /usr/bin/env python
"""Code for runserver"""
import argparse
from sys import exit, stderr
from regapp import APP

def get_filter_terms():
    """User interface. Gets port from user and returns it"""
    parser = argparse.ArgumentParser(description='The registrar application',
                                     prog='runserver.py', allow_abbrev=False,
                                     usage='%(prog)s ' + '[-h] port')

    parser.add_argument('port', help='the port at which ' +
                        'the server should listen')

    return parser.parse_args()


def main():
    """main"""
    try:
        port = int(get_filter_terms().port)
    except Exception:
        print('Port must be an integer.', file=stderr)
        exit(1)

    if port < 0:
        print('Port must be a positive integer', file=stderr)
        exit(1)

    try:
        APP.run(host='localhost', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
