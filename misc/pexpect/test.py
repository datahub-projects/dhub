import sys, pexpect
child = pexpect.spawn("python called.py")
child.logfile_read = sys.stdout.buffer
child.expect('time')
child.sendline('anonymous walrus juice')
child.expect(pexpect.EOF)
