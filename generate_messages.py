#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""generate_messages

Send initialization commands to the driver  
 
Usage:
  generate_messages.py -h | --help
  generate_messages.py (-c <FILENAME> )
   
Options:
  -h --help                      Show this screen.
  -c --ctl_channel=<FILENAME>    Set control channel filename
"""

import struct 
import re
from docopt import docopt

CTL_CHANNEL_NAME = None # /sys/kernel/debug/systemtap/yalas_drv/.cmd"

def write_file(data):
    with open(CTL_CHANNEL_NAME, "wb") as f:
        f.write(struct.pack('{0}B'.format(len(data)), *data))
        
def write_words(data):
    with open(CTL_CHANNEL_NAME, "wb") as f:
        for d in data:
            f.write(struct.pack('<I', d))
    
def write_relocate_string(f, s, size):
    f.write(s)
    padding = size - len(s)
    for _ in range(padding):
        f.write('\x00')
    
def write_relocate(module_name, symbol_name, address):
    STP_MODULE_NAME_LEN = 128
    STP_SYMBOL_NAME_LEN = 128
    
    with open(CTL_CHANNEL_NAME, "wb") as f:
    # STAP_RELOCATE (9)
        f.write(struct.pack('<I', 9))
        write_relocate_string(f, module_name, STP_MODULE_NAME_LEN)
        write_relocate_string(f, symbol_name, STP_SYMBOL_NAME_LEN)
        f.write(struct.pack('<Q', address))
            

    
if __name__ == '__main__':
    try:
        '''
        This is an emulation of staprun logic minus insmod, stapio, access rights
        '''
        arguments = docopt(__doc__, version='c2stp.py')
    
        CTL_CHANNEL_NAME = arguments['--ctl_channel']
        
        print "STP_READY (8)"
        write_words([8])
        
        print "STP_PRIVILEGE_CREDENTIALS (15), see pr_all"
        write_words([15, 14])
        
        print "STP_RELOCATION (can be .__start in PPC)"
        for line in open("/proc/kallsyms", "r"):
            m = re.match(r'(\S+) . (\S+)$', line)
            if m:
                if m.group(2) == "_stext": 
                    write_relocate("kernel", m.group(2), int(m.group(1), 16))
                    break;
                
                    
        # STP_TZINFO (14)
        # TODO
        
        # STP_BUF_INFO (10) deprecated
        #write_words([10])
    
        print "STAP_START (0)"
        write_words([0, 0, 0])
    
    except Exception as e:
        print e        
