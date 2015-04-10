# Copyright (C) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
r"""
:mod:`c4dtools.math`
====================

This module provides functions for common calculations.
"""


def closest_point_on_line(a, b, p):
    r"""
    Returns the closest point to *p* which is on the line through the
    points *a* and *b*. :class:`ZeroDivisionError` is raised if *a* and
    *b* are the same.
    """

    ap = a - p
    ab = b - a
    ab2 = ab.x ** 2 + ab.y ** 2 + ab.z ** 2
    ab_ap = (ap.x * ab.x) + (ap.y * ab.y) + (ap.z * ab.z)
    t = ab_ap / ab2
    return a - ab * t
