import os
from blessings import Terminal
bless_term = Terminal()


def print_blue(s, **kw):
    print (bless_term.blue(s), **kw)


def do(s):
    print_blue(s)
    os.system(s)

do("rm -fr root* *bare my*")

do("./clean")

do("echo '~~~~~~~~~~~~~~~~~~~~~~~~~TEST 1~~~~~~~~~~~~~~~~~~~~~~~~~~~'")
do("ver clone ./rootbare --name myroot --yes --debug")
do("ls -Rrlt myroot")
os.chdir("myroot")
do("ver branch b1 --yes --debug")
do("ver branch --debug")
do("echo 'To another end' > sub1/rooty_file2")
do("ver sync --debug")
do("ver branch master --debug")
do("ver branch --debug")
do("ver save")
os.chdir("sub1")
do("git branch")
do("ver status")