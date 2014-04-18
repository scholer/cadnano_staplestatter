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

import logging
logger = logging.getLogger(__name__)
# Note: Use pytest-capturelog to capture and display logging messages during pytest



def leftrightmaxdiff(T_array):
    """
    For each element in T_array, calculate the difference vs the max up to that element.
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
    """
    T_pad = [0] + T_array + [0] # use 1-based indexing
    # remember, array[0:2] slice goes from index 0 up to BUT NOT INCLUDING 2, i.e. 0 and 1.
    leftbound = [T_pad[i]-max(T_pad[:i]) for i in range(1, len(T_array)+1)]
    rightbound = [T_pad[i]-max(T_pad[i+1:]) for i in range(1, len(T_array)+1)]
    return leftbound, rightbound



def valleyfinder(T_array, limit=0):
    """
    Input array representing lengths of oligos and output an array which for each
    element, Ti, specifies if Ti is less than the cumulative sums on both sides, i.e.
    a local minima not at the edge.
    The argument limit can be used to add some space, i.e.
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
    """
    #leftbound, rightbound = leftrightmaxdiff(T_array)
    #valleyarray = [1 if leftbound[i] < limit and rightbound[i] < limit else 0 for i in range(len(T_array))]
    pointsdiffs = zip(*leftrightmaxdiff(T_array))
    valleyarray = [1 if all(diff < -limit for diff in difftup) else 0 for difftup in pointsdiffs]
    return valleyarray


def valleyscore(T_array, limit=0):
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
    """
    return sum(valleyfinder(T_array, limit))


def isglobalmax(T_array, limit=0):
    """
    For each element in T_array, tests whether the element is the highest.
        >>> isglobalmax([7, 14, 21])
        [0, 0, 1]
        >>> isglobalmax([7, 14, 7])
        [0, 1, 0]
        >>> isglobalmax([14, 13, 12, 13, 14], limit=0)
        [1, 0, 0, 0, 1]
        >>> isglobalmax([14, 13, 12, 13, 14], limit=1)
        [1, 1, 0, 1, 1]
    """
    return [1 if t-max(T_array[:i]+T_array[i+1:])>=-limit else 0 for i, t in enumerate(T_array)]


def globalmaxcount(T_array, limit=0):
    """
    Test whether T_array has a single max.
    Limit can be used to increase the range, i.e.
        >>> globalmaxcount([7, 14, 21])
        1
        >>> globalmaxcount([7, 14, 7])
        1
        >>> globalmaxcount([14, 13, 12, 13, 14], limit=0)
        2
        >>> globalmaxcount([14, 13, 12, 13, 14], limit=1)
        4
    """
    Tcopy = T_array
    return sum(isglobalmax(T_array, limit))

