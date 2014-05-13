
import os
import util
qt_available = util.chosenQtFramework or util.find_available_qt_framework()
qt = qt_available.lower()

if qt == 'pyqt4':
    print "Staplestatter plugin: PyQt4 UI widgets should be picked up automatically through the package structure."
elif qt == 'pyside':
    # Setting __path__ like this should make python look in pyside_ui/ for submodules:
    #print "Current __path__: ", __path__
    curdir = __path__[0]
    __path__ = [os.path.join(curdir, 'pyside_ui')] # Look in these folders for modules (relative to the folder of this __init__.py)
    #print "staplestatter.ui __path__ changed to: ", __path__
else:
    print "WARNING, no PyQt4 or PySide! - Cadnano UI will not be available."
