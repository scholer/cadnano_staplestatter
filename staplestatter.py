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
import yaml
import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest

try:
    import matplotlib
    if not matplotlib.get_backend().lower() == 'Qt4Agg'.lower():
        matplotlib.use('Qt4Agg') # Must always be called *before* importing pyplot
    from matplotlib import pyplot
except ImportError:
    print "matplotlib library not available, unable to plot."
    matplotlib = None
    pyplot = None

#from statutils import valleyscore, globalmaxcount, maxlength
import statutils
import cadnanoreader
import plotutils
from plotutils import plot_frequencies


try:
    import cadnano_api
except ImportError:
    try:
        from cadnano import cadnano_api
    except ImportError:
        print "Could not import cadnano api..."
        class cadnano_api(object):
            """ Used as namespace to simulate the cadnano_api module (by defining a range of static methods) """
            @staticmethod
            def a():
                """ Returns app instance. """
                import cadnano
                return cadnano.app()
            @staticmethod
            def d():
                """ Returns document object (model). """
                return cadnano_api.a().d
            @staticmethod
            def p():
                """ Returns part object (model). """
                return cadnano_api.d().selectedPart()



def score_part_oligos(cadnano_part, scoremethod=None, scoremethod_kwargs=None):
    """
    Evaluate part oligos.
    # This should be a (possibly ordered) dict, as:
    # oligos[<oligo name>] = [list of integers representing hybridization lengths or melting temperatures]
    """
    if scoremethod is None:
        scoremethod = statutils.valleyscore
    if scoremethod_kwargs is None:
        scoremethod_kwargs = dict()
    oligo_hybridization_patterns = cadnanoreader.get_oligo_hyb_patterns(cadnano_part)
    scores = {oligo_key : scoremethod(hyb_pattern, **scoremethod_kwargs) for oligo_key, hyb_pattern in oligo_hybridization_patterns.items()}
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

        output = "\n".join(["Scored oligos: (score, name)",
                            "\n".join("{:6} {}".format(score, name) for score, name in score_name_tups)])
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



def plotpartstats(part=None, designname=None):
    """
    Reference method, will plot a "default" stat spec.
    Invoke with e.g.
        f7, scoreaxes, allscores = plotpartstats(p())
    """
    if not matplotlib:
        print "No matplotlib"
        return
    else:
        import matplotlib.gridspec as gridspec
    if part is None:
        part = cadnano_api.p()
    if designname is None:
        designname = os.path.splitext(os.path.basename(part.document().controller().filename()))[0]

    fig = pyplot.figure()

    scoremethods = ('maxlength', 'valleyscore', 'globalmaxcount')
    xlabels = ["Max hybridization length", "Number of valley stretches", "Number of global maxima"]
    #titles = ["{}: {} histogram".format(designname, desc) for desc in ("Hybridization length", "Valley scores", "Global maxima")]
    titles = ["{} : Staplestrand stats".format(designname), "", ""]
    colors = 'krb'
    # using gridspec, c.f. http://matplotlib.org/users/gridspec.html
    gs = gridspec.GridSpec(2, 2) # two by two, gridspec is 0-based.
    scoreaxes = [pyplot.subplot(gsdef) for gsdef in (gs[0, :], gs[1, 0], gs[1, 1])]

    # alternatively, you could just have used
    # subfigkeys = [211, 223, 224]  # the second and third plot will update automatically.

    allscores = list()
    for i, method in enumerate(scoremethods):
        scoremethod = getattr(statutils, method)
        scores = score_part_oligos(part, scoremethod=scoremethod)
        allscores.append(scores)
        score_freqs = statutils.frequencies(scores)
        plot_frequencies(score_freqs, ax=scoreaxes[i], xlim_min=0,
                         xlabel=xlabels[i], title=titles[i], color=colors[i], label=designname[:10])

    return fig, scoreaxes, allscores


def process_statspec(statspec, part=None, designname=None, fig=None, ax=None):
    """
    Will process a single stat specification.
    statspec is a dict with keys:
      scoremethod : The method name from statutils module to use to score the hyb pattern.
      scoremethod_kwargs: keyword arguments to pass to the score method.
      plot_axis: 211    # n-rows, n-cols, plot-number;
      plot_kwargs: {hold: true}
      plot_xlim: [0, 5]
      plot_ylim: [0, 200]
      plot_title: Plot test
      printspec: { highest : 10, threshold : 0, printstats: false, printtofile : false, hightolow : true }

    Regarding subfigures, you can use e.g.:
        # subfigkeys = [211, 223, 224]  # the first plot will second and third plot will update automatically.
    """
    if part is None:
        part = cadnano_api.p()
    plotspec = statspec.get('plotspec', dict())
    try:
        scoremethod = getattr(statutils, statspec['scoremethod'])
    except AttributeError:
        print "ERROR -- Method '", statspec['scoremethod'], "' in statspec was not found in statutils, continuing with next!"
        return
    except KeyError:
        print "ERROR -- statspec does not have a key 'scoremethod', aborting this entry!"
        return
    scoremethod_kwargs = statspec.get('scoremethod_kwargs', dict())

    # Adjust auto stuff:
    format_keys = dict(plotspec, designname=designname, scoremethod=statspec['scoremethod'], **scoremethod_kwargs)
    print "format_keys: ", format_keys
    autoformat_defaults = dict(title="{scoremethod}", label="{designname}", xlabel="{scoremethod}")
    for autofmtkey in ('title', 'label', 'xlabel'):
        if plotspec.get(autofmtkey, None) in (None, 'auto'):
            fmt = plotspec.get(autofmtkey+'_fmt', autoformat_defaults[autofmtkey])
            # I might want to set to None in the plotspec to NOT have it.
            if fmt:
                plotspec.setdefault('plot_kwargs', dict())[autofmtkey] = fmt.format(**format_keys)

    # Get scores:
    scores = score_part_oligos(part, scoremethod=scoremethod, scoremethod_kwargs=scoremethod_kwargs)
    # Make frequencies:
    scorefreqs = statutils.frequencies(scores) if statspec.get('plot_frequencies', True) else None
    # Plot
    plotutils.plot_statspec(scorefreqs, plotspec, fig=fig, ax=ax)
    # Post-processing (?)

    return scores



def process_statspecs(directive, part=None, designname=None):
    """
    Main processor for the staplestatter directive. Responsible for:
    1) Initialize figure and optionally axes as specified by the directive instructions.
    2) Loop over all statspecs and call process_statspec.
    3) Aggregate and return a list of stats/scores.
    """
    if part is None:
        part = cadnano_api.p()
    if designname is None:
        designname = os.path.splitext(os.path.basename(part.document().controller().filename()))[0]
    print "designname: ", designname

    statspecs = directive['statspecs']
    figspec = directive.get('figure', dict())
    if figspec.get('newfigure', False) or len(pyplot.get_fignums()) < 1:
        fig = pyplot.figure(**figspec.get('figure_kwargs', {}))
    else:
        fig = pyplot.gcf() # Will make a new figure if no figure has been created.
    # Here you can add more "figure/axes" specification logic:
    adjustfuncs = ('title', 'size_inches', 'dpi')
    for cand in adjustfuncs:
        if cand in figspec and figspec[cand]:
            getattr(fig, 'set_'+cand)(figspec[cand]) # equivalent to fig.title(figspec['title'])

    pyplot.ion()
    allscores = list()
    for _, statspec in enumerate(statspecs):
        scores = process_statspec(statspec, part=part, designname=designname, fig=fig)
        allscores.append(scores)
        if 'printspec' in statspec:
            print "Printing highest scores with: statspec['printspec']"
            get_highest_scores(scores, **statspec['printspec']) # This logic is subject to change.
    return dict(figure=fig, scores=allscores)


def process_statspecs_string(directive_string):
    """
    Process a statspecs string, yaml format.
    """
    directive = yaml.load(directive_string)
    return process_statspecs(directive)


def process_statspecs_file(filepath):
    """
    Process a statspecs file, yaml format.
    """
    with open(filepath) as fd:
        directive = yaml.load(fd)
    return process_statspecs(directive)

def savestats(stats, filepath):
    """ save stats to filepath """
    try:
        yaml.dump(stats, open(filepath, 'wb'))
    except IOError as e:
        print "IOError while saving stats to file: ", filepath, " : ", e
