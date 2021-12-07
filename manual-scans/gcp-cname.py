#!/usr/bin/env python
from datetime import datetime

import dns.resolver
import google.cloud.dns
from utils_gcp import list_all_projects
from utils_print import my_print, print_list

vulnerable_domains = []
suspected_domains = []
cname_values = []
vulnerability_list = [
    "azure",
    ".cloudapp.net",
    "core.windows.net",
    "elasticbeanstalk.com",
    "trafficmanager.net",
]


def vulnerable_cname(domain_name):

    global aRecords, isException
    isException = False
    try:
        aRecords = dns.resolver.resolve(domain_name, "A")
        return False, ""
    except dns.resolver.NXDOMAIN:
        if dns.resolver.resolve(domain_name, "CNAME"):
            return True, ""
        else:
            return False, "\tI: Error fetching CNAME Records for " + domain_name
    except:
        return False, ""


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
                    "Searching for vulnerable CNAME records in " + managed_zone.dns_name
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
                                result, exception_message = vulnerable_cname(
                                    cname_record
                                )
                                i = i + 1
                                if result:
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
                                elif (result == False) and (isException == True):
                                    suspected_domains.append(cname_record)
                                    my_print(
                                        str(i)
                                        + ". "
                                        + cname_record
                                        + " CNAME "
                                        + cname_value,
                                        "INFOB",
                                    )
                                    my_print(exception_message, "INFO")
                                else:
                                    my_print(
                                        str(i)
                                        + ". "
                                        + cname_record
                                        + " CNAME "
                                        + cname_value,
                                        "SECURE",
                                    )
                                    my_print(exception_message, "INFO")
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
