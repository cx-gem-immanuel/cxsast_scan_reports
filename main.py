# Initialize the CxSAST client
import time

from cxsast_support import CxSASTClient
import argparse

parser = argparse.ArgumentParser(description="Arguments for generating reports.")  

parser.add_argument('--server', '-s', type=str, help='Server URL.', required=True)  
parser.add_argument('--username', '-u', type=str, help='Username.', required=True)  
parser.add_argument('--password', '-p', type=str, help='Password.', required=True)
parser.add_argument('--projects', '-projects', type=str, help='Projects list file.', required=False)
parser.add_argument('--combine', '-c', action='store_true', help='Combine reports', required=False, default=False)


if __name__ == "__main__":
    

    args = parser.parse_args()

    server = args.server
    username = args.username
    password = args.password

    combine_reports = args.combine

    client = CxSASTClient(server, username, password)

    # If a project list file is provided, read the project IDs from the file
    if args.projects:
        with open(args.projects, 'r') as f:
            project_ids = [line.strip() for line in f if line.strip()]
        print(f"Read {len(project_ids)} project IDs from {args.projects}")

    projects = client.get_projects()

    print(f"Total projects from server: {len(projects)}")

    total_projects = len(project_ids) if args.projects else len(projects)

    report_type = 'csv'
    
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

