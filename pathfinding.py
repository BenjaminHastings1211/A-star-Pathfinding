from tkinter import *
import random,math,time

W,H = 700,700

CPL = 25

colors = {
    "COVERED":"#fff",
    "START" : "#00f",
    "END"   : "#ff0",
    "OPEN" : "#0f0",
    "CLOSED": "#f00",
    "WALL"  : '#000',
    "FINAL" : '#ffaa1d'
}

def mapVal(s,a1,a2,b1,b2):
    return b1 + ((s - a1)*(b2-b1))/(a2-a1)

def CalcHCost(n1,n2):
    cost = 0
    adj = 10
    dia = 14
    xDiff = abs(n1[0]-n2[0])
    yDiff = abs(n1[1]-n2[1])
    while xDiff > 0 or yDiff > 0:
        if xDiff >= 1 and yDiff >= 1:
            xDiff -= 1
            yDiff -= 1
            cost += dia
        else:
            if xDiff >= 1:
                xDiff -= 1
                cost += adj
            else:
                yDiff -= 1
                cost += adj
    return cost


class Board():
    def __init__(self,root,solve):
        self.start = None
        self.end = None
        self.solve = solve
        self.container = Frame(root,width=W,height=H,bg='black')
        self.container.pack(side=RIGHT)
        self.nodes = self.generate_Nodes()
        self.open = []

        self.mode = 'PLACE'
        self.wallPlacing = False
        root.bind('<space>',self.change_mode)
        root.bind('w',self.toggleWall)

        self.placement = Frame(root,width=150,height=H+CPL*2,bg='#fdfdfd')
        self.placement.pack(side=LEFT)

        Label(self.placement,text='A* Pathfinding',justify='center',font=('Arial',22),bg=self.placement['bg']).place(relx=0.5,y=15,anchor='c')
        self.modeL = Label(self.placement,text="Mode: %s"%self.mode,bg=self.placement['bg'])
        self.modeL.place(relx=0.5,y=40,anchor='c')

    def toggleWall(self,e):
        switch = {True : False, False : True}
        self.wallPlacing = switch[self.wallPlacing]


    def change_mode(self,e):
        mode = {
            'RUN' : 'PLACE',
            'PLACE' : 'RUN'
        }
        self.mode = mode[self.mode]
        self.modeL['text'] = "Mode %s"%self.mode

    def generate_Nodes(self):
        size = int(W/CPL)
        final = []
        for y in range(CPL):
            row = []
            for x in range(CPL):
                row.append(Node(self,self.container,[y,x],size))
            final.append(row)
        return final

    def getNode(self,pos):
        return self.nodes[pos[0]][pos[1]]

    def finalPath(self):
        node = self.getNode(self.end)
        pointTo = node
        while pointTo != self.getNode(self.start):
            node = node.pointTo
            node.changeState("FINAL")
            pointTo = node.pointTo
        self.solve()

class Node():
    def __init__(self,parent,root,pos,size,state='COVERED'):
        self.gCost = 0 # dist from Start
        self.hCost = None # dist from End
        self.fCost = None # sum of g and h

        self.pointTo = None

        self.pos = pos
        self.parent = parent
        self.state = state
        self.root = root
        self.Obj = Frame(root,width=size,height=size,bg=colors[self.state])
        self.Obj.grid(row=self.pos[0],column=self.pos[1],padx=1,pady=1)

        self.Obj.bind('<Enter>',lambda x: self._handleWall())
        self.Obj.bind('<Double-Button-1>',lambda x:self.placePoints())

    def placePoints(self):
        if self.parent.mode == 'PLACE':
            if self.parent.start == None:
                self.parent.start = self.pos
                self.changeState('START')
            else:
                self.parent.end = self.pos
                self.changeState('END')

    def changeState(self,state):
        self.state = state
        self.Obj['bg'] = colors[self.state]
        if state == "OPEN" and state != "START":
            self.updateCost()

    def updateCost(self):
        if self.state in ['OPEN', 'CLOSED']:
            self.hCost = CalcHCost(self.pos,self.parent.end)
            self.fCost = self.hCost + self.gCost

    def searchNode(self,removeFromOpen=True):
        n = [[-1,-1,14],[-1,0,10],[-1,1,14],[0,-1,10],[0,1,10],[1,-1,14],[1,0,10],[1,1,14]]

        gCosts = []
        for adj in n:
            y = adj[0] + self.pos[0]
            x = adj[1] + self.pos[1]
            if x >= 0 and x < CPL and y >= 0 and y < CPL:
                node = self.parent.getNode([y,x])

                if node.gCost > self.gCost + adj[2] or node.gCost == 0:
                    node.gCost = self.gCost + adj[2]

                if node.state != 'WALL':
                    gCosts.append([node.gCost,node])

                if node.state not in ['CLOSED','START', 'END','WALL']:
                    if node not in self.parent.open:
                        self.parent.open.append(node)
                    node.changeState("OPEN")
                node.updateCost()


        if self.state != "START" and self.state != "END":
            self.changeState("CLOSED")
            if removeFromOpen == True:
                self.parent.open.remove(self) # CAREFUL!!!!!!!!!!
            node.updateCost()

        nodes = [node.state for node in map(lambda x: x[1],gCosts)]
        if 'START' in nodes:
            self.pointTo = gCosts[nodes.index('START')][1]
        else:
            low = sorted(gCosts,key= lambda x : x[0])[0]
            self.pointTo = low[1]
            if 'END' in nodes:
                gCosts[nodes.index('END')][1].pointTo = self
                self.parent.finalPath()

        if self.state == 'START':
            self.pointTo = 'me!'

    def _handleWall(self):
        if self.parent.mode == 'PLACE' and self.parent.wallPlacing == True:
            if self.state == 'COVERED':
                self.changeState("WALL")
            else:
                self.changeState("COVERED")

    def __str__(self):
        return 'x: %i,y: %i'%(self.pos[1]+1,self.pos[0]+1)


class Algorithum():
    def __init__(self):
        self.first = True
        self.done = False
        self.board = Board(root,self.solved)

    def next(self):
        if self.first == True:
            self.board.getNode(self.board.start).searchNode()
            self.first = False

        minF = sorted(self.board.open, key=lambda x: x.fCost)[0].fCost
        check = sorted([node for node in self.board.open if node.fCost == minF], key= lambda x : x.gCost)[0]
        check.searchNode()

    def solved(self):
        self.done = True
        for row in self.board.nodes:
            for node in row:
                if node.state not in ['WALL', 'FINAL', 'START', 'END']:
                    node.changeState("COVERED")

root = Tk()
root.title('pathfinding')
root.wm_attributes('-topmost',1)
root.resizable(0,0)

a = Algorithum()

# board = Board(root,[3,1],[1,6],lambda : print('hi'))
# board.getNode(board.start).searchNode(inital=True)

W += CPL*2
H += CPL*2
root.geometry("%sx%s"%(W+150,H))

# things

while 1:
    if a.done == False and a.board.mode == 'RUN':
        a.next()
    root.update()
    root.update_idletasks()
    time.sleep(0.001)
