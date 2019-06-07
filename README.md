







Installation (cadnano 2.5):
----------------------------



OBS: There are multiple versions of staplestatter, depending on the version of cadnano that you intend to use.
The main version of staplestatter was written for a specific version of cadnano2.5 from around 2015.
I belive this can be found under the `devlegacy` tag, https://github.com/cadnano/cadnano2.5/tree/devlegacy.

The instructions below should help you install and use this plugin (as of June 2019).


**First**, I recommend setting everything up in a *dedicated conda environment*. To do this:

1. Install Anaconda or Miniconda, if you haven't already. 
    * Anaconda comes with a lot of "ready-to-use" stuff, and is thus a much bigger install. Can be downloaded from https://www.anaconda.com/distribution/.
    * Miniconda is a smaller, more bare-bones distribution. Can be downloaded from https://docs.conda.io/en/latest/miniconda.html.

2. Create a new conda environment (tested with pyqt-5.9.2):

    * `conda create -n cadnano25-legacy python=3 pyqt=5`

3. Activate the dedicated environment. You must do this every time you open a new terminal to work on cadnano:

    * `conda activate cadnano25-legacy`


**Second**, install the "devlegacy" versoin of cadnano2.5:

1. Clone the cadnano2.5 repository to a suitable location and check out the `devlegacy` version:

    * Change directory to a suitable location, e.g. `cd %USERPROFILE%\Dev`.
    * Clone the cadnano2 repository: `git clone git@github.com:scholer/cadnano2.5.git cadnano25-legacy`.
    * Go into the `cadnano25-legacy` directory: `cd cadnano25-legacy`.
    * Important: Check out the `devlegacy` version: `git checkout devlegacy`

2. Unfortunately, the rather old `devlegacy` of cadnano 2.5 didn't support traditional python setup installation. 
    So, the only way to "install cadnano" is to add the `cadnano25-legacy` folder to your path (environment variable).
    You need to do this every time you open a new terminal.
    * `set PATH=%USERPROFILE%\Dev\cadnano25-legacy;%PATH%`

3. Check that your cadnano installation works:
    * Make sure you are in the cadnano2.5 root directory (e.g. `cd cd %USERPROFILE%\Dev\cadnano25-legacy`).
    * Run `python bin/main.py`
    * Open an origami JSON file, or create a new design from scratch.
        * OBS: New versions of cadnano2 will sometimes refuse to open old cadnano JSON files, 
            yielding a ValueError or similar in the terminal stack trace 
            (look for a line including `json\decoder.py` file and the words `decode` or `raw_decode`)
            * This is not a bug, but a feature: Cadnano1 did not actually save in proper JSON format, 
                so the resulting files are actually not valid JSON files. 
                They would still open in early versions of Cadnano2, because instead of actually using 
                the proper json library, the decoder would just use `eval()` to load the file.
                This worked, because JSON format is very similar to Python dicts and lists, 
                but it is obviously a really unsafe way to load files that may come from an unknown source.
            * To convert old cadnano1 json files to new cadnano2 files, use the following python command:
                * `python -c "import json; json.dump(eval(open('<cadnano1-file.json>').read()), open('<cadnano2-file.json>', 'w'))"`
                * Example: 
                    `python -c "import json; json.dump(eval(open('150526_cc6hb_v0_mod.json').read()), open('150526_cc6hb_v0_mod-fixed.json', 'w'))"`




**Third**, download and install staplestatter:

1. Clone the cadnano2 repository: `git clone git@github.com:scholer/staplestatter.git`.

2. If you want to install staplestatter as a "cadnano plugin", 
    you must either move the staplestatter folder to the `plugins` folder inside the `cadnano25-legacy` folder, 
    or alternatively make a directory symlink: 
    1. Go to plugins directory: `cd cadnano25-legacy\cadnano\gui\plugins`
    2. Create symbolic link: `mklink /D staplestatter %USERPROFILE%\Dev\staplestatter`
    3. Traverse the symbolic link: `dir staplestatter`  - make sure you don't get any errors.

3. "Install" staplestatter by adding it to your PATH environment variable. 
    (Again, the old Cadnano2 system didn't really use or support traditional python setup.py installation; this has changed in later versions of cadnano.) 





Installing staplestatter for the old cadnano2 (not 2.5):
---------------------------------------------------------




**First**, I recommend setting everything up in a **dedicated conda environment**. To do this:

1. Install Anaconda or Miniconda, if you haven't already. 
    * Anaconda comes with a lot of "ready-to-use" stuff, and is thus a much bigger install. Can be downloaded from https://www.anaconda.com/distribution/.
    * Miniconda is a smaller, more bare-bones distribution. Can be downloaded from https://docs.conda.io/en/latest/miniconda.html.

2. Create a new conda environment:

    * `conda create -n cadnano2-py27-pyqt4 python=2 pyqt=4 matplotlib biopython`

3. Activate the dedicated environment. You must do this every time you open a new terminal to work on cadnano:

    * `conda activate cadnano2-py27-pyqt4`


**Second, install cadnano2:**

1. Clone the cadnano2 repository to a suitable location:

    * Change directory to a suitable location, e.g. `cd %USERPROFILE%\Dev`.
    * Clone the cadnano2 repository: `git clone git@github.com:scholer/cadnano2.git`.

2. Unfortunately, the rather old "cadnano 2" project didn't support traditional python setup installation. 
    So, the only way to "install cadnano" is to add the cadnano2 folder to your path (environment variable).
    You need to do this every time you open a new terminal.
    * `set PATH=%USERPROFILE%\Dev\cadnano2;%PATH%`

3. Check that your cadnano installation works:
    * `cd cadnano2`
    * `python main.py`
    * Open an origami JSON file, or create a new design from scratch.
        * OBS: New versions of cadnano2 will sometimes refuse to open old cadnano JSON files, 
            yielding a ValueError or similar in the terminal stack trace 
            (look for a line including `json\decoder.py` file and the words `decode` or `raw_decode`)
            * This is not a bug, but a feature: Cadnano1 did not actually save in proper JSON format, 
                so the resulting files are actually not valid JSON files. 
                They would still open in early versions of Cadnano2, because instead of actually using 
                the proper json library, the decoder would just use `eval()` to load the file.
                This worked, because JSON format is very similar to Python dicts and lists, 
                but it is obviously a really unsafe way to load files that may come from an unknown source.
            * To convert old cadnano1 json files to new cadnano2 files, use the following python command:
                * `python -c "import json; json.dump(eval(open('<cadnano1-file.json>').read()), open('<cadnano2-file.json>', 'w'))"`
                * Example: 
                    `python -c "import json; json.dump(eval(open('150526_cc6hb_v0_mod.json').read()), open('150526_cc6hb_v0_mod-fixed.json', 'w'))"`




**Third, download and install staplestatter:**

1. Clone the cadnano2 repository: `git clone git@github.com:scholer/staplestatter.git`.

2. If you want to install staplestatter as a "cadnano plugin", 
    you must **either** move the staplestatter folder to the `plugins` folder inside the `cadnano2` folder, 
    **or alternatively** make a directory symlink:
    (on Windows, this currently requires either being in an elevated admin command prompt, 
    or having your user added to the 'Create symbolic link' group policy).
    1. Go to plugins directory: `cd cadnano2\plugins`
    2. Create symbolic link: `mklink /D staplestatter %USERPROFILE%\Dev\staplestatter`
    3. Traverse the symbolic link: `dir staplestatter`  - make sure you don't get any errors.

<!--
3. "Install" staplestatter by adding it to your PATH environment variable. 
    (Again, the old Cadnano2 system didn't really use or support traditional python setup.py installation; 
    this has changed in later versions of cadnano.) 
-->


**Fourth, check that staplestatter works as cadnano plugin:**

* See "Using staplestatter as cadnano plugin" below.




Using staplestatter as cadnano plugin:
---------------------------------------


1. Open cadnano, and load a cadnano design.
    * It is optimal to open cadnano from the command line, 
        because we use the command line to print useful debug information.
    * Go to the cadnano2 directory: `cd %USERPROFILE%\Dev\cadnano2`.
    * Make sure you have activated the cadnano2 environment: `conda activate cadnano2-py27-pyqt4`
    * Launch cadnano2: `python main.py`
    * Load an existing cadnano design (`.json` file), or create a new one.

2. Press the 'Staplestatter' toolbar icon. 

3. A default configuration should be automatically loaded.
    Go ahead and simply press the "Process and plot!" button.
   (There is currently an issue with cadnano that may reqire you to press the button twice on the first run).

4. You should see a figure with three plots, showing three types of statistics:

5. By default, staplestatter only considers the length of each duplex hybridization. 
    However, not all duplexes have the same hybridization energy; 
    GC-rich duplexes are obviously more stable than AT-rich duplexes.
    If you have the `biopython` package installed, 
    you can perform statistics using actual duplex melting temperatures (TM), 
    rather than just duplex length.
    To use duplex TM values, rather than duplex lengths, locate the file `statsspec_scratchpad_TM.yml`
    and load it by going to the "Specify plots" tab in the Staplestatter dialog window inside cadnano,
    and pressing the "Load..." button. 
    (Please make sure you are not trying to load a *cadnano `.json`* file. 
    The open file dialog should say "Open staplestatter directive", and filter so you only see YAML (.yml/.yaml) files.)
    You can find these predefined staplestatter directives inside the `example_files` folder 
    within the staplestatter folder.
    After loading the `statsspec_scratchpad_TM.yml` directive, press "Process and plot!" again.

6. 




Appendix: Cadnano versions and repositories, overview:
---------------------------------------------------------



### Cadnano2 repositories:

* https://github.com/cadnano/cadnano2 - The most "official" cadnano2 repository.
* https://github.com/sdouglas/cadnano2 - Shawn & Nick's original cadnano2 repository. Has been moved to github.com/cadnano.
* https://github.com/scholer/cadnano2 - Rasmus Scholer's cadnano2 repository. Contains two distinct branches, 
    * `pyside_support`, which implements PySide support in cadnano2, and
    * `separate_api`, which exposes the cadnano internals as a convenient API, which works nicely together with the [cadnano_console](https://github.com/scholer/cadnano_console) cadnano plugin (it gives you a python console that you can use to build and manipulate your cadnano design).


### Cadnano2, using Python3 and PyQt5: 

* https://github.com/douglaslab/cadnano2 - PyQt5 port of cadnano2 (using python 3, I think). Is also a cleaned-out version of the repository to remove the unfortunate installer commits.
* https://github.com/scholer/cadnano2-pyqt5 - Rasmus Scholer's fork of douglaslab's PyQt5 port of cadnano2.


### Cadnano2.5 repositories:

Cadnano2.5 is written for python3 and uses pyqt5 instead of pyqt4.

Cadnano2.5 repositories: 

* https://github.com/cadnano/cadnano2.5 - The most "official" cadnano2.5 repository.
* https://github.com/douglaslab/cadnano2.5 - Fork?
* https://github.com/scholer/cadnano2.5 - Rasmus Scholer's cadnano2.5 repository.

Cadnano2.5 branches and tags:

* `devlegacy` is used to mark the "old" 2.5 version from ~2015-2016.
    * This 2.5 `devlegacy` version does not have a `setup.py`, and is expected to be launched in a similar way as cadnano2, 
        i.e. by changing to the cadnano root directory and executing `python bin/main.py`.
        Newer versions (since August 2016), which uses `setup.py` with entry_points to create executables.
    * The 2.5 `devlegacy` version has plugins in `cadnano/gui/plugins` directory. 
        * The `plugins` folder was removed on Dec 21 2017, commit 47387724943749d93af1132dfeb2a15cf8275300. 
        * The `dummyplugin.py` file, that printed `"Plugin loaded, has access to cadnano: %s" % str(cadnano)`,
            was added with commit d08261340c8c6d on 2016-06-14, and also removed on 2017-12-21.
        * The `autobreak` plugin as added on the initial cadnano2.5 commit f6ebcfef8f on 2014-11-13,
            and removed on 2016-07-29 with commit 9de2689832.
        * I'm not sure how or where plugins should be installed in newer versions 
        * See also: https://github.com/cadnano/cadnano2.5/commits/devlegacy/cadnano/gui/plugins
        


OBS: Cadnano2.5 has been under heavy development for at least five years, and has undergone many significant changes.



Git commands:

```
# To see changes to a single file, use gitk:
gitk --follow -- cadnano/gui/plugins/__init__.py
gitk --follow -- cadnano/gui/plugins/dummyplugin.py
gitk --follow -- cadnano/gui/plugins/autobreak/__init__.py

# Alternatively:
git log -p filename
git log --follow -p -- cadnano/gui/plugins/autobreak/__init__.py
git blame filename

```

