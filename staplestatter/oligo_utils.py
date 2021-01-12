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

Module with oligo utility functions.

Make sure that cadnano is importable before loading/importing/running this.



A good chunk of this module is related to selecting oligos with criteria sets.

This is used for two things:
1. To select what/which oligo(s) to apply a sequence to.
    (Yes, sometimes, although rarely, it's nice to apply one sequence to several oligos.)
2. To select which oligos to export/score/perform some calculation on.

The first use case is implemented in seq-specs.
    An oligo criteria set is usually used as part of a seq_spec for applying a sequence
    to one or more oligos in a cadnano file.
        [{
            seq: <sequence>,
            name: <descriptive name for sequence, mostly for the user.>
            bp: <expected length of the sequence (again, mostly for the user)>
            criteria: {    # this is an "oligo selection criteria set"
                st_type: <"scaf" or "stap">,
                length: <length>,
                5pvhnum: <vhelix number>,
                5pvhcoord: (vhcoord tuple),
                5pbaseidx: <base index>,
                (same for 3p),
                }
            offset: <integer, positive or negative>,
         }, (...) ]

An example of the second use case is seen in criteria_args_to_list, which takes a simple
list of "scaf", "stap" or a file name and produces a criteria set list, which is then used
to select oligos. With gen_matching_oligos.

The functions match_single_oligo and ... is used to match a single oligo against a list of
criteria sets and a single criteria set respectively .

crit_match  - match a single oligo against a single criteria in a criteria set.
match_oligo - match a single oligo against a criteria set.
get_matching_oligos - get all matching oligos in part.

"""

from __future__ import absolute_import, print_function
import os
import json
import yaml


VERBOSE = 0


def load_criteria_list(filepath):
    """
    The criteria list specifies which oligos to export, and can be specified either as json or yaml.
    This will load data.
    """
    try:
        ext = os.path.splitext(filepath)[1]
    except IndexError:
        ext = "yaml"
    with open(filepath) as fd:
        criteria_list = json.load(fd) if "json" in ext else yaml.load(fd)
    return criteria_list


def get_oligo_criteria_list(criteria_args):
    """
    Input criteria_args is a list of command-line args describing
    which oligos to include.
    This can be any or all of ["scaf", "stap", or one or more filenames]
    If "scaf" or "stap" is given, a criteria set selecting either scaffold
    or staple oligos is created. Otherwise, the argument is assumed to be a
    file, which is loaded loaded with load_criteria_list(filename).
    Thus, this can be used to merge multiple criteria lists from several files.

    Example usage:
    >>> criteriasetlist = get_oligo_criteria_list(["scaf", "loweroligos.yaml"])

    Returns a list of criteria sets. This is usually used to select one or more oligos
    in a cadnano design. Each criteria set can match one or more oligos.
    The criteria_list is usually used to generate a list/set of oligos matching
    any of the criteria (set) in the list, but matching all criterium in that criteria set,
    basically:
        include_oligo = any(all(match_crit(oligo, criterium) for criterium in criteria)
                            for criteria in criteria_list)

    """
    # Alternative generation with list comprehension:
    criteria_list = [criteria for arg in criteria_args for criteria in
                     ([{"st_type": arg}] if arg in ("scaf", "stap") else load_criteria_list(arg))]
    return criteria_list


def crit_match(oligo, key, value):
    """
    Match an oligo against a single criteria (key, value)
    Lifted from cadnano_apply_seq in RsUtils repo.
    """
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
            # What if length is a tuple specifying a range, e.g. (100, 150) to apply to all oligos within a certain range?
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
    See if oligo matches the given criteria.
    (Lifted from cadnano_apply_seq in RsUtils repo.)
    (Note: If performance is vital, you can use the dedicated
    oligo_match_criteriaset or oligo_match_criteriaset_list functions)

    Returns True if oligo matches all criterium in the given set of criteria.

    Arguments:
        oligos - a cadnano oligo
        criteria - a set (dict) of criteria, e.g. {"st_type": "scaf", "color": "#ff0000"}, or
        criteria - a list of criteria sets.

    An oligo matches a criteria set (dict) if it matches all entries in the dict,
    i.e. {"st_type": "scaf", "color": "#ff0000"} will match all oligos that are
    (a) scaffold oligos, and (b) colored red.

    If criteria is list of criteria sets (dicts), the oligo is considered a
    match if it matches any of the criteria dicts. Thus,
    [{"st_type": "scaf", "color": "#ff0000"}, {"st_type": "stap", "color": "#0000ff"}]
    will match either red scaffold oligos or blue staple oligos.

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
    if isinstance(criteria, list):
        return any(match_oligo(oligo, criteriaset) for criteriaset in criteria)
    return all(crit_match(oligo, key, value) for key, value in criteria.items())


def oligo_match_criteriaset(oligo, criteriaset):
    """
    Returns True if oligo matches all criterium in the given set of criteria.
    Arguments:
        oligos - a cadnano oligo
        criteria - a set (dict) of criteria, e.g. {"st_type": "scaf", "color": "#ff0000"}, or

    An oligo matches a criteria set (dict) if it matches all entries in the dict,
    i.e. {"st_type": "scaf", "color": "#ff0000"} will match all oligos that are
    (a) scaffold oligos, and (b) colored red.
    """
    return all(crit_match(oligo, key, value) for key, value in criteriaset.items())


def oligo_match_criteriaset_list(oligo, criteriaset_list):
    """
    Returns True if oligo matches all criterium in the given set of criteria.
    Arguments:
        oligos - a cadnano oligo
        criteria - a list of criteria sets (dicts).

    An oligo matches a criteria set (dict) if it matches all entries in the dict,
    i.e. {"st_type": "scaf", "color": "#ff0000"} will match all oligos that are
    (a) scaffold oligos, and (b) colored red.
    [{"st_type": "scaf", "color": "#ff0000"}, {"st_type": "stap", "color": "#0000ff"}]
    will match either red scaffold oligos or blue staple oligos.
    """
    return any(oligo_match_criteriaset(oligo, criteriaset) for criteriaset in criteriaset_list)


def get_matching_oligos(part, criteria):
    """
    Lifted from cadnano_apply_seq in RsUtils repo.
    Get all oligos on part matching the given set of criteria,
    or, if criteria is a list, any oligo that matches either of the criteria sets in the list.

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
        #return {oligo for crit_dict in criteria for oligo in get_matching_oligos(part, crit_dict)}
        #return {oligo for crit_dict in criteria for oligo in get_matching_oligos(part, crit_dict)}
        return [oligo for oligo in part.oligos() if oligo_match_criteriaset_list(oligo, criteria)]
    return [oligo for oligo in part.oligos() if oligo_match_criteriaset(oligo, criteria)]


def print_oligo_criteria_match_report(oligos, criteria, desc=None):
    """ Print standard criteria match report. """
    print("\n{} oligos matching criteria set {}:".format(len(oligos), desc))
    #print("Oligos matching criteria set:", desc)
    if VERBOSE > 1:
        print(yaml.dump({"criteria": [criteria]}, default_flow_style=False).strip("\n"))
        print("The matching oligos are:")
        print("\n".join(" - {}".format(oligo) for oligo in oligos))


def apply_seqspecs(part, seqspecs, offset=None, verbose=None):
    """ Apply sequences in seq_specs to matching oligos in part. """
    if verbose is None:
        verbose = VERBOSE
    for seq_i, seq_spec in enumerate(seqspecs):
        # seq_spec has key "seq" and optional keys "criteria", and "offset".
        # If seq_spec has an offset specified, this is always used.
        # Specifying offset=0 can be used to fix mini-scafs so they are not rotated with the main scaffold.
        seq = seq_spec["seq"]
        L = len(seq)
        seq_offset = seq_spec.get("offset", offset)
        if seq_offset:
            seq = (seq*3)[L+seq_offset:L*2+seq_offset]
        oligos = get_matching_oligos(part, seq_spec["criteria"])
        if verbose > 1:
            print_oligo_criteria_match_report(oligos, seq_spec["criteria"],
                                              desc="for application of sequence #{}".format(seq_i))
        for oligo in oligos:
            oligo.applySequence(seq, use_undostack=False)


def apply_scaffold_sequence(part, seq, offset=None, verbose=None,
                            match_fun=lambda oligo, L: not oligo.isStaple() and oligo.length() > L/2):
    """
    Simple function to apply sequence to part.
    Will apply sequence to the first scaffold oligo in part that passes
    match_fun(oligo, L), where L is the sequence length. match_fun default is:
        lambda oligo, L: not oligo.isStaple() and oligo.length() > L/2
    """
    L = len(seq)
    if offset:
        seq_offset = offset
        seq = (seq*3)[L+seq_offset:L*2+seq_offset]
    oligos = part.oligos()
    # Get the first scaffold oligo:
    scaf_oligo = next(oligo for oligo in oligos if match_fun(oligo, L))
    if verbose:
        print(" - Applying {} nt sequence to oligo of length {}"
              .format(L, scaf_oligo.length()))
    scaf_oligo.applySequence(seq, use_undostack=False)


def apply_sequences(part, seqs, offset=None, verbose=0):
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
        apply_scaffold_sequence(part, seq=seqs, offset=offset, verbose=verbose)
    else:
        # Apply sequences based on seq_spec criteria:
        apply_seqspecs(part, seqs, offset=offset, verbose=verbose)
