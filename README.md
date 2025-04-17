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



