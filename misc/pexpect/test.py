import sys, pexpect
child = pexpect.spawn("python called.py")
child.logfile_read = sys.stdout.buffer

child.expect('\n')
p=(child.before.decode('utf8'))
print ("  Some computer program is asking me:", p)

p=p.replace('?',"").split()
a=int(p[2])
b=int(p[4])
c=a*b

child.sendline(str(c))
child.expect(pexpect.EOF)
