#!/usr/bin/env python
# -*- coding: utf-8 -*-
##    Copyright 2014 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
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

This module deals with everything related to cadnano.

Generally returns "normal" datastructures, e.g. lists or dicts.


Interesting attributes on cadnano objects:

## PART ##
part.oligos(), part._oligos     # set of oligos.


## Oligo ##

oligo.isStaple()                # returns oligo._stand5p.isStaple()
oligo.length(), oligo._length   # total length
oligo.locString()               # Location, e.g. '33[4]'

oligo.strand5p(), oligo._strand5p   #

# Not for immediate consumation:
oligo.increment/decrement/setLength()   #sets length and emits signals)

oligo.color(),  oligo._color    # color as QString
oligo.applyColor()

oligo.sequence()                        # returns sequence
oligo.applySequence(<sequence>)         # sets sequence, uses class method ApplySequenceCommand


useful way to get an oligos strands:
list(oligo.strand5p().generator3pStrand())

## Strand ##

strand.strand5p(), ._strand5p       # Neighboring connected strand, part of same oligo.
strand.strand3p(), ._strand3p       # Neighboring strand on 3p end (None if None)
strand.generator3pStrand            # Returns an iterable from self to the final _strand3p == None
strand.generator5pStrand            # Iterable from self to final _strand5p == None

strand.sequence(), ._sequence       #

strand.highIdx(), _baseIdxHigh      # high index
strand.lowIdx(), ._baseIdxLow       # low index
strand.length()                     # simple highIdx-lowIdx+1 calculation
strand.totalLength()                # accounts for insertions.


strand.strandSet(), ._strandSet
strand.strandType()

strand.setComplementSequence(str seq, oppstrand)   # set sequence on part compelementary to oppstrand.
# simply does:
    sLowIdx, sHighIdx = self._baseIdxLow, self._baseIdxHigh
    cLowIdx, cHighIdx = oppstrand.idxs()
    lowIdx, highIdx = util.overlap(sLowIdx, sHighIdx, cLowIdx, cHighIdx)


## StrandSet ##


strandset._findOverlappingRanges(strand)    # Can be used to find strands complementary to strand.


## Util ##



"""

import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest

import inspect

from cadnanolib import util

# CADNANO_PATH environment variable is set so that the maya plugin works...


def ps(obj):
    """ Print source definition for object obj """
    print inspect.getsource(obj)


def getstrandhybridizationlengths(strand):
    """
    Get inspired by oligo.ApplySequenceCommand and strand.setSequence.
    A strand may hybridize with one or more strands.
    Consider the strand and it's two complementary segments:
        AAAAAAAAAGGGGGGGGGACACACACACACACACACACAC
        TTTTTTTTT         TGTGTGTGTGTGTGTGTGTGTG
    The top strand hybridizes in two places, the AA/TT region and the AC/TG region.

    This should return a list of:
        [9, 22]
    """
    #return strand.totalLength()    # too simple, does not account for ss or hybridized regions...
    hyb_stretches = list()
    compSS = strand.strandSet().complementStrandSet()
    for cStrand in compSS._findOverlappingRanges(strand):
        sLowIdx, sHighIdx = strand.idxs()
        cLowIdx, cHighIdx = cStrand.idxs()
        lowIdx, highIdx = util.overlap(sLowIdx, sHighIdx, cLowIdx, cHighIdx)
        hyb_stretches.append(highIdx - lowIdx + 1)    # If an oligo starts at idx 30 and ends at idx 31, it is 2 nt long.
    return hyb_stretches


def get_oligo_hyb_patterns(cadnanopart, stapleoligos=True, scaffoldoligos=False):
    """
    Return oligo hybridization pattern as dict.

    what

    TODO: Improve "hybridization length" calculation,
    so that only hybridized part is taken into account and
    not single-stranded regions.
    """

    oligoset = cadnanopart.oligos() # simply returns ._oligos. Includes BOTH staples AND scaffold.
    # simple approach:
    #hyb_patterns = {oligo.locString() : [strand.length() for strand in oligo.strand5p().generator3pStrand()]
    #                    for oligo in oligoset}
    hyb_patterns = {oligo.locString() : [l for strand in oligo.strand5p().generator3pStrand()
                                                for l in getstrandhybridizationlengths(strand)]
                        for oligo in oligoset
                            if stapleoligos and oligo.isStaple() or scaffoldoligos and not oligo.isStaple()}

    return hyb_patterns
