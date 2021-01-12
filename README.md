
Staplestatter: Tools and library code for statistical analysis and visualization
of staple strands binding within a cadnano DNA origami design.

This python project contains a library package, as well as a cadnano plugin and CLI tools
for analyzing DNA origami designs created with cadnano (`.json` files).

The binding statistics can be used to check that all staple strands are stably bound,
that the staple strands have only one primary binding domain, and check for kinetic traps during annealing.

The analysis can be done either based purely on domain length,
or based on the actual, sequence-dependent melting temperature of the individual domains.


The installation procedure depends on the version of cadnano you would like to use.
Staplestatter currently works with three versions of cadnano:

1. The original cadnano2 version.
2. The new "Python 3 + PyQt 5" version of cadnano 2 (`cadnano2-pyqt5`).
3. The "devlegacy" version of cadnano2.5.
    (Cadnano2.5 has been in development for so long that there are now many different
    and incompatible versions of cadnano2.5).

If you have no preference, I currently suggest you use the `cadnano2-pyqt5` version of cadnano.





Installation for cadnano2-pyqt5:
---------------------------------


**Cadnano2-pyqt5** is currently my favorite version of cadnano:

* Cadnano2-pyqt5 is a clean fork of cadnano2, ported to use Python 3 and PyQt5,
    instead of the very old Python 2 and PyQt 4.
    This adds a lot of benefits and simplicity over the original Cadnano2 version,
    while still being relatively stable and bug-free.

* Since cadnano2.5 is still under heavy development and therefore have a rather unstable API,
    I don't recommend using cadnano2.5, unless you really need some of the features that it provides.



**First**, I recommend setting everything up in a *dedicated conda environment*. To do this:

1. Install Anaconda or Miniconda, if you haven't already.
    * Anaconda comes with a lot of "ready-to-use" stuff, and is thus a much bigger install. Can be downloaded from https://www.anaconda.com/distribution/.
    * Miniconda is a smaller, more bare-bones distribution. Can be downloaded from https://docs.conda.io/en/latest/miniconda.html.

2. Create a new conda environment (tested with pyqt-5.9.2):

    * If using cadnano2-pyqt5:  `conda create -n cadnano2-pyqt5 python=3 pyqt=5 matplotlib pyyaml biopython six`


3. Activate the dedicated environment. You must do this every time you open a new terminal to work on cadnano:

    * `conda activate cadnano2-pyqt5`


**Second**, install cadnano2-pyqt5:

1. Clone the cadnano2-pyqt5 repository to a suitable location:

    * Change directory to a suitable location, e.g. `cd %USERPROFILE%\Dev`.
    * Clone the cadnano2 repository: `git clone git@github.com:scholer/cadnano2-pyqt5.git cadnano2-pyqt5`.
    * Go into the `cadnano2-pyqt5` directory: `cd cadnano2-pyqt5`.

2. Unfortunately, the rather old cadnano 2 doesn't support traditional python setup installation.
    So, the only way to "install cadnano" is either to always run cadnano from within the `cadnano2-pyqt5` folder,
    or add the `cadnano2-pyqt5` folder to your path by updating the environment `PATH` variable using
    `set PATH=%USERPROFILE%\Dev\cadnano2-pyqt5;%PATH%`.
    You need to do this every time you open a new terminal.

3. Check that your cadnano installation works:
    * Make sure you are in the `cadnano2-pyqt5` root directory (e.g. `cd cd %USERPROFILE%\Dev\cadnano2-pyqt5`).
    * Run `python main.py`.
    * Open an origami JSON file, or create a new design from scratch.
        * OBS: New versions of cadnano2 will sometimes refuse to open old cadnano JSON files created with cadnano1.
            If you have problems openin old `.json` files, see the appendix below for a quick way to
            fix the old files so you can open them with later versions of cadnano.
    * Check that everything works, and that you don't get any errors in the command prompt / terminal.



**Third**, download and install staplestatter:

1. Clone the staplestatter repository: `git clone git@github.com:scholer/staplestatter.git`.

2. If you want to install staplestatter as a "cadnano plugin",
    you must either move the staplestatter folder to the `plugins` folder inside the `cadnano2-pyqt5` folder,
    or alternatively make a directory symlink within the cadnano plugins folder pointing to the staplestatter directory:
    1. Go to plugins directory: `cd cadnano2-pyqt5\plugins`
    2. Create symbolic link: `mklink /D staplestatter %USERPROFILE%\Dev\staplestatter`
    3. Traverse the symbolic link: `dir staplestatter`  - make sure you don't get any errors.

3. If you want to use staplestatter as a library, that you can use from any python script (also outside cadnano),
    you can "pip install" staplestatter by going to the staplestatter root directory,
    and typing `pip install -e .`  (remember the space and period after `-e`).

4. If you are installing staplestatter into an existing cadnano environment/installation,
   please make sure to also install the 'pyyaml', 'matplotlib', and 'biopython' python packages into the cadnano environment,
   e.g. with pip or conda:
   * `pip install pyyaml matplotlib`
   * `conda install pyyaml matplotlib`



**Fourth, check that staplestatter works as cadnano plugin:**

* Re-launch cadnano: Close cadnano if it is currently open,
    then in the command prompt / terminal make sure you are in the cadnano root directory,
    and launch cadnano as usuaal with `python main.py`.
* Check the command prompt / terminal to make sure you don't get any ImportErrors or other errors.
* Open an existing cadnano design (`.json` file).
* In the tool bar inside cadnano you should now see a new button that you can use to open staplestatter plugin widget.
    Click it and see that the staplestatter plugin opens as it should.
* You can run a quick test to see if it works by pressing the "Process and plot!" button in the staplestatter window.
* See "Using staplestatter as cadnano plugin" below.

If the staplestatter icon is not available, please check out the "Troubleshooting" section below.





Installation for cadnano2.5 (legacy branch):
----------------------------------------------


The instructions below should help you install and use this plugin (as of June 2019).

OBS: The most recent versions of cadnano2.5 appears to have removed support for plugins (github master branch).
Thus, to use staplestatter with cadnano2.5, we need to use the 'devlegacy' version (tagged version on github).
In general, since cadnano2.5 is still under heavy development and therefore have a rather unstable API,
I don't recommend using cadnano2.5, unless you really need some of the features that it provides.
Instead, I recommend using `cadnano2-pyqt5`, as detailed in the next section (below).


**First**, I recommend setting everything up in a *dedicated conda environment*. To do this:

1. Install Anaconda or Miniconda, if you haven't already.
    * Anaconda comes with a lot of "ready-to-use" stuff, and is thus a much bigger install. Can be downloaded from https://www.anaconda.com/distribution/.
    * Miniconda is a smaller, more bare-bones distribution. Can be downloaded from https://docs.conda.io/en/latest/miniconda.html.

2. Create a new conda environment (tested with pyqt-5.9.2):

    * If using cadnano2.5:      `conda create -n cadnano25-legacy python=3 pyqt=5 matplotlib pyyaml biopython`


3. Activate the dedicated environment. You must do this every time you open a new terminal to work on cadnano:

    * `conda activate cadnano25-legacy`


**Second**, install the "devlegacy" version of cadnano2.5:

1. Clone the cadnano2.5 repository to a suitable location and check out the `devlegacy` version:

    * Change directory to a suitable location, e.g. `cd %USERPROFILE%\Dev`.
    * Clone the cadnano2 repository: `git clone git@github.com:scholer/cadnano2.5.git cadnano25-legacy`.
    * Go into the `cadnano25-legacy` directory: `cd cadnano25-legacy`.
    * Important: Check out the `devlegacy` version: `git checkout devlegacy`

2. Unfortunately, the rather old `devlegacy` of cadnano 2.5 doesn't support traditional python setup installation.
    So, the only way to "install cadnano" is either to always run cadnano from within the `cadnano25-legacy` folder,
    or add the `cadnano25-legacy` folder to your path by updating the environment `PATH` variable using
    `set PATH=%USERPROFILE%\Dev\cadnano25-legacy;%PATH%`.
    You need to do this every time you open a new terminal.

3. Check that your cadnano installation works:
    * Make sure you are in the cadnano2.5 root directory (e.g. `cd cd %USERPROFILE%\Dev\cadnano25-legacy`).
    * Run `python bin/main.py`.
    * Open an origami JSON file, or create a new design from scratch.
        * OBS: New versions of cadnano2 will sometimes refuse to open old cadnano JSON files created with cadnano1.
            If you have problems openin old `.json` files, see the appendix below for a quick way to
            fix the old files so you can open them with later versions of cadnano.
    * Check that everything works, and that you don't get any errors in the command prompt / terminal.



**Third**, download and install staplestatter:

1. Clone the staplestatter repository: `git clone git@github.com:scholer/cadnano_staplestatter.git`.

2. If you want to install staplestatter as a "cadnano plugin",
   you must either move the staplestatter folder to the `plugins` folder inside the `cadnano25-legacy` folder,
   or alternatively make a directory symlink within the cadnano plugins folder pointing to the staplestatter directory:
   1. Go to plugins directory: `cd cadnano25-legacy\cadnano\gui\plugins`
   2. Create symbolic link: `mklink /D staplestatter %USERPROFILE%\Dev\cadnano_staplestatter`
   3. Traverse the symbolic link: `dir staplestatter`  - make sure you don't get any errors.

3. If you want to use staplestatter as a library, that you can use from any python script (also outside cadnano),
   you can "pip install" staplestatter by going to the staplestatter root directory,
   and typing `pip install -e .`  (remember the space and period after `-e`).




**Fourth, check that staplestatter works as cadnano plugin:**

* Re-launch cadnano: Close cadnano if it is currently open,
    then in the command prompt / terminal make sure you are in the cadnano root directory,
    and launch cadnano as usuaal with `python bin/main.py`.
* Check the command prompt / terminal to make sure you don't get any ImportErrors or other errors.
* Open an existing cadnano design (`.json` file).
* In the tool bar inside cadnano you should now see a new button that you can use to open staplestatter plugin widget.
    Click it and see that the staplestatter plugin opens as it should.
* You can run a quick test to see if it works by pressing the "Process and plot!" button in the staplestatter window.
* See "Using staplestatter as cadnano plugin" below.

If the staplestatter icon is not available, please check out the "Troubleshooting" section below.





Installing staplestatter for the old cadnano2:
------------------------------------------------

The old Cadnano2 is probably what you have been using if you have just downloaded cadnano from the cadnano website.
This version of cadnano is now rather old, but still supported for those who need it.
It uses Python 2 and PyQt 4, which are both really old and mostly obsolete.
If you have a choice, I would probably recommend you give `cadnano2-pyqt5` a try first,
and only use the old cadnano2 version if `cadnano2-pyqt5` doesn't work for you.




**First**, I recommend setting everything up in a **dedicated conda environment**. To do this:

1. Install Anaconda or Miniconda, if you haven't already.
    * Anaconda comes with a lot of "ready-to-use" stuff, and is thus a much bigger install. Can be downloaded from https://www.anaconda.com/distribution/.
    * Miniconda is a smaller, more bare-bones distribution. Can be downloaded from https://docs.conda.io/en/latest/miniconda.html.

2. Create a new conda environment:

    * `conda create -n cadnano2-py27-pyqt4 python=2 pyqt=4 pyyaml matplotlib biopython six`

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
        * OBS: New versions of cadnano2 will sometimes refuse to open old cadnano JSON files created with cadnano1.
            If you have problems openin old `.json` files, see the appendix below for a quick way to
            fix the old files so you can open them with later versions of cadnano.
    * Check that everything works, and that you don't get any errors in the command prompt / terminal.




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

3. If you want to use staplestatter as a library, that you can use from any python script (also outside cadnano),
    you can "pip install" staplestatter by going to the staplestatter root directory,
    and typing `pip install -e .`  (remember the space and period after `-e`).




**Fourth, check that staplestatter works as cadnano plugin:**

* Re-launch cadnano: Close cadnano if it is currently open,
    then in the command prompt / terminal make sure you are in the cadnano root directory,
    and launch cadnano as usuaal with `python main.py`.
* Check the command prompt / terminal to make sure you don't get any ImportErrors or other errors.
* Open an existing cadnano design (`.json` file).
* In the tool bar inside cadnano you should now see a new button that you can use to open staplestatter plugin widget.
    Click it and see that the staplestatter plugin opens as it should.
* You can run a quick test to see if it works by pressing the "Process and plot!" button in the staplestatter window.
* See "Using staplestatter as cadnano plugin" below.

If the staplestatter icon is not available, please check out the "Troubleshooting" section below.





Troubleshooting:
----------------


Symptom: After installing staplestatter, when I open caDNAno there is no icon to open up staplestatter?
* Please run cadnano in a terminal (command prompt) using e.g. `python main.py` for cadnano2,
  and check the terminal output for hints.


Symptom: When I run cadnano from the terminal, I see an error, "No module named 'yaml'."
* Please install the 'pyyaml' package into the same python environment you use to run caDNAno.
* If you have created a conda environment for cadnano, please activate it (in your terminal,
  e.g. using `conda activate cadnano2-pyqt5` or whatever your conda environment is named),
  and then install yaml using `conda install pyyaml`.
  (OBS: In conda, the package is called `pyyaml`, not just `yaml`.)


Symptom: When I try to run staplestatter "Process and plot", nothing happens?
* Please run cadnano in a command prompt/termianl (using e.g. `python main.py` for cadnano2),
  and check the terminal output for hints.


Symptom: When I try to run staplestatter "Process and plot", I get an error, "ERROR: matplotlib.pyplot is not available" in the terminal.
* Staplestater needs the 'matplotlib' python package in order to produce plots and graphs.
* Please install 'matplotlib' into the same python environment you use to run cadnano.
    * E.g. for a conda environment: `conda install matplotlib`.



Using the staplestatter cadnano plugin:
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



Using the staplestatter python library:
---------------------------------------

You can use the functions that staplestatter provides in normal python code outside of cadnano.
This can be useful if you have a lot of designs that you would like to plot,
without having to go through the steps of manually opening each design in cadnano.

After "pip installing" the staplestatter library, you can import the staplestatter packages, modules and functions
like you would any other library.
Note that in order to e.g. load a cadnano `.json` file,
you must also have cadnano "installed" and available in your `PATH`,
as outlined above in the second step about installing cadnano.

    import staplestatter

For more examples on how to use the staplestatter library, see the scripts in the `bin/` folder.





Appendix: Fixing old cadnano `.json` files:
---------------------------------------------

OBS: New versions of cadnano2 will sometimes refuse to open old cadnano JSON files,
yielding a ValueError or similar in the terminal stack trace
(look for a line including `json\decoder.py` file and the words `decode` or `raw_decode`)

* This is not a bug, but a feature: Cadnano1 did not actually save in proper JSON format,
        so the resulting files are actually not valid JSON files.
        They would still open in early versions of Cadnano2, because instead of actually using
        the proper json library, the decoder would just use `eval()` to load the file.
        This worked, because JSON format is very similar to Python dicts and lists,
        but it is obviously a really unsafe way to load files that may come from an unknown source.

To convert old cadnano1 json files to new cadnano2 files, use the following python command: `python -c "import json; json.dump(eval(open('<cadnano1-file.json>').read()), open('<cadnano2-file.json>', 'w'))"`
* Example:
        `python -c "import json; json.dump(eval(open('150526_cc6hb_v0_mod.json').read()), open('150526_cc6hb_v0_mod-fixed.json', 'w'))"`





Appendix: Cadnano versions and repositories, overview:
---------------------------------------------------------



### Cadnano2 repositories:

* https://github.com/cadnano/cadnano2 - The most "official" cadnano2 repository.
* https://github.com/sdouglas/cadnano2 - Shawn & Nick's original cadnano2 repository. Has been moved to github.com/cadnano.
* https://github.com/scholer/cadnano2 - Rasmus Scholer's cadnano2 repository. Contains two distinct branches,
    * `pyside_support`, which implements PySide support in cadnano2, and
    * `separate_api`, which exposes the cadnano internals as a convenient API, which works nicely together with the [cadnano_console](https://github.com/scholer/cadnano_console) cadnano plugin (it gives you a python console that you can use to build and manipulate your cadnano design).


### Cadnano2, using Python3 and PyQt5:

* https://github.com/douglaslab/cadnano2 - A fork of cadnano2, updated to use modern Python 3 and PyQt 5. Is also a cleaned-out version of the repository to remove the unfortunate installer commits.
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
        * I'm not sure how or where plugins should be installed in newer versions.
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

