from datetime import datetime
import asyncio
import dns.resolver
import google.cloud.dns
from utils_gcp import list_all_projects
from utils_print import my_print, print_list

start_time = datetime.now()
vulnerable_domains = []


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

    i = 0

    print(f"Searching for Google Cloud DNS hosted zones in {project} project")
    dns_client = google.cloud.dns.client.Client(project)
    managed_zones = dns_client.list_zones()

    try:
        managed_zones = dns_client.list_zones()

        for managed_zone in managed_zones:
            print(f"Searching for vulnerable NS records in {managed_zone.dns_name}")

            dns_record_client = google.cloud.dns.zone.ManagedZone(name=managed_zone.name, client=dns_client)

            if dns_record_client.list_resource_record_sets():

                records = dns_record_client.list_resource_record_sets()
                resource_record_sets = [r for r in records if "NS" in r.record_type and r.name != managed_zone.dns_name]

                for resource_record_set in resource_record_sets:
                    print(f"Testing {resource_record_set.name} for vulnerability")
                    i = i + 1
                    ns_record = resource_record_set.name
                    result = vulnerable_ns(ns_record)

                    if result:
                        vulnerable_domains.append(ns_record)
                        my_print(f"{str(i)}. {ns_record}", "ERROR")
                    else:
                        my_print(f"{str(i)}. {ns_record}", "SECURE")
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
