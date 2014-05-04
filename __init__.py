# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
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
#
# http://www.opensource.org/licenses/mit-license.php

"""

Package structure:
    cadnano_staplestatter : code to integrate plugin with cadnano's GUI.
    staplestatter : contains non-UI code -- can also be used interactively.
    cadnanoreader : Used to extract data from cadnano objects, typically "cadnano parts" or similar.
    statutils : General statistical functions, deals with simple numerical arrays and is unaware of "cadnano parts", etc.
    plotutils : General plotting functions, also unaware of "cadnano model parts", etc.

"""

try:
    import cadnano
    from cadnano_staplestatter import StaplestatterHandler
except ImportError as e:
    msg = "ImportError: %s - either the cadnano version is too old for this plugin, or you are running without cadnano. This will not be available as a plugin." % (e, )
    print msg
else:
    # If no ImportError:
    def documentWindowWasCreatedSlot(document, win):
        document.staplestatterHandler = StaplestatterHandler(document, win)

    # Initialization: Add handler for existing documents,
    # and make sure a handler is created for new documents in the future.
    for c in cadnano.app().documentControllers:
        doc, win = c.document(), c.window()
        doc.staplestatterHandler = StaplestatterHandler(doc, win) # Maybe this should just be set to the window?
    cadnano.app().documentWindowWasCreatedSignal.connect(documentWindowWasCreatedSlot)
    print "cadnano staplestatter plugin loaded!"