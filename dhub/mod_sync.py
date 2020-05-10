from runrun import git, get_branch

def sync(insist=False, debug=False, show=False):
    branch=get_branch()
    git("fetch origin", show=show, debug=debug)
    git("reset --hard origin/{0}".format(branch), show=show, debug=debug)