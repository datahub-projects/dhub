from runrun import git, get_branch

def mod(message=None, insist=False, debug=False, show=False):
    if message:
        git("commit --all --amend --message {0}".format(message), show=show, debug=debug)
    else:
        git("commit --all --amend --reuse-message HEAD", show=show, debug=debug)
    git("push -f", show=show, debug=debug)

def sync(insist=False, debug=False, show=False):
    branch=get_branch()
    git("fetch origin", show=show, debug=debug)
    git("reset --hard origin/{0}".format(branch), show=show, debug=debug)
