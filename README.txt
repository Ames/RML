

Receipt Markup Language (RML)

not to be confused with any other R* Markup Language

defines a document syntax for printing to a Mini Thermal Printer


 --- links ---
 
https://www.adafruit.com/products/597
http://www.ladyada.net/products/thermalprinter/
http://www.sparkfun.com/products/10438
http://electronicfields.wordpress.com/2011/09/29/thermal-printer-dot-net/
http://bildr.org/2011/08/thermal-printer-arduino/
http://tronixstuff.wordpress.com/2011/07/08/tutorial-arduino-and-a-thermal-printer/


--- format ---

header? probably not. would specify print params, etc.

Most text is sent verbatum
special commands are wrapped in curly braces: {command}

There are several different kinds of commands.
The docs specify the following categories:
  Print
  Line spacing
  Character (user-defined chars)
  Bit Image
  Init (one command)
  Status
  Bar Code
  Board Para

RML commands will not necissarily map directly to printer commands;
the interpreter will worry about the details.

some commands with have arguments: {cmd arg1 ...}


it's unclear at this point whether the printer automatically line wraps.
I will assume no.



comments: {#...}

tab charachters will use the printer's tab stops (do we also want a cmd for this?)
LF will do LF
TAB will to TAB (HT)
CR ignored
FF do we want a cmd for this? {ff}

use {x DEAD BEEF} to send raw data (hex)
 (any hex char after the x is used)

use {x7B} to make "{"

 --- commands ---
  {init}  initialize printer. clears buffer, resets modes, delete user chars.
    maybe the program will always do this at the beginning anyway.
 
  {feedL n} print and feed n lines
  {feedD n} print and feed n dots
    
  {lineSpace [n]} set line spacing to n dots. no argument for default (32)
  
  {(left,center,right)} set alignment
  
  {leftSpace n} set left spacing (unit:0.125mm for now) (why does the spec have two cmds for this?)


   "Set left blank char nums" (ESC B)
  
  "Select print mode" seems to do things that other cmds can't, but they have to all me set together...
    Reverse
    Updown
    Emphasized     (I'm assuming this is bold, not italics as in html)
    Double Height
    Double Width
    Deleteline     (what is this?) - delete text from the buffer?
  perhaps a commands called soemthing like:
  {style [arg1 [arg2 [...]]]} 
  
  What is "Set left blank char nums"?  (maybe like leftspace, but in chars)
  
  there seem three places to make the text wider and two to make it taller.
    do they all do the same thing? can they be combined?
  if they all turn out to be there same, perhaps they should be combined?
  
  
  {b}  {/b}     bold, un-bold  (why are there two commands: (ESC E) and (ESC SP)
  {w}  {/w}     wide, un-wide
  {ud} {/ud}    upside-down, un-ud
  {i}  {/i}     (invert) (white on black), un-invert
  {u n} underline width. (0=none (default), 1=thin, 2=thick)
  
  {charset n}   select charachter set n (see manual)
  {codetable n} 0:437 1:850 (see manual)

  {e [h] [w]} enlarges text width or height. ({e} is no enlarge)
        e.g. "{e h}", "{e HW}", or "{e w h}"

do we care about user-defined chars?  maybe. maybe later.


bar codes.
bar codes have the following properties:
  
  printing position of human readable characters (above, below, both, neither)
  height (1-255 dots)
  width (2 or 3)
  left space
  type (11 options)
  content (different types allow different lengths)
  what are the "Remarks"? allowed char ranges?
  
  it'd be nice to be able to optionally set these options
  
  {bcH n}      set height to n dots (defaults to 50)
  {bcW n}      set width (2 or 3) (defaults to 3)
  {bcSpace n}  set left space
  {barcode type data} make a barcode with specified data
  
  barcode types:
    UPC-A
    UPC-E
    EAN13
    EAN8
    CODE39
    I25
    CODEBAR
    CODE93
    CODE128
    CODE11
    MSI
    
 should the program check for compatibility of data/type? meh...
 there could be a compound command that does some/all of this at once? prob not.


printing parameters? maybe some of them.
    "Setting Control Parameter Command" (ESC 7) 
    "Sleep parameter" (ESC 8)
    "Set printing density" (DC2 #)
    
test page - why not?
    {testPage}

bitmap images.
  
  
  there are a few methods for printing images.
  
  
  the first method is for small images, e.g. for special charachters
  
      "Select bit-image mode" (ESC *)
        loads up to 1024 bytes into memory, sets a mode (8/24 dots, 102/203 dpi)
      
      "Print downloaded bit image" (GS /)
        print the image [downloaded by (ESC *) ?] with H and/or V scaling
    
    
  the second method is for medium images, with width and height
  
       "Define downloaded bit image" (GS *)
          loads a bitmap into memory, define x and y (width and height)
          
       "Print bitmap" (GS v 0)
           seems to download and print a bitmap, with H and/or V scaling
           H and V are wach given two chars, as if thery're expecting big images
           
           
       "位图打印" "Bitmap print" (DC2 *)
           prints an image with w and h, data looks optional;
                                        perhaps can use data from (GS *)
  
  
  finally,there are the full-width methods.
  
      "Print MSB Bitmap" (DC2 V)
      "Print LSB Bitmap" (DC2 v)
        print the (optional?) data. Width is 48 bytes (384px). n (heigth) is spec
  
 
 
 it's unclear how the first two are placed. The first might be inline with text,
    or placed with text?? 
 
 
 
 got that?
 
  
  
  In any event, the image command will probably work like this:
  
  {image file.png}
    there might be max dimensions: I guess max width is 384
    there can't be '}' in the filename
  
  {imageFull file.png}
    do we want this?
      basically, it would force the image to be 384 wide; 
        
  
that's basically that.


 --- printing utility ---

The printing utility will be a simple unix-style utility.

input will come from a specified file, or stdin
output will go to a specified serial device, or stdout

flags:
  -f file    input file
  -p file    output port (or file?)
  -b rate    output baudrate (default to 19200) (shouldn't be necessary)
  -v         verbose
  -q         quiet
  -t         test (parse file, bit don't actually send any commands)
  -s         show device status and exit (normally prints info unless -q)





