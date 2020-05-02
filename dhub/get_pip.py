#get pip package data (versions & release dates)
import sys, json, requests, datetime
from collections import OrderedDict as odic
from pprint import pprint
import dateutil.parser as dup

from runrun import run as rrun

def get_package_dates(p):
    #https://pypi.org/pypi/mido/json
    url = "https://pypi.org/pypi/{0}/json".format(p)
    j=requests.get(url).content
    data=json.loads(j)
    vers = odic()
    for x in data['releases']:
        for y in data['releases'][x]:
            # print (x, y['upload_time'])
            date = dup.parse(y['upload_time'])
            vers[x] = date                                      # FIXME: multiple uploads possible
    return vers


def get_package_info(p):
    dates = get_package_dates(p)
    cmd = ["pip", "install", "{0}==blarchy".format(p)]
    s, ok = rrun(cmd)
    if ok:
        raw = s.split(",")
        vers = odic()
        for x in raw:
            if x.find("ERROR") == -1:
                x=x.strip()
                if x in dates:
                    vers[x]=dates[x]
                else:
                    print ("Warning: version in pip not in pypi:", x)
        for x in dates:
            if x not in vers:
                print ("Warning: version in pypi not in pip:", x)
        return vers


def get_latest(package, before):
    # print ("B4:", before)
    vers = get_package_info(package)
    keys = list(vers.keys())
    keys.reverse()
    for ver in keys:
        # print("DBG", ver, vers[ver])
        if vers[ver] < before:
            break
    return ver, vers[ver]


if __name__=="__main__":
    package = sys.argv[1]
    b4=dup.parse(sys.argv[2])
    ver, date = get_latest(package, b4)
    print ("{0}=={1} released on {2}".format(package, ver, date))
