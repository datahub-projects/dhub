import pexpect
child = pexpect.spawn("python called.py")
child.expect('')
print (child.before.decode('utf8'))
child.sendline('anonymous walrus')
print (child.read().decode('utf8'))
# child.expect('Well')
# print (child.read().decode('utf8'))
