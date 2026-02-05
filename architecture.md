# General
Command line utility dirq. Main principle single command util to navigate in folder structure. Config with following: name, depth, path. Came up with human readable, but simple to parse structure. 

# dirq subcommands
- save [path, optional default is current] [depth, optional, default is 0] [name, optional, default path basename]. Save information to config. Error if name duplicated.
- delete <path>|<name>. Remove folder by name or path
- init config. Generate default empty config in $XDG_CONFIG_HOME/dirq/config.rc
- init shell <fish>|<bash>|<zsh>. Generate function to dirq navigate (so we can change current folder after selection) and autocompletions.
- navigate. Read config, generate list of all pathes, send to fzf to select. After user selection navigate to selected folder. Ctrl+C gracefull stop (no error)

# naviation scenario
Read config file, generate folders list send to fzf for selection. Navigate to selected folder. Logic to convert folder list before sending to fzf
## Path conversion logic
Example we have a structure in folder /Users/Developer/sources, depth is 2 and name source
- ssource 1
    - sub source 1-1
    - sub source 1-2
- ssource 2
- ssource 3
    - sub source 3-1
It should diplay following list of folders:
source:ssource 1/sub source 1-1
source:ssource 1/sub source 1-2
source:ssource 2
source:ssource 3/sub source 3-1

After selection navigation to original folder should happen. 

For depth 1 only direct subfolders displayed. Logic is same as for depth 2

For depth 0 displayed folder itself. For example for ~/specific-folder, depth 0 and name specific-folder-name diplayed
specific-folder-name:/User/username/specific-folder

Navigation works same way