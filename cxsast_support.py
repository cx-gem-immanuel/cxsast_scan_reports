import time
from urllib.parse import urljoin

import requests


class CxSASTClient:
    
    def __init__(self, server, username, password):
        self.server = server
        self.token = self._get_rest_token(server, username, password)
    
    def _get_rest_token(self, server, username, password):
        
        rest_endpoint = urljoin(server, '/cxrestapi/auth/identity/connect/token')
        
        data = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': 'sast_rest_api',
            'client_id': 'resource_owner_client',
            'client_secret': '014DF517-39D1-4453-B7B3-9930C563627C'
        }
        
        response = requests.post(rest_endpoint, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return f"Bearer {token_data['access_token']}"
    

    #     curl --request GET \
    #   --url http://localhost/cxrestapi/projects \
    #   --header 'Accept: application/json;v=5.0' \
    #   --header 'Authorization: Bearer 123'
    def get_projects(self):
        projects_endpoint = urljoin(self.server, '/cxrestapi/projects')
        headers = {
            'Accept': 'application/json;v=5.0', 
            'Authorization': self.token
        }
        response = requests.get(projects_endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    
    #     curl --request POST \
    #   --url http://localhost/cxrestapi/reports/sastScan \
    #   --header 'Accept: application/json;v=1.0' \
    #   --header 'Authorization: Bearer 123' \
    #   --header 'Content-Type: application/json;v=1.0' \
    #   --data '{
    #      "reportType": "string", # CSV, PDF, XML
    #      "scanId": -9007199254740991
    #   }'
    def request_scan_report(self, scan_id, report_type):
        
        # Validate case-insensitive report_type is one of PDF, RTF, CSV, XML
        if report_type.lower() not in ['pdf', 'rtf', 'csv', 'xml']:
            raise ValueError("Invalid report type. Please choose from: PDF, RTF, CSV, XML")

        report_endpoint = urljoin(self.server, '/cxrestapi/reports/sastScan')
        headers = {
            'Accept': 'application/json;v=1.0', 
            'Authorization': self.token,
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
    # id
    # 0=Deleted, 1=In Process, 2=Created or 3=Failed
    def get_report_status(self, report_id):
        status_endpoint = urljoin(self.server, f'/cxrestapi/reports/sastScan/{report_id}/status')
        headers = {
            'Accept': 'application/json;v=1.0', 
            'Authorization': self.token
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
    # $response = Invoke-WebRequest -uri "${fullReportURI}" -method get -contenttype 'application/x-www-form-urlencoded' -header $header -OutFile $fileName
    def download_report(self, project_id, project_name, report_id, file_name, combine_reports=False):
        download_endpoint = urljoin(self.server, f'/cxrestapi/reports/sastScan/{report_id}')
        headers = {
            'Accept': 'application/json;v=1.0', 
            'Authorization': self.token
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
        scans_endpoint = urljoin(self.server, '/cxrestapi/sast/scans')
        headers = {
            'Accept': 'application/json;v=5.0', 
            'Authorization': self.token
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
