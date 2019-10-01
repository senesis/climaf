#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Testing Pre-requisites for CliMAF

Run it as : python -m unittest -v test_req

S.Senesi - jan 2015
"""

from __future__ import print_function, division, unicode_literals, absolute_import

import unittest
import os


class A_externals(unittest.TestCase):
    def setUp(self):
        def test_binary(binary, test_command="type %s > /dev/null 2>&1", error_msg="Cannot execute %s"):
            self.assertEqual(os.system(test_command % binary), 0, error_msg % binary)
        self.my_test=test_binary

    def test_1_convert(self):
        binary = "convert"
        self.my_test(binary=binary)

    def test_2_identify(self):
        binary = "identify"
        self.my_test(binary=binary)

    def test_3_ncatted(self):
        binary = "ncatted"
        self.my_test(binary=binary)

    def test_4_ncdump(self):
        binary = "ncdump"
        self.my_test(binary=binary)

    def test_5_ncwa(self):
        binary = "convert"
        self.my_test(binary=binary)

    def test_6_ncrcat(self):
        binary = "ncrcat"
        self.my_test(binary=binary)

    def test_7_cdo(self):
        binary = "cdo"
        self.my_test(binary=binary)

    def test_9_cdo(self):
        binary = "ncview"
        self.my_test(binary=binary, error_msg="You may have troubles without %s")

    def test_ncl(self):
        binary = "ncl"
        self.my_test(binary=binary, error_msg="You may have troubles without %s")

    def tearDown(self):
        pass


if __name__ == '__main__':
    print("Testing CliMAF pre-requisites")
    unittest.main()
