import json
import os
from datetime import datetime

import google.cloud.dns
import requests
from google.cloud import pubsub_v1
from utils import list_all_projects


def vulnerable_storage(domain_name):

    try:
        response = requests.get("https://" + domain_name, timeout=1)
        if "NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    try:
        response = requests.get("http://" + domain_name, timeout=1)
        if "NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False

def gcp(project):
    i=0

    print(f"Searching for Google Cloud DNS hosted zones in {project} project")
    dns_client = google.cloud.dns.client.Client(project)
    try:
        managed_zones = dns_client.list_zones()

        for managed_zone in managed_zones:
            print(f"Searching for vulnerable A records in {managed_zone.dns_name}")

            dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

            if dns_record_client.list_resource_record_sets():
                resource_record_sets = dns_record_client.list_resource_record_sets()

                for resource_record_set in resource_record_sets:
                    if resource_record_set.record_type in "A":
                        for ip_address in resource_record_set.rrdatas:
                            if not ip_address.startswith("10."):
                                a_record = resource_record_set.name
                                print(f"Testing {resource_record_set.name} for vulnerability")
                                try:
                                    result = vulnerable_storage(a_record)
                                    if result:
                                        print(f"VULNERABLE: {a_record} in GCP project {project}")
                                        vulnerable_domains.append(a_record)
                                        json_data["Findings"].append({"Project": project, "Domain": a_record})
                                except:
                                    pass
    
    except google.api_core.exceptions.Forbidden:
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

    projects = list_all_projects()
    for project in projects:
        gcp(project)

    if len(vulnerable_domains) > 0:
        try:
            #print(json.dumps(json_data, sort_keys=True, indent=2, default=json_serial))
            publisher = pubsub_v1.PublisherClient()
            topic_name = f"projects/{security_project}/topics/{app_name}-results-{app_environment}"
            data=json.dumps(json_data)

            encoded_data = data.encode('utf-8')
            future = publisher.publish(topic_name, data=encoded_data)
            print(f"Message ID {future.result()} published to topic {topic_name}")

        except google.api_core.exceptions.Forbidden:
            print(f"ERROR: Unable to publish to PubSub topic {topic_name}")

#uncomment line below for local testing
#a_storage()