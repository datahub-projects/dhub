import subprocess as sp
p=sp.Popen(["python3", "called.py"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf8')
p.stdin.write("Interactive apps FTW\n")
out, err=p.communicate()
print (out)
