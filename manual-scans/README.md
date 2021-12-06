# domain-protect manual scans
Scans Google Cloud DNS for:
* subdomain NS delegations vulnerable to takeover
* CNAMEs vulnerable to takeover
* CNAMEs for missing storage buckets
* Google Cloud Load Balancers for which the backend storage bucket has been deleted

## requirements
* Python 3.9
* pip
* venv

## Python setup
* optionally create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```
* install dependencies
```
pip install -r requirements.txt
```

## GCP setup
* create a domain-protect service account in one of your projects
* assign built-in roles to the service account at the organization level:
```
DNS Reader (roles/dns.reader)
Folder Viewer (roles/resourcemanager.folderViewer)
Organization Viewer (roles/resourcemanager.organizationViewer) 
```
* create a JSON key for your service account and download to your laptop
* create an environment variable, e.g.
```
export GOOGLE_APPLICATION_CREDENTIALS="/Users/sylvia/gcp/domain-protect-service-account.json"
```

## usage - subdomain NS delegations
```
python gcp-ns.py
```

![Alt text](images/gcp-ns.png?raw=true "Detect vulnerable subdomains")

## usage - vulnerable CNAMEs
```
python gcp-cname.py
```

![Alt text](images/gcp-cname.png?raw=true "Detect vulnerable subdomains")

## usage - CNAMEs for missing storage buckets
```
python gcp-cname-storage.py
```

![Alt text](images/gcp-cname-storage.png?raw=true "Detect vulnerable subdomains")

## usage - A records for missing storage buckets
* looks for Google Cloud Load Balancers for which the backend storage bucket has been deleted
```
python gcp-a-storage.py
```

![Alt text](images/gcp-a-storage.png?raw=true "Detect vulnerable subdomains")

## acknowledgements
* Function to list all GCP projects inspired by [Joan Grau's blog](https://blog.graunoel.com/resource-manager-list-all-projects/)
* NS subdomain takeover detection based on [NSDetect](https://github.com/shivsahni/NSDetect)