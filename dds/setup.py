#!/usr/bin/python

from distutils.core import setup

VERSION = file('debian/changelog').readline().split()[1][1:-1]

setup(name         = 'icedds',
      version      = VERSION,
      description  = 'IceDDS',
      author       = 'Alicia Serrano Sanchez',
      author_email = 'Alicia.Serrano1@alu.uclm.es>',
      license      = 'GPL v2 or later',
      data_files   = [('/usr/bin', ['icedds']),
                      ('/usr/share/slice/icedds', ['slices/DDS.ice']),
                      ('/usr/share/doc/icedds', ['README', 'example.cfg'])],
      packages     = ['IceDDS']
      )
