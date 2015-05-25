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

Draw melting temperatures (TM) for individual strands in a cadnano pathview,
outputting an svg file.
1) Load cadnano file.
2)


Example usage:
    $>

"""


import os
import sys
import glob
import argparse
import webbrowser
#import json
#import time
import yaml
import base64
from six import string_types
#from operator import itemgetter
try:
    import svgwrite     # pylint: disable=F0401
except ImportError:
    sys.path.append(os.path.normpath(r"C:\Users\scholer\Dev\src-repos\my-forked-repos\svgwrite"))
    import svgwrite     # pylint: disable=F0401
try:
    from PIL import Image
except ImportError:
    print("PIL (Python Image Library) or Pillow not available -- will use alternative function to get image size.")
from Bio.SeqUtils.MeltingTemp import Tm_NN
import logging
logger = logging.getLogger(__name__)
#import math
#from importlib import reload
#import PyQt5
#import matplotlib
#matplotlib.use("Qt5Agg")
#from matplotlib import pyplot #, gridspec

# Note regarding ImportError when using Anaconda environtments:
# For some reason, simply using the python.exe in the /envs/pyqt5/ directory is not sufficient, and I will get a
# ImportError: DLL load failed: Det angivne modul blev ikke fundet.
# Instead, activate the environment and then execute python.exe
# If you don't already have this on your path:

BINDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(BINDIR)) # Staplestatter library
# Cadnano library:
sys.path.insert(0, os.path.normpath(r"C:\Users\scholer\Dev\src-repos\cadnano\cadnano2.5"))



# Cadnano library imports
from cadnano.document import Document
from cadnano.fileio.nnodecode import decode #, decodeFile
from cadnano.part.part import Part

# Staplestatter imports
from staplestatter.cadnanoreader import get_part, getstrandhybridizationregions
from staplestatter import staplestatter
from staplestatter import statutils
from staplestatter.fileutils import load_doc_from_file, load_json_or_yaml, ok_to_write_to_file
from staplestatter.oligo_utils import apply_sequences, get_oligo_criteria_list, get_matching_oligos
from staplestatter.sequtils import load_seq
#from staplestatter import plotutils

# Constants:
global VERBOSE
VERBOSE = 0


import struct
import imghdr

def get_image_size(fname):
    '''
    Determine the image type of fhandle and return its size.
    from draco, From:
    http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
    http://stackoverflow.com/questions/15800704/python-get-image-size-without-loading-image-into-memory
    '''
    fhandle = open(fname, 'rb')
    head = fhandle.read(24)
    if len(head) != 24:
        return
    if imghdr.what(fname) == 'png':
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
            return
        width, height = struct.unpack('>ii', head[16:24])
    elif imghdr.what(fname) == 'gif':
        width, height = struct.unpack('<HH', head[6:10])
    elif imghdr.what(fname) == 'jpeg':
        try:
            fhandle.seek(0) # Read 0xff next
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf:
                fhandle.seek(size, 1)
                byte = fhandle.read(1)
                while ord(byte) == 0xff:
                    byte = fhandle.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', fhandle.read(2))[0] - 2
            # We are at a SOFn block
            fhandle.seek(1, 1)  # Skip `precision' byte.
            height, width = struct.unpack('>HH', fhandle.read(4))
        except Exception: #IGNORE:W0703
            return
    else:
        return
    return width, height



def parse_args(argv=None):
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description="Cadnano apply sequence script.")
    parser.add_argument("--verbose", "-v", action="count", help="Increase verbosity.")
    parser.add_argument("--profile", "-p", action="store_true", help="Profile app execution.")
    parser.add_argument("--print-profile", "-P", action="store_true", help="Print profiling statistics.")
    parser.add_argument("--profile-outputfn", default="scaffold_rotation.profile",
                        help="Save profiling statistics to this file.")

    #parser.add_argument("--seqfile", "-s", nargs=1, required=True, help="File containing the sequences")
    parser.add_argument("seqfile", help="File containing the sequences")

    parser.add_argument("--seqfileformat", help="File format for the sequence file.")

    parser.add_argument("--offset",
                        help="Offset the sequence by this number of bases (positive or negative). "\
                        "An offset can be sensible if the scaffold is circular, "\
                        "or you have extra scaffold at the ends and you want to optimize where to start. "
                        "Note: The offset is applied to ALL sequences, unless an individual seq_spec "
                        "specifies an offset.")

    parser.add_argument("--overwrite", "-y", action="store_true",
                        help="Overwrite existing staple files if they already exists. "
                        "(Default: Ask before overwriting)")
    parser.add_argument('--no-overwrite', action='store_false', dest='overwrite', help="Do not overwrite existing png.")

    parser.add_argument("--no-simple-seq", dest="simple_seq", action="store_false", default=True,
                        help="Never load sequences from file as a simple sequence.")
    parser.add_argument("--simple-seq", action="store_true",
                        help="If specified, the sequence loaded can be a simple sequence.")

    parser.add_argument("--config", "-c", help="Load config from this file (yaml format). "
                        "Nice if you dont want to provide all config parameters via the command line.")
    parser.add_argument("--svg-filename", default="{design}.TMs.svg",
                        help="SVG file name to draw melting temperatures on."
                        "The output filename can include named python format parameters, "
                        "e.g. {design}, {cadnano_fname} and {seqfile}. "
                        "Default is {design}.TMs.svg")

    parser.add_argument('--cadnano-svg-length', type=float, default=12,
                        help="Size (length) of a cadnano base (in svg space). "
                        "This can be used to scale the svg text, instead of scaling the png background.")
    parser.add_argument('--cadnano-svg-unit', default="pt", help="SVG/HTML unit for the length.")
    parser.add_argument("--canvas-size", nargs=2, type=int,
                        help="Size of the SVG image canvas (in units of cadnano-svg-length).")
    parser.add_argument("--margins", nargs=4, type=int,
                        help="Margins to add to svg elements (left, top, right, bottom).")


    parser.add_argument('--fontsize', type=int, help="Specify default font size.")
    parser.add_argument('--fontfamily', help="Specify default font family, e.g. arial or MyriadPro.")
    parser.add_argument('--fontweight', help="Font weight: normal | bold | bolder | lighter | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | inherit.")
    parser.add_argument('--tmfmt', help="How to format the TM annotations, e.g. '{TM} C'. Format keys include: TM")

    parser.add_argument('--pngfile', help="Use this pngfile instead of the specified gelfile.")
    parser.add_argument("--png-offset", nargs=2, type=int,
                        help="Offset png file with this amount (horizontal, vertical)")
    parser.add_argument('--embed', action='store_true', default=True, help="Embed image data in svg file. (default)")
    parser.add_argument('--no-embed', dest='embed', action='store_false',
                        help="Do not embed image data in svg file, link to the file instead. (default is to embed)")
    parser.add_argument('--png-scale', help="Scale the png background by this amount. "
                        "Can be given as float (0.1, 2.5) or percentage (10%, 250%).")

    parser.add_argument('--openwebbrowser', action='store_true', default=None,
                        help="Open annotated svg file in default webbrowser. (Default is not to.)")
    parser.add_argument('--no-openwebbrowser', action='store_false', dest='openwebbrowser',
                        help="Do not open file in webbrowser.")
    parser.add_argument('--svgtopng', action='store_true', default=None,
                        help="Save svg as png (requires cairo package).")



    # NOTE: Windows does not support wildcard expansion in the default command line prompt!
    parser.add_argument("cadnano_files", nargs="+", metavar="cadnano_file",
                        help="One or more cadnano design files (.json) to apply sequence(s) to.")

    return parser, parser.parse_args(argv)


def process_args(argns=None, argv=None):
    """
    Process command line args and return a dict with args.

    If argns is given, this is used for processing.
    If argns is not given (or None), parse_args() is called
    in order to obtain a Namespace for the command line arguments.

    Will expand the entry "cadnano_files" using glob matching, and print a
    warning if a pattern does not match any files at all.

    If argns (given or obtained) contains a "config" attribute,
    this is interpreted as being the filename of a config file (in yaml format),
    which is loaded and merged with the args.

    Returns a dict.
    """
    if argns is None:
        _, argns = parse_args(argv)
    args = argns.__dict__.copy()
    if args.get("config"):
        with open(args["config"]) as fp:
            cfg = yaml.load(fp)
        args.update(cfg)
    # On windows, we have to expand *.json manually:
    file_pattern_matches = [(pattern, glob.glob(pattern)) for pattern in args['cadnano_files']]
    for pattern in (pattern for pattern, res in file_pattern_matches if len(res) == 0):
        print("WARNING: File/pattern '%s' does not match any files." % pattern)
    args['cadnano_files'] = [fname for pattern, res in file_pattern_matches for fname in res]
    return args



def ensure_numeric(inval, scalefactor=None, sf_lim=None, converter=None):
    """
    Takes a string value or iterable <inval> (input value)
    with string values and converts them to absolute values.
    Args:
        :inval:     Input to convert to a numeric value. String or iterable.
        :scalefactor: Scale inval by this factor
        :sf_lim:    Only scale if inval is less than this value (or contains '%').
                    Default sf_lim=2.  Uh... what's the point of this??
        :converter: Apply this function before returning.
                    Default is int(float(val)) IF scalefactor is an integer,
                    ELSE float(val)
    Specialities:
        Both inval and scalefactor can be lists.
        inval can even be a "list-like string":  "0.146, 0.16, 177.8%"  -> [0.146, 0.16, '177.8%']
        If scalefactor is a sequence, it is applied with zip(inval, scalefactor).
    Usage:
        >>> ensure_numeric('33%')
        0.33    (float)
        >>> ensure_numeric('33%', 100)
        33      (int)
        >>> ensure_numeric('1.115', 100, converter=float)
        111.5   (float)
        >>> ensure_numeric('5.12', 5.0, sf_lim=10)
        25.6    (float)
        >>> ensure_numeric(0.33, 100)
        33      (int)
        >>> ensure_numeric(5.12, 5, sf_lim=10)
        51    (int)
        >>> ensure_numeric("0.146, 0.16, 177.8%", [100, 200, 300.0]) # scalefactor as a sequence
        [15, 32, 533.4]   # mixed types
    """
    print("ensure_numeric(%s, scalefactor=%s, sf_lim=%s, converter=%s)" % (inval, scalefactor, sf_lim, converter))
    if isinstance(scalefactor, string_types):
        scalefactor = ensure_numeric(scalefactor)
    if converter is None:
        if not (isinstance(scalefactor, (list, tuple)) or hasattr(scalefactor, '__iter__')):
            # Do not infer converter if scalefactor is a sequence:
            converter = (lambda x: int(round(x))) if isinstance(scalefactor, int) else float
    if isinstance(inval, (float, int)):
        print("Inval is numeric:", inval)
        outval = scalefactor*inval if (scalefactor is not None and (inval is not None or inval < sf_lim)) else inval
        print("Outval is:", outval)
        return converter(outval) if converter else outval
    if isinstance(inval, string_types):
        if ', ' in inval:
            # Maybe the user provided inval as a string of values: "left, top, right, lower"
            inval = [item.strip() for item in inval.split(', ')]
            return ensure_numeric(inval, scalefactor, sf_lim, converter)
        outval = float(inval.strip('%'))/100 if '%' in inval else float(inval)
        # Apply scalefactor:
        print("Here")
        if scalefactor is not None and (sf_lim is None or (outval < sf_lim or '%' in inval)):
            print("Applying scalefactor to outval: %s*%s" % (scalefactor, outval))
            outval = scalefactor*outval
        return converter(outval) if converter else outval
    else:
        # We might have a list/tuple:
        try:
            if isinstance(scalefactor, (list, tuple)):
                return [ensure_numeric(item, sf, sf_lim, converter) for item, sf in zip(inval, scalefactor)]
            else:
                return [ensure_numeric(item, scalefactor, sf_lim, converter) for item in inval]
        except TypeError:
            logger.warning("Value '%s' not (float, int) and not string_type and not iterable, returning as-is.", inval)
            return inval


def get_cadnano_canvas_size(part, margins):
    """
    return (xsize, ysize)
    margins = [left, top, right, bottom]
    """
    #use part.maxBaseIdx() to x-size and part.numberOfVirtualHelices() for y-size.
    ysize = (2 * part.numberOfVirtualHelices()) + (2.5 * (part.numberOfVirtualHelices()-1))
    xsize = part.maxBaseIdx() - part.minBaseIdx()
    if margins:
        ysize += margins[1] + margins[3]
        xsize += margins[0] + margins[2]
    return (xsize, ysize)

def draw_strand_TMs(part, svgfilename, params, **kwargs):
    """
    Sequence have been applied at this point.
    """

    args = {} if params is None else params.copy()
    args.update(kwargs)

    ## Get oligos:
    if args.get("calculate_select"):
        oligos = get_oligo_criteria_list(args["calculate_select"])
    else:
        # Select all staple oligos:
        oligos = [oligo for oligo in part.oligos() if oligo.isStaple()]

    ## Prepare svg canvas: (lifted from gelutils.gelannotator module)
    # 72pt = 1 in, http://www.w3.org/TR/SVG11/coords.html#Units
    # A nucleotide is represented by a square. Let's define this as having size 1 ln x 1 ln.
    # Between the helices, there is 2.5 ln. So from the top of 1 double helix to the next, there is
    # (2 x 1 ln) + 2.5 ln = 4.5 ln.
    # The scaffold is drawn on top on even helices and at the bottom on un-even helices.
    # For all helices, if the strand is drawn left-to-right, it also is drawn on top,
    # while if drawn right-to-left, it is always drawn at the bottom.
    # See also cadnano\gui\views\pathview\pathstyles.py
    ln = args.get("cadnano_svg_length", 12)
    ln_unit = args.get("cadnano_svg_unit", "pt" )
    def unit(value):
        return str(value)+ln_unit
    svgargs = dict(helix_radius=ln, dbh_vdistance=2.5*ln, helix_bp_pitch=ln,
                   canvas_size=None, svgoffset=None,
                   background=None, embed=None,
                   margins=[0, 1, 0, 1], # left, top, right, bottom - in units of ln.
                   tmfmt="{TM:0.1f} C", textrotation=0,
                   fontsize=ln, fontfamily='sans-serif', fontweight='bold')
    svgargs.update({k: v for k, v in args.items() if v is not None})
    # svgargs.update({k: v for k, v in kwargs.items() if v is not None})

    # Create svg document:
    dwg = svgwrite.Drawing(svgfilename, profile='tiny') #, **size)      # size can apparently not be specified here
    # set cadnano canvas size:
    canvas_size = {k: v*ln #unit(v)
                   for k, v in zip(("width", "height"),
                                   svgargs.get("canvas_size") or get_cadnano_canvas_size(part, svgargs["margins"]))}
    dwg.attribs.update(canvas_size)

    # Add png background
    pngfile = svgargs.get("pngfile")
    if pngfile:
        pngfp_wo_ext, pngext = os.path.splitext(pngfile)
        g1 = dwg.add(dwg.g(id='Gel'))   # elements group with gel file
        if args.get('embed', True):
            filedata = open(pngfile, 'rb').read()
            # when you DECODE, the length of the base64 encoded data should be a multiple of 4.
            #print "len(filedata):", len(filedata)
            datab64 = base64.encodestring(filedata)
            # See http://www.askapache.com/online-tools/base64-image-converter/ for info:
            mimebyext = {'.jpg' : 'image/jpeg',
                         '.jpeg': 'image/jpeg',
                         '.png' : 'image/png'}
            mimetype = mimebyext[pngext]
            logger.debug("Embedding data from %s into svg file.", pngfile)
            imghref = "data:"+mimetype+";base64,"+datab64.decode()
        else:
            imghref = os.path.relpath(pngfile, start=os.path.dirname(svgfilename))
            logger.debug("Linking to png file %s in svg file:", imghref)
        try:
            pngimage = Image.open(pngfile)
            # image size, c.f. http://stackoverflow.com/questions/15800704/python-get-image-size-without-loading-image-into-memory
            imgwidth, imgheight = pngimage.size
            pngimage.fp.close()
        except NameError:
            imgwidth, imgheight = get_image_size(pngfile)
        # Using size in percentage doesn't work...
        # If excluded they default to 0, and if either is 0 then image is not rendered.
        # However, maybe you should use SVG CSS instead? That might also be better to apply document-wide stuf
        # such as font-size, etc.
        # http://svgwrite.readthedocs.org/en/latest/classes/style.html
        # http://stackoverflow.com/questions/17127083/python-svgwrite-and-font-styles-sizes
        # http://www.w3.org/TR/SVG/styling.html#StyleElementExample
        # http://www.w3.org/TR/SVG/struct.html#ImageElement
        # https://css-tricks.com/using-svg/
        # https://css-tricks.com/scale-svg/
        # http://www.opera.com/docs/specs/presto25/svg/cssproperties/
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/image
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/SVG_Image_Tag
        # https://developer.mozilla.org/en-US/docs/Web/CSS/Scaling_of_SVG_backgrounds
        print("png_scale=%s, sf=%s" % (args.get('png_scale'), ""))
        print("imgwidth, imgheight:", imgwidth, imgheight)
        imgwidth, imgheight = ensure_numeric((imgwidth, imgheight), scalefactor=args.get('png_scale'), sf_lim=3)
        print("imgwidth, imgheight:", imgwidth, imgheight)
        x, y = args['png_offset'] if args.get('png_offset') else (0, 0)
        img = g1.add(dwg.image(imghref, x=x, y=y, width=imgwidth, height=imgheight))
        # Using x, y image attributes is a bit more elegant than a transform
        #if args.get('png_offset'):
        #    img.translate(tx=args['png_offset'][0], ty=args['png_offset'][1])

    ## Create SVG group for TM annotations:
    tmgroup = dwg.add(dwg.g(id='Annotations'))   # Make annotations group

    if svgargs.get("margins") is None:
        leftmargin = topmargin = 0
    else:
        topmargin = svgargs["margins"][1]
        leftmargin = svgargs["margins"][0]

    # Add TMs:
    for oligo in oligos:
        for strand in oligo.strand5p().generator3pStrand():
            # seq = strand.sequence() # primitive way, assuming full complementarity:
            hyb_regions = getstrandhybridizationregions(strand)
            startIdx = strand.idxs()[0]   # strand._base_idx_low
            hyb_seqs = (strand.sequence()[lowIdx-startIdx:highIdx-startIdx+1] for lowIdx, highIdx in hyb_regions)
            hyb_TMs = [Tm_NN(seq, **kwargs) for seq in hyb_seqs]
            for hyb_idxs, TM in zip(hyb_regions, hyb_TMs):
                text = tmgroup.add(dwg.text(svgargs['tmfmt'].format(TM=TM)))
                # Position:  (x-axis is left-to-right, y-axis is up-to-down.)
                xpos = (sum(hyb_idxs)/len(hyb_idxs) + leftmargin) * ln
                #print("xpos = {}/{} + {} = {}  (TM={:.01f})".format(sum(hyb_idxs), len(hyb_idxs), leftmargin, xpos, TM))
                # if not strand.isDrawn5to3() (left-to-right), then it is on the bottom strand:
                # this uses strand.virtualHelix().isEvenParity and strand.strandSet().isScaffold()
                ypos = ln * (topmargin
                             + strand.virtualHelix().number() * 2.5 # the sum of inter-helical distances
                             + strand.virtualHelix().number() * 2.0 # the sum of helical widths (heights)
                             + 1.5*(1 - 2*strand.isDrawn5to3()))      # Offset for above or below helix
                #print("ypos = {} + {} + {} + {} = {}".format(topmargin,
                #                                        strand.virtualHelix().number() * 2.5,
                #                                        strand.virtualHelix().number() * 2.0,
                #                                        2*(1 - 2*strand.isDrawn5to3()),
                #                                        ypos))
                # Transforms must be unit-less:
                text.translate(tx=xpos, ty=ypos)
                # Other:
                if svgargs['textrotation']:
                    text.rotate(svgargs['textrotation']) # rotate(self, angle, center=None)
                # some svg attributes uses dashes, but here we use args without dashes, e.g. fontsize not font-size
                for att in ('font-size', 'font-family', 'font-weight'):
                    argkey = att.replace('-', '')
                    if svgargs[argkey]:
                        text.attribs[att] = svgargs[argkey]
    return dwg






def main(argv=None):
    logging.basicConfig(level=10)
    args = process_args(None, argv)
    if args['profile']:
        import cProfile
        cProfile.runctx('calculate_rotation_scores(args)', globals(), locals(), filename=args['profile_outputfn'])
    if args['print_profile']:
        print("\n\n=========== Profile statistics ===========\n")
        from pstats import Stats
        s = Stats(args['profile_outputfn'])
        print("Cumulative Time Top 20:")
        s.sort_stats('cumulative').print_stats(20)
        print("\nInternal Time Top 40:")
        s.sort_stats('time').print_stats(40)
        return


    seqs = load_seq(args)

    #
    for cadnano_file in args["cadnano_files"]:
        print("\nDrawing strand melting temperatures for cadnano file", cadnano_file)
        design = os.path.splitext(os.path.basename(cadnano_file))[0]
        svg_outputfn = args["svg_filename"].format(design=design,
                                                   cadnano_file=cadnano_file,
                                                   seqfile=args["seqfile"])
        # 1. Load design and apply sequence:
        print(" - Loading design:", design)
        doc = load_doc_from_file(cadnano_file)
        print(cadnano_file, "loaded!")
        part = get_part(doc)
        apply_sequences(part, seqs, offset=args.get("offset")) # global offset
        dwg = draw_strand_TMs(part, svg_outputfn, args)
        dwg.save()
        logger.info("Annotated gel saved to file: %s", dwg.filename)
        if args["openwebbrowser"]:
            webbrowser.open(dwg.filename)




    doc = load_json_or_yaml


if __name__ == '__main__':
    main()
