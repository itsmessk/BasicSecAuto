# Basic Security Scanner Automation

This Flask-based application performs domain scanning by finding subdomains, checking HTTP status codes, and fetching URLs using various external tools such as **Subfinder**, **Assetfinder**, **Waybackurls**, and **Paramspider**.

## Features

- Finds subdomains using **Subfinder** and **Assetfinder**.
- Checks the HTTP status codes of discovered subdomains (returns status codes 200 and 301).
- Fetches URLs from the **Wayback Machine** and **Paramspider** for valid subdomains.
- Consolidates Paramspider results and stores all data in a JSON file.
- Provides a RESTful API (`/scan`) to trigger the scan with a POST request.

---

## Setup

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/my-flask-app.git
cd my-flask-app
```

### 2. Install the Python Dependencies
Make sure you have Python 3.7 or later installed. Install the necessary Python libraries using:

```bash
pip install -r requirements.txt
```

### 3. Install External Tools
This project relies on several external tools that need to be installed separately:

#### Subfinder
Install Subfinder by following the [installation instructions](https://github.com/projectdiscovery/subfinder) in the GitHub repository.

#### Assetfinder
Install Assetfinder by following the [installation instructions](https://github.com/tomnomnom/assetfinder) in the GitHub repository.

#### Waybackurls
Install Waybackurls by following the [installation instructions](https://github.com/tomnomnom/waybackurls) in the GitHub repository.

#### Paramspider 
Install Paramspider by following the [installation instructions](https://github.com/devanshbatham/ParamSpider) in the GitHub repository via its `setup.py` file by running:


```bash
python setup.py install
```

Ensure that all these tools are in your system's `PATH` so they can be accessed from the command line.

### 4. Run the Flask Application
Start the Flask development server by running:

```bash
python app.py
```

The application will run on [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Usage

### 1. Use the `/scan` API
To initiate a scan, send a POST request to the `/scan` endpoint with a JSON payload containing the domain you wish to scan. Example:

```bash
curl -X POST http://127.0.0.1:5000/scan -H "Content-Type: application/json" -d '{"domain": "example.com"}'
```

### 2. Sample Response

```json
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
```

### 3. Check the Results
The scan data will also be saved in a JSON file named after the domain (e.g., `example.com.json`). This file will contain the following data:

- Subdomains with HTTP status codes
- Wayback Machine URLs
- Paramspider URLs

---

## Tools Used

- **Subfinder**: A subdomain discovery tool (Go-based).
- **Assetfinder**: A tool for finding subdomains (Go-based).
- **Waybackurls**: A tool for fetching URLs from the Wayback Machine (Go-based).
- **Paramspider**: A tool for spidering a domain for URLs (installed via `setup.py`).

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

