
## Latest Scan Reports

This script generates reports in supported formats from the latest scans of desired projects from Checkmarx CxSAST.
  

## Usage

    python main.py [-h] --server SERVER --username USERNAME --password PASSWORD [--projects PROJECTS] [--report-type {pdf,rtf,csv,xml}] [--combine]

### Parameters
| Parameter | Description |
|--|--|
| --server, -s | Checkmarx CxSAST URL |
| --username, -u | CxSAST username |
| --password, -p | CxSAST password |
| --projects, -projects | Optional. Text file should contain one project ID per line |
| --report-type, -t | Optional. Supported report formats are pdf, rtf, csv, xml. Default is csv |
| --combine, -c | Optional. Only applies to CSV reports. Combines reports into a single CSV file |


## Examples

**Generate individual PDF reports from the latest scans for all projects**
> python main.py --server https://mycxsast.server --username myuser --password mypass --report-type pdf

**Generate individual PDF reports from the latest scans for a set of project ids from a text file**
> python main.py --server https://mycxsast.server --username myuser --password mypass --projects /path/to/project_ids.txt --report-type pdf 

**Generate individual PDF reports from the latest scans for a set of project ids from a text file**
> python main.py --server https://mycxsast.server --username myuser --password mypass --projects /path/to/project_ids.txt --report-type pdf 

**Generate individual CSV reports from the latest scans for all projects**
> python main.py --server https://mycxsast.server --username myuser --password mypass 
> python main.py --server https://mycxsast.server --username myuser --password mypass --report-type csv

**Generate a single/combined CSV report from the latest scans for all projects**
> python main.py --server https://mycxsast.server --username myuser --password mypass --combine
> python main.py --server https://mycxsast.server --username myuser --password mypass --report-type csv --combine

**Generate a single/combined CSV report from the latest scans for a set of project ids from a text file**
> python main.py --server https://mycxsast.server --username myuser --password mypass --projects /path/to/project_ids.txt --report-type csv --combine
