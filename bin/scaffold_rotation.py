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
# pylint: disable=C0103,C0111,R0913,W0142

"""

Apply one or more sequences to a cadnano design and score the staples (or miniscafs) produced.


Example usage:
    $> cadnano_apply_seq scafs.yaml CircFoldback_07-braced.json
    $> cadnano_apply_seq -y --score stap --score scaf scafs.yaml CircFoldback_07-braced.json
    $> cadnano_apply_seq -y --score score_oligos.yaml scafs.yaml CircFoldback_07-braced.json
    # Score oligos specified by score_oligos.yaml, applying sequences from scafs.yaml, to all
    # cadnano files matching the glob pattern *.json (verbose=1, overwriting existing files if needed):
    $> cadnano_apply_seq --score score_oligos.yaml -y -v scafs.yaml *.json

"""


import os
import sys
import glob
import argparse
import json
from time import clock
import yaml
from operator import itemgetter
#import math
#from importlib import reload
#import PyQt5
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib import pyplot #, gridspec

# Note regarding ImportError when using Anaconda environtments:
# For some reason, simply using the python.exe in the /envs/pyqt5/ directory is not sufficient, and I will get a
# ImportError: DLL load failed: Det angivne modul blev ikke fundet.
# Instead, activate the environment and then execute python.exe

# from importlib import reload
# import matplotlib
# #matplotlib.use("Qt5Agg")
# from matplotlib import pyplot, gridspec

# pylint: disable=C0103

import time
if sys.platform == 'win32':
    # On Windows, the best timer is time.clock
    timer = time.clock
else:
    # On most other platforms the best timer is time.time
    timer = time.time

# If you don't already have this on your path:
sys.path.insert(0, "c:/Users/scholer/dev/src-repos/cadnano/staplestatter")
sys.path.insert(0, os.path.normpath(r"C:\Users\scholer\Dev\src-repos\cadnano\cadnano2.5"))


# Cadnano library imports
from cadnano.document import Document
from cadnano.fileio.nnodecode import decode #, decodeFile
from cadnano.part.part import Part

# Staplestatter imports
from staplestatter import cadnanoreader
from staplestatter import staplestatter
from staplestatter import statutils
#from staplestatter import plotutils

# Constants:
global VERBOSE
VERBOSE = 0


def load_cadnano_file(filename, doc=None):
    if doc is None:
        doc = Document()
    with open(filename) as fp:
        nno_dict = json.load(fp)
    decode(doc, nno_dict)
    return doc



def parse_args(argv=None):
    """
    # grep implements
    #-E, --extended-regexp     PATTERN is an extended regular expression
    #-F, --fixed-strings       PATTERN is a set of newline-separated strings
    #-G, --basic-regexp        PATTERN is a basic regular expression
    #-e, --regexp=PATTERN      use PATTERN as a regular expression

    """

    parser = argparse.ArgumentParser(description="Cadnano apply sequence script.")
    parser.add_argument("--verbose", "-v", action="count", help="Increase verbosity.")
    # NOTE: Windows does not support wildcard expansion in the default command line prompt!

    #parser.add_argument("--seqfile", "-s", nargs=1, required=True, help="File containing the sequences")
    parser.add_argument("seqfile", help="File containing the sequences")

    parser.add_argument("--seqfileformat", help="File format for the sequence file.")

    parser.add_argument("--offset",
                        help="Offset the sequence by this number of bases (positive or negative). "\
                        "An offset can be sensible if the scaffold is circular, "\
                        "or you have extra scaffold at the ends and you want to optimize where to start. "
                        "Note: The offset is applied to ALL sequences, unless an individual seq_spec "
                        "specifies an offset.")

    parser.add_argument("--offsetrange", nargs=2, type=int,
                        help="Calculate scores for this offset range (min, max). ")


    parser.add_argument("--overwrite", "-y", action="store_true",
                        help="Overwrite existing staple files if they already exists. "
                        "(Default: Ask before overwriting)")


    parser.add_argument("--no-simple-seq", dest="simple_seq", action="store_false", default=True,
                        help="Never load sequences from file as a simple sequence.")
    parser.add_argument("--simple-seq", action="store_true",
                        help="If specified, the sequence loaded can be a simple sequence.")


    parser.add_argument("--config", "-c", help="Load config from this file (yaml format). "
                        "Nice if you dont want to provide all config parameters via the command line.")

    parser.add_argument("--score", action="append", help="Which oligos to score sequence for."
                        "The default is to score staple strands. However, this script can also score e.g. "
                        "all scaffold oligos or oligos matching a given set of criteria. "
                        "Recognized values are: 'stap', 'scaf', or a filename."
                        "If a file is given, it should contain a list of criteria provided in the same way "
                        "as the criteria in a sequence file (if yaml format).")

    parser.add_argument("cadnano_files", nargs="+", metavar="cadnano_file",
                        help="One or more cadnano design files (.json) to apply sequence(s) to.")

    parser.add_argument("--plot-filename", default="{design}.scaffold-rotation.png",
                        help="Save the plot to this file. "
                        "The output filename can include named python format parameters, "
                        "e.g. {design}, {cadnano_fname} and {seqfile}. "
                        "Default is {design}.scaffold-rotation.png")

    parser.add_argument("--show-plot", action="store_true",
                        help="Show the plot interactively. ")

    parser.add_argument("--save-rotation-scores", default="{design}.scaffold-rotation.yaml",
                        help="Save stats to this file. Can use the same named format parameters as --plot-filename. "
                        "The save format will depend on file extension, e.g. .yaml, .json, .tsv or .csv")

    parser.add_argument("--no-save-rotation-scores", dest="save_rotation_scores",
                        help="Do not save rotation scores to file.")


    return parser, parser.parse_args(argv)


def process_args(argns=None):
    """ Process command line args. """
    if argns is None:
        _, argns = parse_args()
    args = argns.__dict__.copy()
    if args.get("config"):
        with open(args["config"]) as fp:
            cfg = yaml.load(fp)
        args.update(cfg)
    # On windows, we have to expand *.json manually:
    args['cadnano_files'] = [fname for pattern in args['cadnano_files'] for fname in glob.glob(pattern)]
    return args

def load_criteria_list(filepath):
    try:
        ext = os.path.splitext(filepath)[1]
    except IndexError:
        ext = "yaml"
    with open(filepath) as fd:
        criteria_list = json.load(fd) if "json" in ext else yaml.load(fd)
    return criteria_list


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
                return fd.read()
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


def save_stats(stats, filename):
    """
    Save stats to filename. Save format will depend on filename extension,
    e.g. .yaml, .json, .tsv or .csv. Default is csv format (sep=",").
    """
    try:
        fnext = os.path.splitext(filename)[1].lower()
    except IndexError:
        fnext = ".csv"
    with open(filename, 'w') as fp:
        if "yaml" in fnext:
            yaml.dump(stats, fp)
        elif "json" in fnext:
            json.dump(stats, fp)
        else:
            if "tsv" in fnext:
                sep = "\t"
            else:
                sep = ","
            fp.write("\n".join(sep.join(row) for row in stats))


def get_part(doc):
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


def crit_match(oligo, key, value):
    """ Match an oligo against a single criteria (key, value) """
    org_key = key
    if key == "st_type":
        # logical XOR: equivalent to
        # (oligo.isStaple() and value == "stap") or (not oligo.isStaple() and value == "scaf")
        return oligo.isStaple() == (value == "stap")
    # This seems efficient. Do try it for all keys:
    if key in ("length", "color", "idx5Prime", "vhnumber") or True:
        if key in ("idx5Prime", ):
            crit_obj = oligo.strand5p()
        elif key in ("vhnumber", ):
            crit_obj = oligo.strand5p().virtualHelix()
            key = key[2:]
        else:
            crit_obj = oligo
            # Allow flexible specification:
            # Specify as "5pidx5Prime" or "5pvhnumber" or "5pvhcoord"
            if key[:2] == "5p":
                crit_obj = crit_obj.strand5p()
                key = key[2:]
            if key[:2] == "vh":
                crit_obj = crit_obj.virtualHelix()
                key = key[2:]
        try:
            oval = getattr(crit_obj, key)()
        except AttributeError as e:
            print("\nERROR:", e)
        else:
            # What if length is a tuple specifying a range, e.g. (100, 150)
            # to apply to all oligos within a certain range?
            if isinstance(value, (list, tuple)):
                if len(value) == 2:
                    return value[0] <= oval <= value[1]
                # We have a set of acceptable values:
                return oval in value
            return oval == value
    # Future criterium: sequence, ...?
    #st = oligo.strand5p()
    #if key.lower() == "5pbaseidx":
    #    return st.idx5Prime() == value
    #vh = st.virtualHelix()
    #if key.lower() == "5pvhnum":
    #    return vh.number() == value
    #if key.lower() == "5pvhcoord":
    #    # value can be either (5, 2) or it can be (5, None).
    #    # If a coordinate is None, it should match all, i.e. we are doing row/col matching only.
    #    # So e.g. we'd zip value = (5, None) with vh.coord() = (5, 2) to produce [(5, 5), (None, 2)]
    #    # and compare the equality of these or if v is None:
    #    return all(v == a or v is None for v, a in zip(value, vh.coord()))
    raise KeyError('Criteria key "%s" not recognized.' % org_key)


def match_oligo(oligo, criteria):
    """
    Returns True if oligo matches all criterium in the given set of criteria.

    See if oligo matches the given criteria.
    Criteria is a dict with any of these keys: (case insensitive)
        st_type: <"scaf" or "stap">,
        length: <length>,
        color: <hex color code>
        5pvhnum: <vhelix number>,
        5pvhcoord: (vhcoord tuple),
        5pbaseidx: <base index>,
        (same for 3p),

    Key methods for Oligo:
        applyColor(), color(), setColor()
        applySequence()
        isStaple()
        length(), setLength()
        locString()
        sequence(), sequenceExport()
        strand5p()
    Key methods for Strand:
        highIdx(), lowIdx(), idx3Prime(), idx5Prime(), idxs(),
        connection3p(), connection5p(), connectionHigh(), connectionLow(),
        generator3p(), generator5p(),
        getComplementStrands(),
        sequence(), getSequenceList(),
        strandType(), isScaffold(), isStaple,
        length(), totalLength(),
        strandSet(), oligo(), virtualHelix(), part()
        plus: insertion methods, and a lot of setters.
    """
    return all(crit_match(oligo, key, value) for key, value in criteria.items())


def get_matching_oligos(part, criteria):
    """
    Get all oligos on part matching the given set of criteria.
    Criteria is usually a set of criteria (a dict, actually) of
        criterium-key: criterium-value(s) or range, e.g.
        length: 128
    In this case, return a list of all oligos matching all criteria in the dict.
    However, criteria can also be a list of criteria dicts,
    in which case return the union (set) of all oligos fully matching
    any of the criterium dicts in the list.
    """
    # We'd usually expect only one oligo to match the set of criteria,
    # and we'd probably want to verify that exactly one oligo is matching,
    # so generate a list, not a generator.
    if isinstance(criteria, list):
        # if we have a criteria_list, return the union of oligos matching any criteria (dict) in the list:
        return {oligo for crit_dict in criteria for oligo in get_matching_oligos(part, crit_dict)}
    return [oligo for oligo in part.oligos() if match_oligo(oligo, criteria)]


def print_oligo_criteria_match_report(oligos, criteria, desc=None):
    """ Print standard criteria match report. """
    print("\n{} oligos matching criteria set {}:".format(len(oligos), desc))
    #print("Oligos matching criteria set:", desc)
    if VERBOSE > 1:
        print(yaml.dump({"criteria": [criteria]}, default_flow_style=False).strip("\n"))
        print("The matching oligos are:")
        print("\n".join(" - {}".format(oligo) for oligo in oligos))


def apply_sequences(part, seqs, offset=None):
    """
    Apply sequences in seqs to oligos in part.
    If seqs is just a str, it is assumed to be a single sequence to be applied
    to the first and only scaffold oligo in the design.
    Otherwise, seqs must be a list of seq_spec, each specifying a sequence and a set
    of criteria matching only those oligos to which the sequence should be applied.
    """
    # Apply sequence:
    #with open(os.path.join(folder, sequence_file)) as fd:
    #    scaf_sequence = fd.read()
    #scaf_oligo = next(oligo for oligo in part.oligos() if not oligo.isStaple())
    if isinstance(seqs, str):
        # Perform simple sequence application using just a single sequence with no selection criteria.
        # Can be used if the design has one and only one scaffold.
        seq = seqs
        if offset:
            seq_offset = offset
            L = len(seq)
            seq = (seq*3)[L+seq_offset:L*2+seq_offset]
        oligos = part.oligos()
        # Get the first scaffold oligo:
        scaf_oligo = next(oligo for oligo in oligos if not oligo.isStaple())
        scaf_oligo.applySequence(seq, use_undostack=False)
    else:
        # Apply sequences based on seq_spec criteria:
        for seq_i, seq_spec in enumerate(seqs):
            # seq_spec has key "seq" and optional keys "criteria", and "offset".
            seq = seq_spec["seq"]
            L = len(seq)
            seq_offset = seq_spec.get("offset", offset)
            if seq_offset:
                seq = (seq*3)[L+seq_offset:L*2+seq_offset]
            oligos = get_matching_oligos(part, seq_spec["criteria"])
            if VERBOSE > 3:
                print_oligo_criteria_match_report(oligos, seq_spec["criteria"],
                                                  desc="for application of sequence #{}".format(seq_i))
            for oligo in oligos:
                oligo.applySequence(seq, use_undostack=False)


def score_part(part, method="TM", **method_kwargs):
    """
    Score part (after sequences have been applied).
    Mg=10
    """
    #oligos = part.oligos()
    hyb_pats = cadnanoreader.get_oligo_hyb_pattern(part, method=method, **method_kwargs)
    #scores = staplestatter.score_part_oligos(part, scoremethod=getattr(statutils, 'maxlength'))
    #score_freqs = statutils.frequencies(scores)
    #staplestatter.plot_frequencies(score_freqs)
    #oligo_hybridization_TMs = cadnanoreader.get_oligo_hyb_pattern(cadnano_part, method="TM", **tm_kwargs)
    T_arrays = hyb_pats.values()
    # valley_stretches returns a binary: A stretch is either a valley or not.
    #valley_stretches = [statutils.valleyfinder(T_array) for T_array in T_arrays]
    # valleydepths returns negative values for valleys and 0 for non-valleys.
    #valleydepths = [statutils.valleydepth(T_array) for T_array in T_arrays]
    #valleyscores = [-sum(math.sqrt(-valley) for valley in oligo_valleys) for oligo_valleys in valleydepths]
    #valleyscore = sum(valleyscores)
    valleyscore = staplestatter.score_part_v1(part)
    return valleyscore


def get_offset_rotation_scores(part, seqs, offsetrange=None):
    """
    Optimizations...
    - It takes about or less than 0.1 s to calculate a complete part.
    - For TM based scoring, the TM calculations are about 3 times as expensive as cadnano apply seq.
    - If using length instead of TM, the scoring takes about half the time as cadnano apply seq.
    """
    if offsetrange is None:
        offsetrange = "complete"
    if offsetrange == "complete":
        if isinstance(seqs, str):
            offsetrange = range(len(seqs))
        else:
            try:
                offsetrange = range(len(seqs[0]["seq"]))
            except KeyError:
                raise ValueError("offsetrange must be a specified range for complex sequence specs")
    elif isinstance(offsetrange, (list, tuple)):
        offsetrange = range(offsetrange[0], offsetrange[1])
    scores = []
    timings = [0.0, 0.0]
    for offset in offsetrange:
        if VERBOSE and (offset % 100) == 0:
            print("Applying sequence for offset {}".format(offset))
        start = timer()
        apply_sequences(part, seqs, offset)
        timings[0] += timer() - start
        if VERBOSE and offset % 100 == 0:
            print("Calculating score for offset {}".format(offset))
        #scores.append((offset, staplestatter.score_part_v1(part, hyb_method="TM")))
        start = timer()
        scores.append((offset, staplestatter.score_part_v1(part, hyb_method="TM")))
        #scores.append((offset, staplestatter.score_part_v1(part, hyb_method="length")))
        timings[1] += timer() - start
        if VERBOSE and offset % 100 == 0:
            print("Calculation done for offset {}".format(offset))
    if VERBOSE:
        print("get_offset_rotation_scores timings:")
        print("- apply_sequences: {:.03f} s".format(timings[0]))
        print("- score_part_v1  : {:.03f} s".format(timings[1]))
    return scores


def print_top_scores(scores, top=10):
    sortkey = itemgetter(1)  # lambda tup: tup[1]
    for offset, score in list(reversed(sorted(scores, key=sortkey)))[:top]:
        print("Offset {: >-03} -> {:.02f}".format(offset, score))


def plot_rotationscores(scores, savetofile=None):
    fig = pyplot.figure(figsize=(20, 10))
    #pyplot.plot(*reversed(list(zip(*scores))))
    offset, scorevals = zip(*scores)
    pyplot.plot(offset, scorevals)
    pyplot.xlabel("Scaffold offset")
    pyplot.ylabel("Score")
    if savetofile:
        pyplot.savefig(savetofile)
    return fig


#def score_and_plot(args):


def print_hyb_pats(hyb_pats):
    print("\n".join("{: <8}: {}".format(key, ["{:.01f}".format(tm) for tm in tms]) for key, tms in hyb_pats.items()))


def print_oligo_stats_for_offset(part, offset, scaf):
    #offset = 6
    L = len(scaf)
    scaf = (scaf*3)[L+offset:L*2+offset]
    scaf_oligo = next(oligo for oligo in part.oligos() if not oligo.isStaple())
    scaf_oligo.applySequence(scaf, use_undostack=False)
    hyb_methods = ("length", "TM", "seq")
    kwargs = {"Mg": 10}
    pats = {}
    for method in hyb_methods:
        pats[method] = cadnanoreader.get_oligo_hyb_pattern(part, method=method, **kwargs)
    pats["TM"] = {key: [int(tm) for tm in tms] for key, tms in pats["TM"].items()}
    print("\nFor offset = ", offset)
    for oligo in (oligo for oligo in part.oligos() if oligo.isStaple() and False): # Added and False to disable
        loc = oligo.locString()
        print(loc)
        for method in hyb_methods:
            print("- {: <6}: {}".format(method, pats[method][loc]))
    loc = "0[95]"
    print(loc)
    for method in hyb_methods:
        print("- {: <6}: {}".format(method, pats[method][loc]))


def ok_to_write_to_file(staples_outputfn, args):
    """ Assert whether it is OK to write to staples_outputfn """
    if args["overwrite"] or not os.path.exists(staples_outputfn):
        return True
    # os.path.exists(staples_outputfn) is True
    overwrite = input(staples_outputfn + " already exists. Overwrite? [Y/n]")
    if overwrite and overwrite.lower()[0] == "n":
        return False
    return True


def get_score_criteria_list(args):
    """
    Returns a list of criteria sets. Each criteria set can match one or more oligos.
    The criteria_list is usually used to generate a list/set of oligos matching
    any of the criteria (set) in the list, but matching all criterium in that criteria set,
    basically:
        include_oligo = any(all(match_crit(oligo, criterium) for criterium in criteria)
                            for criteria in criteria_list)
    """
    if args['score'] is None:
        return None
    # Alternative generation with list comprehension:
    criteria_list = [criteria for score in args['score'] for criteria in
                     ([{"st_type": score}] if score in ("scaf", "stap") else load_criteria_list(score))]
    return criteria_list


#def score_oligos(part, csvfilepath=None, criteria_list=None):
#    """
#    Export all oligos from part, matching the any of the set of criteria in criteria_list.
#    criteria_list enables you to have a list of criteria-set, so that you can score both:
#            all staples,
#        and some scaffolds that are read,
#        and scaffold oligos on vhelix 2
#
#    Criteria takes the same format as for applying sequence,
#    see match_oligo()
#    If criteria is None, then all sequences for all staples will be scoreed.
#    """
#    # export staples:
#    if criteria_list is None:
#        csv_text = part.getStapleSequences()
#    else:
#        #oligos = {oligo for criteria in criteria_list for oligo in get_matching_oligos(part, criteria)}
#        oligos = get_matching_oligos(part, criteria_list)
#        if VERBOSE > 2:
#            print_oligo_criteria_match_report(oligos, criteria_list, desc="for export")
#        header = "Start,End,Sequence,Length,Color,5pMod,3pMod\n"
#        csv_text = header + "".join(oligo.sequenceExport() for oligo in oligos)
#    with open(csvfilepath, "w") as fd:
#        n = fd.write(csv_text)
#        if VERBOSE > 0:
#            print("\n{} bytes written to file: {}\n".format(n, csvfilepath))



def main(argv=None):
    global VERBOSE
    args = process_args(argv)
    VERBOSE = args['verbose'] or 0

    # Get sequence(s):
    seqs = load_seq(args)
    # What to score:
    score_criteria_list = get_score_criteria_list(args)
    if VERBOSE > 1:
        print("score criteria list:")
        print(yaml.dump(score_criteria_list))


    for cadnano_file in args["cadnano_files"]:
        # folder = os.path.realpath(os.path.dirname(cadnano_file))
        # "141105_longer_catenane_BsoBI-frag_offset6nt.json"
        design = os.path.splitext(os.path.basename(cadnano_file))[0]
        plot_outputfn = args["plot_filename"]
        if plot_outputfn:
            plot_outputfn = plot_outputfn.format(design=design, cadnano_file=cadnano_file, seqfile=args["seqfile"])
        stats_outputfn = args["save_rotation_scores"]
        if stats_outputfn:
            stats_outputfn = stats_outputfn.format(design=design, cadnano_file=cadnano_file,
                                                   seqfile=args["seqfile"])
        print("\nLoading design:", design)
        doc = load_cadnano_file(cadnano_file)
        print(cadnano_file, "loaded!")
        part = get_part(doc)
        #apply_sequences(part, seqs, offset=args.get("offset")) # global offset
        #score_oligos(part, plot_filepath=plot_outputfn, criteria_list=score_criteria_list)
        print("Calculating rotation scores...")
        rotationscores = get_offset_rotation_scores(part, seqs, args['offsetrange'])
        x, y = zip(*rotationscores)
        print("Rotation scores: N={}, first={}, min={}, max={}"
              .format(len(y), rotationscores[0], min(y), max(y)))
        if stats_outputfn:
            if not ok_to_write_to_file(plot_outputfn, args):
                print("Not  file", cadnano_file)
            else:
                print("Saving rotation scores...")
                save_stats(rotationscores, stats_outputfn)
        if plot_outputfn:
            if not ok_to_write_to_file(plot_outputfn, args):
                print("Aborting staple file write for file", cadnano_file)
            else:
                print("Plotting rotation scores...")
                plot_rotationscores(rotationscores, plot_outputfn)
        if args['show_plot']:
            print("Showing plot...")
            pyplot.show()




if __name__ == '__main__':
    main()
