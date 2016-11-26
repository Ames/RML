
Receipt Markup Language (RML)

not to be confused with any other R* Markup Language

defines a document syntax for printing to a Mini Thermal Printer


Usage: rml.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  input file (default to stdin)
  -p PORT, --port=PORT  serial device (default to stdout)
  -b BAUD, --baud=BAUD  baud rate (default to 19200)
  -v, --verbose         display extra info
  -t, --test            don't send to serial


Please note: this document is basically my notes; I can't guarantee correctness
 of anything here. Much of it was written before the the program.
 See the online doc page, or read the source.
http://www.sccs.swarthmore.edu/users/12/abiele1/RML/


 --- links ---
 
https://www.adafruit.com/products/597
http://www.ladyada.net/products/thermalprinter/
http://www.sparkfun.com/products/10438
http://electronicfields.wordpress.com/2011/09/29/thermal-printer-dot-net/
http://bildr.org/2011/08/thermal-printer-arduino/
http://tronixstuff.wordpress.com/2011/07/08/tutorial-arduino-and-a-thermal-printer/



--- printing and metrics ---

The paper is 57mm (~2.25") wide.
Printable width is 48mm (~1.9").

Print resolution is 8 dots/mm, giving a total width of 384 dots.

The standard font is 12x24; 384/12=32 chars per line

of course this is affected by margins, character size and spacing, 

the printer line-waps, but doesn't respect word breaks,
so best to manually line wrap.



--- format ---


Most text is sent verbatim
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

RML commands will not necessarily map directly to printer commands;
the interpreter will worry about the details.

some commands with have arguments: {cmd arg1 ...}





comments: {#...}

tab characters will use the printer's tab stops (do we also want a cmd for this?)
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

  {charSpace n} set space between charachters, in dots (ESC SP)

   "Set left blank char nums" (ESC B)
  
  "Select print mode" seems to do things that other cmds can't, but they have to all me set together...
    Reverse
    Updown
    Emphasized     (I'm assuming this is bold, not italics as in html)
    Double Height
    Double Width
    Deleteline     (what is this?) - delete text from the buffer?
  perhaps a commands called soemthing like:
  
  
  
  {style [tall | big] [inv] [ud] [b] [strike]}
    tall  - tall text
    big   - big text (tall and wide)
    inv   - inverted (white on black)
    ud    - upside-down
    b     - bold?
    strike- "deleteline", a strange double-strikethrough effect
  
  
  What is "Set left blank char nums"?  (maybe like leftspace, but in chars)
  
  there seem three places to make the text wider and two to make it taller.
    do they all do the same thing? can they be combined?
  if they all turn out to be there same, perhaps they should be combined?
  
  
  character attributes:
    there are two ways of setting things.
    theoretically, things can either be set individually, or all at once
    
  
  {b}   {/b}     bold, un-bold  (ESC E)
  {ud}  {/ud}    upside-down, un-ud -- success
  {inv} {/inv}   (invert) (white on black), un-invert -- success
  {u n}          underline width. (0=none (default), 1=thin, 2=thick) -- fail
  
  {wide}{/wide}  wide, un-wide -- fail

  
  {charset n}   select character set n (see manual)
  {codetable n} 0:437 1:850 (see manual)


  the enlarge command doesn't seem to do anything
   either i'm overlooking something, my printer is weird, or everyone is crazy.
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
  {bcW n}      set width (2 or 3) (defaults to 2)
  {bcSpace n}  set left space
  {bcLoc n} set text location (0:none 1:above 2:below 3:both)
  {barcode type data} make a barcode with specified data
  
  barcode types:
    UPC-A
    UPC-E  --  i haven't gotten this to work…
    EAN13
    EAN8
    CODE39
    I25
    CODEBAR
    CODE93  -- this doesn't actually take all charachters
    CODE128
    CODE11
    MSI
    
 should the program check for compatibility of data/type? meh...
 there could be a compound command that does some/all of this at once? prob not.


printing parameters? maybe some of them.
     
    "Sleep parameter" (ESC 8)
    
    {heat n m k} "Setting Control Parameter Command" (ESC 7)
        n - max printing dots - unit(8) - default to 7 (64 dots)
        m - heating time - unit(10us) - default to 80 (800us)
        k - heating interval - unit(10us) - defaults to 2 (20us)
    
    {heat 3 240 2} seems to make pretty good graphics
    
    
    {density n m} "Set printing density" (DC2 #)
        n - printing density = .5+.05*n
        m - printing break time = 250us*m
    
test page - why not?
    {testPage} -- fail?

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
  {imageR file.png}
    rotates the image 90˚
  
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

I haven't implemented the following. Maybe later:
  -s         show device status and exit (normally prints info unless -q)





