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
# pylint: disable-msg=C0103,C0301,C0302,R0201,R0902,R0904,R0913,W0142,W0201,W0221,W0402

"""

Module related to everything plotting.

Inspiration from:
- http://matplotlib.org/api/pyplot_api.html
- http://matplotlib.org/1.3.1/users/recipes.html
- http://matplotlib.org/1.3.1/gallery.html
- http://matplotlib.org/1.3.1/examples/pylab_examples/vline_hline_demo.html
- http://matplotlib.org/1.3.1/examples/pylab_examples/boxplot_demo2.html


Customizing matplotlib:
    http://matplotlib.org/users/customizing.html
    http://matplotlib.org/faq/usage_faq.html

Regarding Qt:

- http://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html
- http://stackoverflow.com/questions/12459811/how-to-embed-matplotib-in-pyqt-for-dummies



"""



import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest


try:
    import matplotlib
except ImportError:
    print "matplotlib library not available, unable to plot."
    matplotlib = None
    pyplot = None
else:
    # backend must be selected *before* importing pyplot, pylab or matplotlib.backends
    if not matplotlib.get_backend().lower() == 'Qt4Agg'.lower():
        print "matplotlib.get_backend() is: ", matplotlib.get_backend(), " -- resetting to Qt4Agg"
        matplotlib.use('Qt4Agg') # Must always be called *before* importing pyplot
    #matplotlib.use('Qt4Agg')    # 'agg' is just "anti-grain". Default is "Anti-Grain Geometry" C++ library.
    # should be the same as setting
    # matplotlib.rcParams['backend'] = 'Qt4Agg'.
    # Also check:
    # matplotlib.rcParams['backend.qt4'] = 'PyQt4' # or 'PySide'

    # Note: If matplotlib is in interactive mode, pyplot.show() seems to be non-blocking.
    # while if matplotlib is NOT in interactive mode, pyplot.show() will block terminal input.
    # ALWAYS enable interactive mode before showing/drawing plots.
    # You can disable interactive mode if you have a lot of things you want to
    # create before you draw and thus want to postpone rendering until display time.
    matplotlib.interactive(True)    # will display things immediately.

    from matplotlib import pyplot # provides some convenient plotting methods
    plt = pyplot # alias...


def plotscores_histogram(scores):
    """
    Score.
    # Note: instead of using the blocking pyplot.show(),
    # consider using pyplot.draw() instead for displaying plots while in cadnano!
    # set interactive mode to off with pyplot.ioff() and enable interactive mode with pyplot.ion()
    # this just does matplotlib.interactive(False/True), which again just sets
    # rcParams['interactive'] = True/False  # this is also simply returned when checking with matplotlib.is_interactive()
    pyplot.draw()
    # alternatively, if using matplotlib object-oriented code, use fig.canvas.draw()
    """
    #n, bins, patches = pyplot.hist(x, num_bins, normed=1, facecolor='green', alpha=0.5)
    values = scores.values()
    n, bins, patches = pyplot.hist(values)
    pyplot.xlabel = "Score value (lower is better)"
    pyplot.ylabel = "Frequency"
    return n, bins, patches


def plot_frequencies(scorefreqs, min_score_visible=5, xlabel="Score", ylabel="Frequency / count", title=None,
                     ax=None, fig=None, subplotkey=111, xoffset=0, xlim_min=None, autocolors='krbgcmy', **kwargs):
    """
    Plot score frequencies.
    You can re-use an existing figure by providing an axis with ax keyword,
    or fig

    **kwargs are passed to the vlines plotting method. These may include:
        colors, linestyles, label, and generic,
        and other generic matplotlib.collections.LineCollection properties
        (agg_filter, alpha, linewidth, linestyles, etc...)

    Instead of xoffset=<const>, you can also specify offsets=[<float>]*len(scorefreqs)
    as kwarg to ax.vlines.

    to remove a set line collection:
        lc = ax.collections[0]
        lc.remove()
    to remove all lines in an axes:
        loops = 0
        while ax.collections and loops < 15: # prevent infinite loop
            ax.collections.pop().remove()

    subplotkey is provided to add_subplot if making subfigure, keys are (numrows, numcols, plotnum)

    """
    print "xlabel: ", xlabel, "; kwargs: ", kwargs
    if ax is None:
        if fig is None:
            fig = pyplot.figure(figsize=(12, 6))    # If you are in interactive mode, the figure will appear immediately.
        ax = fig.add_subplot(subplotkey)
    values, counts = zip(*scorefreqs)

    # Auto-adjust color:
    if kwargs.get('color') == 'auto':
        autocolors = autocolors*10 # Make sure we have sufficient and don't run into IndexErrors
        kwargs['color'] = autocolors[len(ax.collections)]
        print "color auto adjusted to: ", kwargs['color']
    else:
        print "color: ", kwargs['color']

    # Auto-adjust xoffset:
    if xoffset == 'auto':
        xoffsetmultiplier = 0.1 if max(values) < 10 else 0.2
        xoffset = 0.1 * len(ax.collections)
        print "xoffset auto adjusted to: ", xoffset
    else:
        print "xoffset: ", xoffset
    if xoffset:
        # actually, I think you can just pass offset as offsets kwargs...
        values = [val+xoffset for val in values]

    if 'lw' not in kwargs and 'linewidth' not in kwargs and 'linewidths' not in kwargs:
        kwargs['linewidth'] = 2

    # PLOT:
    #lines = ax.vlines(values, [0], counts, **kwargs)  # lines can also be obtained from ax.collections list.
    lines = pyplot.vlines(values, [0], counts, axes=ax, **kwargs)  # lines can also be obtained from ax.collections list.

    # ADJUST THE PLOT:
    valrange = max(values) - min(values)
    xlim = [min(values)-0.1*valrange, max(max(values), min_score_visible)+0.1*valrange]
    if xlim_min is not None and xlim_min < xlim[0]:
        xlim[0] = xlim_min
    ax.set_xlim(xlim)
    ax.set_ylim(0, max(counts)*1.1)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if valrange > 10:
        #ax.set_xticks([2*i for i in xrange(0, int(xlim[1]))])
        ax.minorticks_on()
    if title:
        print "Setting axes/subplot title: ", title
        ax.set_title(title)
    pyplot.draw()  # update figure (if in interactive mode...)
    # fig.draw(artist, renderer)    # requires you to know how to draw...
    return ax, lines



def plot_statspec(scorefreqs, plotspec, fig=None, ax=None):
    """
    Used by staplestatter.process_statspec() to plot score frequences.
    """
    subplot = plotspec.get('subplot')
    if subplot:
        if fig:
            ax = fig.add_subplot(subplot)
        else:
            ax = pyplot.subplot(subplot)
    ax, lines = plot_frequencies(scorefreqs, fig=fig, ax=ax, **plotspec.get('plot_kwargs', dict()))
    print "plotspec: ", plotspec
    adjustfuncs = ('title', 'xlim', 'ylim', 'ylabel')
    for cand in adjustfuncs:
        if cand in plotspec and plotspec[cand]:
            # consider using ax instead of pyplot? However, then you should use 'set_'+cand
            getattr(pyplot, cand)(plotspec[cand]) # equivalent to pyplot.title(plotspec['title'])
    if 'legend' in plotspec:
        pyplot.legend(**plotspec['legend'])
    return ax, lines
