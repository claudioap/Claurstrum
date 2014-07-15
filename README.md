Claurstrum
==========

This is becoming a tool that aims at the purpose of simplifying the creation of pre-production operating system environments.

Its full operation should be the deployment of a GNU/Linux operating system (not being too tied to any in specific, and easily portable) onto a hard-drive, and based on such operating system defaults for its services (http, ftp, dns, etc...) being able to prompt the user for their configurations.

It its **not meant** to be a *Setup Your System For Dummies*, the user should be aware of what its happening if it is meant to be put into production.

Right now the only purpose of such tool is to save a few minutes at every setup, yet preventing an administrator to miss any crucial step.

###Dependencies:
> As of now, these are the dependencies needed to run this program:

> - Python 3.x
> - GTK >=3.12
> - Pygobject
> - Jinja2
> - root account, or 'sudo' Configured as password free (Ugly security flaw, will be fixed later)

----------
###Modules
> The modules which are bundled now with the program are:

> - Introduction (A simple, text based introduction. Very basic, needs to be improved)
> - Install (Will be the integration of [cnchi][1] into this program, the work is not yet merged into this repo)
> - Web server (Incomplete)
> - SSH server (Very, very incomplete)

----------
### Notes
> It isn't yet stable. It may, or may not work.
> It is overall still very poor, its design is modular, and its modules are just a few to help lifting the structure while keeping it simple.
> As of now, this is a project meant for evaluation, it is a trial on something i've never worked on before, it probably has design failures.

[1]:https://github.com/Antergos/Cnchi