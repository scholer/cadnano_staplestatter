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


Updating the mainwindow's statusbar:
    self.win.statusBar().showMessage(statusString)
"""
import os
import util
import cadnano_api
import cadnano

#try:
#    qt_available = util.chosenQtFramework or util.find_available_qt_framework()
#except AttributeError as e:
#    msg = "AttributeError: %s - this cadnano might be too old for this plugin, aborting load." % (e, )
#    print msg
#    raise ImportError(msg)

#from cadnanonavigator_ui import Ui_Navigator
#if qt_available.lower() == 'pyside':
#    print "Staplestatter: Using PySide."
#    from _ui.cadnano_staplestatter_ui import Ui_Dialog
#else:
#    try:
#        print "Staplestatter: Using PyQt4."
#        from cadnano_staplestatter_ui import Ui_Dialog
#    except ImportError:
#        print "PyQt4 failed, trying PySide..:"
#        try:
#            from pyside_ui.cadnano_staplestatter_ui import Ui_Dialog
#        except ImportError:
#            print "PySide also failed.."
#            raise ImportError("Could not Ui_Dialog from cadnano_staplestatter_ui")

from ui.staplestatter_ui import Ui_Dialog   # logic is handled by ui/__init__.py

util.qtWrapImport('QtGui', globals(), ['QIcon', 'QPixmap', 'QAction'])
util.qtWrapImport('QtGui', globals(), ['QDialog', 'QKeySequence', 'QDialogButtonBox', 'QIntValidator'])
util.qtWrapImport('QtCore', globals(), ['Qt', 'QString'])

import staplestatter



class StaplestatterHandler(object):
    def __init__(self, document, window):
        self.doc, self.win = document, window
        # d().controller().window()
        #self.app = self.win.app()
        icon10 = QIcon()
        icon_path = os.path.join(os.path.dirname(__file__), "res", "staplestatter_icon_32x32.png")
        icon10.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.menuaction = QAction(window)
        #self.menuaction.setIcon(icon10)
        self.menuaction.setText('Staple statter')
        self.menuaction.setToolTip("Use the navigator to quickly navigate around the cadnano views.")
        self.menuaction.setObjectName("actionStaplestatter")
        self.menuaction.triggered.connect(self.menuactionSlot)
        self.win.menuPlugins.addAction(self.menuaction)
        # add to main tool bar
        self.win.topToolBar.insertAction(self.win.actionFiltersLabel, self.menuaction)
        self.win.topToolBar.insertSeparator(self.win.actionFiltersLabel)
        self.staplestatterDialog = None
        #self.use_animation = cadnano_api.ANIMATE_ENABLED_DEFAULT

    def document(self):
        return cadnano.app().d

    def getDirectiveStr(self, ):
        # toPlainText --> returns specfileTextEdit.plainText property.
        return str(self.staplestatterDialog.specfileTextEdit.toPlainText()) # Should always work...
        #try:
        #    directivestr = directivestr.toString()
        #except AttributeError as e:
        #    print "AttributeError while doing directivestr.toString()", e
        #print "Returning directivestr of type: ", type(directivestr)
        #return directivestr

    def setDirectiveStr(self, directive):
        # toPlainText --> returns specfileTextEdit.plainText property.
        self.staplestatterDialog.specfileTextEdit.setPlainText(directive) # should work for plain python strings as well as QStrings.
        #directive = QString(directive)  # Should be ok with pyside, uses QString = str.
        #try:
        #    self.staplestatterDialog.specfileTextEdit.setPlainText(directive)
        #except AttributeError as e:
        #    print "setDirectiveStr Error : ", e


    def load_defaults(self):
        uiDia = self.staplestatterDialog
        filepath = os.path.join(os.path.dirname(__file__), "example_files", "rs_statmethods.yml")
        try:
            defaultdirectivestr = open(filepath).read()
        except IOError:
            print "Could not load default file: ", filepath
        else:
            self.setDirectiveStr(defaultdirectivestr)

        #usageTextEdit
        filepath = os.path.join(os.path.dirname(__file__), "USAGE.txt")
        try:
            uiDia.usageTextEdit.setPlainText(open(filepath).read())
        except IOError:
            print "Could not load USAGE file: ", filepath


    def menuactionSlot(self):
        """Only show the dialog if staple strands exist."""
        print "cadnano_staplestatter.StaplestatterHandler.menuactionSlot() invoked (DEBUG)"
        part = self.doc.controller().activePart()
        if part != None:  # is there a part?
            for o in list(part.oligos()):
                if o.isStaple():  # is there a staple oligo?
                    if self.staplestatterDialog == None:
                        self.staplestatterDialog = StaplestatterDialog(self.win, self)
                        self.make_ui_connections()
                        self.load_defaults()        # Only do this AFTER StaplestatterDialog has been created.
                    self.staplestatterDialog.show()
                    return
        print "You should open a document before you use staplestatter."


    def make_ui_connections(self):
        """
        Note: Using a QtDialog has some disadvantages.
        For instance, it is hard to get correct button focus behavior.
        Dialogs are set up for default-button behavior, which is not really what I want in this widget.
        You can use flat=True to make the button look more like a label.
        """
        uiDia = self.staplestatterDialog
        # You connect a signal to a function/slot.
        uiDia.processButton.clicked.connect(self.processDirectiveSlot)
        uiDia.browsePlotfileButton.clicked.connect(self.browsePlotfileSlot)
        uiDia.browseStatsfileButton.clicked.connect(self.browseStatsfileSlot)
        uiDia.loadSpecFileButton.clicked.connect(self.loadSpecFileSlot)
        uiDia.saveSpecFileButton.clicked.connect(self.saveSpecFileSlot)
        uiDia.browseSpecFileButton.clicked.connect(self.browseSpecFileSlot)



    ### SLOTS ###

    def processDirectiveSlot(self):
        """
        Slots are the callback functions registrered to signals with connect(), e.g.:
            mvh.virtualHelixNumberChangedSignal.connect(vhItem.virtualHelixNumberChangedSlot)
        To emit a signal, one just call <signal>.emit(<args>), e.g.:
            virtualHelixNumberChangedSignal.emit(self, number)  # from model/virtualhelix.py
        With vhItem.virtualHelixNumberChangedSlot connected (registered) to virtualHelixNumberChangedSignal,
        invoking virtualHelixNumberChangedSignal.emit(vhelix, number) would call
            vhItem.virtualHelixNumberChangedSlot(vhelix, number).
        A slots should thus be prepared to consume the same number of arguments as could be passed
        by the signal's emit().
        Typically, a signal would be emitted by its parent, e.g. a button emits a clicked() signal
        when it is pressed.
        """
        print "processDirectiveSlot() invoked by pressing processButton."
        directive = self.getDirectiveStr()
        staplestatter.process_statspecs_string(directive)

    def browsePlotfileSlot(self):
        print "browsePlotfileSlot() invoked by pressing browsePlotfileButton."

    def browseStatsfileSlot(self):
        print "browseStatsfileSlot() invoked by pressing browseStatsfileButton."

    def loadSpecFileSlot(self):
        print "loadSpecFileSlot() invoked by pressing loadSpecFileButton."

    def saveSpecFileSlot(self):
        print "saveSpecFileSlot() invoked by pressing saveSpecFileButton."

    def browseSpecFileSlot(self):
        print "browseSpecFileSlot() invoked by pressing browseSpecFileButton."



class StaplestatterDialog(QDialog, Ui_Dialog):
    def __init__(self, parent, handler):
        QDialog.__init__(self, parent, Qt.Sheet)
        self.setupUi(self)
        self.handler = handler
        # Setting keyboard shortcuts:
        #fb = self.buttonBox.button(QDialogButtonBox.Cancel)
        #fb.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_R ))


    def keyPressEvent(self, e):
        return QDialog.keyPressEvent(self, e)

    def closeDialog(self):
        self.close()

    def accept(self):
        pass
