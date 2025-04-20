## Starting
### goal, motivation and main use cases
I have many versions of python and virtual environments created by pyenv and conda and possibly  
 venv and virtualenv(or other tools!), for many reason, I need to search in all of them to see if   
 given pkgs are installed and for which python versions and in which env 

So I want to search different python version and environments for some packages.
Do we have a tool or script for this? seems like we dont, so lets create it
- we are searching our installed python versions and environments and we call them env and version for simplicity
    - note that each version could have many environments too
    - basically we want to searchj for everything that could have its site-packages   

### features
- maybe a package with CLI. 
- make it more modular and robust and reusable.
- handle different type of python versions or envs
    - pyenv version and pyenv virtualenvironments
    - conda environments
    - normal python versions and venv
    - pipx envs
- handle different kind of search: 
    - search for the exact name of package
    - find or packages related to given keyword(containing it)

### some discussion and decicion making

- searching and checking could be implemented many ways, which can be divided in two main paradigms:
    - activating each env or version and use its internal tools to search:
        - using pip show or pip list of env or version
        - calling `pkg_name --version` for pkg with CLI
        - trying to import it, and use the result of this
    - looking into file system and find directories related to different env and versions and find  
    directories of installed pkgs and search in them
- maybe the best idea is to do the searching through file system, and test it by directly  
activating related python versions/envs and checking if the things find through searching is right
- important point: we could(and probaly should) record the information about different python envs  
and their location and their installed package directories
- keep a list of python envs
- for each python env, we could also keep more information:
    - where is its bin executable
    - its prefix and base bin executable and weather it is a venv
    - which app has created it(pyenv, conda, pythn venv or even virtualenv)
    - its installation type and directories of its installed package, specially site-packages
    - its lib directory location and its sys.path
    - weather it is user installation and its userbase and user site
    - 

- we could have function to update our information about envs


## Design and architecture
### Environment class
- lets have Environment class, to manage important info about each python version or environment
#### features
- add to_dict and from_dict method to make saving and loading each environment info easy
- save and load to a cache file, in json format
- I want different ways of finding info of each env(instance of Environment class)
    - by activating the env python using a suprocess
    - by searching file system 
    - populate env attributes ased on installation scheme used for env(according to python doc)
        - One common structure is # prefix/
        - prefix
            - bin
                - python -> python3.x or base_prefix/bin/python3.x(which is base_in_path)
            - lib
                - python3.x
                    - site-packages
            - pyenv.cfg
