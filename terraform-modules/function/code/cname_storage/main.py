#!/usr/bin/env python
# for local testing:
# pip install google-cloud-dns
# pip install google-cloud-pubsub
# pip install google-cloud-resource-manager
# pip install requests
import os
import google.cloud.dns
from google.cloud import pubsub_v1
from google.cloud import resource_manager
import json
from datetime import datetime
import requests

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")

def vulnerable_storage(domain_name):

    try:
        response = requests.get('http://' + domain_name)
        if "NoSuchBucket" in response.text:
            return "True"
        else:
            return "False"
    except:
        pass

    try:
        response = requests.get('https://' + domain_name)
        if "NoSuchBucket" in response.text:
            return "True"
        else:
            return "False"
    except:
        return "False"

class gcp:
    def __init__(self, project):
        self.project = project
        i=0

        print("Searching for Google Cloud DNS hosted zones in " + project + " project")
        dns_client = google.cloud.dns.client.Client(project=self.project)
        try:
            managed_zones = dns_client.list_zones()

            for managed_zone in managed_zones:
                #print(managed_zone.name, managed_zone.dns_name, managed_zone.description)
                print("Searching for CNAMEs with missing storage buckets in " + managed_zone.dns_name)

                dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

                try:
                    resource_record_sets = dns_record_client.list_resource_record_sets()

                    for resource_record_set in resource_record_sets:
                        #print(resource_record_set.name, resource_record_set.record_type, resource_record_set.rrdatas)
                        if "CNAME" in resource_record_set.record_type:
                            if any(vulnerability in resource_record_set.rrdatas[0] for vulnerability in vulnerability_list):
                                cname_record = resource_record_set.name
                                cname_value = resource_record_set.rrdatas[0]
                                print("Testing " + resource_record_set.name + " for vulnerability")
                                try:
                                    result = vulnerable_storage(cname_record)
                                    if result == "True":
                                        print("VULNERABLE: " + cname_record + "  CNAME  " + cname_value + " in GCP project " + project)
                                        vulnerable_domains.append(cname_record)
                                        json_data["Findings"].append({"Project": project, "Domain": cname_record, "CNAME": cname_value})
                                except:
                                    pass

                except:
                    pass
        except:
            pass

def cname_storage(event, context):
#comment out line above, and uncomment line below for local testing
#def cname_storage():
    security_project = os.environ['SECURITY_PROJECT']
    app_name         = os.environ['APP_NAME']
    app_environment  = os.environ['APP_ENVIRONMENT']

    global vulnerability_list
    vulnerability_list = ["amazonaws.com", "cloudfront.net", "c.storage.googleapis.com"]

    global vulnerable_domains
    vulnerable_domains       = []
    global json_data
    json_data                = {"Findings": [], "Subject": "Vulnerable CNAME records in Google Cloud DNS"}

    client = resource_manager.Client()
    for project in client.list_projects():
        if "sys-" not in project.project_id:
            gcp(project.name)

    if len(vulnerable_domains) > 0:
        try:
            #print(json.dumps(json_data, sort_keys=True, indent=2, default=json_serial))
            publisher = pubsub_v1.PublisherClient()
            topic_name = 'projects/' + security_project + '/topics/' + app_name + '-results-' + app_environment
            data=json.dumps(json_data)

            encoded_data = data.encode('utf-8')
            future = publisher.publish(topic_name, data=encoded_data)
            print("Message ID " + future.result() + " published to topic projects/" + security_project + "/topics/" + app_name + "-results-" + app_environment)

        except:
            print("ERROR: Unable to publish to PubSub topic projects/" + security_project + "/topics/" + app_name + "-results-" + app_environment)

#uncomment line below for local testing
#cname_storage()