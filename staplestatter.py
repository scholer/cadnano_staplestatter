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


Other nice-to-have:

designname = os.path.splitext(os.path.basename(dc().filename()))[0]

"""

import os

import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest


try:
    import matplotlib
    from matplotlib import pyplot
except ImportError:
    print "matplotlib library not available, unable to plot."
    matplotlib = None
    pyplot = None

cadnano_api = None
try:
    import cadnano_api
except ImportError:
    try:
        from cadnano import cadnano_api
    except ImportError:
        print "Could not import cadnano api..."
        def a():
            import cadnano
            return cadnano.app()
        def d():
            return a().d
        def p():
            return d().selectedPart()
        # Provisory api:
        api = dict(a=a, d=d, p=p)

if cadnano_api:
    api = cadnano_api.get_api()
    locals().update(api)

from statutils import valleyscore, globalmaxcount, maxlength
import cadnanoreader
import plotutils
from plotutils import plot_frequencies


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


def get_highest_scores(scores, highest=10, threshold=0, printstats=False, printtofile=False, hightolow=True):
    """
    Returns a sorted list of tuples:
        (score, oligo-name)
    The list is cut of after <highest> number of elements.
    Additionally, only elements with threshold

    If printstats=True, will print to stdout
    If printtofile is a filepath, will print to this filepath.
    """
    score_name_tups = sorted(((score, name) for name, score in scores.items() if score>threshold), reverse=hightolow)
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
    try:
        values = scores.values()
    except AttributeError:
        # if not a dict, it is probably just a list of values...
        values = scores
    valueset = set(values)
    scorefreq = sorted((value, values.count(value)) for value in valueset)
    return scorefreq




def plotpartstats(part=None, filename=None):
    """
    Invoke with e.g.
        f7, scoreaxes, allscores = plotpartstats(p())

    """

    if not matplotlib:
        print "No matplotlib"
        return

    import matplotlib.gridspec as gridspec

    if part is None:
        # only works if run in e.g. interactive cadnano with a p() global
        part = api.p()
    if filename is None:
        filename = part.document().controller().filename()

    filename = os.path.basename(filename)
    designname = os.path.splitext(filename)[0]

    fig = pyplot.figure()

    scoremethods = maxlength, valleyscore, globalmaxcount
    xlabels = ["Max hybridization length", "Number of valley stretches", "Number of global maxima"]
    #titles = ["{}: {} histogram".format(designname, desc) for desc in ("Hybridization length", "Valley scores", "Global maxima")]
    titles = ["{} : Staplestrand stats".format(designname), "", ""]
    colors = 'krb'
    # using gridspec, c.f. http://matplotlib.org/users/gridspec.html
    gs = gridspec.GridSpec(2, 2) # two by two, gridspec is 0-based.
    gridspecs = (gs[0, :], gs[1, 0], gs[1, 1])
    scoreaxes = [pyplot.subplot(gsdef) for gsdef in gridspecs]

    # alternatively, you could just have used
    # subfigkeys = [211, 223, 224]  # the second and third plot will update automatically.

    allscores = list()
    for i, method in enumerate(scoremethods):
        scores = evaluate_part_oligos(part, scoremethod=method)
        allscores.append(scores)
        score_freqs = score_frequencies(scores)
        plot_frequencies(score_freqs, ax=scoreaxes[i], xlim_min=0,
                         xlabel=xlabels[i], title=titles[i], color=colors[i], label=designname[:10])

    return fig, scoreaxes, allscores
