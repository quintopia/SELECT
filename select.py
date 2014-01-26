# -*- coding: utf-8 -*-
try:
    from Tkinter import * 
except ImportError:
    from tkinter import *    
import mpmath
import sys,os
import re,random
from collections import deque
from itertools import islice
import optparse

myname = "SELECT. interpreter v0.3"
#create a Tk instance
master = Tk()
master.resizable(width = False, height = False)
master.title(myname)

parser = optparse.OptionParser(description=myname+" by Quintopia. SELECT. Language by Por Gammer.", usage="%prog [options] <filename>")
parser.add_option('-v', '--verbose', help="Turn on verbose output.", dest="verbose", action="store_true", default=False)
parser.add_option('-k', help="Set the tape initialization value.", metavar="<value>", action="store", dest="val", type=float, default=1)
parser.add_option('-p', help="Set the precision of arithmetic.", metavar="<value>", action="store", dest="precision", type=int, default=100)
(options, args) = parser.parse_args()
#open and load file
if len(args)<1:
    parser.error('Please specify the filename of the SELECT. program to be run.')
filename = args[0]
try:
    openfile = open(filename,"r")
except IOError:
    print("File '"+filename+"' not found.")
    sys.exit()
else:
    theFile = openfile.read()
    origFile=theFile
    openfile.close()
#set precision and default value
#pick a random fill value (very close to 1 to protect against rounding errors when doing things like k^(k^n) )
if options.val==1:
    val = mpmath.mpf(random.uniform(1,1.0000001))
else:
    val = mpmath.mpmathify(args['val'])

mpmath.mp.dps=options.precision
verbose=options.verbose
if verbose:
    print("Using tape value: "+mpmath.nstr(val))

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
if verbose:
    print("Width: "+str(w)+" Height: "+str(h))
canv = Canvas(master, width=w, height=h, background="white")
canv.pack()

#replace all commands with single character for ease of parsing
theFile = theFile.replace("\n","")
theFile = theFile.replace(" ","")
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
a=[val]

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
theFile = list(theFile)
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
            a[argindex]=mpmath.power(a[argindex],a[listindex])
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
    if listindex==0:
        a.insert(0,val)
        if lastop>0:
            argindex+=1
    else:
        listindex-=1
def right():
    global listindex,a,val
    if listindex==len(a)-1:
        a.append(val)
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
    x = int(mpmath.nint(mpmath.re(a[listindex])))+centerx
    y = int(mpmath.nint(mpmath.im(a[listindex])))+centery
    if (x,y) in pixdict:
        canv.delete(pixdict[(x,y)])
        del pixdict[(x,y)]
    pixdict[(x,y)] = canv.create_rectangle(x*z-z+1,y*z-z+1,x*z+1,y*z+1,fill=rgb(red,green,blue),width=0)
def deletepix():
    global pixdict,canv
    canv.delete(ALL)
    pixdict.clear()
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
    if realpart>impart and not mpmath.almosteq(realpart,impart):
        pointer=loopdict[pointer]
def end():
    global a,listindex,pointer,loopdict
    realpart = mpmath.re(a[listindex])
    impart = mpmath.im(a[listindex])
    if realpart<=impart or mpmath.almosteq(realpart,impart):
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
}
def main():
    #start the eval loop
    global pointer,waiting,cycles
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
master.after_idle(main)
mainloop()

