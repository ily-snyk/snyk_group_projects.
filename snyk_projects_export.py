import requests
import csv
import os
from dotenv import load_dotenv

# --------------------
# Load .env file
# --------------------
load_dotenv()

SNYK_TOKEN = os.getenv("SNYK_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

BASE_URL = "https://api.snyk.io/rest"
HEADERS = {
    "Authorization": f"token {SNYK_TOKEN}",
    "Content-Type": "application/json",
    # Explicitly request version 2024-10-15
    "Accept": "application/vnd.api+json;version=2024-10-15"
}

# --------------------
# Fetch Orgs for Group
# --------------------
def get_orgs(group_id):
    url = f"{BASE_URL}/groups/{group_id}/orgs"
    orgs = []
    page = 1
    while True:
        resp = requests.get(url, headers=HEADERS, params={"page": page})
        resp.raise_for_status()
        data = resp.json()
        orgs.extend(data.get("data", []))

        if "next" not in data.get("links", {}):
            break
        page += 1
    return orgs

# --------------------
# Fetch Projects for Org (npm only)
# --------------------
def get_projects(org_id, project_type="npm"):
    url = f"{BASE_URL}/orgs/{org_id}/projects"
    projects = []
    page = 1
    while True:
        resp = requests.get(
            url,
            headers=HEADERS,
            params={"page": page, "types": project_type}
        )
        resp.raise_for_status()
        data = resp.json()
        projects.extend(data.get("data", []))

        if "next" not in data.get("links", {}):
            break
        page += 1
    return projects

# --------------------
# Main
# --------------------
def main():
    if not SNYK_TOKEN or not GROUP_ID:
        raise ValueError("Missing SNYK_TOKEN or GROUP_ID in .env file")

    all_data = []
    orgs = get_orgs(GROUP_ID)
    print(f"Found {len(orgs)} orgs in group {GROUP_ID}")

    for org in orgs:
        org_id = org["id"]
        org_name = org["attributes"]["name"]
        print(f"Fetching npm projects for org: {org_name} ({org_id})")

        projects = get_projects(org_id, "npm")
        for project in projects:
            all_data.append({
                "org_id": org_id,
                "org_name": org_name,
                "project_id": project["id"],
                "project_name": project["attributes"]["name"],
                "type": project["attributes"].get("type"),
                "origin": project["attributes"].get("origin")
            })

    # Write results to CSV
    with open("snyk_group_npm_projects.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["org_id", "org_name", "project_id", "project_name", "type", "origin"]
        )
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Exported {len(all_data)} npm projects to snyk_group_npm_projects.csv")

if __name__ == "__main__":
    main()
