# elm_team_formation

## INTRODUCTION:

This is a simple code and GUI to create teams for the Experiential Learning Module (ELM) of the Young India Fellowship (2020). This code was born out of necessity, as the new batch will be the first (and hopefully only) YIF batch to begin their fellowship online, and as a result would not be able to get to know their batchmates well enough to form optimum teams with mutually shared interests.

The code works on data provided in a CSV file, a sample template is the file *Biased Data.csv* in the repository. Such a file requires some characeristic features:

1. **A unique identifier per student:** This is used to differentiate the different students, and so *no* duplicates should exist. Beware of studets having the same first names or even full names!

2. **A "preferred team-mate" column:** Each students is given the option to opt for *one* preferred team-mate, however the assumption is that their preferred team-mate has opted for them as well. If this is not satisfied, **the code will still run, but preferred teams are not guaranteed for everyone**. Two additional important points *must* be checked for manually before the code is run:

  * **The preferred team-mate should be indexed by the *same* identifier as the unique identifier mentioned before**. (i.e. don't use, say, the student's email address to be the UID, but have the preferred team-mate to be populated by full-names, for example.) 
  * Also, each pair of teammates will be assumed to have exactly the same preferences. 
  
3. **Up to five preferences by which the teams can be formed:** These could be project preferences, domain choices, etc. They will be given weightages according to their order, so make sure they are entered in the right order on the GUI.


The output file (csv) will be created in the same folder from which the code is run. The GUI allows for the name of the output to be changed, but every output file will have the current date and time appended to this name, in order to avoid overwrites. (For example, if you choose to name the output file "groups", the actual name of the output will be *groups-2020-Aug-09_11-23-17.csv*.)


## RUNNING THE CODE:

The code is originally written on Python 3, and the entire code can be found in the *ELM_Team_Formation_Code.py* file. However, understanding that those most likely to use this code are not particularly comfortable with python, I have created a Windows executable, *ELM_Team_Formation_Code.exe* which can be found in the **dists** folder. You may download this file, as well as the input from *Biased_Data.csv*, and it should run by simply double-clicking it. Normally, you should not need to download anything else. (None of the other files should be necessary, they are mainly there for housekeeping.)

When you run the .exe file, you should see a simple GUI like this which should be quite self-explanatory. If you have any issues with this, please let me know.

![Image of GUI](ELM_Team_Formation_GUI.png)



