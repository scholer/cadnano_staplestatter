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
    matplotlib.use('Qt4Agg')    # 'agg' is just "anti-grain". Default is "Anti-Grain Geometry" C++ library.
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


def plot_frequencies(scorefreqs, min_score_visible=5, xlabel="Score", ylabel="Frequency / count"):
    """
    Plot score frequencies.
    """
    fig = pyplot.figure(figsize=(12, 6))    # If you are in interactive mode, the figure will appear immediately.
    ax = fig.add_subplot(111)
    values, counts = zip(*scorefreqs)
    lines = ax.vlines(values, [0], counts)  # lines can also be obtained from ax.collections list.
    valrange = max(values) - min(values)
    ax.set_xlim(min(values)-0.1*valrange, max(values+(min_score_visible,))+0.1*valrange)
    ax.set_ylim(0, max(counts)*0.1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    pyplot.draw()  # update figure (if in interactive mode...)
    # fig.draw(artist, renderer)    # requires you to know how to draw...
    return fig, ax, lines


