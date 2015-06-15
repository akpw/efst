## Copyright (c) 2014 Arseniy Kuznetsov
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

import os
from ..base import test_base
from efst.encfs.encfs_cfg import EncFSCFG, EncFSCipherAlg, EncFSNameAlg


class EFSCTest(test_base.BMPTest):
    @classmethod
    def setUpClass(cls):
        cls.src_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), 'data'))
        cls.bckp_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '.data'))
        super(EFSCTest, cls).setUpClass()

    @property
    def test_cfg_entry_name(self):
        return 'TestEFSTCfgEntry'

    @property
    def test_cfg_entry_name_shortcut(self):
        return 'tEFSTCfg'

    @property
    def test_cfg_entry(self):
        return EncFSCFG.EncFSCfgEntry(
                    'Blowfish',
                    '160',
                    '2048',
                    'Block32',
                    True,
                    True,
                    True,
                    '8',
                    False)

    @property
    def test_cfg_entry_config(self):
        entry_tr = lambda bool_value: 'y' if bool_value else 'n'

        cfg_entry = self.test_cfg_entry
        return EncFSCFG.EncFSCfgEntry(
                                      EncFSCipherAlg.alg_type_by_name(cfg_entry.cipherAlg).value,
                                      cfg_entry.keySize,
                                      cfg_entry.blockSize,
                                      EncFSNameAlg.alg_type_by_name(cfg_entry.nameAlg).value,
                                      entry_tr(cfg_entry.chainedNameIV),
                                      entry_tr(cfg_entry.uniqueIV),
                                      entry_tr(cfg_entry.blockMACBytes),
                                      cfg_entry.blockMACRandBytes,
                                      entry_tr(cfg_entry.allowHoles)
                                      )
