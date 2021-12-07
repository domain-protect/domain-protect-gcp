#!/usr/bin/env python

import dns.resolver
import google.cloud.dns

from utils_gcp import list_all_projects
from utils_print import my_print, print_list

vulnerable_domains = []


def vulnerable_ns(domain_name):

    try:
        dns.resolver.resolve(domain_name)
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoNameservers:
        try:
            ns_records = dns.resolver.resolve(domain_name, "NS")
            if len(ns_records) > 0:
                return False
            else:
                return True
        except:
            return True
    except:
        return False


class gcp:
    def __init__(self, project):
        self.project = project
        i = 0

        print("Searching for Google Cloud DNS hosted zones in " + project + " project")
        dns_client = google.cloud.dns.client.Client(project=self.project)
        managed_zones = dns_client.list_zones()

        try:
            
            managed_zones = dns_client.list_zones()

            for managed_zone in managed_zones:

                # print(managed_zone.name, managed_zone.dns_name, managed_zone.description)
                print("Searching for vulnerable NS records in " + managed_zone.dns_name)

                dns_record_client = google.cloud.dns.zone.ManagedZone(
                    name=managed_zone.name, client=dns_client
                )

                if dns_record_client.list_resource_record_sets():
                    resource_record_sets = dns_record_client.list_resource_record_sets()

                    for resource_record_set in resource_record_sets:
                        # print(resource_record_set.name, resource_record_set.record_type, resource_record_set.rrdatas)
                        if "NS" in resource_record_set.record_type:
                            if resource_record_set.name != managed_zone.dns_name:
                                print(
                                    "Testing "
                                    + resource_record_set.name
                                    + " for vulnerability"
                                )
                                i = i + 1
                                ns_record = resource_record_set.name
                                result = vulnerable_ns(ns_record)

                                if result:
                                    vulnerable_domains.append(ns_record)
                                    my_print(str(i) + ". " + ns_record, "ERROR")
                                else:
                                    my_print(str(i) + ". " + ns_record, "SECURE")
        except google.api_core.exceptions.Forbidden:
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
