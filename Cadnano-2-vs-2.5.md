
This document was created to keep track of important changes between cadnano versions 2 and 2.5,
from the perspective of plugin development.


### DocumentControllers:

Cadnano2.5 is using more "pythonic" attributes:

* Using lower-case with underscore instead of camelCase.
* E.g. Cadnano2 `app.documentController()` has been moved to cadnano2.5 `self.document_controllers = set()`.


### Getting oligos:

* Cadnano2:            ``
* Cadnano2.5-legacy:   `doc.controller().activePart().oligos()`

* See `get_part()` function.
