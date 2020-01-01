## ver -- versioning for the masses

# commands:

* status [sub1[, sub2]]

Print useful information about the project and all its followed submodules
names, paths, remotes
Modified, added, deleted, renamed
list of non-followed submodules

* follow [sub1[, sub2]]

Initiialize and checkout the specified submodules

If no submodules are specified, prompt user whether to follow all submodules (ovveride prompt with -y)

Looks for exact path match first, then assumes subs are specified by last path component only (ie data/train can be specified as train if there are no conflicts)

If data needed is not cached, prompt user that data needs to be downloaded (override prompt with -y)

* untracked

Print a list of all untracked files and folders, recursively in all submodules

* up [commit|branch]

update project from remote (pull) and (recursively) all followed submodules to sync with project

If data needed is not cached, prompt user that data needs to be downloaded (override prompt with -y or -yy)

If untracked data will be clobbered, prompt user (override prompt with -yy)

* save

push main project and (recursively) all subprojects to respective remotes

Prompt user if there will be a significant amount of data to upload (override prompt with -y)

* clone <remmote> [sub1[, sub2]]

Recursively clone a project and all specified submodules (and follow them)

If no subs specified, show user a list and prompt for which ones to clone & follow (override prompt with -a as in all)

* see [commit|branch

Report status of working tree vs latest on remote (or branch, commit)

No diffs, fast-forward, merge commit (if up'd), conflict (if saved)

For all submodules recursively

