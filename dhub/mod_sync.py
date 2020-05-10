from runrun import git, get_branch

def sync(insist=False):
    branch=get_branch()
    git("fetch origin", show=True, debug=True)
    git("reset --hard origin/{0}".format(branch), show=True, debug=True)