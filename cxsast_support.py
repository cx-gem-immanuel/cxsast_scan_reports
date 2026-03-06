from datetime import datetime, timedelta
import time
from urllib.parse import urljoin

import requests


class CxSASTClient:
    
    def __init__(self, server, username, password):
        """
        Initialize the CxSAST support instance.

        Args:
            server (str): The server URL or address for the CxSAST instance.
            username (str): The username for authentication.
            password (str): The password for authentication.

        Attributes:
            server (str): The server URL or address for the CxSAST instance.
            username (str): The username for authentication.
            password (str): The password for authentication.
            bearer_token (str or None): The bearer token for authenticated requests. Initially None.
            token_expiration (datetime or None): The expiration time of the bearer token. Initially None.
        """
        self.server = server
        self.username = username
        self.password = password
        self.bearer_token = None
        self.token_expiration = None
    
    def get_bearer_token(self):

        if self.bearer_token is not None and datetime.now() < self.token_expiration:
            return self.bearer_token
        else:
            print("Requesting new auth token...")

        rest_endpoint = urljoin(self.server, '/cxrestapi/auth/identity/connect/token')
        
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'scope': 'sast_rest_api',
            'client_id': 'resource_owner_client',
            'client_secret': '014DF517-39D1-4453-B7B3-9930C563627C'
        }
        
        response = requests.post(rest_endpoint, data=data)
        response.raise_for_status()
        
        # If successful, return the access token
        if response.status_code == 200:  
            responseJson = response.json()
            expires_in = responseJson['expires_in']
            now = datetime.now()
            # print(f"Obtained new bearer token. Expires in {expires_in} seconds at {now + timedelta(seconds=expires_in)}")
            # 10 minute expiration buffer
            self.token_expiration = now + timedelta(seconds=expires_in - 600)
            return response.json()['access_token'] 
        else:
            raise Exception(f"Failed to get token: {response.status_code} - {response.text}")
    
    def get_scan_report(self, project_id, project_name, report_type, combine_reports=False):
        last_scan_id = self.get_latest_scan(project_id)
        print(f"Latest scan ID: {last_scan_id}")
        if last_scan_id:
            report_id = self.request_scan_report(last_scan_id, report_type)
            while True:
                status = self.get_report_status(report_id)
                if status == 2:  # Report is ready
                    filename = f"{project_name}_{project_id}_report.{report_type}"
                    self.download_report(project_id, project_name, report_id, filename, combine_reports)
                    print(f"Done. [{filename}]")
                    break
                elif status == 3:  # Report generation failed
                    print("ERROR: Report generation failed.")
                    break
                else:
                    time.sleep(5)

    # curl --request GET \
    #   --url http://localhost/cxrestapi/projects \
    #   --header 'Accept: application/json;v=5.0' \
    #   --header 'Authorization: Bearer 123'
    def get_projects(self):
        """
        Retrieve a list of all projects from the CxSAST server.
        This method authenticates using a bearer token and makes a GET request
        to the CxSAST REST API projects endpoint to retrieve project information.
        Returns:
            dict: A JSON response containing the list of projects and their details.
        Raises:
            requests.exceptions.HTTPError: If the HTTP request returns an error status code.
        """
        
        # Ensure bearer token is available
        self.bearer_token = self.get_bearer_token()

        projects_endpoint = urljoin(self.server, '/cxrestapi/projects')
        headers = {
            'Accept': 'application/json;v=5.0', 
            'Authorization': f'Bearer {self.bearer_token}'
        }
        response = requests.get(projects_endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    
    # curl --request POST \
    #   --url http://localhost/cxrestapi/reports/sastScan \
    #   --header 'Accept: application/json;v=1.0' \
    #   --header 'Authorization: Bearer 123' \
    #   --header 'Content-Type: application/json;v=1.0' \
    #   --data '{
    #      "reportType": "string", # CSV, PDF, XML
    #      "scanId": -9007199254740991
    #   }'
    def request_scan_report(self, scan_id, report_type):
        """
        Request a scan report from the CxSAST server.
        Args:
            scan_id (int): The ID of the scan for which to generate the report.
            report_type (str): The format of the report. Must be one of: PDF, RTF, CSV, or XML.
                              The parameter is case-insensitive.
        Returns:
            str: The report ID that can be used to retrieve the generated report.
        Raises:
            ValueError: If report_type is not one of the supported formats (PDF, RTF, CSV, XML).
            requests.exceptions.HTTPError: If the HTTP request to the server fails.
        Note:
            This method requires a valid bearer token, which is automatically obtained
            via get_bearer_token() if not already available.
        """
        
        # Ensure bearer token is available
        self.bearer_token = self.get_bearer_token()

        # Validate case-insensitive report_type is one of PDF, RTF, CSV, XML
        if report_type.lower() not in ['pdf', 'rtf', 'csv', 'xml']:
            raise ValueError("Invalid report type. Please choose from: PDF, RTF, CSV, XML")

        report_endpoint = urljoin(self.server, '/cxrestapi/reports/sastScan')
        headers = {
            'Accept': 'application/json;v=1.0', 
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json;v=1.0'
        }
        data = {
            "reportType": report_type,
            "scanId": scan_id
        }
        print(f"Requesting {report_type} report for scan ID {scan_id}...")
        response = requests.post(report_endpoint, headers=headers, json=data)
        response.raise_for_status()
        # Response contains reportId
        # Return report id
        reportId = response.json().get('reportId')
        # print(f"Report ID for scan {scan_id}: {reportId}")
        return reportId

    # curl --request GET \
    #   --url http://localhost/cxrestapi/reports/sastScan/{id}/status \
    #   --header 'Accept: application/json;v=1.0' \
    #   --header 'Authorization: Bearer 123'
    # Reponse can be:status
    #   0=Deleted, 1=In Process, 2=Created or 3=Failed
    def get_report_status(self, report_id):
        """
        Retrieve the status of a SAST scan report.
        Args:
            report_id: The unique identifier of the report whose status is to be retrieved.
        Returns:
            The status ID (status['id']) if the report status exists, None otherwise.
        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the status endpoint fails.
        Note:
            - Automatically obtains a bearer token for authentication if not already available.
            - Sends a GET request to the SAST scan status endpoint with proper headers.
        """
        
        # Ensure bearer token is available
        self.bearer_token = self.get_bearer_token()

        status_endpoint = urljoin(self.server, f'/cxrestapi/reports/sastScan/{report_id}/status')
        headers = {
            'Accept': 'application/json;v=1.0', 
            'Authorization': f'Bearer {self.bearer_token}'
        }
        response = requests.get(status_endpoint, headers=headers)
        response.raise_for_status()
        response_str = response.json()
        status = response_str.get('status')
        # print the value in the status
        # print(f"Report ID {report_id}, Current Status: {status['value']}")
        # Return id in the status
        return status['id'] if status else None
    
    # curl --request GET \
    #   --url http://localhost/cxrestapi/reports/sastScan/{id} \
    #   --header 'Accept: application/json;v=1.0' \
    #   --header 'Authorization: Bearer 123'
    def download_report(self, project_id, project_name, report_id, file_name, combine_reports=False):
        """
        Download a SAST scan report from the Checkmarx server and save it locally.
        Args:
            project_id (str): The unique identifier of the project.
            project_name (str): The name of the project.
            report_id (str): The unique identifier of the report to download.
            file_name (str): The name of the file to save the report as (used when combine_reports is False).
            combine_reports (bool, optional): If True, append the report data to a combined report file 
                                             with project_id and project_name as the first two columns.
                                             If False, save the report as a separate file. Defaults to False.
        Returns:
            None
        Raises:
            requests.exceptions.HTTPError: If the HTTP request to download the report fails.
        Side Effects:
            - Retrieves and refreshes the bearer token for authentication.
            - Creates or modifies files in the 'reports/' directory:
              - If combine_reports is True: appends data to 'reports/combined_report.csv'
              - If combine_reports is False: creates/overwrites 'reports/{file_name}'
            - Prints a message to console when appending to combined report.
        """

        # Ensure bearer token is available
        self.bearer_token = self.get_bearer_token()

        download_endpoint = urljoin(self.server, f'/cxrestapi/reports/sastScan/{report_id}')
        headers = {
            'Accept': 'application/json;v=1.0', 
            'Authorization': f'Bearer {self.bearer_token}'
        }
        response = requests.get(download_endpoint, headers=headers)
        response.raise_for_status()

        # response.content contains CSV data.
        # Insert project_id and project_name as the first two columns in the CSV data.
        # If combine_reports is True, append the data to a combined report file. Otherwise, save it as a separate file.
        if combine_reports:
            combined_file_name = f"reports/combined_report.csv"
            with open(combined_file_name, 'a') as f:
                # Write header only if the file is new (i.e., it doesn't exist or is empty)
                if f.tell() == 0:
                    f.write(f"Project ID,Project Name,{response.content.splitlines()[0]}\n")
                for line in response.content.splitlines()[1:]:
                    f.write(f"{project_id},{project_name},{line}\n")
            print(f"Appended report for project {project_name} to {combined_file_name}")
        else:
            with open(f"reports/{file_name}", 'wb') as f:
                f.write(response.content)        

    # curl --request GET \
    #   --url http://localhost/cxrestapi/sast/scans \
    #   --header 'Accept: application/json;v=5.0' \
    #   --header 'Authorization: Bearer 123'
    # With Query Parameters: 
    # last
    # Amount of the latest scans

    # projectId
    # Unique ID of a specific project

    # scanStatus
    # Specifies the scan stage
    # Allowed values:
    # Scanning
    # Finished
    # Canceled
    # Failed
    def get_latest_scan(self, project_id):
        """
        Retrieve the ID of the latest finished scan for a given project.
        This method queries the Checkmarx SAST API to fetch the most recent
        completed scan for the specified project. It uses bearer token
        authentication to authorize the request.
        Args:
            project_id (int or None): The ID of the project to retrieve scans for.
                If None, the latest scan across all projects will be returned.
        Returns:
            str: The ID of the latest finished scan for the project.
        Raises:
            requests.exceptions.HTTPError: If the API request fails or returns
                an error status code.
            IndexError: If no finished scans are found for the project.
            KeyError: If the expected 'id' field is missing from the API response.
        Note:
            The method automatically retrieves a valid bearer token before
            making the request. The API is queried with filters to return
            only finished scans, limited to the most recent one.
        """

        # Ensure bearer token is available
        self.bearer_token = self.get_bearer_token()

        scans_endpoint = urljoin(self.server, '/cxrestapi/sast/scans')
        headers = {
            'Accept': 'application/json;v=5.0', 
            'Authorization': f'Bearer {self.bearer_token}'
        }
        params = {}
        if project_id is not None:
            params['projectId'] = project_id
        params['last'] = 1
        params['scanStatus'] = "Finished"
        
        response = requests.get(scans_endpoint, headers=headers, params=params)
        response.raise_for_status()
        # Return the id of the latest scan for the project
        scans = response.json()
        if scans:
            return scans[0]['id']  # Return the latest scan details