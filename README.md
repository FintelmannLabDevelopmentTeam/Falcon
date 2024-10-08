# FALCON <img src="icons/falcon.png" align="right" width="100">
### Fully-automated Labeling of CT Anatomy and IV Contrast

Welcome to **FALCON**, a CT data curation tool developed by Philipp Kaess for the Fintelmann Lab at Massachusetts General Hospital, Boston, MA. FALCON provides an efficient, accurate, and fully automated solution for labeling body parts (Head/Neck, Chest, Abdomen) and intravenous (IV) contrast status (Contrast / No Contrast) across CT series within any folder or patient directory.

Body part and IV contrast information is often missing or inaccurate in DICOM headers, and manual labeling can be time-consuming. FALCON solves this problem by generating highly reliable labels based purely on CT image predictions, ensuring critical metadata is available for downstream tasks such as automated diagnosis. By automating this process, FALCON significantly reduces the burden of manual annotation while enhancing data reliability.

For more details about FALCON’s internal structure, or to review comprehensive reports on its performance, please refer to the associated publication [REFERENCE TO PUBLICATION].


## Installation
There are two possible ways to install and run FALCON on your system:

### 1. Standalone .zip installation
We recommend to install FALCON via the release .zip files provided with this repo. This installation is faster and does not require the installation of conda packages or python interpreters. To install FALCON, simply search for the latest release of this github repo (on the right side of the page, under "Releases") and click it. Depending on your operating system, download either the Mac or Windows zip file of FALCON. Once downloaded, move the zip to the desired location in your file system and unpack it. The unpacked folder will contain the FALCON executable, and an "_internal" folder containing all necessary packages and files. To launch FALCON, simply double-click the executable. 

Please note that moving the executable to a new location (without the internal folder) might break the application. However, it is possible to move the entire FALCON folder, or to create a shortcut to the executable.
Unfortunately, this method is currently only supported for Windows and Mac.

### 2. Cloning the repo
Alternatively, it is possible to clone the repo, create a conda environment with all necessary packages, and run main.py. We recommend this method of installation if your operating system runs on neither Windows nor Mac, if you have security concerns regarding the execution of executables, if you wish to modify the source code of FALCON yourself, or if installation method 1 did not work due to e.g. version incompatibilities.

Start by ensuring that you have a recent miniconda/anaconda version on your machine. If not, please install the latest version, e.g. via https://docs.anaconda.com/miniconda/. Then open a terminal where conda is accessible, and execute the following:


1. Clone the repository:
    ```bash
    git clone https://github.com/FintelmannLabDevelopmentTeam/Falcon.git
    cd Falcon
    ```

2. Create and activate a new conda environment. For development and testing, Python 3.9 has been used, so we recommend using this Python version. We provide an environment.yml file for both Windows and Mac, in case you use Mac, please replace "windows" with "mac" in the line below.
    ```bash
    conda env create -f environment_windows.yml  
    conda activate falcon_env
    ```
    Alternatively, you can of course create an empty environment and install the necessary dependencies yourself. In this case, we also recommend to use Python 3.9.

3. Run main.py. You can now launch FALCON with
    ```bash
    python main.py
    ```

## User Guide
ToDo: Fill User Guide


<br>
<br>
<div style="display: flex; align-items: center; justify-content: space-between;">
    <img src="icons/fintelmann_lab.png" align="left" width="200">
    <span style="text-align: center;">&copy; Philipp Kaess, 2024. All rights reserved.</span>
    <img src="icons/harvard_mgh.png" align="right" width="100">
</div>
