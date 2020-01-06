import  subprocess, time, os, sys

MAXLINES=100

def run(*args, **kw):
    # print ("DBG", args, kw)
    if 'showoutput' in kw:
        showoutput = kw['showoutput']
        # print("showoutput:", showoutput)
        del kw['showoutput']
    else:
        showoutput = False
    if 'timeout' in kw:
        timeout = float(kw['timeout'])
        if showoutput:
            print("running", args[0], "with timeout:", timeout, end=' ')
        del kw['timeout']
    else:
        timeout = 0
    try:
        if not timeout:
            timeout = 10**10
        proc = subprocess.Popen(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t0 = time.time()
        out = ""
        complete = False
        while time.time() < t0 + timeout:
            line = proc.stdout.readline().decode('utf8')
            # print ("DBG", type(out), type(line))
            out += line
            i = 0
            while line != "":
                if showoutput:
                    sys.stdout.write(line)
                i += 1
                if i >= MAXLINES:
                    break
                line = proc.stdout.readline().decode('utf8')
                out += line
            if proc.poll() != None:
                complete = True
                #get all output
                line = proc.stdout.readline().decode('utf8')
                out += line
                while line != "":
                    if showoutput:
                        sys.stdout.write(line)
                    sys.stdout.write(line)
                    line = proc.stdout.readline().decode('utf8')
                    out += line
                sys.stdout.flush()
                break
##                sys.stdout.write(".")
##                sys.stdout.flush()
            time.sleep(0.2)
        if not complete:
            proc.kill()

    except subprocess.CalledProcessError as e:
        out = e.output
    return out, complete

if __name__ == "__main__":
    print("test run.py")
    cmd = sys.argv[1:]
    s, err = run(cmd, timeout=10, showoutput=False)
    print("output----------\n", s)
    print("end output------")
    print("completed:", err)
