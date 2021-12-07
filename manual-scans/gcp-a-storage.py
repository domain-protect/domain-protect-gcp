#!/usr/bin/env python
from datetime import datetime

import google.cloud.dns
import requests
from utils_gcp import list_all_projects
from utils_print import my_print, print_list

vulnerable_domains = []
suspected_domains = []
cname_values = []
global vulnerability_list
vulnerability_list = ["amazonaws.com", "cloudfront.net", "c.storage.googleapis.com"]


def vulnerable_storage(domain_name):

    try:
        response = requests.get("https://" + domain_name, timeout=1)
        if "NoSuchBucket" in response.text:
            return "True"
        else:
            return "False"
    except:
        pass

    try:
        response = requests.get("http://" + domain_name, timeout=1)
        if "NoSuchBucket" in response.text:
            return "True"
        else:
            return "False"
    except:
        return "False"


class gcp:
    def __init__(self, project):
        self.project = project
        i = 0

        print("Searching for Google Cloud DNS hosted zones in " + project + " project")
        dns_client = google.cloud.dns.client.Client(project=self.project)
        try:
            managed_zones = dns_client.list_zones()

            for managed_zone in managed_zones:
                # print(managed_zone.name, managed_zone.dns_name, managed_zone.description)
                print(
                    "Searching for A records with missing storage buckets in "
                    + managed_zone.dns_name
                )

                dns_record_client = google.cloud.dns.zone.ManagedZone(
                    name=managed_zone.name, client=dns_client
                )

                try:
                    resource_record_sets = dns_record_client.list_resource_record_sets()

                    for resource_record_set in resource_record_sets:
                        # print(resource_record_set.name, resource_record_set.record_type, resource_record_set.rrdatas)
                        if resource_record_set.record_type in "A":
                            for ip_address in resource_record_set.rrdatas:
                                if not ip_address.startswith("10."):
                                    a_record = resource_record_set.name
                                    print("Testing " + a_record + " for vulnerability")
                                    try:
                                        result = vulnerable_storage(a_record)
                                        i = i + 1
                                        if result == "True":
                                            vulnerable_domains.append(a_record)
                                            my_print(str(i) + ". " + a_record, "ERROR")
                                        elif result == "False":
                                            suspected_domains.append(a_record)
                                            my_print(str(i) + ". " + a_record, "SECURE")
                                    except:
                                        pass
                                else:
                                    my_print("WARNING: no response from test", "INFOB")
                except:
                    pass
        except:
            pass


if __name__ == "__main__":

    projects = list_all_projects()

    for project in projects:
        gcp(project)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
