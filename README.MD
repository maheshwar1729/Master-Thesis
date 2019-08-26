# Project Title

 "A Search-Based Approach for Robustness Testing of Business Support Systems Web Applications".

## Introduction

This tool uses multi-objective search-based approach to automatically maximise fault revelation while minimising test sequence length.

This tool simulates a random user actions: It click anywhere in the window, enter random data in forms, or move the mouse over elements that don't expect it. Their goal: triggering errors, or making the application fail.

This practice, also known as Monkey testing or Fuzz testing, is very common in mobile application development. Now that frontend (MV*, d3.js, Backbone.js, Angular.js, etc.) and backend (Node.js) development use persistent JavaScript applications, this technique becomes valuable for web applications.

### Installing (Works Only in Ericsson internal):

clone the repository from https://gerrit.epk.ericsson.se/#/admin/projects/bssf/tools/rm_analytics.

Enter the following commands to complete the Installation

1. cd  rm_analytics/Tpg-GUI-Testing

2. python main.py --url http://example.com --ngen 1 --npop 4 --nchromo 4


The second command clones all the required dependencies and installs automatically.



## Running the tool

Run the following command from the tool directory Tpg-GUI-Testing: sudo python main.py --url https://examples.com --ngen 1 --npop 4 --nchromo 4 --headless 0

Different command line arguments in the command:

1. ngen : To specify Number of Generations for the Algorithm. For example --ngen 1 , --ngen 2 etc

2. npop : To specify Number of populations/evaluations. For example --npop 4 , --npop 8 etc

3. nchromo : nchromo is for specifying the number of chromosomes to use. For example --nchromo 4 etc

4. headless : --headless 0 means "NO" & --headless 1 means "YES" : Run in headless mode


The arguments npop & nchromo must be multiple of 4 for the algorithm to run correctly. It is a requirement from the DEAP Framework that the npop value needs to be in the multiple of 4 . For example 4,8,12,16 etc. So the arguments must be specified as --npop 4 --nchromo 4, --npop 8 --nchromo 8 etc.

main.py automates all the things. It collects all the logs from the Gremlinsmonkey tool and then utils.py uses those logs to perform the evolutionary actions now. There is an option to run the evolutionary directly as we will already have some seed data in genes.csv.

Instead of running main.py just replace the command with python utils.py --url http://example.com --ngen 1 --npop 4 --nchromo 4. This is useful when you are running tests on same web application. If you would like to compare with different web applications then simply use main.py.
..................................................................................
bash script:
To check the CPU load (like RAM, Memory percentage) on this tool, run the following command from the same directory: sudo script.sh
In sample.txt you can see the results of a CPU load on this tool.
Note: run in headless mode to check CPU load.

#############################################################################################################################################

Please refer to README.md in Examples folder if you would like to play with gremlins directly

#############################################################################################################################################


### Bug Reports

After completing the test, the tool generates bug reports representing the type of the bug/errors found during the evaluation. There is also a sqlite3 database for storing the bug reports.

### Requirements

1. Selenium
2. Node v7.9.0
3. Chromedriver for Google chrome
4. Geckodriver for Mozilla firefox
5. npm
6. Python 3.6


To install Node and npm please follow these steps:

sudo apt install npm

1. sudo npm cache clean -f
2. sudo npm install -g n
3. sudo n stable
4. sudo npm cache clean -f
5. sudo npm install -g n
6. sudo n 7.9.0

Please go through the pdf file document for complete understanding of this project: https://github.com/maheshwar1729/Master-Thesis/blob/master/thesis_doc.pdf
