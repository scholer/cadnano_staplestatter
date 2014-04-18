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
Main module for evaluating a cadnano design.


If using interactively, use
    reload(staplestatter)
to reload module ;-)

If you just want to execute some code, the easiest way is:
    execfile(<path-to-file>)


"""


import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest


from statutils import valleyscore, globalmaxcount
import cadnanoreader


def evaluate_part_oligos(cadnano_part, scoremethod=None):
    """
    Evaluate part oligos.
    """
    if scoremethod is None:
        scoremethod = valleyscore

    oligo_hybridization_patterns = cadnanoreader.get_oligo_hyb_patterns(cadnano_part)

    # This should be a (possibly ordered) dict, as:
    # oligos[<oligo name>] = [list of integers representing hybridization lengths or melting temperatures]
    scores = {oligo_key : scoremethod(hyb_pattern) for oligo_key, hyb_pattern in oligo_hybridization_patterns.items()}


    return scores


def get_highest_scores(scores, highest=10, threshold=0, printstats=False, printtofile=False):
    """
    Returns a sorted list of tuples:
        (score, oligo-name)
    The list is cut of after <highest> number of elements.
    Additionally, only elements with threshold

    If printstats=True, will print to stdout
    If printtofile is a filepath, will print to this filepath.
    """
    score_name_tups = sorted(((score, name) for name, score in scores.items() if score>threshold), reverse=True)
    if highest and highest < len(score_name_tups):
        score_name_tups = score_name_tups[:highest]
    if printstats or printtofile:

        output = "\n".join("Scored oligos: (score, name)",
                            "\n".join("{:6} {}".format(score, name) for score, name in score_name_tups))
        if printstats:
            print output
        if printtofile:
            try:
                with open(printtofile, 'wb') as fh:
                    fh.write(output)
            except (IOError, OSError) as e:
                print "Could not save to file '", printtofile, "', got error: ", e

    logging.debug("Scored oligos from part: %s", score_name_tups)
    return score_name_tups


def score_frequencies(scores):
    """
    Produce a sorted list of tuples
        (value, count)
    where value is a score value and count is the number of
    entries in scores with that value.
    Mostly usable for scoremethods that produce integer values.
    """
    valueset = set(scores.values())
    scorefreq = sorted((value, scores.values().count(value)) for value in valueset)
    return scorefreq

