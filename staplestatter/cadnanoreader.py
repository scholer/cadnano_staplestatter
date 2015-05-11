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
# pylint: disable-msg=C0103,C0301,C0302,R0201,R0902,R0904,R0913,W0142,W0201,W0221,W0402,W0212

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

from __future__ import absolute_import, print_function
import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest

import inspect
try:
    from Bio.SeqUtils.MeltingTemp import Tm_NN
except ImportError:
    print("Could not import from Bio.SeqUtils.MeltingTemp - Tm calculations will not be available!")

try:
    from .cadnanolib import util
except SystemError:
    from cadnanolib import util

# CADNANO_PATH environment variable is set so that the maya plugin works...


def ps(obj):
    """ Print source definition for object obj """
    print(inspect.getsource(obj))


def get_part(doc):
    """
    Get the documents first part.
    This version uses doc.parts()/doc.children(), but you can also use the more direct
    doc.selectedPart() or - for new cadnano - doc.selectedInstance().parent
    """
    try:
        parts = doc.parts()  # Older versions.
    except AttributeError:
        parts = doc.children()
    return parts[0]



def getstrandhybridizationregions(strand, sort="5p3p"):
    """
    A strand may hybridize with one or more strands.
    Consider the strand and it's two complementary segments:
        AAAAAAAAAGGGGGGGGGACACACACACACACACACACAC
         TTTTTTTTT       TGTGTGTGTGTGTGTGTGTGTG
    The top strand hybridizes in two places, the AA/TT region and the AC/TG region.
    This should return a list tuples where each tuple is start and end of hybridization region:
        [(1, 9), (18, 39)]
    Code inspired by oligo.ApplySequenceCommand and strand.setSequence.

    Notes:
    Hmm, _findOverlappingRanges has been removed in cadnano2.5 with commit b8563 and replaced partly
    by strandset.getOverlappingStrands(base_idx_low, base_idx_high) or strand.getComplementStrands()
    or just use of strandset.strand_array (briefly named _strand_list), which is a (degenerate)
    list of strands by base_index,
    or use strandset.strand_heap, which is just a list of the strands on the strandset.
    (it is still in master branch as of 2015/04/24, but not in e.g. outlinerdev)
    """
    try:
        compl_strands = strand.getComplementStrands()
    except AttributeError:
        # pre-version2.5 :
        compl_strands = strand.strandSet().complementStrandSet()._findOverlappingRanges(strand)
    #hyb_regions = []
    #for cStrand in compl_strands:
    #    sLowIdx, sHighIdx = strand.idxs()
    #    cLowIdx, cHighIdx = cStrand.idxs()
    #    lowIdx, highIdx = util.overlap(sLowIdx, sHighIdx, cLowIdx, cHighIdx)
    #    hyb_regions.append((lowIdx, highIdx))    # If an oligo starts at idx 30 and ends at idx 31, it is 2 nt long.
    hyb_regions = [util.overlap(*(strand.idxs() + cStrand.idxs()))
                   for cStrand in compl_strands]

    # Note: The hyb stretches MUST BE SORTED. The strands in hybpattern are processed from 5p to 3p, so
    # the hyb_stretches within each strand must also come in order 5p to 3p.
    # _findOverlappingRanges() yields strands in the same order as strandSet._strandList,
    # i.e. from low index to high (left to right in pathview).
    if sort == "5p3p" and not strand.isDrawn5to3():
        return hyb_regions[::-1]    # reverse the list
    return hyb_regions

def getstrandhybridizationseqs(strand, **kwargs):
    """
    Consider the strand and it's two complementary segments:
        AAAAAAAAAGGGGGGGGGACACACACACACACACACACAC
        TTTTTTTTT         TGTGTGTGTGTGTGTGTGTGTG
    The top strand hybridizes in two places, the AA/TT region and the AC/TG region.
    This should return a list of:
        ["AAAAAAAAA", "ACACACACACACACACACACAC"]
    DOES NOT ACCOUNT FOR SKIPS OR LOOPS!
    """
    hyb_regions = getstrandhybridizationregions(strand)
    startIdx = strand._base_idx_low
    hyb_seqs = (strand.sequence()[lowIdx-startIdx:highIdx-startIdx+1] for lowIdx, highIdx in hyb_regions)
    # Uh, maybe just:
    # hyb_seqs = st.getSequenceList()
    # No, not sure this does exactly what I want...
    # Return [(idx, (strandItemString, insertionItemString), ...]
    return hyb_seqs

def getstrandhybridizationtm(strand, **kwargs):
    """
    Consider the strand and it's two complementary segments:
        AAAAAAAAAGGGGGGGGGACACACACACACACACACACAC
        TTTTTTTTT         TGTGTGTGTGTGTGTGTGTGTG
    The top strand hybridizes in two places, the AA/TT region and the AC/TG region.
    This should return a list of Tm values for each of the hybridization stretches,
    considering ONLY the hybridized part (no dangling sequences or end-stacking, sorry):
        [20, 70]
    kwargs is passed on to the Tm calculating method (currently Bio.SeqUtils.MeltingTemp.Tm_NN)
    """
    #from Bio.SeqUtils.MeltingTemp import Tm_NN
    hyb_seqs = getstrandhybridizationseqs(strand)
    hyb_TMs = (Tm_NN(seq, **kwargs) for seq in hyb_seqs)
    return hyb_TMs



def getstrandhybridizationlengths(strand, **kwargs):
    """
    Consider the strand and it's two complementary segments:
        AAAAAAAAAGGGGGGGGGACACACACACACACACACACAC
        TTTTTTTTT         TGTGTGTGTGTGTGTGTGTGTG
    The top strand hybridizes in two places, the AA/TT region and the AC/TG region.
    This should return a list of:
        [9, 22]
    """
    #return strand.totalLength()    # too simple, does not account for ss or hybridized regions...
    #hyb_stretches = list()
    #try:
    #    compl_strands = strand.strandSet().complementStrandSet()._findOverlappingRanges(strand)
    #except AttributeError:
    #    compl_strands = strand.getComplementStrands()
    #for cStrand in compl_strands:
    #    sLowIdx, sHighIdx = strand.idxs()
    #    cLowIdx, cHighIdx = cStrand.idxs()
    #    lowIdx, highIdx = util.overlap(sLowIdx, sHighIdx, cLowIdx, cHighIdx)
    #    hyb_stretches.append(highIdx - lowIdx + 1)  # If an oligo starts at idx 30 and ends at idx 31, it is 2 nt long.

    hyb_regions = getstrandhybridizationregions(strand)
    hyb_lengths = [(highIdx - lowIdx + 1) for lowIdx, highIdx in hyb_regions]
    return hyb_lengths

    # Note: The hyb stretches MUST BE SORTED. The strands in hybpattern are processed from 5p to 3p, so
    # the hyb_stretches within each strand must also come in order 5p to 3p.
    # _findOverlappingRanges() yields strands in the same order as strandSet._strandList,
    # i.e. from low index to high (left to right in pathview).
    #if strand.isDrawn5to3():
    #    return hyb_stretches
    #else:
    #    return hyb_stretches[::-1]

def getstrandhybridizationmask(strand):
    """
    Returns a "hybridization mask" indicating for each base whether the strand is paired (True) or not (False).
    There are many ways to produce this, but let's just take one way using strandset.strand_array.
    """
    # Assume that the baseindex is the same for this and the complementary strandset.
    compl_ss = strand.strandSet().complementStrandSet()
    mask = [compl_ss.strand_array[base_idx] is not None
            for base_idx in range(strand._base_idx_low, strand._base_idx_high+1)]
    return mask



def get_oligo_hyb_lengths(cadnanopart, stapleoligos=True, scaffoldoligos=False):
    """
    Return oligo hybridization lengths for cadnano part, as dict:
        oligo_locString : <list of oligo hybridization lenghts>
    """
    #oligoset = cadnanopart.oligos() # simply returns ._oligos. Includes BOTH staples AND scaffold.
    # simple approach:
    #hyb_patterns = {oligo.locString() : [strand.length() for strand in oligo.strand5p().generator3pStrand()]
    #                    for oligo in oligoset}
    #hyb_patterns = {oligo.locString(): [l for strand in oligo.strand5p().generator3pStrand()
    #                                      for l in getstrandhybridizationlengths(strand)]
    #                for oligo in oligoset
    #                if stapleoligos and oligo.isStaple() or scaffoldoligos and not oligo.isStaple()}
    hyb_lengths = get_oligo_hyb_pattern(cadnanopart, stapleoligos, scaffoldoligos, method="lengths")
    return hyb_lengths


def get_oligo_hyb_pattern(cadnanopart, stapleoligos=True, scaffoldoligos=False, method="TM", **kwargs):
    """
    Return oligo hybridization lengths for cadnano part, as dict:
        oligo_locString : <list of oligo hybridization lenghts>
    """
    oligoset = cadnanopart.oligos() # simply returns ._oligos. Includes BOTH staples AND scaffold.

    if isinstance(method, str):
        if "length" in method:
            method = getstrandhybridizationlengths
        elif "seq" in method:
            method = getstrandhybridizationseqs
        else:
            method = getstrandhybridizationtm
    hyb_patterns = {oligo.locString(): [val for strand in oligo.strand5p().generator3pStrand()
                                        for val in method(strand, **kwargs)]
                    for oligo in oligoset
                    if stapleoligos and oligo.isStaple() or scaffoldoligos and not oligo.isStaple()}
    return hyb_patterns