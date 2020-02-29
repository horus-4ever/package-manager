# package-manager
It is a very simple package manager, that can be used to do updates.
It is quite simple to use, since there are only two functions:
- create(input_directory, output_file)
- install(input_file, destination_directory)

The input_directory must be an absolute pathname.

This code works fine up to 14Gb of datas (I didn't try more, but it should work on larger datas). Since it is written in Python, it can slow down your computer during creation or installation of packages (because memory isn't freed directly).
