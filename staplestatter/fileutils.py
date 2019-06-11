#!/usr/bin/env python
# -*- coding: utf-8 -*-
##    Copyright 2015 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##

# pylintxx: disable-msg=C0103,C0301,C0302,R0201,R0902,R0904,R0913,W0142,W0201,W0221,W0402
# pylint: disable-msg=C0103

"""

This module is used to load cadnano json files using cadnano2.5 library.

You have to make sure that cadnano is importable before loading/importing/running this.

"""

from __future__ import absolute_import, print_function
import os
import json
import yaml

# This module is currently only for cadnano2.5 - I need to update this for cadnano2:
from cadnano.document import Document
from cadnano.fileio.nnodecode import decodeFile, decode


def load_doc_from_file(filename, doc=None):
    """
    Load cadnano json file by filename and return a cadnano Document.
    Usually the doc is not of much use; rather, use the part object:
        part = doc.children()[0]   # or doc.parts() if using an earlier cadnano2.5 commit
    """
    if doc is None:
        doc = Document()
    with open(filename) as fp:
        nno_dict = json.load(fp)
    decode(doc, nno_dict)
    return doc


def load_json_or_yaml(filepath, ext=None):
    """ Load """
    if ext is None:
        try:
            ext = os.path.splitext(filepath)[1]
        except IndexError:
            ext = "yaml"
    with open(filepath) as fd:
        data = json.load(fd) if "json" in ext else yaml.load(fd)
    return data


def ok_to_write_to_file(filename, overwrite):
    """ Assert whether it is OK to write to staples_outputfn """
    if overwrite or not os.path.exists(filename):
        return True
    # os.path.exists(staples_outputfn) is True
    overwrite = input(filename + " already exists. Overwrite? [Y/n]")
    if overwrite and overwrite.lower()[0] == "n":
        return False
    return True

