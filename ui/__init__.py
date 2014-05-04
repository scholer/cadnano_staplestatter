
import os
import util
qt_available = util.chosenQtFramework or util.find_available_qt_framework()
qt = qt_available.lower()

if qt == 'pyqt4':
    print "PyQt4 UI widgets should be picked up automatically through the package structure."
elif qt == 'pyside':
    # Setting __path__ like this should make python look in pyside_ui/ for submodules:
    __path__ = [os.path.join('ui', 'pyside_ui')]
else:
    print "WARNING, no PyQt4 or PySide! - Cadnano UI will not be available."
