from __future__ import print_function

import json

import netaddr
import requests

GOOG_IPS_URL = {
                 'url': 'https://www.gstatic.com/ipranges/goog.json',
                 'file': 'google-owned-ips.json',
               }
CLOUD_IPS_URL = {
                 'url': 'https://www.gstatic.com/ipranges/cloud.json',
                 'file': 'google-cloud-customer-ips.json'
                }


def read_url(url):
    response = requests.get(url)
    return response.json()

def get_data(url):
    data = read_url(url['url'])
    filename = url['file']
    filepath = f'ips/{filename}'
    print(f'{filename} published: {data.get("creationTime")}')
    
    # drop createTime and syncToken which seem to change without
    # any other changes creating git noisiness.
    del data['creationTime']
    del data['syncToken']

    cidrs = netaddr.IPSet()
    for i, e in enumerate(data.get('prefixes', [])):
        if 'ipv4Prefix' in e:
            e['ipPrefix'] = e['ipv4Prefix']
            del e['ipv4Prefix']
        if 'ipv6Prefix' in e:
            e['ipPrefix'] = e['ipv6Prefix']
            del e['ipv6Prefix']
        data['prefixes'][i] = e
        cidrs.add(e.get("ipPrefix"))
    with open(filepath, 'w') as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))
    return cidrs


def main():
    goog_ips = get_data(GOOG_IPS_URL)
    cloud_ips = get_data(CLOUD_IPS_URL)
    goog_default_ips = {'prefixes': []}
    for ip_range in (goog_ips - cloud_ips).iter_cidrs():
        ip_range_str = str(ip_range.cidr)
        goog_default_ips['prefixes'].append({'ipPrefix': ip_range_str})
    filepath = 'ips/google-non-cloud-service-ips.json'
    with open(filepath, 'w') as f:
        f.write(json.dumps(goog_default_ips, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
