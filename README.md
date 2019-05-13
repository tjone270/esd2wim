# esd2wim
Converts Windows Electronic Software Distribution (ESD) files to Windows Imaging Format (WIM) files.

```
C:\users\thomas\desktop>esd2wim.exe --help
usage: esd2wim [-h] [--compression {none,fast,max}] [--verbose] esd_file

Convert Windows ESD images to Windows WIM images. Version v0.1

positional arguments:
  esd_file              path to an ESD file

optional arguments:
  -h, --help            show this help message and exit
  --compression {none,fast,max}
                        configure compression (default: max)
  --verbose             show extra information

Created by Thomas Jones - 01/05/2019
```
