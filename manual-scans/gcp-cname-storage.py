#!/usr/bin/env python

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
                    "Searching CNAMEs with missing storage buckets in "
                    + managed_zone.dns_name
                )

                dns_record_client = google.cloud.dns.zone.ManagedZone(
                    name=managed_zone.name, client=dns_client
                )

                try:
                    resource_record_sets = dns_record_client.list_resource_record_sets()

                    for resource_record_set in resource_record_sets:
                        # print(resource_record_set.name, resource_record_set.record_type, resource_record_set.rrdatas)
                        if "CNAME" in resource_record_set.record_type:
                            if any(
                                vulnerability in resource_record_set.rrdatas[0]
                                for vulnerability in vulnerability_list
                            ):
                                cname_record = resource_record_set.name
                                cname_value = resource_record_set.rrdatas[0]
                                print(
                                    "Testing "
                                    + resource_record_set.name
                                    + " for vulnerability"
                                )
                                result = vulnerable_storage(cname_record)
                                i = i + 1
                                if result == "True":
                                    vulnerable_domains.append(cname_record)
                                    cname_values.append(cname_value)
                                    my_print(
                                        str(i)
                                        + ". "
                                        + cname_record
                                        + " CNAME "
                                        + cname_value,
                                        "ERROR",
                                    )
                                elif result == "False":
                                    suspected_domains.append(cname_record)
                                    my_print(
                                        str(i)
                                        + ". "
                                        + cname_record
                                        + " CNAME "
                                        + cname_value,
                                        "SECURE",
                                    )
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
