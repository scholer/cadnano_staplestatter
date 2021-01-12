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
    print("staplestatter: Could not import from Bio.SeqUtils.MeltingTemp - Tm calculations will not be available!")
    # TODO: Consider having a local copy of Bio.SeqUtils.MeltingTemp, so as not to require the whole biopython package.
    # See your Nascent project (although that one is strictly Python3, I think.
    # OBS: The biopython package is only 2.3 MB, so not too bad a dependency matplotlib is much larger.

# Cadnano imports:
try:
    # cadnano2.5:
    from cadnano.part.part import Part
except ImportError:
    # cadnano2.0:
    from model.parts.part import Part

# Local imports:
# We just need the `overlap()` function from cadnano's `util.py` module,
# so I've copied it to a local module, so we can use it independently of cadnano.
from .cadnanolib import util


# CADNANO_PATH environment variable is set so that the maya plugin works...

VERBOSE = 0


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


def get_part_alt(doc):
    """ Cadnano is currently a little flaky regarding how to get the part. This tries to mitigate that. """
    try:
        # New-style cadnano:
        part = doc.selectedInstance()
    except AttributeError:
        # Old-style:
        part = doc.selectedPart()
    if VERBOSE > 1:
        print("Part:", part)
    if not isinstance(part, Part):
        if hasattr(part, "parent"):
            # part is actually just a cadnano.objectinstance.ObjectInstance
            # we need the cadnano.part.squarepart.SquarePart which is ObjectInstance.parent
            try:
                part = part.parent()
            except TypeError:
                # There are also some issues with parent being a getter or not...
                part = part.parent
        else:
            # Try something else
            part = doc.children()[0]
    return part


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
        compl_strands = strand.getComplementStrands()  # Cadnano2.5 API
    except AttributeError:
        # Cadnano2 API:
        compl_strands = strand.strandSet().complementStrandSet()._findOverlappingRanges(strand)

    # # Code debugging:
    # print("Strand %s, complementary strands: %s" % (strand, compl_strands))
    # sLowIdx, sHighIdx = strand.idxs()
    # print("- Strand", strand, "sLowIdx, sHighIdx:", sLowIdx, sHighIdx)
    # hyb_regions = []
    # for cStrand in compl_strands:
    #    cLowIdx, cHighIdx = cStrand.idxs()
    #    lowIdx, highIdx = util.overlap(sLowIdx, sHighIdx, cLowIdx, cHighIdx)
    #    print("- cStrand", cStrand, "cLowIdx, cHighIdx:", cLowIdx, cHighIdx)
    #    print(" - overlap, lowIdx, highIdx:", lowIdx, highIdx)
    #    hyb_regions.append((lowIdx, highIdx))    # If an oligo starts at idx 30 and ends at idx 31, it is 2 nt long.
    hyb_regions = [util.overlap(*(strand.idxs() + cStrand.idxs())) for cStrand in compl_strands]

    # Note: The hyb stretches MUST BE SORTED. The strands in hybpattern are processed from 5p to 3p, so
    # the hyb_stretches within each strand must also come in order 5p to 3p.
    # _findOverlappingRanges() yields strands in the same order as strandSet._strandList,
    # i.e. from low index to high (left to right in pathview).
    if sort == "5p3p" and not strand.isDrawn5to3():
        return hyb_regions[::-1]    # reverse the list
    # print(" - hyb_regions:", hyb_regions)
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
    try:
        # Cadnano2.5:
        startIdx = strand._base_idx_low
    except AttributeError:
        # Cadnano2:
        startIdx = strand._baseIdxLow

    strand_sequence = strand.sequence()
    # It is okay to have unhybridized loops or dangling ends, they don't change anything in terms of kinetic traps.
    # It is only a problem is you have a whole oligo with undefined sequence.
    # print("strand_sequence:", strand_sequence)
    # if not strand_sequence:
    #     print("\nError: strand %s has no sequence;" % strand,
    #     "you should apply a sequence before doing any sequence-specific things.\n")
    # assert strand_sequence  # Make sure we don't try this with an empty strand sequence.
    hyb_seqs = (strand_sequence[lowIdx-startIdx:highIdx-startIdx+1] for lowIdx, highIdx in hyb_regions)
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
    from Bio.SeqUtils.MeltingTemp import Tm_NN
    # Trim out empty strand hybridizations:
    hyb_seqs = list(seq for seq in getstrandhybridizationseqs(strand) if seq.strip())  # Remove loops and dangling ends
    # print("hyb_seqs:")
    # print(hyb_seqs)
    # An oligo consists of one or more strands (straight stretches on the same vhelix).
    # The strand may be broken up into different hybridizad regions, depending on the complementary strandset.
    # Having one or more strands without specified sequence is OK, e.g. if used for making loops.
    # If you want to check for issues, do it on the oligo level.
    # if len(hyb_seqs) == 0:
    #     # No defined hybridization sequences:
    #     raise ValueError("Strand %s does not have any hybridized, sequence-specified " % (strand,))
    try:
        hyb_TMs = [Tm_NN(seq, **kwargs) for seq in hyb_seqs]
    except IndexError as e:
        #print("IndexError:", e)
        #print(" - for hyb_seqs:", hyb_seqs)
        raise ValueError("hyb_seqs {} produced by strand {} part of oligo {} raised IndexError {}"
                         .format(hyb_seqs, strand, strand.oligo(), e))
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


def get_oligo_hyb_pattern(cadnanopart, stapleoligos=True, scaffoldoligos=False, method="length", **kwargs):
    """
    Return oligo hybridization lengths for cadnano part, as dict:
        oligo_locString : <list of oligo hybridization lenghts>
    """
    oligoset = cadnanopart.oligos()  # simply returns ._oligos. Includes BOTH staples AND scaffold.

    print("get_oligo_hyb_pattern(): method =", method)
    if isinstance(method, str):
        if "length" in method:
            method = getstrandhybridizationlengths
        elif "seq" in method:
            method = getstrandhybridizationseqs
        elif "tm" in method or "TM" in method or "melt" in method or "temp" in method:
            method = getstrandhybridizationtm
        else:
            err_msg = "ERROR: method='%s' is not a recognized value." % (method,)
            raise ValueError(err_msg)
    print("- get_oligo_hyb_pattern(): method =", method)
    # For a strand, getstrandhybridization_methods will return a list of
    # values. This is because strand may not be hybridized to the same complementary strand all the way.
    hyb_patterns = {oligo.locString(): [val for strand in oligo.strand5p().generator3pStrand()
                                        for val in method(strand, **kwargs) if val]
                    for oligo in oligoset
                    if stapleoligos and oligo.isStaple() or scaffoldoligos and not oligo.isStaple()}
    return hyb_patterns
