import json
import os
from datetime import datetime

import dns.resolver
import google.cloud.dns
from google.cloud import pubsub_v1
from utils import list_all_projects


def vulnerable_ns(domain_name):

    try:
        dns.resolver.resolve(domain_name)

    except dns.resolver.NXDOMAIN:
        return False

    except dns.resolver.NoNameservers:

        try:
            ns_records = dns.resolver.resolve(domain_name, "NS")
            if len(ns_records) == 0:
                return True

        except dns.resolver.NoNameservers:
            return True

    except dns.resolver.NoAnswer:
        return False

    return False
    

def gcp(project):
    i=0

    print(f"Searching for Google Cloud DNS hosted zones in {project} project")
    dns_client = google.cloud.dns.client.Client(project)
    try:
        managed_zones = dns_client.list_zones()

        for managed_zone in managed_zones:
            print(f"Searching for vulnerable NS records in {managed_zone.dns_name}")

            dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

            if dns_record_client.list_resource_record_sets():
                resource_record_sets = dns_record_client.list_resource_record_sets()

                for resource_record_set in resource_record_sets:
                    if "NS" in resource_record_set.record_type:
                        if resource_record_set.name != managed_zone.dns_name:
                            print(f"Testing {resource_record_set.name}")
                            i = i + 1
                            ns_record = resource_record_set.name
                            result = vulnerable_ns(ns_record)

                            if result:
                                print(f"VULNERABLE DOMAIN: {ns_record}")
                                vulnerable_domains.append(ns_record)
                                json_data["Findings"].append({"Project": project, "Domain": ns_record})
    
    except google.api_core.exceptions.Forbidden:
        pass

def ns(event, context):
#comment out line above, and uncomment line below for local testing
#def ns():
    security_project = os.environ['SECURITY_PROJECT']
    app_name         = os.environ['APP_NAME']
    app_environment  = os.environ['APP_ENVIRONMENT']

    global vulnerable_domains
    vulnerable_domains = []
    global json_data
    json_data = {"Findings": [], "Subject": "Vulnerable NS subdomain records found in Google Cloud DNS"}

    projects = list_all_projects()
    for project in projects:
        gcp(project)

    if len(vulnerable_domains) > 0:
        try:
            publisher = pubsub_v1.PublisherClient()
            topic_name = f"projects/{security_project}/topics/{app_name}-results-{app_environment}"
            data=json.dumps(json_data)

            encoded_data = data.encode('utf-8')
            future = publisher.publish(topic_name, data=encoded_data)
            print(f"Message ID {future.result()} published to topic {topic_name}")

        except google.api_core.exceptions.Forbidden:
            print(f"ERROR: Unable to publish to PubSub topic {topic_name}")

#uncomment line below for local testing
#ns()