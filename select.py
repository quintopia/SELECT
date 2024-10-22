# -*- coding: utf-8 -*-
#SELECT. Interpreter v0.6 by Quintopia
#SELECT. Language by Por Gammer
#TODO: make debug output work with optimized code
try:
    from Tkinter import * 
except ImportError:
    from tkinter import *    
import mpmath
import sys,os
import re,random
from collections import deque,defaultdict
from itertools import islice,repeat
import optparse

myname = "SELECT. interpreter v0.6"


parser = optparse.OptionParser(description=myname+" by Quintopia. SELECT. Language by Por Gammer.", usage="%prog [options] <filename>")
parser.add_option('-v', '--verbose', help="Turn on verbose output.", dest="verbose", action="store_true", default=False)
parser.add_option('-d', '--debug', help="Print out all of memory after every cycle.", dest="debug", action="store_true", default=False)
parser.add_option('-m', '--minify', help="Write back a minified version of the program instead of executing it.", dest="minify", action="store_true", default=False)
parser.add_option('-0', '--no_opt', help="Turn off optimization.", dest="optimize", action="store_false", default=True)
parser.add_option('-k', help="Set the tape initialization value.", metavar="<value>", action="store", dest="val", type=float, default=1)
parser.add_option('-p', help="Set the precision of arithmetic.", metavar="<value>", action="store", dest="precision", type=int, default=100)
(options, args) = parser.parse_args()

#open and load file
if len(args)<1:
    parser.error('Please specify the filename of the SELECT. program to be run.')
filename = args[0]
sys.stdout.write("Reading file...");sys.stdout.flush()
try:
    openfile = open(filename,"r")
except IOError:
    print("File '"+filename+"' not found.")
    sys.exit()
else:
    theFile = openfile.read()
    origFile=theFile
    openfile.close()

#get Canvas dimensions from file, dike them out, create the canvas
pattern = re.compile(r"""\(\s*(?P<x>[0-9]+?)\s*
                          ,\s*(?P<y>[0-9]+?)\s*
                          ,\s*(?P<z>[0-9]+?)\s*\)""",re.VERBOSE)
match=pattern.match(theFile)
if match is None:
    print("Program must begin with (xres,yres,pixsize)")
    sys.exit()
x = int(match.group("x"))
y = int(match.group("y"))
z = int(match.group("z"))
if x%2==0 or y%2==0:
    print('Width and height must both be odd numbers.')
    sys.exit()
w = x*z
h = y*z
centerx = (x+1)/2
centery = (y+1)/2
theFile = theFile.replace(match.group(),"")
sys.stdout.write("done.\n")

#replace all commands with single character for ease of parsing
sys.stdout.write("Compressing...");sys.stdout.flush()
theFile = theFile.replace("\n","")
theFile = re.sub('<<<\$.*%>>>','',theFile)
theFile = theFile.replace('SELECT.','<<<$s%>>>')
theFile = theFile.replace('EXP.','<<<$e%>>>')
theFile = theFile.replace('LOG.','<<<$l%>>>')
theFile = theFile.replace('LEFT.','<<<$<%>>>')
theFile = theFile.replace('RIGHT.','<<<$>%>>>')
theFile = theFile.replace('CONJ.','<<<$*%>>>')
theFile = theFile.replace('LOOP.','<<<$[%>>>')
theFile = theFile.replace('END.','<<<$]%>>>')
theFile = theFile.replace('PRINT.','<<<$.%>>>')
theFile = theFile.replace('GET.','<<<$,%>>>')
theFile = theFile.replace('CLEAR.','<<<$X%>>>')
theFile = theFile.replace('COLOR.','<<<$c%>>>')
theFile = theFile.replace('HALT.','<<<$h%>>>')
#dike out non-commands
theFile = re.sub('%>>>.*?<<<\$','',theFile)
theFile = re.sub('%>>>.*?$','',theFile)
theFile = re.sub('^.*?<<<\$','',theFile)
sys.stdout.write("done.\n")

if options.minify:
    with open(filename,'w') as openfile:
        sys.stdout.write("Writing golfed file...");sys.stdout.flush()
        openfile.write("(%d,%d,%d)"%(x,y,z))
        i=0
        for c in theFile:
            if c=='s': openfile.write("SELECT.")
            elif c=='e': openfile.write("EXP.")
            elif c=='l': openfile.write("LOG.")
            elif c=='<': openfile.write("LEFT.")
            elif c=='>': openfile.write("RIGHT.")
            elif c=='*': openfile.write("CONJ.")
            elif c=='[': openfile.write("LOOP.")
            elif c==']': openfile.write("END.")
            elif c=='.': openfile.write("PRINT.")
            elif c==',': openfile.write("GET.")
            elif c=='X': openfile.write("CLEAR.")
            elif c=='c': openfile.write("COLOR.")
            elif c=='h': openfile.write("HALT.")
            i+=1
            if i%16==0:openfile.write("\n")
        sys.stdout.write("done.\n")
    sys.exit(0)

#optimizations
if options.optimize:
    newFile = "";i=0
    sys.stdout.write("Optimizing");sys.stdout.flush()
    re1 = re.compile(r"e(>+)s")
    re2 = re.compile(r"e(<+)s")
    re3 = re.compile(r"l(>+)s")
    re4 = re.compile(r"l(<+)s")
    re5 = re.compile(r"<{2,}")
    re6 = re.compile(r">{2,}")
    numdots = 1
    while True:
        type=0
        m = re1.search(theFile,pos=i)
        if m is not None: type = 1
        m2 = re2.search(theFile,pos=i)
        if m is None or (m2 is not None and m2.start()<m.start()): m=m2;type = 2
        m2 = re3.search(theFile,pos=i)
        if m is None or (m2 is not None and m2.start()<m.start()): m=m2;type = 3
        m2 = re4.search(theFile,pos=i)
        if m is None or (m2 is not None and m2.start()<m.start()): m=m2;type = 4
        m2 = re5.search(theFile,pos=i)
        if m is None or (m2 is not None and m2.start()<m.start()): m=m2;type = 5
        m2 = re6.search(theFile,pos=i)
        if m is None or (m2 is not None and m2.start()<m.start()): m=m2;type = 6
        if m is not None:
            newFile += theFile[i:m.start()]
            if type == 1:
                newFile += "f"+str(len(m.group(1)))
            elif type == 2:
                newFile += "g"+str(len(m.group(1)))
            elif type == 3:
                newFile += "m"+str(len(m.group(1)))
            elif type == 4:
                newFile += "n"+str(len(m.group(1)))
            elif type == 5:
                newFile += "{"+str(len(m.group(0)))
            elif type == 6:
                newFile += "}"+str(len(m.group(0)))
            else:
                assert False
            i=m.end()
            if i > numdots*len(theFile)/6:
                sys.stdout.write(".");sys.stdout.flush()
                numdots+=1
        else:
            theFile = newFile + theFile[i:]
            sys.stdout.write("done.\n")
            break

#create a Tk instance
sys.stdout.write("Preparing interface...");sys.stdout.flush()
master = Tk()
master.resizable(width = False, height = False)
master.title(myname)

#set precision and default value
#pick a random fill value (very close to 1 to protect against rounding errors when doing things like k^(k^n) )
if options.val==1:
    val = mpmath.mpf(random.uniform(1,1.0000001))
else:
    val = mpmath.mpmathify(options.val)

mpmath.mp.dps=options.precision
verbose=options.verbose
if verbose:
    print("Using tape value: "+mpmath.nstr(val))


if verbose:
    print("Width: "+str(w)+" Height: "+str(h))
canv = Canvas(master, width=w, height=h, background="white")
canv.pack()



#waiting for input
waiting = False

#counter for screen update
cycles=0

#lastop: 0 = none, 1 = exp, 2 = log
lastop=0

#index of the location to be modified by exp or log
argindex=0

#the index into the list
listindex=0

#the list data structure
a=defaultdict(repeat(val).next)

#instruction pointer
pointer=0

#the dictionary of pixels on the canvas
pixdict={}

#tolerance for zeroing
tol = int(0.8*mpmath.mp.dps)
tol = mpmath.mpf('1e-'+str(tol))

#colors
red = 0
green = 0
blue = 0

#clickevent queue
eventqueue = deque([])
def click(event):
    global waiting
    #convert click location to pix address
    x=(event.x-centerx*z)/z+1
    y=(event.y-centery*z)/z+1
    qev = mpmath.mpmathify(complex(x,y))
    if event.type==4 or not eventqueue or eventqueue[-1]!=qev:
        eventqueue.append(qev)
    if waiting:
        waiting=False
        master.after_idle(main)

#bind click
canv.bind("<Button-1>",click)
canv.bind("<B1-Motion>",click)

#create loop point dictionary
brackstack = []
loopdict = {}
for i in range(len(theFile)):
    if theFile[i]=='[':
        brackstack.append(i)
    elif theFile[i]==']':
        if len(brackstack)==0:
            print('Found END. unpreceded by corresponding LOOP. at instruction '+str(i))
            sys.exit()
        b=brackstack.pop()
        loopdict[b]=i
if len(brackstack)>0:
    print('Found LOOP. unterminated by END. at instruction '+str(brackstack[0]))
    sys.exit()
        
def rgb(red, green, blue):
    """ Convert RGB value of 0 to 255 to
    hex Tkinter color string.
    """
    return '#%02x%02x%02x' % (red, green, blue)
    
    
def greporig(num):
    global origFile
    pattern=re.compile("(SELECT\.|EXP\.|LEFT\.|RIGHT\.|HALT\.|COLOR\.|LOG\.|LOOP\.|END\.|PRINT\.|GET\.|CONJ\.)")
    matches=re.finditer(pattern,origFile)
    thematch=islice(matches,num,num+1).next()
    left=origFile.find('\n',max(0,thematch.start()-200))
    right=origFile.find('\n',thematch.end()+150)
    return origFile[left+1:thematch.start()]+'***'+thematch.group()+'***'+origFile[thematch.end():right]
    
    
#define all commands
def select():
    global lastop,a,listindex,argindex,theFile
    if lastop==0:
        print('Parse Error: SELECT. came before corresponding EXP. or LOG. at instruction '+str(pointer))
        print(greporig(pointer))
        left=val
        middle=a[listindex]
        right=val
        if listindex>0:
            left=a[listindex-1]
        if listindex<len(a)-1:
            right=a[listindex+1]
        print('Nearby Tape Values: '+mpmath.nstr(left)+','+mpmath.nstr(middle)+','+mpmath.nstr(right))
        sys.exit()
    elif lastop==1:
        if a[argindex]!=0 or mpmath.im(a[listindex])!=0 or a[listindex]>=0:
            try:
                a[argindex]=mpmath.power(a[argindex],a[listindex])
            except OverflowError:
                print('Number too large to represent. Try increasing precision or moving default tape value closer to 1.')
                print(greporig(pointer))
            a[argindex]=mpmath.chop(a[argindex],tol)
        else:
            a[argindex]=mpmath.mpc('inf')
    else:
        if a[listindex]==1:
            print('Tried to take a log base one at instruction '+str(pointer))
            print(greporig(pointer))
            left=val
            middle=a[listindex]
            right=val
            if listindex>0:
                left=a[listindex-1]
            if listindex<len(a)-1:
                right=a[listindex+1]
            print('Nearby Tape Values: '+mpmath.nstr(left)+','+mpmath.nstr(middle)+','+mpmath.nstr(right))
            sys.exit()
        a[argindex]=mpmath.log(a[argindex],a[listindex])
        #patch up nans when arg is infinite, since we usually want zero for the real part then
        if mpmath.isinf(mpmath.im(a[argindex])) and mpmath.isnan(mpmath.re(a[argindex])):
            a[argindex]=mpmath.mpc(0,mpmath.im(a[argindex]))
        a[argindex]=mpmath.chop(a[argindex],tol)
    oparg=0
def repexpright():
    global a,pointer,listindex
    pass
def repexpleft():
    global a,pointer,listindex
    pass
def expright():
    global pointer,listindex,lastop,argindex
    num = re.match(r"\d*",theFile[(pointer+1):]).group(0)
    pointer+=len(num)
    lastop=1
    argindex = listindex
    listindex+=int(num)
    select()
def expleft():
    global pointer,listindex,lastop,argindex
    num = re.match(r"\d*",theFile[(pointer+1):]).group(0)
    pointer+=len(num)
    lastop=1
    argindex = listindex
    listindex-=int(num)
    select()
def logright():
    global a,pointer,listindex,lastop,argindex
    num = re.match(r"\d*",theFile[(pointer+1):]).group(0)
    pointer+=len(num)
    lastop=2
    argindex = listindex
    listindex+=int(num)
    select()
def logleft():
    global a,pointer,listindex,lastop,argindex
    num = re.match(r"\d*",theFile[(pointer+1):]).group(0)
    pointer+=len(num)
    lastop=2
    argindex = listindex
    listindex-=int(num)
    select()
def repright():
    global pointer,listindex
    num = re.match(r"\d*",theFile[(pointer+1):]).group(0)
    pointer+=len(num)
    listindex+=int(num)
def repleft():
    global pointer,listindex
    num = re.match(r"\d*",theFile[(pointer+1):]).group(0)
    pointer+=len(num)
    listindex-=int(num)
def exp():
    global lastop,argindex,listindex
    lastop = 1
    argindex=listindex
    return
def log():
    global lastop,argindex,listindex
    lastop = 2
    argindex=listindex
def left():
    global listindex,a,val,lastop,argindex
    listindex-=1
def right():
    global listindex,a,val
    listindex+=1
def conj():
    global a,listindex
    a[listindex]=mpmath.conj(a[listindex])
def color():
    global red,green,blue
    red = int(mpmath.fdiv(mpmath.re(a[listindex]),256))
    green = int(mpmath.fmod(mpmath.re(a[listindex]),256))
    blue = int(mpmath.fmod(mpmath.im(a[listindex]),256))
def drawbox():
    global a,listindex,centerx,centery,pixdict,z,red,green,blue,canv,verbose
    if verbose:
        print('Outputting: '+mpmath.nstr(mpmath.chop(a[listindex])))
    if mpmath.isnan(a[listindex]) or mpmath.isinf(a[listindex]):
        return
    try:
        x = int(mpmath.nint(mpmath.re(a[listindex])))+centerx
        y = int(mpmath.nint(mpmath.im(a[listindex])))+centery
        if (x,y) in pixdict:
            canv.delete(pixdict[(x,y)])
            del pixdict[(x,y)]
        pixdict[(x,y)] = canv.create_rectangle(x*z-z+1,y*z-z+1,x*z+1,y*z+1,fill=rgb(red,green,blue),width=0)
    except OverflowError:
        #the number is so huge it's not going to be displayed anyway, so just suppress the error and move on
        pass
def deletepix():
    global pixdict,canv
    canv.delete(ALL)
    pixdict.clear()
    if verbose:
        print("=======Clearing Display=======")
    eventqueue = deque([])                                  #if the screen is cleared, we probably don't want the old events hanging around either
def getmouse():
    global eventqueue,a,listindex,pointer,waiting
    if len(eventqueue)>0:
        a[listindex]=eventqueue.popleft()
    else:
        waiting=True
        pointer-=1
        
def loop():
    global a,listindex,pointer,loopdict
    realpart = mpmath.re(a[listindex])
    impart = mpmath.im(a[listindex])
    if mpmath.workdps(mpmath.mp.dps*3/4)(mpmath.chop)(realpart-impart)>0:
        pointer=loopdict[pointer]
def end():
    global a,listindex,pointer,loopdict
    realpart = mpmath.re(a[listindex])
    impart = mpmath.im(a[listindex])
    if mpmath.workdps(mpmath.mp.dps*3/4)(mpmath.chop)(realpart-impart)<=0:
        pointer=next(key for key,value in loopdict.items() if value==pointer)
def halt():
    global pointer
    pointer=len(theFile)
#create command map (switch-case)
commands = {'s': select,
            'e': exp,
            'l': log,
            '<': left,
            '>': right,
            '*': conj,
            '[': loop,
            ']': end,
            '.': drawbox,
            ',': getmouse,
            'X': deletepix,
            'c': color,
            'h': halt,
            'f': expright,
            'g': expleft,
            'm': logright,
            'n': logleft,
            '{': repleft,
            '}': repright
}
def main():
    #start the eval loop
    global pointer,waiting,cycles
    try:
        c = theFile[pointer]
        commands[c]();
        pointer+=1
        if pointer<len(theFile) and not waiting:
            if cycles<200:
                master.after(0,main)
            else:
                master.after(1,main)
                cycles=0
            cycles+=1
            if options.debug:
                sys.stdout.write(c)
                if c in ['s',',','*']:
                    sys.stdout.write('\n')
                    for n in a:
                        sys.stdout.write(mpmath.nstr(n,4)+", ")
                    sys.stdout.write('\n')
        elif pointer>=len(theFile):
            #TODO:this should really be a dialog saying the program is done, rerun it or quit?
            master.after(3000,quit)
    except KeyboardInterrupt,SystemExit:
        print('Program terminated by user while executing instruction '+str(pointer))
        print(greporig(pointer))
        quit()
    except:
        raise
sys.stdout.write("done.\n");sys.stdout.flush()
master.after_idle(main)
try:
    mainloop()
except KeyboardInterrupt,SystemExit:
    print('Program terminated by user while executing instruction '+str(pointer))
    print(greporig(pointer))
    quit()
except:
    raise
