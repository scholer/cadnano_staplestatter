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
Main plugin module with StaplestatterHandler class.

This module and StaplestatterHandler connects the generic
data processing/plotting logic of staplestatter.py
with the cadnano data extraction logic in cadnanoreader.py

Updating the mainwindow's statusbar:
    self.win.statusBar().showMessage(statusString)


"""

from __future__ import absolute_import, print_function
import os

# Cadnano imports:
import cadnano
from cadnano import util

try:
    # Cadnano2-pyqt5 and Cadnano2.5-legacy:
    from cadnano import util
    from PyQt5.QtGui import QIcon, QPixmap
    from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QAction
    from PyQt5.QtCore import Qt, QSettings, QDir, QUrl
except ImportError:
    # Cadnano2:
    import util
    util.qtWrapImport('QtGui', globals(), ['QIcon', 'QPixmap', 'QAction'])
    util.qtWrapImport('QtGui', globals(), ['QDialog', 'QDialogButtonBox', 'QFileDialog'])
    util.qtWrapImport('QtCore', globals(), ['Qt', 'QString', 'QSettings', 'QDir', 'QUrl'])


# Staplestatter imports:
from .ui import StaplestatterUiDialog   # logic is handled by ui/__init__.py
from .staplestatter import staplestatter
from .staplestatter.staplestatter import process_statspecs_string, savestats
from .staplestatter.cadnanoreader import get_part_alt, get_part


class StaplestatterHandler(object):
    """
    Main plugin object, takes care of showing GUI widget/window
    and connecting events/slots.
    """
    def __init__(self, document, window):
        self.doc, self.win = document, window
        # d().controller().window()
        # self.app = self.win.app()
        icon10 = QIcon()
        icon_path = os.path.join(os.path.dirname(__file__), "res", "staplestatter_icon_32x32.png")
        # print "os.path.isfile(", icon_path, ") : ", os.path.isfile(icon_path)
        icon10.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.menuaction = QAction(window)
        self.menuaction.setIcon(icon10)
        self.menuaction.setText('Staplestatter')
        self.menuaction.setToolTip("Staplestatter plugin provides some quick metrics for your cadnano design.")
        self.menuaction.setObjectName("actionStaplestatter")
        self.menuaction.triggered.connect(self.menuactionSlot)
        try:
            # Cadnano2 API:
            self.win.menuPlugins.addAction(self.menuaction)
            # add to main tool bar
            self.win.topToolBar.insertAction(self.win.actionFiltersLabel, self.menuaction)
            self.win.topToolBar.insertSeparator(self.win.actionFiltersLabel)
        except AttributeError:
            # Cadnano2.5-legacy API:
            self.win.menu_plugins.addAction(self.menuaction)  # Cadnano2.5-legacy
            self.win.selection_toolbar.insertAction(self.win.action_filters_label, self.menuaction)
            self.win.selection_toolbar.insertSeparator(self.win.action_filters_label)

        self.staplestatterDialog = None
        self.settings = QSettings()
        self._fileOpenPath = None
        self._readSettings()
        self._lastResult = None  # dict(figure=fig, scores=allscores)

    def _readSettings(self):
        """ Reads settings.
        Currenly this just loads the path of the last opened file, which is stored as self._fileOpenPath
        """
        self.settings.beginGroup("Staplestatter")
        self._fileOpenPath = self.settings.value("openpath", None)  # QVariant for PyQt4
        try:
            self._fileOpenPath = self._fileOpenPath.toString()
        except AttributeError:
            print("self._fileOpenPath is:", self._fileOpenPath)
        self.settings.endGroup()
        # If there is not a separate "Staplestatter" settings group, use cadnano's "FileSystem" group.
        if not self._fileOpenPath:
            self.settings.beginGroup("FileSystem")
            self._fileOpenPath = self.settings.value("openpath", None)
            try:
                self._fileOpenPath = self._fileOpenPath.toString()
            except AttributeError:
                print("self._fileOpenPath is:", self._fileOpenPath)
            self.settings.endGroup()

    def _writeFileOpenPath(self, path):
        """ Makes sure to save/remember the *directory* path of the last opened file to settings. """
        self._fileOpenPath = path
        self.settings.beginGroup("Staplestatter")
        self.settings.setValue("openpath", path)
        self.settings.endGroup()

    def document(self):
        """ Returns the main document. """
        return cadnano.app().d

    def getDirectiveStr(self, ):
        """ Returns content of the specfile text input field as plain text. """
        # toPlainText --> returns specfileTextEdit.plainText property.
        return str(self.staplestatterDialog.specfileTextEdit.toPlainText())  # Should always work...

    def setDirectiveStr(self, directive):
        """ Sets the content of the specfile text input field. """
        # toPlainText --> returns specfileTextEdit.plainText property.
        # This should work for plain python strings as well as QStrings:
        self.staplestatterDialog.specfileTextEdit.setPlainText(directive)

    def getSpecfilepath(self):
        """ Returns specfilepath from lineedit widget. """
        return str(self.staplestatterDialog.specfilepathLineEdit.text())

    def setSpecfilepath(self, filepath):
        """ Sets specfilepath in lineedit widget. """
        self.staplestatterDialog.specfilepathLineEdit.setText(filepath)

    def load_defaults(self):
        """ Load default settings using hard-wired directive file in example_files. """
        uiDia = self.staplestatterDialog
        filepath = os.path.join(os.path.dirname(__file__), "example_files", "statsspec_scratchpad_auto.yml")
        self.loadSpecFromFile(filepath, rememberDir=False)
        filepath = os.path.join(os.path.dirname(__file__), "USAGE.html")
        relpath = os.path.relpath(filepath, os.path.abspath(os.getcwd()))
        print("filepath:", filepath)
        print("relpath:", relpath)
        try:
            # TODO: Swap the 'usage' QPlainTextEdit widget with QTextBrowser and show HTML instead of plain-text.
            # uiDia.usageTextEdit.setPlainText(open(filepath).read())
            uiDia.usageTextEdit.setSource(QUrl(":"+relpath))
        except IOError:
            print("Could not load USAGE file: ", filepath)

    def menuactionSlot(self):
        """Only show the dialog if staple strands exist."""
        print("cadnano_staplestatter.StaplestatterHandler.menuactionSlot() invoked (DEBUG)")
        # part = self.doc.controller().activePart()
        # cadnano2.5 is a little flaky about how to get document parts, so I've created a function to figure this out:
        doc = self.doc
        try:
            print("doc.parts():", doc.parts())
        except AttributeError:
            print("doc.children():", doc.children())  # Works, [<SquarePart 1960>]
        try:
            print("doc.selectedInstance():", doc.selectedInstance())  # Works, cadnano.objectinstance.ObjectInstance
        except AttributeError:
            print("doc.selectedPart():", doc.selectedPart())

        try:
            part = get_part(self.doc)
        except IndexError:
            # This happens if no document/parts have been created or loaded:
            print("You should open a document before you use staplestatter.")
            return
        print("Part:", part)
        if part is None:
            print("You should open a document before you use staplestatter.")
        for o in list(part.oligos()):
            print("Oligo:", o, "(staple)" if o.isStaple() else "(scaf)")
            if o.isStaple():  # is there a staple oligo?
                print("self.staplestatterDialog:", self.staplestatterDialog)
                if self.staplestatterDialog is None:
                    self.staplestatterDialog = StaplestatterDialog(self.win, self)
                    self.make_ui_connections()
                    self.load_defaults()        # Only do this AFTER StaplestatterDialog has been created.
                print("self.staplestatterDialog:", self.staplestatterDialog)
                print(" - invoking self.staplestatterDialog.show() ...")
                self.staplestatterDialog.show()
                return

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
        uiDia.processButton2.clicked.connect(self.processDirectiveSlot)
        uiDia.browsePlotfileButton.clicked.connect(self.savePlotToFileSlot)
        uiDia.browseStatsfileButton.clicked.connect(self.saveStatsToFileSlot)
        uiDia.newSpecfileButton.clicked.connect(self.newSpecfileSlot)
        uiDia.loadSpecfileButton.clicked.connect(self.loadSpecfileSlot)
        uiDia.saveSpecfileButton.clicked.connect(self.saveSpecfileSlot)
        uiDia.saveSpecfileAsButton.clicked.connect(self.saveSpecfileAsSlot)

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
        print("processDirectiveSlot() invoked by pressing processButton.")
        directive = self.getDirectiveStr()
        self._lastResult = staplestatter.process_statspecs_string(directive)

    def savePlotToFileSlot(self):
        """
        savefig(fname, dpi=None, facecolor='w', edgecolor='w', orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1)
        """
        print("savePlotToFileSlot() invoked by pressing browsePlotfileButton.")
        cur = str(self.staplestatterDialog.plotsfileLineEdit.text())
        directory = os.path.dirname(cur) if cur else self._fileOpenPath
        filepath = self.browseForNewOrExistingFile(dialog_title="Save plot as file...",
                                                   filefilter="Graphics file (*.png *.jpg *.pdf)", directory=directory)
        if not filepath:
            print("Filepath is: '%s' - not saving..." % (filepath, ))
            return
        self.staplestatterDialog.plotsfileLineEdit.setText(filepath)
        if self._lastResult:
            self._lastResult['figure'].savefig(filepath)
        else:
            print("No stats yet: self._lastResult: ", self._lastResult)

    def saveStatsToFileSlot(self):
        """ Qt event slot, saves stats to file. """
        print("saveStatsToFileSlot() invoked by pressing browseStatsfileButton.")
        cur = str(self.staplestatterDialog.statsfileLineEdit.text())
        directory = os.path.dirname(cur) if cur else self._fileOpenPath
        filepath = self.browseForNewOrExistingFile(dialog_title="Save stats as file...", directory=directory)
        if not filepath:
            print("Filepath is: '%s' - not saving..." % (filepath, ))
            return
        self.staplestatterDialog.statsfileLineEdit.setText(filepath)
        if self._lastResult:
            staplestatter.savestats(self._lastResult['scores'], filepath)
        else:
            print("No stats yet. Run process and plot once first. self._lastResult: ", self._lastResult)

    def newSpecfileSlot(self):
        """ Qt event slot, creates new specfile. """
        print("loadSpecfileSlot() invoked by pressing loadSpecfileButton.")
        filepath = self.browseForNewOrExistingFile()
        if not filepath:
            print("Filepath is: '%s' - not creating new..." % (filepath, ))
            return
        self.setSpecfilepath(filepath)
        self.setDirectiveStr("")

    def loadSpecfileSlot(self):
        """ Qt event slot, loads a specfile. """
        print("loadSpecfileSlot() invoked by pressing loadSpecfileButton.")
        filepath = self.browseForExistingFile()
        if not filepath:
            print("Filepath is: '%s' - not loading..." % (filepath, ))
            return
        self.loadSpecFromFile(filepath)

    def saveSpecfileSlot(self):
        """ Qt event slot, saves content of spec text input to specfile. """
        print("saveSpecfileSlot() invoked by pressing saveSpecfileButton.")
        self.saveSpecToFile()

    def saveSpecfileAsSlot(self):
        """ Qt event slot, prompts for file with browser and saves content of spec text input to specified file. """
        print("browseSpecfileSlot() invoked by pressing browseSpecfileButton.")
        filepath = self.browseForNewOrExistingFile()
        if not filepath:
            print("Filepath is: '%s' - not saving..." % (filepath, ))
            return
        self.setSpecfilepath(filepath)
        self.saveSpecToFile()

    def loadSpecFromFile(self, filepath, rememberDir=True):
        """ Loads specfile from filepath. """
        self.setSpecfilepath(filepath)
        try:
            directivestr = open(filepath).read()
        except IOError:
            print("Could not load spec file: ", filepath)
            return
        self.setDirectiveStr(directivestr)
        if rememberDir:
            self._writeFileOpenPath(os.path.dirname(filepath))

    def saveSpecToFile(self, filepath=None):
        """ Saves content of the directory plainTextEdit to filepath. """
        if filepath is None:
            filepath = self.getSpecfilepath()
        directivestr = self.getDirectiveStr()
        try:
            with open(filepath, 'w') as fd:
                fd.write(directivestr)
        except IOError:
            print("Could not save directive to spec file: ", filepath)

    def browseForExistingFile(
            self, dialog_title="Open staplestatter directive",
            filefilter="YAML data structure (*.yml *.yaml)"
    ):
        """ Opens Qt file dialog and lets the user select an existing file. """
        # QFileDialog.getOpenFileName(<parent>, <str title>, <str directory>, <str "Filter name (glob filters)")
        filepath = QFileDialog.getOpenFileName(self.staplestatterDialog, dialog_title, self._fileOpenPath, filefilter)
        if isinstance(filepath, (tuple, list)):
            filepath = filepath[0]  # PySide returns a two-tuple, where the 2nd item is the filter used.
            print("Filepath: ", filepath)
        return str(filepath)

    def browseForNewOrExistingFile(
            self, dialog_title="Open staplestatter directive",
            filefilter= "YAML data structure (*.yml *.yaml)",
            directory=None):
        """ Opens Qt file dialog and lets the user select a new or existing file. """
        if directory is None:
            directory = self._fileOpenPath
            print("self._fileOpenPath is:", self._fileOpenPath)
        print("directory is:", directory)
        try:
            directory = directory.toString() # In case it is a QVariant for some reason...
        except AttributeError:
            pass
        # QFileDialog.getOpenFileName(<parent>, <str title>, <str directory>, <str "Filter name (glob filters)")
        filepath = QFileDialog.getSaveFileName(self.staplestatterDialog, dialog_title, directory, filefilter)
        if isinstance(filepath, (tuple, list)):
            filepath = filepath[0]  # PySide returns a two-tuple, where the 2nd item is the filter used.
        return str(filepath)


class StaplestatterDialog(QDialog, StaplestatterUiDialog):
    """ Staplestatter dialog window/widget.
    Combines QDialog with the generated StaplestatterUiDialog (created from .ui file).
    """
    def __init__(self, parent, handler):
        QDialog.__init__(self, parent, Qt.Sheet)
        self.setupUi(self)
        self.handler = handler
        # Setting keyboard shortcuts:
        #fb = self.buttonBox.button(QDialogButtonBox.Cancel)
        #fb.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_R ))

    def keyPressEvent(self, e):
        """ Use QDialog parent class to deal with key presses. """
        return QDialog.keyPressEvent(self, e)

    def closeDialog(self):
        """Closes the dialog window."""
        self.close()

    def accept(self):
        """ Does nothing. """
        pass
