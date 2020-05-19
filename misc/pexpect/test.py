import sys, pexpect
child = pexpect.spawn("python called.py")
child.logfile_read = sys.stdout.buffer

try:
    child.expect('xxxxx', timeout=3)
except:
    print ("TIME")
p=(child.before.decode('utf8'))
print ("  Some computer program is asking me:", p)

# p=p.replace('?',"").split()
# a=int(p[2])
# b=int(p[4])
# c=a*b

child.sendline("11")
child.expect(pexpect.EOF)
child.wait()