
# Dartmouth 112/317 Rocket Lab GSE codes for shields.

------------------------------------------------------------------------------

## Quick Start Guide

### Core Files
* SHIELD\_Data\_Monitor.py: Monitor realtime shield data without saving to a file. 
* SHIELD\_Data\_Realtime.py: Monitor and Save realtime shield data. (Saves data to .bin file)
* parse\_shield\_fall2022.py: Parse .bin files, save parsed data in Frickle file (.hdf5 format) and make survey plots of shield data. 

### Run Codes
**Get Data From Shield**
1. Find Serial Port
    * On Mac: 
        1. In Command Line Type _ls /dev/cu.\*_ 
        2. In the output of the above, find your <port>.
2. If Using Anaconda, Check in Correct Python Environment
3. Run Realtime Parser Code
    * Quick Check **Without** Saving Data: _python SHIELD_Data_Monitor.py <port>_
    * Full Realtime Monitor and Save Data: _python SHIELD_Data_Realtime.py <port>_
        * Outputs datafile in same directory run from. 

**Parse Shield's .bin File**
1. Open Jupyter Notebooks _jupyter notebook_
2. Run _parse\_shield\_fall2022.ipynb_

------------------------------------------------------------------------------

## Description of Files & Folders
* archived: Holds previous versions of GSE codes.  
    >> * archived\_fall21: Subfolder that holds the versions of parse\_erpabob\_summer2021\_stri.ipynb and parse\_erpabob\_summer2021\_stripped.ipynb prior to the 2021/10/07 update/partial-merge.
    >> * archived\_summer21: Subfolder that holds previous versions of GSE code as well as miscellaneous GSE codes generated prior to 2021/08/05 update.  
* *delamere\_extraCode*: Another archive folder that contains code that was used and may need to be referenced in analysis of the Delamere rocket. [python2] 
* *useful\_pyscripts*: Collection of useful (OPTIONAL) python scripts for various purposes. (See bellow)
* *erpabob\_data\_collection\_summer\_2021.ipynb*: [python2] IPython notebook for collecting data from a shield and saving it to a file. 
* *erpabob\_realtime\_plot\_summer2021\_delamere.py*: [python2] Python script that collects, saves and plots realtime shield data for shields with both original and 10s buffered data in their transmissions (like for Delamere).
    --> *NOTE*: Must specify data transmission speed in code!
* *erpabob\_realtime\_plot\_summer2021\_stripped.py*: [python2] Python script that collects, saves and plots realtime shield data for shields with only current data in their transmissions. 
    --> *NOTE*: Must specify data transmission speed in code!
* *parse\_erpabob\_summer2021\_delamere.ipynb*: [python2] IPython notebook for parsing and plotting data files output from erpabob\_realtime\_plot\_summer2021\_delamere.py OR erpabob\_data\_collection\_summer\_2021.ipynb 
* *parse\_erpabob\_summer2021\_stripped.ipynb*: [python2] IPython notebook for parsing and plotting data files output from erpabob\_realtime\_plot\_summer2021\_stripped.py OR erpabob\_data\_collection\_summer\_2021.ipynb 
* *parse\_erpabob\_fall2021\_delamere.ipynb*: [python2] Same as parse\_erpabob\_summer2021\_delamere.ipynb except for cleaner plotting section. [IPython notebook for parsing and plotting data files output from erpabob\_realtime\_plot\_summer2021\_delamere.py OR erpabob\_data\_collection\_summer\_2021.ipynb] 
* *parse\_erpabob\_fall2021\_stripped.ipynb*: [python2] Same as parse\_erpabob\_summer2021\_delamere.ipynb except for cleaner plotting section. [IPython notebook for parsing and plotting data files output from erpabob\_realtime\_plot\_summer2021\_stripped.py OR erpabob\_data\_collection\_summer\_2021.ipynb]

------------------------------------------------------------------------------
*Files in useful\_pyscripts Folder* 
---------------------------------
* TestHelp\_fun.py: [python2] Collection of functions by Magdalina Moses to help with some of the test data analysis. NOT required for any other file in this repo.
* erpabob\_functions.py: [python2] A start on a collection of functions used often in gse data handling and analysis.  
* make\_pickle\_files.py: [python2] A script intended for batch conversion of shield data files to processed pickle files.
------------------------------------------------------------------------------


------------------------------------------------------------------------------

## Master Branch Update Log**
* Update 2022/11/16: Magda changed notebook parser output file type from pickle to frickle (i.e. hdf5) in order to save hard drive space AND to make the datafiles much more 'portable'/sharable.
* Update 2022/03   : Jules re-wrote realtime data parser/plotter python script and parser notebook to work in python3. As part of this, changed output realtime data files to .bin format. Also, created new python reealtime data monitor to just do quick checks of shield operation without making a file. 
* Update 2021/10/20: Implemented new method of converting pip screen voltage to nA using pip-specific voltage offsets instead of assuming 1V for all pips. Also, added option to set cadance plots' xlims to the plotting section. 
* Update 2021/10/11: Created parse\_erpabob\_fall2021\_delamere.ipynb and parse\_erpabob\_fall2021\_stripped.ipynb. These are identical to the summer2021 versions EXCEPT for the plotting section. The fall2021 plotting section has a more straightforward method of setting x and y axis limits for the plot (based on crex\_gse code). 
* Update 2021/10/07: Merged notebook parser files from zoom\_GPS. This merge corrected errors in some of the parsed time arrays and have better pickle file outputs. Created "archived" folder to hold all archived codes. Added parse\_erpabob\_summer2021\_delamere/stripped.ipynbs to archived/archived\_fall21/ prior to merge. 
* Update 2021/08/24: Added shield numbers to y-axes of realtime IMU plots generated by erpabob\_realtime\_plot\_summer2021\_stripped.py. [Accomplished by merging the version of this file from the crex\_gse branch.]
* Update 2021/08/05: As a lot of changes were made to the GSE code between summer 2020 and summer 2021, we decided to update the master branch. However, as a lot of extra code had been generated by students in the most recent git branches, much of it had to be archived for neatness and simplicity. 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
