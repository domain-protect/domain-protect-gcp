from datetime import datetime
import asyncio
import google.cloud.dns
import requests
from utils_vulnerable import get_vulnerable_list
from utils_gcp import list_all_projects
from utils_print import my_print, print_list
from secrets import choice
from string import ascii_letters, digits

start_time = datetime.now()
vulnerable_domains = []
suspected_domains = []
cname_values = []
vulnerability_list = get_vulnerable_list()


def vulnerable_storage(domain_name):
    # Handle wildcard A records by passing in a random 5 character string
    if domain_name[0] == "*":
        random_string = "".join(choice(ascii_letters + digits) for _ in range(5))
        domain_name = random_string + domain_name[1:]

    try:
        response = requests.get(f"http://{domain_name}", timeout=1)
        if "NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False


def gcp(project):
    i = 0

    print(f"Searching for Google Cloud DNS hosted zones in {project} project")
    dns_client = google.cloud.dns.client.Client(project)
    try:
        managed_zones = dns_client.list_zones()

        for managed_zone in managed_zones:
            print(f"Searching CNAMEs with missing storage buckets in {managed_zone.dns_name}")

            dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

            if dns_record_client.list_resource_record_sets():

                records = dns_record_client.list_resource_record_sets()
                resource_record_sets = [
                    r
                    for r in records
                    if "CNAME" in r.record_type
                    and r.rrdatas
                    and any(vulnerability in r.rrdatas[0] for vulnerability in vulnerability_list.keys())
                ]
                for resource_record_set in resource_record_sets:
                    cname_record = resource_record_set.name
                    cname_value = resource_record_set.rrdatas[0]
                    print(f"Testing {resource_record_set.name} for vulnerability")
                    result = vulnerable_storage(cname_record)
                    i = i + 1
                    if result:
                        vulnerable_domains.append(cname_record)
                        cname_values.append(cname_value)
                        my_print(
                            f"{str(i)}. {cname_record} CNAME {cname_value}",
                            "ERROR",
                        )
                    elif not result:
                        suspected_domains.append(cname_record)
                        my_print(
                            f"{str(i)}. {cname_record} CNAME {cname_value}",
                            "SECURE",
                        )
                    else:
                        my_print("WARNING: no response from test", "INFOB")
        return 1
    except google.api_core.exceptions.Forbidden:
        return 0


async def main():
    to_scan = []
    for project in await list_all_projects():
        to_scan.append(asyncio.to_thread(gcp, project))

    total_projects = len(to_scan)
    scanned_projects = sum(await asyncio.gather(*to_scan))
    scan_time = datetime.now() - start_time
    print(f"Scanned {str(scanned_projects)} of {str(total_projects)} projects in {scan_time.seconds} seconds")

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)


if __name__ == "__main__":
    asyncio.run(main())
