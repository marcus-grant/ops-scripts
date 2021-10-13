# Ops/Scripts

A repository of my smaller scripts that I use for developer operations, system administration, terminal utilities and all sorts of helper scripts. Every script in this directory gets its own directory where the main executable file lies in that subdirectory root. In the repository root there's a script that will either list all the executables with absolute path to be linked to their proper binary directory on the host system.


## Managing Scripts

Since all these scripts are meant for linux/unix based systems, including MacOS (unix) and Windows Subsystem (Linux), they will all have a `/usr/local/bin` directory. This is where system administrators are expected to install binaries and scripts and scripts in the root will manage, or make it easier for automation systems like ansible to properly link or copy the correct files in this repository to `/usr/local/bin`.
