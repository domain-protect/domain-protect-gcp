from json import loads
from requests import get


def get_vulnerable_list():
    return {
        cname: fingerprint['fingerprint']
        for fingerprint in
        loads(get("https://github.com/EdOverflow/can-i-take-over-xyz/raw/master/fingerprints.json").text)
        if fingerprint['vulnerable'] and fingerprint['cname']
        for cname in fingerprint['cname']
    }
