#!/usr/bin/env python
# coding=utf8
## Copyright (c) 2015 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from efst.cli.efst.efst_dispatch import EFSTDispatcher
from efst.cli.efsc.efsc_options import EFSCOptionsParser, EFSCCommands


class EFSCDispatcher(EFSTDispatcher):
    ''' EFSC Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = EFSCOptionsParser()

    # Dispatcher
    def dispatch(self):
        if not super().dispatch():
            args = self.option_parser.parse_options()

            if args['sub_cmd'] in ('create-key'):
                self.create_key(args)

            else:
                print('Nothing to dispatch')
                return False

        return True

def main():
    EFSCDispatcher().dispatch()

if __name__ == '__main__':
    main()

