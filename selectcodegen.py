# -*- coding: utf-8 -*-
#SELECT. Code Generator v0.3 by Quintopia
# All code-generating functions in this file are right-growing, meaning they make the following guarantees:
# * They do not read or write cells to the left of the current cell at call time.
# * The result that the algorithm computes will be contained in the rightmost cell clobbered by the algorithm.
# * The current cell upon completion will be the one containing the answer.
# * They do not clobber the arguments passed to them (or rather, if they do, they restore them before returning)
# At call time, you must be able to guarantee the current cell is the leftmost argument and that there are 
# sufficiently many unclobbered cells to the right of the current cell.
# See comments inside individual generating functions for info on which cells need to be untouched, which are clobbered,
# and what values they contain upon algorithm completion.
# To use a left-growing algorithm instead, use leftgr(). 
# E.g.: leftgr(add) writes out a left-growing addition algorithm with the sum leftmost

#TODO: test padded conditionals, arg


from re import sub,DOTALL
import sys

s=''
h=0
w=0
indentlevel=0
vardict = {}
offset = 0
dike = False

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
               '.':[(-1,3)],
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

#optimize the program string and write it to the named file
def writetofile(filename):
    global s,code
    s = sub('\n\s*?\n\s*?\n','\n\n',s)
    filename = sub('.sel','',filename)
    oldstring=s
    while True:
        oldstring=s
        s=sub('(?s)LEFT\.(?P<comment>(?:(?=(?P<tmp>\s*\*%.*?%\*\s*))(?P=tmp))*)RIGHT\. ','\g<comment>',s)
        if oldstring==s:
            break
    while True:
        oldstring=s
        s=sub('(?s)RIGHT\.(?P<comment>(?:(?=(?P<tmp>\s*\*%.*?%\*\s*))(?P=tmp))*)LEFT\. ','\g<comment>',s)
        if oldstring==s:
            break
        
    s = sub('\n\s*?\n\s*?\n','\n\n',s)
    s = sub('\*%(?P<comment>.*)%\*','\g<comment>',s)
    s = sub('\n\n','\n \n',s) #so we can post these to the wiki easily
    
    s+='\n######GENERATION CODE######'+code+'\n'
    
    try:
        openfile = file(filename+'.sel',"w")
    except IOError:
        print("File not found.")
        sys.exit()
    theFile = openfile.write(s)
    openfile.close()
    s=''
    
def leftgr(fun,arg1=None,arg2=None):
    global s
    startlength = len(s)
    if arg==None:
        fun()
    elif arg2==None:
        fun(arg1)
    else:
        fun(arg1,arg2)
    if len(s)>startlength:
        newend=s[startlength:].replace('RIGHT. ','repl ')
        newend=newend.replace('LEFT. ','RIGHT. ')
        newend=newend.replace('repl ','LEFT. ')
        s=s[0:startlength]+newend

def turnoff():
    global dike
    dike=True
    
def turnon():
    global dike
    dike=False
#######################FILE FORMATTING AND DECORATION#########################

def comment(note):
    global s,indentlevel,dike
    if dike:
        return
    s+='\n*%'+(' '*indentlevel)+note+'%*\n'+(' '*indentlevel)

def init(x,y,z):
    global s,h,w
    h=y
    w=x
    s="("+str(x)+","+str(y)+","+str(z)+")\n"

def upindent():
    global s,indentlevel
    indentlevel+=3
    s+='\n'+(' '*indentlevel)

def downindent():
    global s,indentlevel
    indentlevel-=3
    s+='\n'+(' '*indentlevel)
    
    
    
    
    
    

#################################IO CODE GENERATORS#############################
#TODO: drawing letterforms
#TODO: R,G,B to complex number conversion
def output():
    global s,dike
    if dike:
        return
    s+='PRINT. '

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
    global s,dike
    if dike:
        return
    s+='GET. '

def outputleft(n):
    global s,dike
    if dike:
        return
    output()
    for i in range(n-1):
        left(1)
        output()
    right(n-1)

def outputright(n):
    global s,dike
    if dike:
        return
    output()
    for i in range(n-1):
        right(1)
        output()
    left(n-1)

def clear():
    global s,dike
    if dike:
        return
    s+='CLEAR. '

def color():
    global s,dike
    if dike:
        return
    s+='COLOR. '

def drawString(string,x,y,top=0,bottom=None,left=0,right=None):
    global dike,h,w
    if dike:
        return
    upindent()
    comment('DRAW STRING LITERAL "'+string+"'")
    if bottom is None:
        bottom=h
    if right is None:
        right=w
    string = string.replace('\n',' \n')  #insert a space before every newline to simplify algorithm
    string = string.replace('\t',' \t')  #same for tabs
    for i,c in enumerate(string):
        if y>bottom:                            #if we would go off the bottom of the screen, block for input instead, then clear once we have it
            go(-1)
            input()
            go(1)
            clear()
            y=top
        if c=='\t':
            x=x+15                                      #counting the space before the tab, a tab is four spaces
            continue
        remainder = string.find(' ',i+1)-i
        nextword = string.find(' ',i+remainder+1)-remainder
        if x>right or c=='\n' or (x+5*remainder>right and remainder*5<right-left and nextword*5<right-left):  #reset to left side if we're off the right side (from tabbing) or at newline or will not see whitespace before we hit the right side unless the next word is longer than a line
            y=y+12
            x=left
            if c=='\n':                             #go on to next character if it was a newline, otherwise try to print current char
                continue
        if c!=' ':
            drawLetterXY(c,x,y)
        x=x+5
    comment('END DRAW STRING LITERAL "'+string+"'")
    downindent()

def drawLetterXY(c,x,y):
    global letterforms,dike
    if dike:
        return
    upindent()
    comment('DRAW LETTER "'+c+'" AT ('+str(x)+','+str(y)+')')
    form = letterforms[c]
    if form is None:
        return
    for n in form:
        makenum(x+n[0]+3,y+n[1]+6)
        output()
        go(1)
    comment('END DRAW LETTER "'+c+'"')
    downindent()


def drawLetter(c):
    global letterforms,dike
    if dike:
        return
    upindent()
    comment('DRAW LETTER "'+c+'"')
    var('drawLetterPosition')
    if c=='\t':
        go(1)
        makenum(20)
        add(-1)
        return
    if c=='\n':
        go(1)
        makenum(imag=12)
        add(-1)
        return
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
    global s,offset,dike
    if dike:
        return
    for i in range(n):
        s+='LEFT. '
        offset-=1

def right(n):
    global s,offset,dike
    if dike:
        return
    for i in range(n):
        s+='RIGHT. '
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
    global s,indentlevel,dike
    if dike:
        return
    s+='EXP. '
    if n<0:
        left(-n)
    elif n>0:
        right(n)
    s+='SELECT.\n'+(' '*indentlevel)

def logtarget(n):
    global s,indentlevel,dike
    if dike:
        return
    s+='LOG. '
    if n<0:
        left(-n)
    elif n>0:
        right(n)
    s+='SELECT.\n'+(' '*indentlevel)

def copyfrom(n):
    global dike
    if dike:
        return
    exptarget(n)
    go(-n)
    logtarget(1)
    left(1)

def var(name):
    global dike
    if dike:
        return
    global vardict,offset,s,indentlevel
    vardict[name] = offset
    #add the comment here manually so that it doesn't get the left/right stripped from around it, so that we actually are on the cell the comment claims to be marking.
    #yes, it doesn't change the behavior of the code to strip them, but the code we output should be correctly documented
    s+='\n'+(' '*indentlevel)+'MARK AS '+name+'\n'+(' '*indentlevel)

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
    s+='HALT. \n!!!!PROGRAM EXIT POINT!!!!\n'






################################################LOOPING############################################
#TODO: Test loops with their counts stored on tape.
#TODO: Test (bounded and simple) loops with the auto-fetching savelist
def loop(name,start=0,end=None,step=1,computei=False,savelist=None):
    global s,dike
    if dike:
        return
    #input: [(k) | (x) k] k k k k k k k k k k k k k k k k k k k {k k k k {k k} {k k k k {k k k}}} (20,24/26,28/30,31/33)k's
    #output: 1/sqrt(2) -1 1/2 i -1 k^i k^-1 -1+i (-1+i)/sqrt(2) -1 1/n 1/2 i^(1/(2n)) k k*i^(1/(2n)) (sentinel) {k}...
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
    go(1)
    makeneg1()
    go(1)
    if end is None:
        copyFrom(-10)
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
    #...-1 1/n 1/2 i^(1/(2n)) k (k*i^(1/(2n))) k
    if savelist is not None:
        go(1)
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
        go(1) #leave a gap for where the old sentinel will be fetched in endloop
        fetch(name+'step')
        var(name+'step')
    #invalidate all variables which are not being saved (as looping will make their offsets wrong anyway)
    for key in savelist:
        if key not in savelist and key!=name+'step' and key!=name+'sentinel':
            del vardict[key]
    go(1)
    fetch(name+'sentinel')
    var(name+'sentinel')
    s+='LOOP. '
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
            go(-1)
            add()
            #...loopcount {step loopcount*step} start k^(loopcount*step) k^start (i) k
        elif start<0:
            go(1)
            makeneg(-start)
            go(1)
            copyfrom(-5)
            go(-1)
            add()

            #...loopcount {step loopcount*step} 2 -1 -start start loopcount*step k^start k^loopcount*step (i) sentinel step i k
    #do not down indent. that is in endloop()
    
def endloop(name,computei=False,start=0,savelist=None):
    global s,dike
    if dike:
        return
    #input: (k) k k k {k k k k k {k k k k {k k k k}}} (4,9,13,17)k's
    #output: oldsentinel step (newsentinel) {k}...
       #...1/2 sentinel* loopcount step...                                                  computei=True and...
       #...(i) k                                                                            ...start=0
       #...loopcount*step start k^(loopcount*step) k^start (i) k                            ...start>0
       #...loopcount*step 2 -1 -start start loopcount*step k^start k^loopcount*step (i) k   ...start<0
    if savelist is not None:
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
    s+='END. '
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
            makeneg(-start)
            go(1)
            copyfrom(-5)
            go(-1)
            add()
            #...loopcount step loopcount*step 2 -1 -start start loopcount*step k^start k^loopcount*step (i) k
            #do not down indent. that is in endloop()
    comment('END OF LOOP '+name)
    downindent()

def repeat(savelist=None):
    global s,dike
    if dike:
        return
    upindent()
    comment("WHILE")
    if savelist is not None:
        var("repeatsentinel")
        go(1)
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
        fetch("repeatsentinel")
    s+="LOOP. "

def endrepeat(savelist=None):
    global s,dike
    if dike:
        return
    if savelist is not None:
        var("repeatsentinel")
        go(1)
        for varname in savelist:
            fetch(varname)
            var(varname)
            go(1)
        fetch("repeatsentinel")
    s+="END. "
    comment("END WHILE")
    downindent()







##############################################CONDITIONALS##################################################
def ifnonpositive(name):
    global s,dike
    if dike:
        return
    #x must be a real number!
    #input: (x) ?
    #output: (x) ?
    upindent()
    comment('IF ('+name+'):')
    s+='LOOP. '
    var('ifstart'+name)
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
    global s,dike,offset
    if dike:
        return
    #input: (x|?) k k k k
    #output: x k 0 (x) k
    if s.rfind('PADPOINT1'+name)<0:
        padpoint1(name)
    go(1)
    var('ifone'+name)
    go(1)
    makezero()
    go(-1)
    downindent()
    s+='END. '
    go(1)
    lnot()
    comment('ELSE ('+name+'):')
    s+='LOOP. '
    #THE OFFSET HERE WOULD BE THE SAME AS THE OFFSET AT THE BEGINNING OF THE FIRST IF BLOCK PLUS 2 (since only one of the two will be executed)
    offset+=getoffset('ifstart'+name)+2
    var('ifelse'+name)
    upindent()
    if copy:
        go(1)
        copyfrom(-2)

def endif(name):
    global s,dike,vardict,offset
    if dike:
        return
    #input: (x) k
    #output: (x) k 
    #if an else branch wasn't needed for program logic but the tapehead moved, insert one anyway just to prevent tape usage differing depending on conditional result
    if 'ifelse'+name not in vardict and getoffset('ifstart'+name)!=0:
        els(name,False)
    #no padding necessary if there is no else block and the tape head did not move
    if 'ifelse'+name in vardict:
        #calculate displacement of first branch
        b1length = getoffset('ifone'+name)-getoffset('ifstart'+name)
        if s.rfind('PADPOINT2'+name)<0:
            padpoint2(name)
        go(1)
        #calculate displacement of second branch
        b2length = -getoffset('ifelse'+name)
        #output rights
        if b2length>b1length:
            #this branch is further right. insert rights at padpoint1
            padlength=b2length-b1length
            offset+=padlength
            s=s.replace('PADPOINT1'+name,'({'+'RIGHT. '*padlength+'})')
            s=s.replace('PADPOINT2'+name,'')
        else:
            #insert rights at padpoint2
            padlength=b1length-b2length
            offset+=padlength
            s=s.replace('PADPOINT2'+name,'({ '+'RIGHT. '*padlength+'}) ')
            s=s.replace('PADPOINT1'+name,'')
    downindent()
    s+='END. '
    go(1)
    comment('END IF ('+name+')')
    downindent()
    
def padpoint1(name):
    global s,dike
    if dike:
        return
    s+='PADPOINT1'+name
    
def padpoint2(name):
    global s,dike
    if dike:
        return
    s+='PADPOINT2'+name

#combined if/else/end overhead: firstbranch: x {...} k 1 (k)
#                               secondbranch: x 0 x {...} (k)
#for ifzero:                     firstbranch: x 1/2 x* |x| {...} k 1 (k)
#                               secondbranch: x 1/2 x* |x| 0 x {...} (k)
#because of automatic padding, the overhead is the same no matter which branch is chosen ...this is what makes looping over conditionals possible!




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
    #input: y...x ...(k) k or (k) k ... y ... x (or x and y flipped)
    #output: y...x...(x*y) k or (x*y) k ... y ... x (etc.)
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

def reciprocal():
    global dike
    #this only works if x!=1! obviously, in that case you needn't be reciprocating anyway, but if you can't guarantee it, do x^-1 manually instead
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
    #input (x) k k
    #output x (-x) k
    if dike:
        return
    upindent()
    comment('(opposite)')
    reciprocal()
    #x (1/x) k
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
    global s,dike
    if dike:
        return
    s+='CONJ. '

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
    #input: (x) k k k k k k k k k (9 k's)
    #output: x x* k^x k^x* 2Re(x) 1/2 2Re(x) (Re(x)) k
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
    right(1)
    copyfrom(-2)
    left(1)
    multiply()
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
    #input (x) k k k k k k k k k k k k k (13 k's)
    #output #x -1 x* 1/|x| logK(x/|x|) 3.09485e+26 1/2 -i 3.23117e-27 k^(3.23117e-27) 1/logK(e) ln(x/|x|) (arg(x)) k
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
    go(4)
    multiply(-2,-5)
    #x 1/2 x* 1/|x| i (x/|x|)
    ln(True)
    #x 1/2 x* 1/|x| i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) (ln(x/|x|))
    go(-8)
    exptarget(4)
    go(4)
    multiply(-8)
    #x 1/2 x* 1/|x| -i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) ln(x/|x|) (arg(x))
    comment('END ARGUMENT')
    #x 1/2 x* 1/|x| -i logK(x/|x|) 3.09485e+26 2 -1 3.23117e-27 k^(3.23117e-27) 1/logK(e) ln(x/|x|) (arg(x)) k
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
    print('SELECT. Code generator v. 1.0 by Quintopia.\nUsage: python selectcodegen.py [filename]')
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