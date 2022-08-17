#!/usr/bin/env python3

from logging import info, error

if __name__ == '__main__':
    import argparse
    import logging
    import subprocess
    import shutil

    parser = argparse.ArgumentParser(description='Tool to check if IPv6 prefix changed and update docker with the new one')
    parser.add_argument('-i', '--interface', required=True, help='Interface of which the IPv6 prefix should be taken')
    args = parser.parse_args()

    # check for the ip utility
    if shutil.which('ip') is None:
        error('Unix tool \'ip\' is not installed')
        exit(1)

    output = subprocess.run(['ip','-6','-json','add','sh','dev',args.interface,'scope','global'])
    print(output)