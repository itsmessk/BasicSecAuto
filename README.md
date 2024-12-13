# Basic Security Scanner Automation

This Flask-based application performs domain scanning by finding subdomains, checking HTTP status codes, and fetching URLs using various external tools such as **Subfinder**, **Assetfinder**, **Waybackurls**, and **Paramspider**.

## Features

- Finds subdomains using **Subfinder** and **Assetfinder**.
- Checks the HTTP status codes of discovered subdomains (returns status codes 200 and 301).
- Fetches URLs from the **Wayback Machine** and **Paramspider** for valid subdomains.
- Consolidates Paramspider results and stores all data in a JSON file.
- Provides a RESTful API (`/scan`) to trigger the scan with a POST request.

## Setup

### 1. Clone the repository

bash
git clone https://github.com/your-username/my-flask-app.git
cd my-flask-app

2. Install the Python dependencies
Make sure you have Python 3.7 or later installed, then install the necessary Python libraries using:

bash
Copy code
pip install -r requirements.txt
3. Install external tools
This project relies on several external tools that need to be installed separately:

Subfinder: Install Subfinder by following the installation instructions in the GitHub repository.

Assetfinder: Install Assetfinder by following the installation instructions in the GitHub repository.

Waybackurls: Install Waybackurls by following the installation instructions in the GitHub repository.

Paramspider: Install Paramspider via setup.py by running:

bash
Copy code
python setup.py install
Ensure that these tools are in your system's PATH so they can be accessed from the command line.

4. Run the Flask application
Start the Flask development server by running:

bash
Copy code
python app.py
This will run the application on http://127.0.0.1:5000.

5. Use the /scan API
To initiate a scan, send a POST request to the /scan endpoint with a JSON payload containing the domain you wish to scan. Example:

bash
Copy code
curl -X POST http://127.0.0.1:5000/scan -H "Content-Type: application/json" -d '{"domain": "example.com"}'
Sample Response:

json
Copy code
{
  "message": "Scan completed",
  "data": {
    "subdomains_with_status": [
      {"subdomain": "sub.example.com", "status_code": 200},
      {"subdomain": "api.example.com", "status_code": 301}
    ],
    "wayback_data": {
      "sub.example.com": ["https://web.archive.org/web/xyz", "https://web.archive.org/web/abc"],
      "api.example.com": ["https://web.archive.org/web/123"]
    },
    "paramspider_data": {
      "sub.example.com": ["https://sub.example.com/page1", "https://sub.example.com/page2"],
      "api.example.com": ["https://api.example.com/endpoint1"]
    }
  }
}
6. Check the results
The scan data will also be saved in a JSON file named after the domain (e.g., example.com.json). This file will contain the following data:

Subdomains with HTTP status codes
Wayback Machine URLs
Paramspider URLs
Tools Used
Subfinder: A subdomain discovery tool (Go-based).
Assetfinder: A tool for finding subdomains (Go-based).
Waybackurls: A tool for fetching URLs from the Wayback Machine (Go-based).
Paramspider: A tool for spidering a domain for URLs (installed as a CLI tool via setup.py).
License
This project is licensed under the MIT License - see the LICENSE file for details.

go
Copy code

With these updates, your `requirements.txt` and `README.md` now correctly reflect the dependenc