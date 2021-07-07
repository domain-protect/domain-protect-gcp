#!/usr/bin/env python
# pip install google-cloud-dns
# pip install google-cloud-resource-manager
# pip install requests
import google.cloud.dns
from google.cloud import resource_manager
import json
import argparse
from datetime import datetime
import requests

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
global vulnerability_list
vulnerability_list = ["amazonaws.com", "cloudfront.net", "c.storage.googleapis.com"]
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
                print("Searching for A records with missing storage buckets in " + managed_zone.dns_name)

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
                                        i = i + 1
                                        if result == "True":
                                            vulnerable_domains.append(a_record)
                                            my_print(str(i) + ". " + a_record,"ERROR")
                                        elif result == "False":
                                            suspected_domains.append(a_record)
                                            my_print(str(i) + ". " + a_record, "SECURE")
                                    except:
                                        pass    
                                else:
                                    my_print("WARNING: no response from test","INFOB")
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
