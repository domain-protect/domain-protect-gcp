# domain-protect manual scans
Scans Google Cloud DNS for:
* subdomain NS delegations vulnerable to takeover
* CNAMEs vulnerable to takeover
* CNAMEs for missing storage buckets
* Google Cloud Load Balancers for which the backend storage bucket has been deleted

## requirements
* Python 3.x
```
pip install google-cloud-dns
pip install google-cloud-resource-manager
pip install dnspython
pip install requests
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

## acknowledgement
* NS subdomain takeover detection based on [NSDetect](https://github.com/shivsahni/NSDetect)