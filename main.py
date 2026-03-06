import time
from cxsast_support import CxSASTClient
import argparse

parser = argparse.ArgumentParser(description="Arguments for generating reports.")  

parser.add_argument('--server', '-s', type=str, help='Server URL.', required=True)  
parser.add_argument('--username', '-u', type=str, help='Username.', required=True)  
parser.add_argument('--password', '-p', type=str, help='Password.', required=True)
parser.add_argument('--projects', '-projects', type=str, help='Projects list file.', required=False)
parser.add_argument('--report-type', '-t', type=lambda s: s.lower(), help='Report type.', required=False, default='csv', choices=['pdf', 'rtf', 'csv', 'xml'])
parser.add_argument('--combine', '-c', action='store_true', help='Combine reports', required=False, default=False)


"""
Generate and retrieve scan reports from a CxSAST server for specified projects.
This script initializes a CxSAST client connection and processes projects to generate
reports based on their latest scans. It supports filtering projects via a file list,
selecting different report formats, and combining multiple reports.
Command-line Arguments:
    --server, -s (str): Server URL for CxSAST instance. Required.
    --username, -u (str): Username for authentication. Required.
    --password, -p (str): Password for authentication. Required.
    --projects (str): Path to file containing project IDs to process (one per line).
                        Optional. If not provided, all projects are processed.
    --report-type, -t (str): Format of the report to generate.
                            Choices: 'pdf', 'rtf', 'csv', 'xml'. Default: 'csv'.
    --combine, -c (bool): Flag to combine multiple reports into a single file.
                            Only applicable when report-type is 'csv'. Default: False.
Behavior:
    - Authenticates with the CxSAST server using provided credentials.
    - Retrieves all projects from the server.
    - If a project list file is provided, filters projects to only those in the file.
    - Generates a report for each project's latest scan in the specified format.
    - Implements rate limiting by sleeping 5 seconds after every 5 requests to avoid
        exceeding the API limit of 100 requests per minute.
    - Ignores the combine flag if report type is not 'csv'.
Returns:
    None
"""
if __name__ == "__main__":
    
    args = parser.parse_args()

    server = args.server
    username = args.username
    password = args.password
    report_type = args.report_type.lower()

    # Combine reports option is only applicable for CSV report type. If report type is not CSV, ignore the combine option.
    combine_reports = args.combine if report_type == 'csv' else False

    client = CxSASTClient(server, username, password)

    # If a project list file is provided, read the project IDs from the file
    if args.projects:
        with open(args.projects, 'r') as f:
            project_ids = [line.strip() for line in f if line.strip()]
        print(f"Read {len(project_ids)} project IDs from {args.projects}")

    projects = client.get_projects()

    print(f"Total projects from server: {len(projects)}")

    total_projects = len(project_ids) if args.projects else len(projects)
    
    # For each project, print the project name and last scan ID, then request a report for the latest scan.
    # API rate-limits is 100 requests per minute. Sleep for 5 second after every 5 requests to avoid hitting the rate limit.
    idx = 1
    for project in projects:
        
        project_id = project['id']
        project_name = project['name']

        # Skip if project ID is not in the provided list (if any)
        if args.projects and str(project_id) not in project_ids:
            # print(f"Skipping project ID {project_id} as it's not in the provided list.")
            continue
        
        print(f"--------------------------- ID: {project_id}, {project_name} :: {idx} of {total_projects} ------------------------------")
        client.get_scan_report(project_id, project_name, report_type, combine_reports)

        # Sleep after every 5 requests to avoid hitting the rate limit
        if (idx) % 5 == 0:
            print("Sleeping for 5 seconds to avoid hitting API rate limit...")
            time.sleep(5)

        idx += 1

