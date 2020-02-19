#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Tools to deal with tests.
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import subprocess
import unittest

from climaf.api import cshow, ncview, cfile
from climaf import xdg_bin


def skipUnless_CNRM_Lustre():
    if os.path.exists('/cnrm'):
        return lambda func: func
    return unittest.skip("because CNRM's Lustre not available")


def skipUnless_Ciclad():
    if os.path.exists('/prodigfs') or os.path.exists('/home/senesi/tmp/ciclad/prodigfs/esg/CMIP5'):
        return lambda func: func
    return unittest.skip("because not on Ciclad")


def remove_dir_and_content(dirname):
    if os.path.isdir(dirname):
        # Deal with files
        listfiles = list()
        listdirs = list()
        for (d, subdirs, files) in os.walk(dirname):
            for name in files:
                listfiles.append(os.path.sep.join([d, name]))
            for subd in subdirs:
                listdirs.append(os.path.sep.join([d, subd]))
        for f in listfiles:
            os.remove(f)
        # Deal with subdirectories
        for d in sorted(listdirs, reverse=True):
            os.rmdir(d)


def compare_html_files(file_test, file_ref):
    if not os.path.exists(file_test) or not os.path.exists(file_ref):
        raise OSError("Check files existence: %s - %s" % (file_test, file_ref))
    if file_ref.split(".")[-1] != "html":
        raise ValueError("This function only apply to html files.")
    if file_test.split(".")[-1] != file_ref.split(".")[-1]:
        raise ValueError("Files have different formats: %s / %s" % (os.path.basename(file_test),
                                                                    os.path.basename(file_ref)))
    os.system("firefox file://{} &".format(file_test))
    os.system("firefox file://{} &".format(file_ref))
    rep = None
    while rep not in ["y", "n"]:
        rep = raw_input("Are the html pages identical? y/n\n").lower()
    return rep == "y"


def compare_netcdf_files(file_test, file_ref, display=False):
    # Todo: Check the metadata of the files
    if not os.path.exists(cfile(file_test)) or not os.path.exists(file_ref):
        raise OSError("Check files existence: %s - %s" % (cfile(file_test), file_ref))
    if file_ref.split(".")[-1] != "nc":
        raise ValueError("This function only apply to netcdf files.")
    if cfile(file_test).split(".")[-1] != file_ref.split(".")[-1]:
        raise ValueError("Files have different formats: %s / %s" % (os.path.basename(cfile(file_test)),
                                                                    os.path.basename(file_ref)))
    if display:
        ncview(file_test)
    rep = subprocess.check_output("cdo diffn {} {}".format(cfile(file_test), file_ref), shell=True)
    if len(rep.split("\n")) > 1:
        raise ValueError("Files' content are different.")


def compare_picture_files(object_test, fic_ref, display=True):
    # TODO: Check the metadata of the files
    # Transform the strings in list of strings
    fic_test = cfile(object_test)
    fic_test = fic_test.split(" ")
    if not isinstance(fic_ref, list):
        fic_ref = [fic_ref, ]
    # Loop on the files
    for (file_test, file_ref) in zip(fic_test, fic_ref):
        # Check the existence and the consistency of the comparison
        if not (os.path.exists(file_test) and os.path.exists(file_ref)):
            raise ValueError("Check files existence: %s - %s" % (file_test, file_ref))
        # Find out the format of the files and the dedicated display command
        files_format = list(set([file_test.split(".")[-1], file_ref.split(".")[-1]]))
        if len(files_format) > 1:
            raise ValueError("Files to compare have not the same format: %s" % " - ".join(files_format))
        else:
            files_format = files_format[0]
        if files_format not in ["png", "eps", "jpeg", "pdf"]:
            raise ValueError("Unknown format found %s" % files_format)
        if xdg_bin and files_format in ["eps", "pdf"]:
            display_cmd = "xdg-open {}"
        else:
            display_cmd = "display {}"
        diff_file = file_test + "_diff.{}".format(files_format)
        if display:
            cshow(object_test)
        # Compare the two files, display the difference if needed
        try:
            subprocess.check_call("compare -compose src -metric AE {} {} {}".format(file_test, file_ref, diff_file),
                                  shell=True)
        except subprocess.CalledProcessError:
            if display:
                subprocess.check_call(display_cmd.format(diff_file))
            raise ValueError("The files following files are different: %s - %s" % (file_test, file_ref))
        finally:
            os.remove(diff_file)
