
from __future__ import absolute_import, print_function
import os

# Cadnano imports:
try:
    # Cadnano2: PyQt4 and Python2.
    import util
except ImportError:
    # Cadnano2.5-legacy: PyQt5 and Python3.
    from cadnano import util

try:
    # This might fail on old versions of cadnano which fail to set util.chosenQtFramework properly
    # and does not have a util.find_available_qt_framework function:
    qt_available = util.chosenQtFramework or util.find_available_qt_framework()
except AttributeError as e:
    print("AttributeError '%s' while determining Qt binding framework. "
          "You are probably either using cadnano2.5, or a really old version of cadnano2."
          "PySide support will not be available.")
    qt_available = 'PyQt5'
    qt = qt_available.lower()
    from .staplestatter_ui_pyqt5 import Ui_Dialog as StaplestatterUiDialog
else:
    qt = qt_available.lower()
    if qt[0:4] == 'pyqt':   # only checking the first four letters; qt can be 'pyqt' or pyqt4...
        print("Staplestatter plugin: PyQt4 UI widgets should be picked up automatically through the package structure.")
        from .staplestatter_ui_pyqt4 import Ui_Dialog as StaplestatterUiDialog
    elif qt == 'pyside':
        from .pyside_ui.staplestatter_ui import Ui_Dialog as StaplestatterUiDialog
        # Setting __path__ like this should make python look in pyside_ui/ for submodules:
        #print "Current __path__: ", __path__
        curdir = __path__[0]
        __path__ = [os.path.join(curdir, 'pyside_ui')] # Look in these folders for modules (relative to the folder of this __init__.py)
        #print "staplestatter.ui __path__ changed to: ", __path__
    else:
        print("WARNING, no PyQt4 or PySide! - Cadnano UI will not be available.")
