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

Takes arbitrary numeric arrays and process them.

"""

from collections import Counter

import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest



def leftrightmaxdiff(T_array):
    """
    For each element in T_array, calculate the difference vs the max up to that element.
    (T_array is expected to be an array of strand hybridization lengths or melting temperatures)
    Returns two arrays, one with the difference vs the max to the left
    and another array with the difference vs the max to the right.
    >>> leftrightmaxdiff([7, 14, 21])
    ([7, 7, 7], [-14, -7, 21])
    >>> leftrightmaxdiff([14, 7, 14, 21])
    ([14, -7, 0, 7], [-7, -14, -7, 21])
    >>> leftrightmaxdiff([14, 7, 7, 21])
    ([14, -7, -7, 7], [-7, -14, -14, 21])
    >>> leftrightmaxdiff([14, 13, 12, 13, 14])
    ([14, -1, -2, -1, 0], [0, -1, -2, -1, 14])
    >>> leftrightmaxdiff([23])
    ([23], [23])
    >>> leftrightmaxdiff([])
    ([], [])
    """
    T_pad = [0] + T_array + [0] # use 1-based indexing
    # remember, array[0:2] slice goes from index 0 up to BUT NOT INCLUDING 2, i.e. 0 and 1.
    leftbound = [T_pad[i]-max(T_pad[:i]) for i in range(1, len(T_array)+1)]
    rightbound = [T_pad[i]-max(T_pad[i+1:]) for i in range(1, len(T_array)+1)]
    return leftbound, rightbound



def valleyfinder(T_array, margin=0):
    """
    Input array representing lengths of oligos and output an array which for each
    element, Ti, specifies if Ti is less than the cumulative sums on both sides, i.e.
    a local minima not at the edge.
    The argument margin can be used to add some space, i.e.
    allow minor fluctuations, e.g. [14, 13, 14] --> is ok.
        >>> valleyfinder([7, 14, 21], 0)
        [0, 0, 0]
        >>> valleyfinder([14, 7, 14, 21], 0)
        [0, 1, 0, 0]
        >>> valleyfinder([14, 7, 7, 21], 0)
        [0, 1, 1, 0]
        >>> valleyfinder([14, 13, 12, 13, 14], 0)
        [0, 1, 1, 1, 0]
        >>> valleyfinder([14, 13, 12, 13, 14], 1)
        [0, 0, 1, 0, 0]
        >>> valleyfinder([23])
        [0]
        >>> valleyfinder([])
        []

    """
    #leftbound, rightbound = leftrightmaxdiff(T_array)
    #valleyarray = [1 if leftbound[i] < margin and rightbound[i] < margin else 0 for i in range(len(T_array))]
    pointsdiffs = zip(*leftrightmaxdiff(T_array))
    valleyarray = [1 if all(diff < -margin for diff in difftup) else 0 for difftup in pointsdiffs]
    return valleyarray


def valleyscore(T_array, margin=0):
    """
    Evaluate T_array for valley points:
        >>> valleyscore([7, 14, 21])
        0
        >>> valleyscore([14, 7, 14, 21], 0)
        1
        >>> valleyscore([14, 7, 7, 21], 0)
        2
        >>> valleyscore([14, 13, 12, 13, 14], 0)
        3
        >>> valleyscore([14, 13, 12, 13, 14], 1)
        1
        >>> valleyscore([23])
        0
        >>> valleyscore([])
        0
    """
    return sum(valleyfinder(T_array, margin))


def isglobalmax(T_array, margin=0):
    """
    For each element in T_array, tests whether the element is the highest.
        >>> isglobalmax([7, 14, 21])
        [0, 0, 1]
        >>> isglobalmax([7, 14, 7])
        [0, 1, 0]
        >>> isglobalmax([14, 13, 12, 13, 14], margin=0)
        [1, 0, 0, 0, 1]
        >>> isglobalmax([14, 13, 12, 13, 14], margin=1)
        [1, 1, 0, 1, 1]
        >>> isglobalmax([23])
        [1]
        >>> isglobalmax([])
        []
    """
    if len(T_array) == 1:
        # T_array[i+1:] would fail for this
        return [1]
    return [1 if t-max(T_array[:i]+T_array[i+1:])>=-margin else 0 for i, t in enumerate(T_array)]


def globalmaxcount(T_array, margin=0):
    """
    Test whether T_array has a single max.
    margin can be used to increase the range, i.e.
        >>> globalmaxcount([7, 14, 21])
        1
        >>> globalmaxcount([7, 14, 7])
        1
        >>> globalmaxcount([14, 13, 12, 13, 14], margin=0)
        2
        >>> globalmaxcount([14, 13, 12, 13, 14], margin=1)
        4
        >>> globalmaxcount([23])
        1
        >>> globalmaxcount([])
        0
    """
    return sum(isglobalmax(T_array, margin))


def maxlength(T_array):
    return max(T_array) if T_array else 0




def frequencies(scores):
    """
    Produce a sorted list of tuples
        (value, count)
    where value is a score value and count is the number of
    entries in scores with that value.
    Mostly usable for scoremethods that produce integer values.

    Original RS implementation:
        scorefreq = sorted((value, values.count(value)) for value in set(values))

    This can also be re-implemented by:
    From Raymond Hettinger video:
        freqs = collections.defaultdict(int) # int() will default to 0.
        for value in values:
            freqs[value] += 1   # or, for a standard dict(), use freqs.setdefault(value, 0) += 1
    # This is actually the fastest method for pretty much all cases I have encountered... but only for making dict.
    # Then you also need to make the items() list...

    Alternative with collections.Counter, which is basically an advanced dict, or
    actually a set that keeps track of how many times an element has been added to it.
        >>> freqs = Counter([1, 3, 5, 2, 1, 5])
        >>> freqs[1], freqs[3]
        2, 1
        >>> freqs.elements()
        iter([1, 3, 5, 2, 1, 5])
        >>> freqs.keys(), freqs.values(), freqs.items()
        [1, 2, 3, 5], [2, 1, 1, 2], [(1, 2), (2, 1), (3, 1), (5, 2)]

    For values a list of 10'000 random integers [0, 30],
    Counter is 30% faster than counting (creating the set is super fast).
    For a list of 200 random integers [20, 40], there is,
    no measurable difference, and for smaller lists,
    values.count(value) is the faster method.
    Counter is, however, better if there is a large spread.
    values.count(value) takes a steep performance hit if there are only one or a few
    of each element in the list.
    I.e for [randint(0, 30) for i in xrange(200)], Counter and values.count(value)
    are both 70 us per loop, (using %timeit), while for
        values = [randint(0, 1000) for i in xrange(200)], Counter and values.count(value)
    Counter(values) is 89 us per loop while values.count(value) is a wooping 530 us.
    Conversely for:
        values = [random.randint(0, 3) for i in xrange(200)]
    Counter(values) is 68 us per loop while values.count(value) is only 16 us.
    """
    try:
        values = scores.values()
    except AttributeError:
        # if not a dict, it is probably just a list of values...
        values = scores
    #scorefreq = sorted((value, values.count(value)) for value in set(values)) # Faster short lists with few unique values.
    scorefreq = sorted(Counter(values).iteritems()) # Faster for long list with many unique elements.
    return scorefreq
