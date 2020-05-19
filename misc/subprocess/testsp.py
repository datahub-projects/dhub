import subprocess as sp
p=sp.Popen(["python3", "called.py"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf8')
p.stdin.write("BOOM\n")
p.stdin.write("BOOM BOOM\n")
out, err=p.communicate()
print (out)
