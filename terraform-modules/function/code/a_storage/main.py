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
                print("Searching for vulnerable A records in " + managed_zone.dns_name)

                dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

                try:
                    resource_record_sets = dns_record_client.list_resource_record_sets()

                    for resource_record_set in resource_record_sets:
                        #print(resource_record_set.name, resource_record_set.record_type, resource_record_set.rrdatas)
                        if resource_record_set.record_type in "A":
                            for ip_address in resource_record_set.rrdatas:
                                if not ip_address.startswith("10."):
                                    a_record = resource_record_set.name
                                    print("Testing " + a_record + " for vulnerability")
                                    try:
                                        result = vulnerable_storage(a_record)
                                        if result == "True":
                                            print("VULNERABLE: " + a_record + " in GCP project " + project)
                                            vulnerable_domains.append(a_record)
                                            json_data["Findings"].append({"Project": project, "Domain": a_record})
                                    except:
                                        pass

                except:
                    pass
        except:
            pass

def a_storage(event, context):
#comment out line above, and uncomment line below for local testing
#def a_storage():
    security_project = os.environ['SECURITY_PROJECT']
    app_name         = os.environ['APP_NAME']
    app_environment  = os.environ['APP_ENVIRONMENT']

    global vulnerable_domains
    vulnerable_domains       = []
    global json_data
    json_data                = {"Findings": [], "Subject": "Vulnerable A record in Google Cloud DNS - missing storage bucket"}

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
#a_storage()