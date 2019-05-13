# esd2wim
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

It's best to use maximum compression, as you'll get a much smaller file with minimal time penalty. 154 second difference between the `none` and `max` options, with more than half the filesize compressed.

![screenshot of output](https://tjone270.org/assets/esd2wim_output.PNG)
