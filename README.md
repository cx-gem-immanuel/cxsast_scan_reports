
## Latest Scan Reports

This script generates reports in supported formats from the latest scans of desired projects from Checkmarx CxSAST.
  

## Usage

    python main.py [-h] --server SERVER --username USERNAME --password PASSWORD [--projects PROJECTS] [--report-type {pdf,rtf,csv,xml}] [--combine]

  
Arguments for generating reports.
options:

--help, -h
--server, -s SERVER ***Checkmarx CxSAST URL***
--username, -u USERNAME ***CxSAST username***
--password, -p PASSWORD ***CxSAST password***
--projects, -projects PROJECT_IDS_FILE ***Optional. Text file should contain one project ID per line.***
--report-type, -t [pdf, rtf, csv, xml] ***Optional. Supported report formats. Default is csv.***
--combine, -c ***Optional. Only applies to CSV reports. Combines reports into a single CSV file.***

## Examples

**Generate individual PDF reports from the latest scans for all projects**
python main.py --server https://mycxsast.server --username myuser --password mypass --report-type pdf

**Generate individual PDF reports from the latest scans for a set of project ids from a text file**
python main.py --server https://mycxsast.server --username myuser --password mypass --report-type pdf --projects /path/to/project_ids.txt

**Generate individual PDF reports from the latest scans for a set of project ids from a text file**
python main.py --server https://mycxsast.server --username myuser --password mypass --report-type pdf --projects /path/to/project_ids.txt

**Generate individual CSV reports from the latest scans for all projects**
python main.py --server https://mycxsast.server --username myuser --password mypass 
python main.py --server https://mycxsast.server --username myuser --password mypass --report-type csv

**Generate a single/combined CSV report from the latest scans for all projects**
python main.py --server https://mycxsast.server --username myuser --password mypass --combine
python main.py --server https://mycxsast.server --username myuser --password mypass --report-type csv --combine

**Generate a single/combined CSV report from the latest scans for a set of project ids from a text file**
python main.py --server https://mycxsast.server --username myuser --password mypass --report-type csv --projects /path/to/project_ids.txt --combine
