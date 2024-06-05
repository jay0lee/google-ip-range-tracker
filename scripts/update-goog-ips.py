from __future__ import print_function

import json
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen
    from urllib.error import HTTPError

import netaddr

IPRANGE_URLS = {
    "goog": "https://www.gstatic.com/ipranges/goog.json",
    "cloud": "https://www.gstatic.com/ipranges/cloud.json",
}


def read_url(url):
    try:
        filename = url.split('/')[-1]
        filepath = f'scripts/{filename}'
        data = urlopen(url).read()
        with open(filepath, 'w') as f:
            f.write(data)
        return json.loads(data)
    except (IOError, HTTPError):
        print("ERROR: Invalid HTTP response from %s" % url)
    except json.decoder.JSONDecodeError:
        print("ERROR: Could not parse HTTP response from %s" % url)


def get_data(link):
    data = read_url(link)
    if data:
        print("{} published: {}".format(link, data.get("creationTime")))
        cidrs = netaddr.IPSet()
        for e in data["prefixes"]:
            if "ipv4Prefix" in e:
                cidrs.add(e.get("ipv4Prefix"))
            if "ipv6Prefix" in e:
                cidrs.add(e.get("ipv6Prefix"))
        return cidrs


def main():
    cidrs = {group: get_data(link) for group, link in IPRANGE_URLS.items()}
    if len(cidrs) != 2:
        raise ValueError("ERROR: Could process data from Google")
    goog_default_ips = {'prefixes': []}
    for ip in (cidrs["goog"] - cidrs["cloud"]).iter_cidrs():
        print(type(ip))
    filepath = 'scripts/goog-default.json'
    with open(filepath, 'w') as f:
        f.write(goog_default_ips)

if __name__ == "__main__":
    main()
