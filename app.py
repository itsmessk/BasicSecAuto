from flask import Flask, jsonify, request
import os
import json
import asyncio
import httpx
import logging
from pathlib import Path

# Initialize Flask application
app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def run_tool_async(command):
    """Run external tools asynchronously using subprocess."""
    logging.info(f"Running command: {' '.join(command)}")
    process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if stderr:
        logging.error(f"Error running {command}: {stderr.decode('utf-8')}")

    logging.info(f"Command {command} completed successfully.")
    return stdout.decode('utf-8').splitlines()

async def find_subdomains(domain):
    """Use subfinder and assetfinder to find subdomains asynchronously."""
    logging.info(f"Finding subdomains for {domain} using subfinder and assetfinder...")
    subfinder_task = run_tool_async(['subfinder', '-d', domain])
    assetfinder_task = run_tool_async(['assetfinder', '--subs-only', domain])
    subfinder_subs, assetfinder_subs = await asyncio.gather(subfinder_task, assetfinder_task)

    # Log subdomains found
    logging.info(f"Subdomains found by subfinder: {len(subfinder_subs)}")
    logging.info(f"Subdomains found by assetfinder: {len(assetfinder_subs)}")

    return list(set(subfinder_subs + assetfinder_subs))

async def check_subdomain_status_async(subdomains):
    """Check HTTP status of subdomains using httpx."""
    logging.info(f"Checking HTTP status for {len(subdomains)} subdomains...")
    async with httpx.AsyncClient(timeout=10, limits=httpx.Limits(max_connections=100)) as client:
        tasks = [client.get(f"http://{subdomain}", follow_redirects=True) for subdomain in subdomains]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log status checks
        for subdomain, result in zip(subdomains, results):
            if isinstance(result, Exception):
                logging.warning(f"Error checking {subdomain}: {result}")
            else:
                logging.info(f"Subdomain {subdomain} returned status code {result.status_code}")

        # Only return subdomains with status code 200 or 301
        return [{"subdomain": subdomains[i], "status_code": result.status_code if not isinstance(result, Exception) else "Error"} 
                for i, result in enumerate(results) if isinstance(result, httpx.Response) and result.status_code in [200, 301]]

async def fetch_urls(subdomains):
    """Fetch URLs from Wayback URLs and Paramspider for validated subdomains."""
    logging.info(f"Fetching URLs from Wayback URLs and Paramspider for {len(subdomains)} subdomains...")
    tasks = []
    for subdomain in subdomains:
        if subdomain['status_code'] in [200, 301]:
            tasks.append(run_tool_async(['waybackurls', subdomain['subdomain']]))
            tasks.append(run_tool_async(['paramspider', '--domain', subdomain['subdomain']]))

    results = await asyncio.gather(*tasks)

    wayback_data = {}
    paramspider_data = {}

    # Log URL fetching process
    for i in range(0, len(results), 2):
        subdomain = subdomains[i//2]['subdomain']
        wayback_data[subdomain] = results[i]
        paramspider_data[subdomain] = results[i+1]
        logging.info(f"Fetched URLs for subdomain {subdomain}: {len(results[i])} from WaybackURLs, {len(results[i+1])} from Paramspider")

    return wayback_data, paramspider_data

def consolidate_paramspider_results(results_dir='results'):
    """Consolidate Paramspider results stored in a directory."""
    logging.info(f"Consolidating Paramspider results from {results_dir}...")
    paramspider_data = {}
    for result_file in Path(results_dir).glob('*.txt'):  # Assuming ParamSpider saves results as .txt files
        subdomain = result_file.stem  # Get the subdomain from the filename
        with result_file.open() as f:
            urls = f.readlines()
        paramspider_data[subdomain] = [url.strip() for url in urls]  # Strip newlines and extra spaces
        logging.info(f"Consolidated {len(urls)} URLs for subdomain {subdomain} from Paramspider.")

    return paramspider_data

def store_in_json(all_data, domain):
    """Store all data in a JSON file named after the domain, including URLs by subdomain."""
    file_path = os.path.join(os.getcwd(), f"{domain}.json")
    logging.info(f"Storing data in {file_path}...")

    try:
        with open(file_path, "w") as file:
            json.dump(all_data, file, indent=4)
        logging.info(f"Data for {domain} has been successfully stored in {file_path}.")
    except Exception as e:
        logging.error(f"Error writing JSON file {file_path}: {e}")

@app.route('/scan', methods=['POST'])
async def scan_domain():
    """API endpoint to scan a domain for subdomains, URLs, and Paramspider results."""
    domain = request.json.get('domain')
    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    logging.info(f"Starting subdomain discovery and data collection for {domain}...")

    # Step 1: Find subdomains
    subdomains = await find_subdomains(domain)
    logging.info(f"Found {len(subdomains)} subdomains.")

    # Step 2: Check subdomain status
    subdomains_with_status = await check_subdomain_status_async(subdomains)

    # Step 3: Format subdomains with status
    formatted_subdomains = [{"subdomain": subdomain["subdomain"], "status_code": subdomain["status_code"]} for subdomain in subdomains_with_status]

    # Step 4: Fetch URLs
    wayback_data, paramspider_data = await fetch_urls(subdomains_with_status)

    # Step 5: Consolidate ParamSpider results
    paramspider_data_consolidated = consolidate_paramspider_results()

    # Structure the final output for the JSON
    all_data = {
        "subdomains_with_status": formatted_subdomains,
        "wayback_data": wayback_data,
        "paramspider_data": paramspider_data_consolidated
    }

    # Step 6: Store the data in a JSON file
    store_in_json(all_data, domain)

    return jsonify({"message": "Scan completed", "data": all_data}), 200

if __name__ == "__main__":
    app.run(debug=True)
