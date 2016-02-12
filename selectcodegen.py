# -*- coding: utf-8 -*-
#SELECT. Code Generator v0.6 by Quintopia
# All code-generating functions in this file are right-growing, meaning they make the following guarantees:
# * They do not read or write cells to the left of the current cell at call time.
# * The result that the algorithm computes will be contained in the rightmost cell clobbered by the algorithm.
# * The current cell upon completion will be the one containing the answer.
# * They do not clobber the arguments passed to them (or rather, if they do, they restore them before returning)
# At call time, you must be able to guarantee the current cell is the leftmost argument and that there are 
# sufficiently many unclobbered cells to the right of the current cell.
# See comments inside individual generating functions for info on which cells need to be untouched, which are clobbered,
# and what values they contain upon algorithm completion.
# To use a left-growing algorithm instead, use startleftgr() and endleftgr(). 
# E.g.: startleftgr();add();endleftgr() writes out a left-growing addition algorithm with the sum leftmost

#TODO: update docs for: switch, drawStringLiteral, drawLetterXY, drawdigitXY, repeat, endRepeat, opposite, reciprocal, intdiv, mod


from re import sub,DOTALL,finditer
from itertools import dropwhile,islice
import sys

version = 0.6
#the list of strings that becomes the program
l=[]
#the height of the display
h=0
#the width of the display
w=0
#the position (in the complex plane) of the top row on the display
toploc=0
#the position (in the complex plane) of the left column on the display
leftloc=0
#the number of spaces to put at the beginning of a line
indentlevel=0
#a table of named tape locations
vardict = {}
#a list of variables that MUST be saved by a loop (e.g. internal variables created by a loop)
mustsave = []
#the "absolute" location of the tape head (maybe)
offset = 0
#set to True to prevent any code output. set by turnon() and turnoff()
dike = False
#set to True to allow LEFT. and RIGHT. to be output. only becomes true once a SELECT., CONJ., or GET. are output, as these are the only commands which can change the tape. prevents extraneous tapehead
#motion at the beginning of a program.
domove = False
#painstakingly drawn pixelmaps of printable ASCII characters. based on 7pt Deja Vu Sans Mono (with the anti-aliasing removed)
letterforms = {' ':[],
               '!':[(0,-4),(0,-3),(0,-2),(0,-1),(0,0),(0,2)],
               '"':[(1,-4),(1,-3),(-1,-4),(-1,-3)],
               '#':[(0,-4),(2,-4),(-1,-3),(1,-3),(-2,-2),(-1,-2),(0,-2),(1,-2),(2,-2),(3,-2),(-1,-1),(1,-1),(2,0),(1,0),(0,0),(-1,0),(-2,0),(-3,0),(1,1),(-1,1),(0,2),(-2,2),(0,3),(-2,3)],
               '$':[(0,-4),(0,-3),(1,-3),(2,-3),(2,-3),(-1,-3),(-2,-2),(-2,-1),(-1,-1),(0,-2),(0,-1),(0,0),(1,0),(2,0),(2,1),(1,2),(0,1),(0,2),(0,3),(-1,2),(-2,2)],
               '%':[(-2,-4),(-3,-3),(-2,-2),(-1,-3),(-2,0),(-1,0),(0,-1),(1,-1),(1,1),(0,2),(1,3),(2,2),(2,-2),(-3,1),],
               "'":[(-1,-4),(-1,-3)],
               '(':[(0,-5),(0,3),(-1,2),(-1,1),(-1,0),(-1,-1),(-1,-2),(-1,-2),(-1,-3),(-1,-4),],
               ')':[(-1,-5),(-1,3),(0,2),(0,2),(0,1),(0,0),(0,-1),(0,-2),(0,-2),(0,-3),(0,-4),],
               '*':[(-3,-4),(-2,-3),(-2,-2),(-3,-1),(-1,-4),(-1,-3),(-1,-2),(-1,-1),(0,-3),(0,-2),(1,-4),(1,-1),],
               '+':[(-1,3),(-1,2),(-3,1),(-2,1),(-1,1),(0,1),(1,1),(-1,0),(-1,-1),],
               ',':[(-1,5),(-1,4),],
               '-':[(-1,1),(0,1),],
               '.':[(-1,2)],
               '/':[(0,-4),(-1,-3),(-1,-2),(-2,-1),(-2,0),(-2,1),(-3,2),],
               '0':[(-1,-4),(0,-4),(-2,-3),(1,-3),(-2,-2),(1,-2),(-2,-1),(0,-1),(1,-1),(-2,0),(1,0),(-2,1),(1,1),(-1,2),(0,2),],
               '1':[(-1,-4),(0,-4),(0,-3),(0,-2),(0,-1),(0,0),(0,1),(0,2),(-1,2),(1,2)],
               '2':[(-2,-3),(-1,-4),(0,-4),(1,-3),(1,-2),(0,-1),(-1,0),(-2,1),(-2,2),(-1,2),(0,2),(1,2),],
               '3':[(-2,-3),(-1,-4),(0,-4),(1,-3),(1,-2),(0,-1),(-1,-1),(1,0),(1,1),(0,2),(-1,2),(-2,1),],
               '4':[(0,-4),(0,-3),(0,-2),(0,-1),(0,0),(0,1),(0,2),(1,1),(-1,1),(-2,1),(-2,0),(-1,-1),(-1,-2),],
               '5':[(-2,-4),(-1,-4),(0,-4),(1,-4),(-2,-3),(-2,-2),(-2,-1),(-1,-1),(0,-1),(1,0),(1,1),(0,2),(-1,2),(-2,2),],
               '6':[(0,-4),(1,-4),(-1,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,1),(1,0),(0,-1),(-1,-1),],
               '7':[(-2,-4),(-2,-4),(-1,-4),(0,-4),(1,-4),(1,-3),(0,-2),(0,-1),(0,0),(-1,1),(-1,2),],
               '8':[(-1,-4),(0,-4),(-2,-3),(1,-3),(-2,-2),(1,-2),(-1,-1),(0,-1),(-2,0),(1,0),(-2,1),(1,1),(-1,2),(0,2),],
               '9':[(-1,-4),(0,-4),(-2,-3),(1,-3),(-2,-2),(1,-2),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,2),(-1,2),(-2,2),],
               ':':[(-1,-2),(-1,2)],
               ';':[(-1,-2),(-1,2),(-1,3),(-1,4)],
               '<':[(-2,-1),(-2,0),(-1,-1),(-1,0),(0,-1),(0,0),(1,-2),(1,1),(2,-2),(2,1),],
               '=':[(-3,-1),(-2,-1),(-1,-1),(0,-1),(1,-1),(-3,1),(-2,1),(-1,1),(0,1),(1,1),],
               '>':[(-2,-2),(-2,1),(-1,-2),(-1,1),(0,-1),(0,0),(1,-1),(1,0),(2,-1),(2,0),],
               '?':[(-2,-4),(-1,-4),(0,-4),(1,-3),(0,-2),(-1,-1),(-1,0),(-1,0),(-1,2),],
               '@':[(-1,-3),(0,-3),(-2,-2),(1,-2),(-2,-1),(1,-1),(0,-1),(-2,0),(0,0),(1,0),(0,1),(1,1),(-2,1),(-2,2),(-1,2),(-1,3),(0,3),],
               'A':[(-1,-4),(0,-4),(-1,-3),(0,-3),(-2,-2),(1,-2),(-2,-1),(1,-1),(-2,0),(1,0),(-2,1),(-1,1),(0,1),(1,1),(1,2),(-2,2),],
               'B':[(-2,-4),(-1,-4),(0,-4),(1,-3),(-2,-3),(-2,-2),(1,-2),(-2,-1),(-1,-1),(0,-1),(1,0),(1,1),(-2,0),(-2,1),(-2,2),(-1,2),(0,2),],
               'C':[(-1,-4),(0,-4),(0,-4),(1,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,2),],
               'D':[(-2,-4),(-1,-4),(0,-4),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(0,2),(-1,2),(-2,2),(-2,1),(-2,0),(-2,-1),(-2,-2),(-2,-3),],
               'E':[(-2,-4),(-1,-4),(0,-4),(1,-4),(-2,-3),(-2,-2),(-2,-1),(-1,-1),(0,-1),(1,-1),(-2,0),(-2,1),(-2,2),(-1,2),(0,2),(1,2),],
               'F':[(-2,-4),(-1,-4),(0,-4),(1,-4),(-2,-3),(-2,-2),(-2,-1),(-1,-1),(0,-1),(1,-1),(-2,0),(-2,1),(-2,2),],
               'G':[(-1,-4),(0,-4),(1,-4),(-2,-3),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,2),(1,1),(1,0),(1,-1),(0,-1)],
               'H':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(1,2),(1,-2),(1,-3),(1,-4),],
               'I':[(-2,-4),(-1,-4),(0,-4),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(-2,2),(-1,2),(0,2),],
               'J':[(-1,-4),(0,-4),(1,-4),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(0,2),(-1,2),(-2,2),],
               'K':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(1,-4),(0,-3),(-1,-2),(-1,-1),(0,0),(0,1),(1,2),],
               'L':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,2),(0,2),(1,2),],
               'M':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-3),(0,-3),(1,-4),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(1,2),(-1,0),(0,0),(0,-1),(-1,-1),(-1,-2),(0,-2),],
               'N':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-3),(-1,-2),(-1,-1),(0,-1),(1,-4),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(1,2),(0,0),(0,1),],
               'O':[(-1,-4),(0,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,-3),(1,-2),(1,-1),(1,0),(1,1),],
               'P':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-4),(-1,-4),(-1,-1),(0,-4),(0,-1),(1,-3),(1,-2),],
               'Q':[(-1,-4),(0,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(0,3),(1,3),],
               'R':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-4),(0,-4),(1,-3),(1,-2),(0,-1),(-1,-1),(0,0),(1,1),(1,2),],
               'S':[(-1,-4),(0,-4),(1,-3),(-2,-3),(-2,-2),(-1,-1),(0,-1),(1,0),(1,1),(0,2),(-1,2),(-2,1),],
               'T':[(-3,-4),(-2,-4),(-1,-4),(0,-4),(1,-4),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),],
               'U':[(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,1),(1,0),(1,-1),(1,-2),(1,-3),(1,-4),],
               'V':[(-2,-4),(-2,-3),(-2,-2),(-1,-1),(-1,-1),(-1,0),(-1,1),(-1,2),(0,2),(0,1),(0,0),(0,-1),(1,-2),(1,-3),(1,-4),],
               'W':[(-3,-4),(-3,-3),(-3,-2),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-2),(-1,-1),(0,-2),(0,-1),(0,0),(0,1),(0,2),(1,-4),(1,-3),(1,-2),],
               'X':[(-2,-4),(-2,-3),(-2,1),(-2,2),(-1,-2),(-1,-1),(-1,0),(0,-2),(0,-1),(0,0),(1,1),(1,2),(1,-4),(1,-3),],
               'Y':[(-3,-4),(-2,-3),(-2,-2),(-1,-2),(0,-2),(0,-3),(1,-4),(-1,-1),(-1,0),(-1,1),(-1,2),],
               'Z':[(-2,-4),(-1,-4),(0,-4),(1,-4),(1,-3),(0,-2),(0,-1),(-1,0),(-2,1),(-2,2),(-1,2),(0,2),(1,2),(-1,-1),],
               '[':[(-1,-5),(0,-5),(-1,-4),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(0,2),],
               '\\':[(-3,-4),(-2,-3),(-2,-2),(-1,-1),(-1,0),(0,1),(0,2),],
               ']':[(-2,-5),(-1,-5),(-1,-4),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(-2,2),],
               '^':[(-2,-3),(-1,-4),(0,-5),(1,-4),(1,-4),(2,-3),],
               '_':[(-3,4),(-2,4),(-1,4),(0,4),(1,4),],
               '`':[(-2,-5),(-1,-4),],
               'a':[(-2,-2),(-1,-2),(0,-2),(1,-1),(1,0),(1,1),(1,2),(0,2),(-1,2),(-2,1),(-1,0),(0,0),],
               'b':[(-2,-5),(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-2),(-1,2),(0,-2),(0,2),(1,-1),(1,0),(1,1),],
               'c':[(-1,-2),(0,-2),(1,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,2),],
               'd':[(1,-5),(1,-4),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(1,2),(0,-2),(0,2),(-1,-2),(-1,2),(-2,-1),(-2,0),(-2,1),],
               'e':[(-1,-2),(0,-2),(-2,-1),(1,-1),(-2,0),(-1,0),(0,0),(1,0),(-2,1),(-1,2),(0,2),(1,2),],
               'f':[(0,-5),(1,-5),(-1,-4),(-1,-3),(-1,-2),(-2,-2),(0,-2),(1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),],
               'g':[(-1,-2),(0,-2),(1,-2),(-2,-1),(1,-1),(-2,0),(1,0),(-2,1),(1,1),(-1,2),(0,2),(1,2),(1,3),(0,4),(-1,4),],
               'h':[(-2,-5),(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-2),(0,-2),(1,-1),(1,0),(1,1),(1,2),],
               'i':[(-1,-5),(-1,-2),(-2,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(-2,2),(-3,2),(0,2),(1,2),],
               'j':[(0,-5),(-1,-2),(-1,-2),(0,-2),(0,-1),(0,0),(0,1),(0,2),(0,3),(-1,4),(-1,4),(-2,4),],
               'k':[(-2,-5),(-2,-4),(-2,-3),(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,0),(0,-1),(1,-2),(0,1),(1,2),],
               'l':[(-3,-5),(-2,-5),(-1,-5),(-1,-4),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(0,2),(1,2),],
               'm':[(-2,-2),(-1,-2),(0,-2),(1,-2),(-2,-1),(-2,-1),(-2,0),(-2,1),(-2,2),(0,-1),(0,0),(0,1),(0,2),(2,-1),(2,0),(2,1),(2,2),],
               'n':[(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-2),(0,-2),(1,-1),(1,0),(1,1),(1,2),],
               'o':[(-1,-2),(0,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,-1),(1,0),(1,1),],
               'p':[(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-2,3),(-2,4),(-1,-2),(0,-2),(1,-1),(1,0),(1,1),(0,2),(-1,2),],
               'q':[(-1,-2),(0,-2),(1,-2),(-2,-1),(-2,0),(-2,1),(-1,2),(0,2),(1,-1),(1,0),(1,1),(1,2),(1,3),(1,4),],
               'r':[(-1,-2),(0,-2),(1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),],
               's':[(-1,-2),(0,-2),(1,-2),(-2,-1),(-1,0),(0,0),(1,1),(0,2),(-1,2),(-2,2),],
               't':[(-1,-3),(-2,-2),(-1,-2),(0,-2),(1,-2),(-1,-1),(-1,0),(-1,1),(0,2),(1,2),],
               'u':[(-2,-2),(-2,-1),(-2,0),(-2,1),(1,-2),(1,-1),(1,0),(1,1),(-1,2),(0,2),(1,2),],
               'v':[(-2,-2),(-2,-1),(-2,0),(-1,1),(-1,2),(0,2),(0,1),(1,0),(1,-1),(1,-2),],
               'w':[(-3,-2),(-3,-1),(-3,0),(-2,1),(-2,2),(-1,0),(-1,-1),(0,1),(0,2),(1,0),(1,-1),(1,-2),],
               'x':[(-2,-2),(-2,2),(-1,-1),(-1,0),(-1,1),(1,-2),(1,2),(0,-1),(0,0),(0,1),],
               'y':[(-2,-2),(-2,-1),(1,-2),(1,-1),(-1,0),(0,0),(0,1),(-1,1),(-1,2),(-1,3),(-2,4),],
               'z':[(-2,-2),(-1,-2),(0,-2),(1,-2),(0,-1),(-1,0),(-1,1),(-2,2),(-1,2),(0,2),(1,2),],
               '{':[(-1,-5),(0,-5),(-1,-4),(-1,-3),(-1,-2),(-1,-2),(-2,-1),(-1,0),(-1,1),(-1,2),(0,2),],
               '|':[(-1,-5),(-1,-4),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(-1,3),],
               '}':[(-2,-5),(-1,-5),(-1,-4),(-1,-3),(-1,-2),(0,-1),(-1,0),(-1,1),(-1,2),(-2,2),],
               '~':[(-2,-1),(-1,-2),(0,-2),(1,-1),(2,-2),],
}




#############UTILITY FUNCTIONS#####################

def _rindex(lst, item):
    try:
        return dropwhile(lambda x: lst[x] != item, reversed(xrange(len(lst)))).next()
    except StopIteration:
        raise ValueError, "_rindex(lst, item): item not in list"

#optimize the program string and write it to the named file

def writetofile(filename):
    global l,code
    s=''.join(l)
    s = sub('\n\s*?\n\s*?\n','\n\n',s)
    filename = sub('.sel','',filename)
    oldstring=s
    while True:
        oldstring=s
        s=sub('(?s)LEFT\.(?P<comment>(?:(?=(?P<tmp>\s*\*%.*?%\*\s*))(?P=tmp))*)\s*RIGHT\. ','\g<comment>',s)
        s=sub('(?s)RIGHT\.(?P<comment>(?:(?=(?P<tmp>\s*\*%.*?%\*\s*))(?P=tmp))*)\s*LEFT\. ','\g<comment>',s)
        s=sub('(?s)CONJ\.(?P<comment>(?:(?=(?P<tmp>\s*\*%.*?%\*\s*))(?P=tmp))*)\s*CONJ\.','\g<comment>',s)
        if oldstring==s:
            break
    #find last occurrence of (END. |PRINT. )
    match=None
    for match in finditer(r"(END. |PRINT. )", s):
        pass
    #throw out all but HALT. (because it might be there for emphasis) and LOOP. (whose presence may indicate a bug that should be brought to the user's attention)
    #all the rest of these commands are orphaned and will have no user-visible effect
    if match is not None:
        s=s[:match.start()+1]+sub('(COLOR\. |CONJ\. |EXP\. |LOG\. |SELECT\. |GET\. |LEFT\. |RIGHT\. )','',s[match.start()+1:])
    s = sub('\n\s*?\n\s*?\n','\n \n',s)
    s = sub('\*%(?P<comment>.*)%\*','\g<comment>',s)
    s = sub('\n\n','\n \n',s) #so we can post these to the wiki easily
    
    s+='\n######GENERATION CODE######'+code
    
    try:
        openfile = file(filename+'.sel',"w")
    except IOError:
        print("File not found.")
        sys.exit()
    theFile = openfile.write(s)
    openfile.close()
    l=[]
    
def startleftgr():
    if dike:
        return
    l.append('STARTLEFTGROWING')
    
def endleftgr():
    global l
    doreplace = False
    for i,s in enumerate(l):
        if s=='STARTLEFTGROWING':
            doreplace=True
            del l[i]
            continue
        if doreplace:
            s=s.replace('RIGHT. ','repl ')
            s=s.replace('LEFT. ','RIGHT. ')
            l[i]=s.replace('repl ','LEFT. ')

def turnoff():
    global dike
    dike=True
    
def turnon():
    global dike
    dike=False
#######################FILE FORMATTING AND DECORATION#########################

def comment(note):
    global l,indentlevel,dike
    if dike:
        return
    note=note.replace('\n','\\n')
    l.append('\n*%'+(' '*indentlevel)+note+'%*\n'+(' '*indentlevel))

def init(x,y,z,desc=None):
    global l,h,w,toploc,leftloc
    h=y
    w=x
    toploc=-(h-1)/2
    leftloc=-(w-1)/2
    l.append("("+str(x)+","+str(y)+","+str(z)+")\n")
    if desc is not None:
        l.append(desc+'\n')
    l.append("Generated by Quintopia's Select. Code Generator version "+str(version)+'\n')

def upindent():
    global l,indentlevel
    indentlevel+=3
    l.append('\n'+(' '*indentlevel))

def downindent():
    
    global l,indentlevel
    indentlevel-=3
    l.append('\n'+(' '*indentlevel))
    
    
    
    
    
    

#################################IO CODE GENERATORS#############################
#TODO: drawing letterforms
#TODO: R,G,B to complex number conversion
def output():
    global l,dike
    if dike:
        return
    l.append('PRINT. ')

def drawpixel(x,y):
    global dike,h,w
    if dike:
        return
    upindent()
    comment("DRAW PIXEL AT ("+str(x)+","+str(y)+")")
    makenum(x-(w-1)/2,y-(h-1)/2)
    output()
    comment("END DRAW PIXEL")
    downindent()

def input():
    global l,dike,domove
    if dike:
        return
    domove=True
    l.append('GET. ')

def outputleft(n):
    global dike
    if dike:
        return
    output()
    for i in range(n-1):
        left(1)
        output()
    right(n-1)


def outputright(n):
    global dike
    if dike:
        return
    output()
    for i in range(n-1):
        right(1)
        output()
    left(n-1)


def clear():
    global l,dike,domove
    if dike:
        return
    l.append('CLEAR. ')


def color():
    global l,dike,domove
    if dike:
        return
    l.append('COLOR. ')

def digitprintXY(x,y):
    if dike:
        return
    #input: (x) k*86
    #output: x 1/2 x* |x| x {...} 1|k (k)
    def digits(n):
        if n<10 and n>=0:
            drawletterXY(chr(n+48),x,y)
    switch("digits",10,digits)


def drawstringliteral(string,x,y,top=0,bottom=None,left=0,right=None):
    global dike,h,w
    if dike:
        return
    #input: (k) k*infinity (actually probably less than 25*len(string))
    #output: {...} (k)
    upindent()
    comment('DRAW STRING LITERAL "'+string+'"')
    if bottom is None:
        bottom=h
    if right is None:
        right=w
    string = string+' '
    string = string.replace('\n',' \n')  #insert a space before every newline to simplify algorithm
    string = string.replace('\t',' \t')  #same for tabs
    for i,c in enumerate(string):
        if c=='\t':
            x=x+15                                      #counting the space before the tab, a tab is four spaces
            continue
        remainder = min(string.find(' ',i+1)-i,string.find('-',i+1)-i+1)
        if remainder<0:
            if string.find(' ',i+1)-i>0:
                remainder=string.find(' ',i+1)-i
            elif string.find('-',i+1)-i>0:
                remainder=string.find('-',i+1)-i+1
            else:
                remainder=len(string)-i
        nextword = min(string.find(' ',i+remainder+1)-i-remainder-1,string.find('-',i+remainder+1)-i-remainder)
        if nextword<0:
            if string.find('-',i+remainder+1)-i-remainder-1>0:
                nextword=string.find('-',i+remainder+1)-i-remainder
            elif string.find(' ',i+remainder+1)-i-remainder-1>0:
                nextword=string.find(' ',i+remainder+1)-i-remainder-1
            else:
                nextword=0
        if x>right-5 or c=='\n' or (x+5*remainder>right-5 and remainder*5<right-left and nextword*5<right-left):  #reset to left side if we're off the right side (from tabbing) or at newline or will not see whitespace before we hit the right side unless the next word is longer than a line
            if i+1<len(string) and string[i+1]=='\n' and c!='\n':
                continue
            y=y+12
            x=left
            if y>bottom-12:                            #if we would go off the bottom of the screen, block for input instead, then clear once we have it
                go(-1)
                input()
                go(1)
                clear()
                y=top
            if c=='\n' or c==' ':                             #go on to next character if it was a newline or space, otherwise try to print current char
                continue
        if c!=' ':
            drawletterXY(c,x,y)
        x=x+5
    comment('END DRAW STRING LITERAL "'+string+"'")
    downindent()


def drawletterXY(c,x,y,simulate=False):
    global letterforms,dike,top,left
    #input: (k) {k k? k? k? k?}*(at most 25)
    #output: differentnumbers*(at most 125) (k)
    if dike:
        return
    upindent()
    comment('DRAW LETTER "'+c+'" AT ('+str(x)+','+str(y)+')')
    form = letterforms[c]
    if form is None:
        return
    for n in form:
        makenum(x+n[0]+3+leftloc,y+n[1]+6+toploc)
        if not simulate:
            output()
        go(1)
    comment('END DRAW LETTER "'+c+'"')
    downindent()


def drawletter(c):
    global letterforms,dike
    if dike:
        return
    #input: (x+yi) {k k k k k k? k? k? k?}*(at most 25)
    #output: x+yi {? ?? ?? ?? ?? x+yi k^(?) k^(x+yi) (x+?)+(y+?)i} (k)
    upindent()
    comment('DRAW LETTER "'+c+'"')
    var('drawLetterPosition')
    form = letterforms[c]
    if form is None:
        return
    for n in form:
        go(1)
        makenum(n[0]+3,n[1]+6)
        go(1)
        fetch('drawLetterPosition')
        var('drawLetterPosition')
        add(-1)
        output()
    go(1)
    makenum(5)
    go(1)
    fetch('drawLetterPosition')
    add(-1)
    comment('END DRAW LETTER "'+c+'"')
    downindent()

#######################COMMON ACTIONS IN SELECT############################
def left(n):
    global l,offset,dike
    if dike or not domove:
        return
    for i in range(n):
        l.append('LEFT. ')
        offset-=1

def right(n):
    global l,offset,dike
    if dike or not domove:
        return
    for i in range(n):
        l.append('RIGHT. ')
        offset+=1
        
def go(n):
    global dike
    if dike:
        return
    if n<0:
        left(-n)
    else:
        right(n)

def exptarget(n):
    global l,indentlevel,dike,domove
    if dike:
        return
    l.append('EXP. ')
    if n<0:
        left(-n)
    elif n>0:
        right(n)
    l.append('SELECT.\n'+(' '*indentlevel))
    domove=True

def logtarget(n):
    global l,indentlevel,dike,domove
    if dike:
        return
    l.append('LOG. ')
    if n<0:
        left(-n)
    elif n>0:
        right(n)
    l.append('SELECT.\n'+(' '*indentlevel))
    domove=True

def copyfrom(n):
    global dike
    if dike:
        return
    exptarget(n)
    go(-n)
    logtarget(1)
    left(1)

def var(name,savelist=None):
    global dike
    if dike:
        return
    global vardict,offset,s,indentlevel
    vardict[name] = offset
    if savelist is not None:
        savelist.append(name)
    #add the comment here manually so that it doesn't get the left/right stripped from around it, so that we actually are on the cell the comment claims to be marking.
    #yes, it doesn't change the behavior of the code to strip them, but the code we output should be correctly documented
    l.append('\n'+(' '*indentlevel)+'MARK AS '+name+'\n'+(' '*indentlevel))

def fetch(name):
    global vardict,offset,dike
    if dike:
        return
    #input: (k) k
    #output: ($name) k
    comment("FETCH "+name)
    copyfrom(getoffset(name))
    #vardict[name] = offset
    comment(name+" FETCHED")

#return how far we have to go() to get to the named position, unless no position is named, in which case return absolute position
def getoffset(name=None):
    global vardict,offset
    if name is None:
        return offset
    if name not in vardict:
        print("No location called '"+name+"' exists.")
        sys.exit(1)
    return vardict[name]-offset

def halt():
    global s,dike
    if dike:
        return
    l.append('HALT. \n!!!!PROGRAM EXIT POINT!!!!\n')






################################################LOOPING############################################
def loop(name,start=0,end=None,step=1,computei=False,savelist=[]):
    global l,dike,mustsave
    if dike:
        return
    #input: [(k) | (x) k] k k k k k k k k k k k k k k k k k k k {k k k k {k k} {k k k k {k k k}}} (20,24/26,28/30,31/33)k's
    #output: 1/sqrt(2) -1 1/2 i -1 k^i k^-1 -1+i (-1+i)/sqrt(2) -1 1/n 1/2 i^(1/n) k k*i^(1/n) (sentinel) {k}...
          #... 1/2 sentinel* sentinel ...                                                               computei=True and...  
            #... (i) k                                                                                  ...step=1 or
            #... {loopcount step} ...                                                                   ...step>1 and...
          #... (i) k                                                                                    ...start=0
          #... loopcount*step start k^(loopcount*step) k^start (i) k                                    ...start>0
          #... loopcount*step -1 -start start loopcount*step k^start k^loopcount*step (i) k           ...start<0
    #also creates the variables <name>sentinel, <name>step, used internally.
    upindent()
    if end is None:
        comment("LOOP '"+name+"' FROM 0 TO VALUE ON TAPE BY INCREMENTS OF 1")
        go(1)
    else:
        comment("LOOP '"+name+"' FROM "+str(start)+" TO "+str(end)+" BY INCREMENTS OF "+str(step))
    makenum(2)
    right(1)
    makeneg1()
    right(1)
    makei()
    #2 -1 1/2 (i)
    add(-2)
    #2 -1 1/2 i k^i k^-1 (-1+i) k
    go(-6)
    exptarget(2)
    go(-2)
    exptarget(1)
    #1/sqrt(2) (-1) 1/2 i k^i k^-1 -1+i k
    go(5)
    multiply(-6)
    #1/sqrt(2) -1 1/2 i k^i k^-1 -1+i ((-1+i)/sqrt(2)) k
    var(name+'sentinel')
    mustsave.append(name+'sentinel')
    go(1)
    makeneg1()
    go(1)
    if end is None:
        copyfrom(-10)
    else:
        makenum((end-start)/step)
    #...-1 (n) k
    exptarget(-1)
    go(2)
    makei()
    #...-1 1/n 1/2 (i)  k
    exptarget(-2)
    #...-1 (1/n) 1/2 i^(1/n) k
    go(2)
    multiply()
    var(name+'step')
    mustsave.append(name+'step')
    #...-1 1/n 1/2 i^(1/n) k (k*i^(1/n)) k
    if len(mustsave)>2:
        go(1)
        for varname in mustsave:
            if varname!=name+'sentinel' and varname!=name+'step':
                fetch(varname)
                var(varname)
                go(1)
        if savelist:
            go(-1)
        else:
            go(1)
            fetch(name+'step')
            var(name+'step')
    if savelist:
        go(1)
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
        go(1) #leave a gap for where the old sentinel will be fetched in endloop
        fetch(name+'step')
        var(name+'step')
        #invalidate all variables which are not being saved (as looping will make their offsets wrong anyway)
        for key in vardict.keys():
            if key not in savelist and key not in mustsave:
                del vardict[key]
    go(1)
    fetch(name+'sentinel')
    var(name+'sentinel')
    l.append('LOOP. ')
    upindent()
    if computei:
        absval()
        #...sentinel 1/2 sentinel* (|sentinel|) k
        logtarget(1)
        #...loopcount (k)
        if step>1:
            makenum(step)
            #...loopcount (step) k
            go(-1)
            multiply()
        else:
            go(-1)
        #...loopcount {step (loopcount*step)} k
        #output()
        if start>0:
            go(1)
            makenum(start)
            add(-1)
            #...loopcount {step loopcount*step} start k^(loopcount*step) k^start (i) k
        elif start<0:
            go(1)
            makenum(start)
            #...loopcount {step loopcount*step} -1 (start)
            add(-2)
            #...loopcount {step loopcount*step} -1 start k^(loopcount*step) k^start (i) k

    #do not down indent. that is in endloop()
    
def endloop(name,computei=False,start=0,savelist=[]):
    global l,dike,mustsave
    if dike:
        return
    #input: (k) k k k {k k k k k {k k k k {k k k k}}} (4,9,13,17)k's
    #output: oldsentinel step (newsentinel) {k}...
       #...1/2 sentinel* loopcount step...                                                  computei=True and...
       #...(i) k                                                                            ...start=0
       #...loopcount*step start k^(loopcount*step) k^start (i) k                            ...start>0
       #...loopcount*step 2 -1 -start start loopcount*step k^start k^loopcount*step (i) k   ...start<0
    del mustsave[mustsave.index(name+"sentinel")]
    del mustsave[mustsave.index(name+"step")]
    go(1)
    if mustsave:
        for varname in mustsave:
            fetch(varname)
            var(varname)
            go(1)
    if savelist:
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
    fetch(name+'sentinel')
    go(1)
    fetch(name+'step')
    go(-1)
    multiply()
    #sentinel step (sentinel*step) k
    downindent()
    l.append('END. ')
    if computei:
        absval()
        #...sentinel 1/2 sentinel* (|sentinel|) k
        logtarget(1)
        #...loopcount (k)
        makenum(step)
        #...loopcount (step) k
        go(-1)
        multiply()
        #...loopcount step (loopcount*step) k
        if start>0:
            go(1)
            makenum(start)
            go(-1)
            add()
            #...loopcount step loopcount*step start k^(loopcount*step) k^start (i) k
        elif start<0:
            go(1)
            makenum(-start)
            go(1)
            copyfrom(-5)
            go(-1)
            add()
            #...loopcount step loopcount*step 2 -1 -start start loopcount*step k^start k^loopcount*step (i) k
            #do not down indent. that is in endloop()
    comment('END OF LOOP '+name)
    downindent()

def repeat(name,savelist=[]):
    global l,dike,mustsave
    if dike:
        return
    upindent()
    comment("WHILE")
    var(name+"sentinel")
    mustsave.append(name+"sentinel")
    if len(mustsave)>1:
        go(1)
        for varname in mustsave:
            if varname!=name+"sentinel":
                fetch(varname)
                var(varname)
                go(1)
        if savelist:
            go(-1)
        else:
            fetch(name+"sentinel")
    if savelist:
        go(1)
        
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
        fetch(name+"sentinel")
    l.append("LOOP. ")

def endrepeat(name,savelist=[]):
    global l,dike
    if dike:
        return
    del mustsave[mustsave.index(name+"sentinel")]
    var(name+"sentinel")
    if mustsave:
        go(1)
        for varname in mustsave:
            fetch(varname)
            var(varname)
            go(1)
        if savelist:
            go(-1)
        else:
            fetch(name+"sentinel")
    if savelist:
        go(1)
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
        fetch(name+"sentinel")
    l.append("END. ")
    comment("END WHILE")
    downindent()







##############################################CONDITIONALS##################################################
def ifnonpositive(name):
    global l,dike,mustsave
    if dike:
        return
    #x must be a real number!
    #input: (x) ?
    #output: (x) ?
    upindent()
    comment('IF ('+name+'):')
    l.append('LOOP. ')
    var('ifstart'+name)
    mustsave.append('ifstart'+name)
    upindent()
    #no downindent
    
def ifzero(name):
    global dike
    #input (x) k k k k k
    #output: x 1/2 x* |x| (x) k
    if dike:
        return
    comment('IF ZERO ('+name+'):')
    absval()
    ifnonpositive(name)
    go(1)
    copyfrom(-4)
    
def els(name,copy=True):
    global l,dike,offset
    if dike:
        return
    #input: (x|?) k k k k
    #output: x k 0 (x) k
    if 'PADPOINT1'+name not in l:
        padpoint(1,name)
    go(1)
    var('ifone'+name)
    mustsave.append('ifone'+name)
    go(1)
    makezero()
    go(-1)
    downindent()
    l.append('END. ')
    #THE OFFSET HERE WOULD BE THE SAME AS THE OFFSET AT THE BEGINNING OF THE FIRST IF BLOCK (since only one of the two will be executed)
    offset+=getoffset('ifstart'+name)
    go(1)
    lnot()
    comment('ELSE ('+name+'):')
    l.append('LOOP. ')
    var('ifelse'+name)
    mustsave.append('ifelse'+name)
    upindent()
    if copy:
        go(1)
        copyfrom(-3)

def endif(name):
    global l,dike,vardict,offset
    if dike:
        return
    #input: (x) k
    #output: (x) k 
    #if an else branch wasn't needed for program logic but the tapehead moved, insert one anyway just to prevent tape usage differing depending on conditional result
    if 'ifelse'+name not in vardict and getoffset('ifstart'+name)!=0:
        els(name,True)
    #no padding necessary if there is no else block and the tape head did not move
    if 'ifelse'+name in vardict:
        #calculate displacement of first branch
        b1length = getoffset('ifone'+name)-getoffset('ifstart'+name)
        if 'PADPOINT2'+name not in l:
            padpoint(2,name)
        #go(1)
        #calculate displacement of second branch
        b2length = -getoffset('ifelse'+name)
        #output rights
        if b2length>b1length:
            #this branch is further right. insert rights at padpoint1
            padlength=b2length-b1length
            pp=_rindex(l,'PADPOINT1'+name)
            l[pp]='({'+'RIGHT. '*padlength+'})'
            pp=_rindex(l,'PADPOINT2'+name)
            del l[pp]
        elif b1length>b2length:
            #insert rights at padpoint2
            padlength=b1length-b2length
            offset+=padlength
            pp=_rindex(l,'PADPOINT2'+name)
            l[pp]='({'+'RIGHT. '*padlength+'})'
            pp=_rindex(l,'PADPOINT1'+name)
            del l[pp]
        else:
            pp=_rindex(l,'PADPOINT2'+name)
            del l[pp]
            pp=_rindex(l,'PADPOINT1'+name)
            del l[pp]
    downindent()
    l.append('END. ')
    del mustsave[mustsave.index('ifstart'+name)]
    del mustsave[mustsave.index('ifone'+name)]
    del mustsave[mustsave.index('ifelse'+name)]
    comment('END IF ('+name+')')
    downindent()
    
def padpoint(n,name):
    global l,dike
    if dike:
        return
    l.append('PADPOINT'+str(n)+name)
    

#combined if/else/end overhead: firstbranch: x {...} k 1 (k)
#                               secondbranch: x 0 x {...} (k)
#for ifzero:                     firstbranch: x 1/2 x* |x| {...} k 1 (k)
#                               secondbranch: x 1/2 x* |x| 0 x {...} (k)
#because of automatic padding, the overhead is the same no matter which branch is chosen ...this is what makes looping over conditionals possible!


#evaluate f(x) by generating code for f(k) for k from 1 to n and running the code for f(k) only if x=k (x must be a positive integer!!!!)
#so really it's just an unrolled loop, with a conditional for each iteration, and in between it decrements k, entering a conditional when k hits zero (which will correspond to the original value of k)
#or a giant if/else chain, where the conditions are sequential guesses at the value of x
#n is the number of cases to try (the integers 1..n), and f is a function that takes an integer argument (or None) and generates code (None is the "default" case--for when all cases fail)
#fetchx specifies whether the code generated by f needs x under the tapehead when it executes, and so if True, will copy it there
def switch(name,n,f,fetchx=False):
    global l,dike,offset
    offsets = []
    if dike:
        return
    #input: (x) k*(10+f's max tape usage)
    #let fin=i^(2^((n-1)/x-2))
    #output: zero: x 1/2 x* |x| x {...} k 1 (k)
    #        regular: x 1/2 x* |x| x 1/x -1 2^(1/x) i^(1/4) {...} 1 (k)
    #        default: x 1/2 x* |x| x 1/x -1 2^(1/x) fin^2 {...} k (k)
    upindent()
    comment('SWITCH ('+name+') WITH '+str(n)+' CASES')
    #we'll start with the test case for zero. it won't change much except the tape use profile. it needs to be padded too. but wait...it gets auto-padded already.
    #create the test sentinel and step just like the one for loop()
    ifzero("switchbigcond"+name)
    comment("CASE ("+name+") #0:")
    if not fetchx:
        go(1)
    f(0)
    comment("END CASE ("+name+") #0")
    els("switchbigcond"+name)
    var(name+'X')
    go(1)
    copyfrom(-1)
    go(1)
    makeneg1()
    go(-1)
    exptarget(1)
    #x 1/x (-1) k
    go(1)
    makei()
    #x 1/x -1 1/2 (i) k
    exptarget(-1)
    go(1)
    #x 1/x -1 1/2 (i^(1/2)) k
    exptarget(-1)
    exptarget(-1)
    #x 1/x (-1) 2 i^(1/4) k
    go(1)
    exptarget(-2)
    #x (1/x) -1 2^(1/x) i^(1/4) k
    go(3)
    exptarget(-1)
    go(1)
    startpoint=getoffset()
    for k in range(1,n):
        l.append('LOOP. ')
        upindent()
        comment('CASE ('+name+') #'+str(k)+':')
        go(1)
        if fetchx:
            fetch(name+'X')
        f(k)
        if 'PADPOINT'+str(k-1)+name not in l:
            padpoint(k-1,name)
        go(1)
        #make sure that none of the cases after this one will run.
        makeone()
        offsets.append(getoffset()-startpoint)
        comment('END CASE ('+name+') #'+str(k))
        downindent()
        l.append('END. ')
        offset=startpoint
        exptarget(-1)
        go(1)
        #if something has run: x 1/x -1 2^(1/x) i^(1/4) {...} (1) k
        #if something has not run: x 1/x -1 2^(1/x) (i^(2^((n-1)/x-2))=fin) k
    #now the default case. If one of the above cases has run, then sentinel=1 (the current tape cell), so we run this one for all other values.
    square() #squaring will move any valid sentinel into the "true" range but fix 1
    l.append('LOOP. ')
    upindent()
    comment('DEFAULT CASE:')
    go(1)
    if fetchx:
        fetch('switch'+name+'X')
    f(n)
    if 'PADPOINT'+str(n-1)+name not in l:
        padpoint(n-1,name)
    
    offsets.append(getoffset()-startpoint) #?
    go(1)
    comment('END DEFAULT CASE')
    downindent()
    l.append('END. ')
    #compute the max tape usage in any branch (we'll pad up to it in other branches)
    maxpad=max(offsets)
    #iterate through and pad too-small branches
    for k in range(len(offsets)):
        padlength=maxpad-offsets[k]
        pp=_rindex(l,'PADPOINT'+str(k)+name)
        if padlength>0:
            l[pp]='({'+'RIGHT. '*padlength+'})'
        else:
            del l[pp]
    offset=startpoint+maxpad+1
    #if something has run: x 1/x -1 2^(1/x) i^(1/4) {...} (1) k
    #if something has not run: x 1/x -1 2^(1/x) fin^2 {...} (k) k
    endif("switchbigcond"+name)
    comment('END SWITCH ('+name+')')
    downindent()
    

############################LOGIC###########################

def lnot(target=0):
    global dike
    #turns positive real numbers into zero, and zero into 1.
    #only works for positive real numbers!!! call abs() first!!!
    #input (x) k 
    #output x (~x)
    # or
    #input x ... (k) k or (k) k ... x
    #output x ... (~x) k or (~x) k ... x
    if dike:
        return
    upindent()
    comment('LOGICAL NOT:')
    if target==0:
        go(1)
        target=-1
    makezero()
    exptarget(target)
    go(-target)
    comment('END NOT')
    downindent()

def tobit():
    global dike
    #converts everything but zero into 1
    #input (x) k k k k k k
    #output x 1/2 x* x |x| ~|x| (~~|x|)
    if dike:
        return
    upindent()
    comment('CONVERT TO BIT:')
    absval()
    lnot()
    lnot()

def land(target1=1,target2=0):
    global dike
    if dike:
        return
    comment('AND:')
    multiply(target1,target2)
    
def lor(target=1):
    global dike
    if dike:
        return
    comment('OR:')
    add(target)
    




##############################CONSTANTS#########################
def makenum(real=0,imag=0):
    global dike
    if dike:
        return
    upindent()
    sign=1
    if imag==0:
        comment('MAKE '+str(real)+':')
    elif real==0:
        comment('MAKE '+str(imag)+'I:')
    else:
        comment('MAKE '+str(real)+'+'+str(imag)+'I:')
    if imag!=0:
        if real<0:
            makenum(-imag)
        else:
            makenum(imag)
        go(1)
        makei()
        #n 1/2 (i)
        go(1)
        exptarget(-1)
        go(1)
        exptarget(-3)
        go(3)
        #n 1/2 i k^(n*i)
        var('makenumimagpart')
        go(1)
    if real==0:
        if imag==0:
            makezero()
            downindent()
            return
        else:
            go(-1)
            logtarget(1)
            go(-1)
            downindent()
            return
    if real==1:
        if imag==0:
            makeone()
            downindent()
            return
    if real<0:
        upindent()
        comment('MAKE 1/K:')
        go(1)
        exptarget(0)
        go(-1)
        logtarget(1)
        # 1/k (k^k)
        exptarget(-1)
        var('makenumsign')
        # (1/k) k
        logtarget(1)
        comment('END MAKE 1/K')
        downindent()
        sign=-1
        real=-real
    if real>1 or (real==1 and imag!=0):
        exptarget(0)
        i=0
        while i<real-1:
            exptarget(1)
            left(1)
            i+=1
        if imag!=0:
            comment('COMBINE IMAGINARY PART')
            shift=getoffset('makenumimagpart')
            exptarget(shift)
            go(-shift)
        logtarget(1)
        left(1)
        if sign==-1:
            comment('COMBINE SIGN')
            shift=getoffset('makenumsign')
            exptarget(shift)
            go(-shift) 
        logtarget(1)
        #TODO: We could special case 4,27,64 using 2^2,3^3,(2^2)^(2^2)
        left(1)
    real=sign*real
    if real==-1 and imag==0:
        go(-1)
    if imag==0:
        comment('END MAKE '+str(real))
    elif real==0:
        comment('END MAKE '+str(imag)+'I')
    else:
        comment('END MAKE '+str(real)+'+'+str(imag)+'I')
    downindent()

def makehalf():
    global dike
    #input: (k) k
    #output: (1/2) k
    if dike:
        return
    upindent()
    comment('MAKE 1/2:')
    right(1)
    exptarget(0)
    exptarget(-1)
    #(k) k^(k^2)
    right(1)
    logtarget(-1)
    #(k) k^2
    logtarget(1)
    #1/2 (k^2)
    exptarget(-1)
    #(1/2) k
    comment('END MAKE 1/2')
    downindent()
    
def makeone():
    global dike
    if dike:
        return
    logtarget(0)

def makezero():
    global dike
    if dike:
        return
    makeone()
    logtarget(1)
    left(1)

def makeroot2():
    global dike
    #input: (k) k k
    #output: 1/2 (sqrt(2)) k
    if dike:
        return
    makehalf()
    right(1)
    makenum(2)
    exptarget(-1)
    right(1)

def makehalfroot2():
    global dike
    #input: (k) k
    #output: (1/sqrt(2)) k
    if dike:
        return
    makehalf()
    exptarget(0)
    
def makei():
    global dike
    #input: (k) k k
    #output: 1/2 (i)
    if dike:
        return
    upindent()
    comment('MAKE I:')
    makehalf()
    go(1)
    makeneg1()
    #1/2 (-1)
    exptarget(-1)
    right(1)
    #1/2 (i)
    comment('END MAKE I')
    downindent()

def makeneg1():
    #input: (k) k
    #output: (-1) k
    makenum(-1)
    


def makee():
    global dike
    #input: (k) k k k k k k
    #output: 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e) k
    if dike:
        return
    upindent()
    comment('MAKE E:')
    makenum(2)
    right(1)
    makenum(2)
    right(1)
    makeneg1()
    #2 2 (-1)
    left(2)
    for i in range(3):
        exptarget(0)
    #(3.2317e+616) 2 -1
    #this number is too big for mpmath to print at default precision
    logtarget(1)
    left(1)
    exptarget(1)
    left(1)
    exptarget(1)
    left(1)
    exptarget(1)
    right(2)
    copyfrom(-3)
    #3.09485e+26 2 -1 (3.09485e+26) k
    exptarget(-1)
    #3.09485e+26 2 (-1) 3.23117e-27 k k
    right(2)
    exptarget(-1)
    #3.09485e+26 2 -1 (3.23117e-27) k^(3.23117e-27)
    right(2)
    multiply(-1,1)
    #3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) k^(3.23117e-27+1) k
    logtarget(1)
    left(1)
    #3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (3.23117e-27+1) k
    exptarget(-5)
    right(5)
    comment('END MAKE E')
    downindent()
    #3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) k *e k

def maketaufourth():
    global dike
    #input (k) k k k k k k k k k k k (12 k's)
    #output 1/2 logK(i) 3.09485e+26 2 i 3.23117e-27 k^(3.23117e-27) 1/logK(e) tau/4i -tau/4i (tau/4) k
    if dike:
        return
    upindent()
    comment('MAKE TAU/4:')
    makei()
    #1/2 (i)
    ln(True)
    #1/2 logK(i) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) (ln(i)=tau/4i)
    go(-4)
    exptarget(-4)
    go(8)
    #1/2 logK(i) 3.09485e+26 2 i 3.23117e-27 k^(3.23117e-27) 1/logK(e) (tau/4i)
    conj()
    multiply(-4)
    #1/2 logK(i) 3.09485e+26 2 i 3.23117e-27 k^(3.23117e-27) 1/logK(e) tau/4i (tau/4) k
    comment('END MAKE TAU/4')
    downindent()

def maketauhalf():
    global dike
    if dike:
        return
    upindent()
    comment('MAKE TAU/2:')
    #input (k) k k k k k k k k k k k k (13 k's)
    #output 1/2 logK(i) 3.09485e+26 2 i 3.23117e-27 k^(3.23117e-27) tau/4i tau/4 (tau/2) k
    maketaufourth()
    multiply(-6)
    comment('END MAKE TAU/2')
    downindent()

def maketau():
    global dike
    #input (k) k k k k k k k k k k k k k (14 k's)
    #output 1/2 logK(i) 3.09485e+26 2 i 3.23117e-27 k^(3.23117e-27) tau/4i tau/4 tau/2 (tau) k
    if dike:
        return
    upindent()
    comment('MAKE TAU:')
    maketauhalf()
    multiply(-7)
    comment('END MAKE TAU')
    downindent()
    
    
    
    
    
    




###################MATHEMATICAL FUNCTIONS##############################
def multiply(target=1,target2=0):
    global dike
    #input: (x) y k k
    #output: x y (x*y) k
    #target!=1:
    #input: y ... (x) k k or (x) k k ... y
    #output: y ... x (x*y) k or x (x*y) k ... y
    #target2!=0:
    #input: y...x ...(k) k or (k) k ... y ... x
    #output: y...x...(x*y) k or (x*y) k ... y ... x
    if dike:
        return
    upindent()
    comment('(multiply)')
    if target==1 and target2==0:
        right(2)
        exptarget(-2)
        right(2)
        exptarget(-1)
        right(1)
    elif target2==0:
        right(1)
        exptarget(-1)
        right(1)
        exptarget(target-1)
        go(-target+1)
    else:
        exptarget(target)
        go(-target)
        exptarget(target2)
        go(-target2)
    logtarget(1)
    left(1)
    downindent()

def square(target=0):
    global dike
    #input: (x) k k
    #output: x x^2 k
    #target!=0
    #input: x ... (k) k or (k) k ... x
    #output: x ... (x^2) k or (x^2) k ... x
    if dike:
        return
    upindent()
    comment('(square)')
    if target==0:
        right(1)
        exptarget(-1)
        right(1)
        exptarget(-1)
        right(1)
    else:
        exptarget(target)
        go(-target)
        exptarget(target)
        go(-target)
    logtarget(1)
    left(1)
    downindent()

#cannot increment 1 or 0
def inc():
    global dike
    #input (x) k k
    #output x (x+1) k
    if dike:
        return
    upindent()
    comment('(inc)')
    go(1)
    copyfrom(-1)
    exptarget(0)
    exptarget(0)
    logtarget(-1)
    go(1)
    logtarget(-1)
    go(1)
    downindent()

#cannot decrement 1 or 0
def dec():
    global dike
    #input (x) k k k
    #output: x x^-2 (x-1) k
    if dike:
        return
    upindent()
    comment('(dec)')
    go(1)
    copyfrom(-1)
    go(1)
    copyfrom(-2)
    go(-2)
    exptarget(0)
    exptarget(1)
    #x^x^2 (x) x k
    logtarget(-1)
    #(x^x^2) x^-2 x k
    exptarget(1)
    #x (x^-2) x k
    go(1)
    exptarget(0)
    exptarget(0)
    #x x^-2 (x^x^(x+1)) k
    exptarget(-1)
    #x (x^-2) x^x^(x-1) k
    go(1)
    logtarget(-2)
    go(2)
    logtarget(-2)
    go(2)
    downindent()

#cannot reciprocal 1 or -1 (or 0, duh)
def reciprocal():
    global dike
    #this only works if x!=±1! obviously, in that case you needn't be reciprocating anyway, but if you can't guarantee it, do x^-1 manually instead
    #input (x) k k
    #output x (1/x) k
    if dike:
        return
    upindent()
    comment('(reciprocal)')
    go(1)
    copyfrom(-1)
    go(-1)
    exptarget(0)
    go(1)
    logtarget(-1)
    exptarget(1)
    downindent()

def opposite():
    global dike
    #since this depends on reciprocal, you can't use it on ±1
    #input (x) k k
    #output x (-x) k
    if dike:
        return
    upindent()
    comment('(opposite)')
    reciprocal()
    #x (1/x) k
    output()
    exptarget(-1)
    #(x) x^-x k
    go(1)
    logtarget(-1)
    go(1)
    downindent()
    
    

def add(target=1):
    global dike
    #input: (x) y k k k k
    #output: x y k^x k^y (x+y) k
    #target!=1:
    #input: (x) k k k k ... y or y ... (x) k k k k
    #output: x k^x k^y (x+y) k ... y or y ... x k^x k^y (x+y) k
    if dike:
        return
    upindent()
    comment('ADD:')
    if target==1:
        right(2)
        exptarget(-2)
        right(3)
        exptarget(-2)
        right(1)
    else:
        right(1)
        exptarget(-1)
        right(2)
        exptarget(target-2)
        go(-target+1)
    multiply()
    logtarget(1)
    left(1)
    comment('END ADD')
    downindent()

def conj():
    global l,dike,domove
    if dike:
        return
    domove=True
    l.append('CONJ. ')

def ln(clobberinput=False):
    global dike
    #input (x) k k k k k k k k k {k} (8/9k's)
    #output {x|logK(x)} {logK(x)} 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 (ln(x)) k
    if dike:
        return
    upindent()
    comment('NATURAL LOG:')
    if clobberinput==False:
        go(1)
        copyfrom(-1)
    logtarget(1)
    makee()
    # x logK(x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e) k
    logtarget(1)
    go(-1)
    exptarget(-3)
    go(3)
    multiply(-6)
    # x logK(x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) (ln(x)) k
    comment('END NATURAL LOG')
    downindent()
    
def absval():
    global dike
    #input (x) k k k k (4 k's)
    #output x 1/2 x* (|x|) k
    if dike:
        return
    upindent()
    comment('MAGNITUDE:')
    right(1)
    makehalf()
    right(1)
    copyfrom(-2)
    conj()
    multiply(-2)
    # x 1/2 x* (x*x*)
    exptarget(-2)
    right(2)
    comment('END MAGNITUDE')
    downindent()

def re():
    global dike
    #input: (x) k k k k k k k k (8 k's)
    #output: x x* k^x k^x* 2Re(x) 1/2 (Re(x)) k
    if dike:
        return
    upindent()
    comment('REAL PART:')
    right(1)
    copyfrom(-1)
    conj()
    left(1)
    add()
    right(1)
    makehalf()
    multiply(-1)
    comment('END REAL PART')
    downindent()

def im():
    global dike
    #input (x) k k k k k k k k k k k k k (13 k's)
    #output: x 2 1/2 -1 i*x -i*x (-i*x)* k^(-i*x) k^(-i*x)* 2Re(-i*x) 1/2 2Re(-i*x) (Im(x)) k
    if dike:
        return
    upindent()
    comment('IMAGINARY PART:')
    right(1)
    makenum(2)
    right(1)
    makei()
    #x 2 1/2 (i)
    multiply(-3)
    #x 2 1/2 i (i*x)
    go(-1)
    exptarget(-2)
    go(2)
    multiply()
    re()
    #x 2 1/2 -1 i*x -i*x (-i*x)* k^(-i*x) k^(-i*x)* 2Re(-i*x) 1/2 2Re(-i*x) (Im(x)) k
    comment('END IMAGINARY PART')
    downindent()
    
def arg():
    global dike
    #input (x) k k k k k k k k k k k k k k (14 k's)
    #output x 1/2 x* 1/|x| -i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) ln(x/|x|) (arg(x)) k
    if dike:
        return
    upindent()
    comment('ARGUMENT:')
    absval()
    #x 1/2 x* (|x|)
    go(1)
    makeneg1()
    #x 1/2 x* |x| (-1)
    go(-1)
    exptarget(1)
    #x 1/2 x* 1/|x| (-1)
    exptarget(-3)
    go(3)
    conj()
    go(1)
    multiply(-2,-5)
    #x 1/2 x* 1/|x| -i (x/|x|)
    ln(True)
    #x 1/2 x* 1/|x| -i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) (ln(x/|x|))
    multiply(-8)
    #x 1/2 x* 1/|x| -i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) ln(x/|x|) (arg(x))
    comment('END ARGUMENT')
    #x 1/2 x* 1/|x| -i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) ln(x/|x|) (arg(x)) k
    downindent()

def mod(target=1):
    global dike
    #will not work if the dividend is ±1 (but you should know the answer in that case)
    #input (x) y [19 k's] or y .... (x) [20 k's]
    #output x y 1/y 2 2/y (-1)^(2/y) x%y{-x?} -1 -x%y{+x?} k 1|k 0|k y|x%y k^y|k k^(x%y-x)|k x%y k 0|1 k (x%y) k
    if dike:
        return
    upindent()
    comment('MODULUS:')
    go(1)
    if target!=1:
        copyfrom(target-1)
    reciprocal()
    go(1)
    makenum(2)
    multiply(-1)
    go(1)
    makeneg1()
    exptarget(-1)
    go(2)
    copyfrom(-1)
    exptarget(-6)
    go(6)
    logtarget(-1)
    go(2)
    makeneg1()
    multiply(-1)
    ifnonpositive("fliptest")
    go(7)
    copyfrom(-9)
    els("fliptest")
    go(1)
    copyfrom(-11)
    add(-6)
    endif("fliptest")
    go(1)
    copyfrom(-4)
    comment('END MODULUS')
    downindent()

def intdiv(target=1):
    global dike
    #input (x) y [19 k's] or y ... (x) [20 k's]
    #output x y 1/y 2 2/y (-1)^(2/y) x%y{-x?} -1 -x%y{+x?} k 1|k 0|k y|x%y k^y|k k^(x%y-x)|k x%y k 0|1 k x%y -(x%y) k^-(x%y) k^x x-x%y (x//y) k
    if dike:
        return
    upindent()
    comment('INTEGER DIVISION:')
    mod(target)
    multiply(-12)
    add(-20)
    multiply(-21)
    comment('END INTEGER DIVISION')
    downindent()
    
    

def sin(hyperbolic=False):
    global dike
    #input (x) k k k k k k k k k k k k k k k k k (17 k's) (16 for hyperbolic)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) -e^(i*x) e^(-i*x) k^(-e^(i*x)) k^(e^(-i*x)) 2*i*sin(x) -i*sin(x) {(sin(x))} k
    if dike:
        return
    upindent()
    if hyperbolic:
        comment('HYPERBOLIC SINE:')
    else:
        comment('SINE:')
    right(1)
    if hyperbolic:
        go(1)
        makeneg1()
    else:
        makei()
        #x 1/2 (i)
    multiply(-2)
    go(1)
    makee()
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e)
    exptarget(-6)
    go(6)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e^(i*x))
    multiply(-3)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) (-e^(i*x))
    go(1)
    copyfrom(-2)
    exptarget(-5)
    go(4)
    add()
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) -e^(i*x) e^(-i*x) k^(-e^(i*x)) k^(e^(-i*x)) (-(e^(i*x)-e^(-i*x))=-2*i*sin(x))
    multiply(-13)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) -e^(i*x) e^(-i*x) k^(-e^(i*x)) k^(e^(-i*x)) -2*i*sin(x) (-i*sin(x))
    if not hyperbolic:
        multiply(-13)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) -e^(i*x) e^(-i*x) k^(-e^(i*x)) k^(e^(-i*x)) 2*i*sin(x) -i*sin(x) (sin(x)) k
    if hyperbolic:
        comment('END HYPERBOLIC SINE')
    else:
        comment('END SINE')
    downindent()
    
def cos(hyperbolic=False):
    global dike
    #input (x) k k k k k k k k k k k k k k k k (16 k's)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) e^(-i*x) k^(e^(i*x)) k^(e^(-i*x)) 2*cos(x) (cos(x)) k
    if dike:
        return
    upindent()
    if hyperbolic:
        comment('HYPERBOLIC COSINE:')
    else:
        comment('COSINE:')
    right(1)
    if hyperbolic:
        go(1)
        makeneg1()
    else:
        makei()
    multiply(-2)
    go(1)
    makee()
    exptarget(-6)
    go(7)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) (k)
    copyfrom(-1)
    exptarget(-4)
    go(3)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e^(i*x)) e^(-i*x)
    add()
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) e^(-i*x) k^(e^(i*x)) k^(e^(-i*x)) (e^(i*x)+e^(-i*x)=2*cos(x))
    multiply(-12)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(i*x) e^(-i*x) k^(e^(i*x)) k^(e^(-i*x)) 2*cos(x) (cos(x)) k
    if hyperbolic:
        comment('END HYPERBOLIC COSINE')
    else:
        comment('END COSINE')
    downindent()
    
def tan(hyperbolic=False):
    global dike
    #input (x) k k k k k k k k k k k k k k k k k k (18 k's) (17 for hyperbolic)
    #output #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x)) 1-e^(-2*i*x) (1+e^(-2*i*x))^-1 i*tan(x) -i*tan(x) {(tan(x))} k
    if dike:
        return
    upindent()
    if hyperbolic:
        comment('HYPERBOLIC TANGENT:')
    else:
        comment('TANGENT:')
    right(1)
    if hyperbolic:
        go(1)
        makeneg1()
    else:
        makei()
    #x 1/2 (i)
    multiply(-2)
    go(1)
    makee()
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e)
    exptarget(-6)
    go(6)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) (e^(i*x))
    exptarget(-3)
    go(3)
    exptarget(-4)
    go(4)
    multiply(-3)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x))
    go(1)
    exptarget(-2)
    go(3)
    exptarget(-2)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x))
    go(3)
    multiply(-1,1)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x)) (k^(1-e^(-2*i*x))) k
    logtarget(1)
    multiply(-3,1)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x)) 1-e^(-2*i*x) (k^(1+e^(-2*i*x))) k 
    logtarget(1)
    go(-1)
    exptarget(-8)
    go(7)
    multiply()
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x)) 1-e^(-2*i*x) (1+e^(-2*i*x))^-1 ((1-e^(-2*i*x))/(1+e^(-2*i*x))=i*tan(x))
    multiply(-9)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x)) 1-e^(-2*i*x) (1+e^(-2*i*x))^-1 i*tan(x) (-i*tan(x))
    if not hyperbolic:
        multiply(-14)
    #x 1/2 i i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) e^(-2*i*x) (-e^(-2*i*x)) k^(e^(-2*i*x)) k^(-e^(-2*i*x)) 1-e^(-2*i*x) (1+e^(-2*i*x))^-1 i*tan(x) -i*tan(x) (tan(x)) k
    if hyperbolic:
        comment('END HYPERBOLIC TANGENT')
    else:
        comment('END HYPERBOLIC TANGENT')
    downindent()
    
def asin(hyperbolic=False):
    global dike
    #input (x) k k k k k k k k k k k k k k k k k k k k (20 k's) (19 for hyperbolic)
    #output: x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) i i*x k^(i*x) k^((1-x^2)^(1/2)) (1-x^2)^(1/2)+i*x 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*asin(x) -i*asin(x) (asin(x)) k
    if dike:
        return
    upindent()
    if hyperbolic:
        comment('INVERSE HYPERBOLIC SINE:')
    else:
        comment('INVERSE SINE:')
    go(1)
    makenum(2)
    go(1)
    makeneg1()
    go(1)
    # x 2 -1 (k)
    copyfrom(-3)
    exptarget(-2)
    go(3)
    # x 2 -1 x^2 (k)
    if not hyperbolic:
        exptarget(-2)
    go(2)
    # x 2 -1 x^2 (k^-1)
    exptarget(-1)
    go(2)
    # x 2 -1 x^2 k^(-x^2) (k)
    exptarget(0)
    # x 2 -1 x^2 k^(-x^2) (k^k)
    exptarget(-1)
    go(1)
    # x 2 -1 x^2 k^(-x^2) (k^k^(-x^2+1))
    logtarget(1)
    go(-1)
    logtarget(1)
    go(-1)
    # x 2 -1 x^2 k^(-x^2) (1-x^2)
    go(-4)
    exptarget(1)
    exptarget(-1)
    go(4)
    exptarget(-4)
    go(5)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) (k)
    if hyperbolic:
        makeneg1()
    else:
        copyfrom(-4)
    multiply(-6)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) i (i*x)
    add(-2)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) i i*x k^(i*x) k^((1-x^2)^(1/2)) ((1-x^2)^(1/2)+i*x)
    ln(True)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) i i*x k^(i*x) k^((1-x^2)^(1/2)) logK((1-x^2)^(1/2)+i*x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 (ln((1-x^2)^(1/2)+i*x)=i*asin(x))
    multiply(-4)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) i i*x k^(i*x) k^((1-x^2)^(1/2)) logK((1-x^2)^(1/2)+i*x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*asin(x) (-i*asin(x))
    if not hyperbolic:
        multiply(-12)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) i i*x k^(i*x) k^((1-x^2)^(1/2)) logK((1-x^2)^(1/2)+i*x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*asin(x) -i*asin(x) (asin(x))
    if hyperbolic:
        comment('END INVERSE HYPERBOLIC SINE')
    else:
        comment('END INVERSE SINE')
    downindent()

def acos(hyperbolic=False):
    global dike
    #input (x) k k k k k k k k k k k k k k k k k k k k (19 k's) (18 for hyperbolic)
    #output: x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) (1-x^2)^(1/2)*i k^((1-x^2)^(1/2)*i) k^x logK((1-x^2)^(1/2)*i+x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*acos(x) -i*acos(x) (acos(x)) k
    if dike:
        return
    upindent()
    if hyperbolic:
        comment('INVERSE HYPERBOLIC COSINE')
    else:
        comment('INVERSE COSINE:')
    go(1)
    makenum(2)
    go(1)
    makeneg1()
    go(1)
    # x 2 -1 (k)
    copyfrom(-3)
    exptarget(-2)
    go(3)
    # x 2 -1 x^2 (k)
    exptarget(-2)
    go(2)
    # x 2 -1 x^2 (k^-1)
    exptarget(-1)
    go(2)
    # x 2 -1 x^2 k^(-x^2) (k)
    exptarget(0)
    # x 2 -1 x^2 k^(-x^2) (k^k)
    exptarget(-1)
    go(1)
    # x 2 -1 x^2 k^(-x^2) (k^k^(-x^2+1))
    logtarget(1)
    go(-1)
    logtarget(1)
    go(-1)
    # x 2 -1 x^2 k^(-x^2) (1-x^2)
    go(-4)
    exptarget(1)
    exptarget(-1)
    go(4)
    exptarget(-4)
    go(4)
    # x 1/2 i x^2 k^(-x^2) ((1-x^2)^(1/2)) k
    multiply(-3)
    add(-6)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) (1-x^2)^(1/2)*i k^((1-x^2)^(1/2)*i) k^x (x+(1-x^2)^(1/2)*i)
    ln(True)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) (1-x^2)^(1/2)*i k^((1-x^2)^(1/2)*i) k^x logK((1-x^2)^(1/2)*i+x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 (ln((1-x^2)^(1/2)*i+x)=i*acos(x))
    multiply(-4)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) (1-x^2)^(1/2)*i k^((1-x^2)^(1/2)*i) k^x logK((1-x^2)^(1/2)*i+x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*acos(x) (-i*acos(x))
    if not hyperbolic:
        multiply(-15)
    # x 1/2 i x^2 k^(-x^2) (1-x^2)^(1/2) (1-x^2)^(1/2)*i k^((1-x^2)^(1/2)*i) k^x logK((1-x^2)^(1/2)*i+x) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*acos(x) -i*acos(x) (acos(x)) k
    if hyperbolic:
        comment('END INVERSE HYPERBOLIC COSINE')
    else:
        comment('END INVERSE COSINE')
    downindent()
    
#TODO: Make sure this has the same result in terms of k's consumed for all possible inputs, including adjacent associates, and returns the proper infinities
def atan2():
    global dike
    #input: (y) x k k k k k k k k k k k k k k k k k k k k k k k k {k {k k k}} (24/25/28 k's)
    #output: y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 
    #         logK(e)^-1 i*atan2(y,x) -i*atan2(y,x) (atan2(y,x)) k
    # OR
    #        y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|² |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty (infty*i) k
    # OR
    #        y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|² |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty infty*i (-infty*i) k
    if dike:
        return
    upindent()
    comment('INVERSE TANGENT:')
    go(2)
    copyfrom(-1)
    conj()
    multiply(-1)
    go(1)
    makeneg1()
    go(1)
    makei()
    #y x x* |x|² -1 1/2 (i)
    multiply(-6)
    #y x x* |x|² -1 1/2 i (yi)
    add(-6)
    #y x x* |x|² -1 1/2 i yi k^yi k^x (x+yi)
    go(1)
    square(-11)
    go(1)
    square(-11)
    #y x x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 (x^2)
    go(-1)
    add()
    #y x x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)
    go(1)
    copyfrom(-1)
    conj()
    multiply(-1)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* (|x^2+y^2|²)
    exptarget(-14)
    go(14)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* (|x^2+y^2|^(2|x|²))
    ifnonpositive('atan2')
    #so x is nonzero but the denominator is zero
    copyfrom(-8)
    ifzero('atan2inner')
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| (k)
    #so the numerator is zero so the answer is i*infty
    go(-1)
    reciprocal()
    multiply(-17)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty (infty*i) k
    els('atan2inner')
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| 1 |x+yi| ~|x+yi| (k)
    #so the numerator is nonzero so the answer is -i*infty
    go(-1)
    reciprocal()
    multiply(-17)
    multiply(-19)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty infty*i (-infty*i) k
    endif('atan2inner')
    els('atan2')
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 (k)
    go(-5)
    exptarget(-11)
    go(11)
    exptarget(-10)
    go(15)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 (k)
    multiply(-5,-10)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 ((x+yi)/(x^2+y^2)^(1/2))
    ln(True)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 (ln((x+yi)/(x^2+y^2)^(1/2))=i*atan2(y,x))
    multiply(-4)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*atan2(y,x) (-i*atan2(y,x))
    multiply(-22)
    #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*atan2(y,x) -i*atan2(y,x) (atan2(y,x))
    endif('atan2')
    left(2)
    comment('END INVERSE TANGENT')
    downindent()

#TODO: make this use only one argument, and add ability to do artanh.
def atan(hyperbolic=False):
    global dike
    #input: (y) x k k k k k k k k k k k k k k k k k k k k k k k k {k {k k k}} (24/25/28 k's)
    #output: y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 
    #         logK(e)^-1 i*atan2(y,x) -i*atan2(y,x) (atan2(y,x)) k
    # OR
    #        y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|² |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty (infty*i) k
    # OR
    #        y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|² |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty infty*i (-infty*i) k
    if dike:
        return
        upindent()
        if hyperbolic:
            comment('INVERSE HYPERBOLIC TANGENT')
        else:
            comment('INVERSE TANGENT:')
        go(2)
        copyfrom(-1)
        conj()
        multiply(-1)
        go(1)
        makeneg1()
        go(1)
        makei()
        #y x x* |x|² -1 1/2 (i)
        multiply(-6)
        #y x x* |x|² -1 1/2 i (yi)
        add(-6)
        #y x x* |x|² -1 1/2 i yi k^yi k^x (x+yi)
        go(1)
        square(-11)
        go(1)
        square(-11)
        #y x x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 (x^2)
        go(-1)
        add()
        #y x x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)
        go(1)
        copyfrom(-1)
        conj()
        multiply(-1)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* (|x^2+y^2|²)
        exptarget(-14)
        go(14)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* (|x^2+y^2|^(2|x|²))
        ifnonpositive('atan')
        #so x is nonzero but the denominator is zero
        copyfrom(-8)
        ifzero('ataninner')
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| (k)
        #so the numerator is zero so the answer is i*infty
        go(-1)
        reciprocal()
        multiply(-17)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty (infty*i) k
        els('ataninner')
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| 1 |x+yi| ~|x+yi| (k)
        #so the numerator is nonzero so the answer is -i*infty
        go(-1)
        reciprocal()
        multiply(-17)
        multiply(-19)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) x+yi 1/2 (x+yi)* |x+yi| infty infty*i (-infty*i) k
        endif('ataninner')
        els('atan')
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 (k)
        go(-5)
        exptarget(-11)
        go(11)
        exptarget(-10)
        go(15)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 (k)
        multiply(-5,-10)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 ((x+yi)/(x^2+y^2)^(1/2))
        ln(True)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 (ln((x+yi)/(x^2+y^2)^(1/2))=i*atan2(y,x))
        multiply(-4)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*atan2(y,x) (-i*atan2(y,x))
        if not hyperbolic:
            multiply(-22)
        #y x  x* |x|² -1 1/2 i yi k^yi k^x x+yi y^2 x^2 k^y^2 k^x^2 (x^2+y^2)^(-1/2) (x^2+y^2)* |x^2+y^2|^(2|x|²) k 0 logK((x+yi)/(x^2+y^2)^(1/2)) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) logK(e)^-1 i*atan2(y,x) -i*atan2(y,x) (atan2(y,x))
        endif('atan')
        left(2)
        if hyperbolic:
            comment('END INVERSE HYPERBOLIC TANGENT')
        else:
            comment('END INVERSE TANGENT')
        downindent()
    
    
###CODE GENERATION AREA
if len(sys.argv)<2:
    print('SELECT. Code generator v.'+str(version)+' by Quintopia.\nUsage: python selectcodegen.py [filename]')
try:
    openfile = file(sys.argv[1],"r")
except IOError:
    print("File not found.")
    sys.exit()
else:
    theFile = openfile.read()
    openfile.close()

testlist = theFile.split('######GENERATION CODE######')
if len(testlist)<2:
    print "File must contain ######GENERATION CODE######"
else:
    code = testlist[1]
    exec(code)