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

# pylint: disable-msg=C0103

"""

Module with sequence utility functions.

"""

import os
import yaml
import json


VERBOSE = 0


def load_seq(args):
    """
    I figure there are a couple of ways I'd want to specify the sequences, from low to high complexity:
    1) Just one fucking sequence.
    2) One sequence, but with an offset
    3) Several sequences.

    In the case of several sequences, I would need some way to determine which sequence to apply to which oligo.
    That could be any of:
    * Length
    * Scaffold or staple strand(set)
    * Start (5p) position vhelix[baseidx] --
    * End (3p) position vhelix[baseidx] --
    I don't think it would be too hard to make a general filtering function that could take any or all
    of these discriminators into consideration.

    This will always return a list of dicts: (The only guaranteed key is 'seq').
        [{
            seq: <sequence>,
            name: <descriptive name for sequence, mostly for the user.>
            bp: <expected length of the sequence (again, mostly for the user)>
            criteria: {
                st_type: <"scaf" or "stap">,
                length: <length>,
                5pvhnum: <vhelix number>,
                5pvhcoord: (vhcoord tuple),
                5pbaseidx: <base index>,
                (same for 3p),
                }
            offset: <integer, positive or negative>,
         }, (...) ]
    """
    seqfile = args["seqfile"]
    try:
        ext = os.path.splitext(seqfile)[1]
    except IndexError:
        ext = "txt"
    if VERBOSE > 1:
        print("seqfile:", seqfile, "- ext:", ext)
    with open(seqfile) as fd:
        if "txt" in ext:
            if args["simple_seq"]:
                print("Returning simple sequence rather than seq_spec.")
                return fd.read().strip()
            # Treat the file as a simple txt file
            seq = next(line for line in (l.strip() for l in fd) if line and line[0] != "#")
            seq = "".join(b for b in seq.upper() if b in "ATGCU")
            seqs = [{"seq": seq,
                     "criteria": {"st_type": "scaf"}
                    }]
        elif "fasta" in ext:
            # File is fasta format
            raise NotImplementedError("Fasta files are not yet implemented. (But that is easy to do when needed.)")
        elif "yaml" in ext:
            seqs = yaml.load(fd)
        elif "json" in ext:
            seqs = json.load(fd)
        else:
            raise ValueError("seqfile extension %s not recognized format." % ext)
    return seqs


def apply_sequence_reminder(part, sequence, criteria=None):
    """
    Reminder on how to apply a sequence.
    Use the apply_sequence functions in oligo_utils module!
    """
    if criteria is None:
        scaf_oligo = next(oligo for oligo in part.oligos() if not oligo.isStaple())
        scaf_oligo.applySequence(sequence, use_undostack=False)
    #

