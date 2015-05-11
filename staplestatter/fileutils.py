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


"""

This module is used to load cadnano json files using cadnano2.5 library.

You have to make sure that cadnano is importable before loading/importing/running this.

"""

from __future__ import absolute_import, print_function
import json

from cadnano.document import Document
from cadnano.fileio.nnodecode import decodeFile, decode


def load_doc_from_file(filename):
    """
    Load cadnano json file by filename and return a cadnano Document.
    Usually the doc is not of much use; rather, use the part object:
        part = doc.children()[0]   # or doc.parts() if using an earlier cadnano2.5 commit
    """
    with open(filename) as fd:
        nno_dict = json.load(fd)
    doc = Document()
    decode(doc, nno_dict)
    return doc


def apply_sequence(part, sequence):
    """ Reminder on how to apply a sequence. """
    scaf_oligo = next(oligo for oligo in part.oligos() if not oligo.isStaple())
    scaf_oligo.applySequence(sequence, use_undostack=Fales)
