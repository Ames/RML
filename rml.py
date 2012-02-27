

import sys
from math import ceil
from string import hexdigits

# argparse is only for python 2.7
from optparse import OptionParser


# a little class for basically storing global things
class IOClass:
    def __init__(self):
        self.verbose = False
        self.dry = False
        self.port = False

myIO=IOClass()


def main():
    
    options, args = parseArgs()
    
    myIO.verbose=options.verbose
    myIO.dry=options.dry
    
    if(options.file):
        # they want to read a file
        doc = open(options.file)
    else:
        # we'll listen to stdin
        doc = sys.stdin


    if(options.port):
        # they want to use a serial port
        try:
            import serial
        except:
            err("serial interface not supported")
            return
        
        try:
            myIO.port=serial.serial_for_url(options.port, baudrate=options.baud)
        except IOError as error:
            err(str(error))
            err("SERIAL PORT FAIL! falling back to dry mode")
            myIO.dry=True

    else:
        err("no port specified. using stdout")
        myIO.port = sys.stdout
    
    parse(doc)
    
    doc.close()
    
    if not myIO.dry:
        myIO.port.close()    

def parse(doc):
    
    cmdMode=False
    cmd=""
    
    while(1):
        c=doc.read(1) # read 1 char
        
        if c == "": # EOF
            break
        
        # usually we want to just send the charachter
        #  unless we are in command mode
        #  or the c is {
        
        if cmdMode:
            if c == '}':
                cmdMode = False
                # end of command. time to parse it.
                handleCmd(cmd.strip());
                continue
            
            # append to cmd
            cmd=cmd+c
            continue
        
        if c == '{':
            # entering command mode
            
            cmdMode = True
            cmd=""
            continue
        
        # we'll allow characters 0x20 thru 0x7E and 0x0A (LF)
        # all others are ignored.
        
        #print c
        if (ord(c)>=0x20 and ord(c)<=0x7E) or ord(c)==0x0A:
            # send the char! do eet!
            devSend(c)
    
    

def parseArgs():

    parser = OptionParser()
    
    parser.add_option("-f", "--file", dest="file", default=False,
                      help="input file (default to stdin)", metavar="FILE")
                      
    parser.add_option("-p", "--port", dest="port", default=False,
                      help="serial device (default to stdout)")
                      
    parser.add_option("-b", "--baud", dest="baud", default="19200",
                      help="baud rate (default to 19200)")
    
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="display extra info")
    
    parser.add_option("-t", "--test",
                      action="store_true", dest="dry", default=False,
                      help="don't send to serial")
    
    parser.add_option("-s", "--status",
                      action="store_true", dest="doStatus", default=False,
                      help="show device status and exit")
    
    return parser.parse_args()



def handleCmd(command):
    
    # most commands map directly to device commands
    # some take arguments
    
    #if command=='{':
    #    devSend('{')
    
    # the first thing is the command. Later things are arguments.
    cmd=command.split()
    
    valid=False
    
    # empty
    if len(cmd)==0:
        return
    
    name=cmd[0].lower()
    
    # commands that are directly mapped
    if name in theCommands:
        sCmd=theCommands[name]
        
        info(sCmd[1])

        devSend(sCmd[0])
        
        valid=True
    
    # things that take one number
    if name in oneArg:
        if len(cmd)==1:
            devSend(chr(oneArg[name]))
        if len(cmd)==2:
            devSend(chr(int(cmd[1])))
        
        valid=True

    if name == 'e':
        h=0
        w=0
        if 'h' in command or 'H' in command:
            h=1
        if 'w' in command or 'W' in command:
            w=1
        
        devSend(chr(h*0x01 + w*0x10))
        
    
    # leftSpace has special parsing
    if name == 'leftSpace':
        if len(cmd)==1:
            devSend(chr(0));
        if len(cmd)==2:
            devSend(twoBytes(int(cmd[1])));

    # barcode - more special
    if name == 'barcode':
        if len(cmd)==3:
        
            type=0 # type defaults to UPC-A
            
            if cmd[1].upper() in bcTypes:
                type=bcTypes.index(cmd[1])
            
            dat=cmd[2]
            
            
            info('barcode type='+str(type)+' data='+dat)
        
            # we'll use "format 2" syntax, with explicit length
            devSend('\x1D\x6B'+str(type)+chr(len(dat))+dat)
            
            # I think we should wait for the data to print
            
    if name == 'image':
        if len(cmd)>1:
            # allows spaces in the file name
            doImage(command.split(' ',1)[1])

    if name[0] == 'x':
        # no other commands can start with x
        
        dat=command.upper();
        
        # remove things that aren't hex digits
        dat="".join([c for c in dat if c in hexdigits])
        
        # pad with 0 if necessary
        if len(dat)%2==1:
            dat=dat+'0'
        
        info("eXplicit heX: "+dat)
        
        devSend(dat.decode('hex'))
    

def doImage(path):
    try:
        from PIL import Image, ImageOps
    except:
        err("please install Python Image Library")
        return
    
    try:
        img = Image.open(path)
    except:
        err("file "+path+" not found!")
        return
    

    # convert to greyscale, invert, convert to B+W
    img=ImageOps.invert(img.convert('L')).convert('1')
    
    # figure out the desired W and H
    
    if img.size[0]<=384:
        # if the image is less than the max, 
        # round the width up to a multible of 8
        img=img.crop((0,0,int(ceil(img.size[0]/8.)*8),img.size[1]))
    else:
        # if the image is larger than the max,
        # scale it down to the max
        img=img.resize((384,img.size[1]*384/img.size[0]))
    
    img.show()
    
    # stringify
    imgStr=img.tostring()
    
    info(path+' '+str(img.size))
    
    # (GS v)
    devSend('\x1D\x76\0\0'+twoBytes(img.size[0]/8)+twoBytes(img.size[1])+imgStr)
    
    # I think we should wait for the data to send/print
    

# some commands take a number (n) as two bytes (nL nH)
def twoBytes(num):
    #         low byte     high byte
    return chr(num%256)+chr(num//256)

# informative messages
# print to stderr if verbose
def info(s):
    if myIO.verbose:
        sys.stderr.write(s+'\r\n')

# important messages
# print to stderr
def err(s):
    sys.stderr.write(s+'\r\n')

# send data to printer
def devSend(s):
    #err(s)
    if not myIO.dry: # (wet?)
        myIO.port.write(s)
        #sys.stdout.write(s)

# commands that map directly to device commands
theCommands={
    'feedL':('\x1B\x64'    ,'feed (lines)'),
    'feedD':('\x1B\x4A'    ,'feed (dots)'),
    
'lineSpace':('\x1B\x33'    ,'line space'),
'leftSpace':('\x1D\x4C'    ,'left space'),

   'left'  :('\x1B\x61\x00','align left'),
   'center':('\x1B\x61\x01','align center'),
   'right' :('\x1B\x61\x02','align right'),

        'b':('\x1B\x20\x01','bold'),
       '/b':('\x1B\x20\x00','un-bold'),

#        'b':('\x1B\x45\x01','bold'),
#       '/b':('\x1B\x45\x00','un-bold'),

        'w':('\x1B\x0B'    ,'wide'),
       '/w':('\x1B\x14'    ,'un-wide'),
    
       'ud':('\x1B\x7B\x01','updown'),
      '/ud':('\x1B\x7B\x00','un-updown'),
    
        'i':('\x1D\x42\x01','invert'),
       '/i':('\x1D\x42\x00','un-invert'),
    
        'u':('\x1B\x27'    ,'underline'),
        
        'e':('\x1D\x21','enlarge'),
#        'e':('\x1D\x21\x00','no enlarge'),
#       'eh':('\x1D\x21\x01','enlarge H'),
#       'ew':('\x1D\x21\x10','enlarge W'),
#      'ehw':('\x1D\x21\x11','enlarge H & W'),

  'charset':('\x1B\x52'    ,'charachter set'),
'codetable':('\x1B\x74'    ,'code table'),

    'bcLoc':('\x1D\x48'    ,'barcode text location'),
      'bcH':('\x1D\x68'    ,'barcode height'),
      'bcW':('\x1D\x77'    ,'barcode width'),
  'bcSpace':('\x1D\x78'    ,'barcode left space'),

 'testPage':('\x12\x54'    ,'test page'),
}

# commands that take one argument, and the default value
oneArg={
   'u':0,
   'feedL':0,
   'feedD':0,
   'lineSpace':0,
   'charset':0,
   'codetable':0,
   'bcLoc':0,
   'bcH':50,
   'bcW':3,
   'bcSpace':0,
}

# barcode types
bcTypes=[
    'UPC-A',
    'UPC-E',
    'EAN13',
    'EAN8',
    'CODE39',
    'I25',
    'CODEBAR',
    'CODE93',
    'CODE128',
    'CODE11',
    'MSI'
]


# go.
main()
