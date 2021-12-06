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
## setup
* optionally create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```
* install dependencies
```
pip install -r requirements.txt
```

## usage - subdomain NS delegations
```
gcloud auth login
python gcp-ns.py
```

![Alt text](images/gcp-ns.png?raw=true "Detect vulnerable subdomains")

## usage - vulnerable CNAMEs
```
gcloud auth login
python gcp-cname.py
```

![Alt text](images/gcp-cname.png?raw=true "Detect vulnerable subdomains")

## usage - CNAMEs for missing storage buckets
```
gcloud auth login
python gcp-cname-storage.py
```

![Alt text](images/gcp-cname-storage.png?raw=true "Detect vulnerable subdomains")

## usage - A records for missing storage buckets
* looks for Google Cloud Load Balancers for which the backend storage bucket has been deleted
```
gcloud auth login
python gcp-a-storage.py
```

![Alt text](images/gcp-a-storage.png?raw=true "Detect vulnerable subdomains")

## acknowledgements
* Function to list all GCP projects inspired by [Joan Grau's blog](https://blog.graunoel.com/resource-manager-list-all-projects/)
* NS subdomain takeover detection based on [NSDetect](https://github.com/shivsahni/NSDetect)