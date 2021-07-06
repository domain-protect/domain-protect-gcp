# domain-protect manual scans

* scans Google Cloud DNS for subdomain NS delegations vulnerable to takeover
* scans Google Cloud DNS for CNAMES vulnerable to takeover

## important note
* for a fuller set of functionality, deploy the Google Cloud Function installation

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

## acknowledgement
* NS subdomain takeover detection based on [NSDetect](https://github.com/shivsahni/NSDetect)