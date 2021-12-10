import base64
import json
import os

import google.cloud.dns
import requests
from google.cloud import pubsub_v1


def vulnerable_storage(domain_name):

    try:
        response = requests.get(f"http://{domain_name}", timeout=1)
        if "NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False


def gcp(project):

    print(f"Searching for Google Cloud DNS hosted zones in {project} project")
    dns_client = google.cloud.dns.client.Client(project)
    try:
        managed_zones = dns_client.list_zones()

        for managed_zone in managed_zones:
            print(f"Searching for CNAMEs with missing storage buckets in {managed_zone.dns_name}")

            dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

            if dns_record_client.list_resource_record_sets():
                records = dns_record_client.list_resource_record_sets()
                resource_record_sets = [
                    r
                    for r in records
                    if "CNAME" in r.record_type
                    and any(vulnerability in r.rrdatas[0] for vulnerability in vulnerability_list)
                ]
                for resource_record_set in resource_record_sets:
                    cname_record = resource_record_set.name
                    cname_value = resource_record_set.rrdatas[0]
                    print(f"Testing {resource_record_set.name} for vulnerability")
                    result = vulnerable_storage(cname_record)
                    if result:
                        print(f"VULNERABLE: {cname_record}  CNAME {cname_value} in GCP project {project}")
                        vulnerable_domains.append(cname_record)
                        json_data["Findings"].append({"Project": project, "Domain": cname_record, "CNAME": cname_value})

    except google.api_core.exceptions.Forbidden:
        pass


def cname_storage(event, context):  # pylint:disable=unused-argument
    # comment out line above, and uncomment line below for local testing
    # def cname_storage():
    security_project = os.environ["SECURITY_PROJECT"]
    app_name = os.environ["APP_NAME"]
    app_environment = os.environ["APP_ENVIRONMENT"]

    global vulnerability_list
    vulnerability_list = ["amazonaws.com", "cloudfront.net", "c.storage.googleapis.com"]
    global vulnerable_domains
    vulnerable_domains = []
    global json_data
    json_data = {"Findings": [], "Subject": "Vulnerable CNAME records in Google Cloud DNS"}

    if "data" in event:
        pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
        projects_json = json.loads(pubsub_message)
        projects = projects_json["Projects"]
        scanned_projects = 0
        for project in projects:
            gcp(project)
            scanned_projects = scanned_projects + 1

        print(f"Scanned {str(scanned_projects)} of {str(len(projects))} projects")

        if len(vulnerable_domains) > 0:
            try:
                # print(json.dumps(json_data, sort_keys=True, indent=2, default=json_serial))
                publisher = pubsub_v1.PublisherClient()
                topic_name = f"projects/{security_project}/topics/{app_name}-results-{app_environment}"
                encoded_data = json.dumps(json_data).encode("utf-8")
                future = publisher.publish(topic_name, data=encoded_data)
                print(f"Message ID {future.result()} published to topic {topic_name}")

            except google.api_core.exceptions.Forbidden:
                print(f"ERROR: Unable to publish to PubSub topic {topic_name}")


# uncomment line below for local testing
# cname_storage()
