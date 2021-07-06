#!/usr/bin/env python
# pip install google-cloud-dns
# pip install google-cloud-resource-manager
# pip install dnspython
import google.cloud.dns
from google.cloud import resource_manager
import json
import argparse
from datetime import datetime
import dns.resolver

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")

class bcolors:
    TITLE = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[93m'
    OKRED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    UNDERLINE = '\033[4m'
    FGWHITE = '\033[37m'
    FAIL = '\033[95m'

vulnerable_domains = []
suspected_domains = []
cname_values = []
vulnerability_list = ["azure", ".cloudapp.", "core.windows.net", "elasticbeanstalk.com", "google", "trafficmanager.net" ]
verbose_mode = False

def my_print(text, type):
    if type=="INFO":
        if verbose_mode:
            print(bcolors.INFO+text+bcolors.ENDC)
        return
    if type=="PLAIN_OUTPUT_WS":
        print(bcolors.INFO+text+bcolors.ENDC)
        return
    if type=="INFOB":
        print(bcolors.INFO+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="ERROR":
        print(bcolors.BGRED+bcolors.FGWHITE+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="MESSAGE":
        print(bcolors.TITLE+bcolors.BOLD+text+bcolors.ENDC+"\n")
        return
    if type=="INSECURE_WS":
        print(bcolors.OKRED+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="INSECURE":
        print(bcolors.OKRED+bcolors.BOLD+text+bcolors.ENDC+"\n")
        return
    if type=="OUTPUT":
        print(bcolors.OKBLUE+bcolors.BOLD+text+bcolors.ENDC+"\n")
        return
    if type=="OUTPUT_WS":
        print(bcolors.OKBLUE+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="SECURE":
        print(bcolors.OKGREEN+bcolors.BOLD+text+bcolors.ENDC)

def print_list(lst):
    counter=0
    for item in lst:
        counter=counter+1
        entry=str(counter)+". "+item
        my_print("\t"+entry, "INSECURE_WS")

def vulnerable_cname(domain_name):

    global aRecords, isException
    isException=False
    try:
        aRecords= dns.resolver.resolve(domain_name, 'A')
        return False, ""
    except dns.resolver.NXDOMAIN:
        if dns.resolver.resolve(domain_name, 'CNAME'):
            return True, ""
        else:
            return False, "\tI: Error fetching CNAME Records for " + domain_name
    except:
        return False, ""

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
                print("Searching for vulnerable CNAME records in " + managed_zone.dns_name)

                dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

                try:
                    resource_record_sets = dns_record_client.list_resource_record_sets()

                    for resource_record_set in resource_record_sets:
                        #print(resource_record_set.name, resource_record_set.record_type, resource_record_set.rrdatas)
                        if "CNAME" in resource_record_set.record_type:
                            if any(vulnerability in resource_record_set.rrdatas[0] for vulnerability in vulnerability_list):
                                if ".dv.googlehosted.com" not in resource_record_set.rrdatas[0]:
                                    cname_record = resource_record_set.name
                                    cname_value = resource_record_set.rrdatas[0]
                                    print("Testing " + resource_record_set.name + " for vulnerability")
                                    result, exception_message = vulnerable_cname(cname_record)
                                    i = i + 1
                                    if result:
                                        vulnerable_domains.append(cname_record)
                                        cname_values.append(cname_value)
                                        my_print(str(i) + ". " + cname_record + " CNAME " +  cname_value ,"ERROR")
                                    elif (result==False) and (isException==True):
                                        suspected_domains.append(cname_record)
                                        my_print(str(i) + ". " + cname_record + " CNAME " +  cname_value,"INFOB")
                                        my_print(exception_message, "INFO")
                                    else:
                                        my_print(str(i) + ". " + cname_record + " CNAME " +  cname_value,"SECURE")
                                        my_print(exception_message, "INFO")
                except:
                    pass
        except:
            pass

if __name__ == "__main__":

    client = resource_manager.Client()
    for project in client.list_projects():
        if "sys-" not in project.project_id:
            gcp(project.name)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: "+str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
