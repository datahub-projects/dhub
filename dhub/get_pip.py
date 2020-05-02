#get pip package data (versions & release dates)

from runrun import run as rrun

def get_package_info(p):
    cmd = ["pip", "install", "{0}==blarchy".format(p)]
    s, ok = rrun(cmd)
    if ok:
        raw = s.split(",")
        vers = {}
        for x in raw:
            if x.find("ERROR") == -1:
                x=x.strip()
                vers[x]="1/1/1111"
        print (vers)

if __name__=="__main__":
    get_package_info("mido")