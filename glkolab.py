# GLKolab: OpenGL based 2D Whiteboard System

# Putu Wiramaswara Widya <initrunlevel0@gmail.com>
# https://github.com/initrunlevel0/GLKolab

### MAIN LIBRARY IMPORT
import ctypes
import pyglet
from pyglet.gl import *

### GLOBAL VARIABLE
window = pyglet.window.Window(800,600) 

# Text Label Definition
logoLabel = pyglet.text.HTMLLabel('<font size=5 face="Helvetica" color="white"><strong>GL</strong>Kolab</font>', x=100, y=580, anchor_x='center', anchor_y='center')
cldis = pyglet.clock.ClockDisplay()
toolLabel = {} 
userLoginLabel = {}

canvasDrawObject = []
selected_color = [1.0, 1.0, 1.0]
state = "None"
selected_tool = "Select"



### DRAWING CLASS DEFINITION
class DrawObject:
	selected = False
	def draw(self):
		raise NotImplementedError()
	
	def __init__(self):
		raise NotImplementedError()
	
class VertexedObject(DrawObject):
	
	def draw(self):
		raise NotImplementedError()
	
	def get_far_left(self):
		a = float('inf')
		for v in self.vertex:
			a = min(a, v[0])
		return int(a)

				
	def get_far_right(self):
		a = 0
		for v in self.vertex:
			a = max(a, v[0])
		return int(a)

	
	def get_far_top(self):
		a = 0
		for v in self.vertex:
			a = max(a, v[1])
		return int(a)

			
	def get_far_bottom(self):
		a = float('inf')
		for v in self.vertex:
			a = min(a, v[1])
		return int(a)
	
	
	def get_size_x(self):
		return self.get_far_right() - self.get_far_left()

	def get_size_y(self):
		return self.get_far_bottom() - self.get_far_top()
		pass

	def draw_selected(self):
		# Draw rectangle of selection
		glLineWidth(1.0)
		glColor3f(0.0,0.0, 0.0)
		glBegin(GL_LINE_LOOP)
		glVertex3f(self.get_far_left(), self.get_far_top(), 0.0)
		glVertex3f(self.get_far_right(), self.get_far_top(), 0.0)
		glVertex3f(self.get_far_right(), self.get_far_bottom(), 0.0)
		glVertex3f(self.get_far_left(), self.get_far_bottom(), 0.0)
		glEnd()

		# Draw mini point for every corner
		glPointSize(10.0)
		
		# Top-Left
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_left(), self.get_far_top(), 0.0)
		glEnd()
		
		# Top-Right
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_right(), self.get_far_top(), 0.0)
		glEnd()

		# Bottom-Right
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_right(), self.get_far_bottom(), 0.0)
		glEnd()

		# Bottom-Left
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_left(), self.get_far_bottom(), 0.0)
		glEnd()

				
	def __init__(self):
		self.vertex = []
	

class BezierCurve(VertexedObject):
	curvePrecision = 101
	def draw(self):
		# Draw only its line curve
		c_vertex = ((ctypes.c_float * 3) * len(self.vertex)) (*self.vertex)
		glMap1f(GL_MAP1_VERTEX_3, 0.0, 100.0, 3, len(self.vertex), c_vertex[0])
		glEnable(GL_MAP1_VERTEX_3)
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		for i in range(0, self.curvePrecision):
			glEvalCoord1f(i)
		glEnd()
		
		if state == "None":
			pass
			
		elif (state == "Drawing") and (self.selected == True):
			
			# Draw dot for every vertex
			for v in self.vertex:
				glPointSize(10.0)
				glBegin(GL_POINTS)
				glVertex3f(v[0], v[1], 0.0)
				glEnd()
			pass
		
		elif (state == "Selecting") and (self.selected == True):
			self.draw_selected()
		glFlush()
	def __init__(self, firstX, firstY, isPolygon):
		global state
		VertexedObject.__init__(self)
		
		self.vertex = []
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

class Pencil(VertexedObject):
	def draw(self):
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		for v in self.vertex:
			glVertex3f(v[0], v[1], 0.0)
		glEnd();

		if (state == "Selecting") and (self.selected == True):
			self.draw_selected()
		
		glFlush()
	def __init__(self, firstX, firstY):
		global state
		VertexedObject.__init__(self)
		self.vertex = []
		self.selected = False
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

class Line(VertexedObject):
	def draw(self):
		# Draw only its line curve
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		for v in self.vertex:
			glVertex3f(v[0], v[1], 0.0)
		glEnd()
		
		if state == "None":
			pass
			
		elif (state == "Drawing") and (self.selected == True):
			
			# Draw dot for every vertex
			for v in self.vertex:
				glPointSize(10.0)
				glBegin(GL_POINTS)
				glVertex3f(v[0], v[1], 0.0)
				glEnd()
		elif (state == "Selecting") and (self.selected == True):
			self.draw_selected()
		
		glFlush()
	def __init__(self, firstX, firstY, isPolygon):
		global state
		VertexedObject.__init__(self)
		self.selected = False
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))
		
### DO DRAWING PRIMITIVE
def getSelectedObject(X, Y):
	global state, drawedObject
	# Clear All Selection First
	drawedObject = -1
	for obj in canvasDrawObject:
		obj.selected = False

	# Choose ONLY ONE object which in the point
	for obj in canvasDrawObject:
		if(obj.get_far_left() <= X and obj.get_far_right() >= X and obj.get_far_top() >= Y and obj.get_far_bottom() <= Y):
			state = "Selecting"
			print "Selecting on " + str(X) + " " + str(Y)	
			drawedObject = obj
			obj.selected = True
			break
		else:
			obj.selected = False
			drawedObject = -1
			state = "None"
				
def doMovement(dX, dY):
	if(drawedObject != -1):
		for i in range(len(drawedObject.vertex)):
			drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)

def doResize(dX, dY, side):
	if(drawedObject != -1):
		for i in range(len(drawedObject.vertex)):

			if(side == "TopLeft"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_bottom() and drawedObject.vertex[i][0] != drawedObject.get_far_right()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
		
			elif(side == "TopRight"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_bottom() and drawedObject.vertex[i][0] != drawedObject.get_far_left()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
			elif(side == "BottomRight"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_top()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_top()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_top() and drawedObject.vertex[i][0] != drawedObject.get_far_left()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
			elif(side == "BottomLeft"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_top()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_top()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_top() and drawedObject.vertex[i][0] != drawedObject.get_far_right()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
			
def drawBezierCurve(firstX, firstY, isPolygon):
	global drawedObject, state
	bc = BezierCurve(firstX, firstY, isPolygon)
	canvasDrawObject.append(bc)
	drawedObject = bc
	bc.selected = True
	window.flip()
	state = "Drawing"
	
def drawPencil(firstX, firstY):
	global drawedObject, state
	p = Pencil(firstX, firstY)
	canvasDrawObject.append(p)
	drawedObject = p
	p.selected = True
	
	window.flip
	state = "Drawing"

def drawLine(firstX, firstY, isPolygon):
	global drawedObject, state
	l = Line(firstX, firstY, isPolygon)
	canvasDrawObject.append(l)
	drawedObject = l
	l.selected = True
	window.flip()
	state = "Drawing"
	
### UI DESIGN

def drawButton(x, y, text, selected):
	# Draw surrounding rectangle
	glColor3f(1.0, 1.0, 1.0)
	
	if(selected == True):
		glLineWidth(5.0)
	else:
		glLineWidth(1.0)

	glBegin(GL_LINE_LOOP)
	glVertex3f(x-95, y-10, 0.0)
	glVertex3f(x-95, y+10, 0.0)
	glVertex3f(x+95, y+10, 0.0)
	glVertex3f(x+95, y-10, 0.0)
	glEnd()

	toolLabel[text].draw()

button = ["Select", "Vertex", "Pencil", "Line", "Curve", "Line P", "Curve P", "Text"]

color = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 1), (1, 1, 1)]

def drawToolbox():
	global label
	# Toolbox Box (0,0) (200, 0), (200, 600), (0, 600)
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_POLYGON)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(200.0, 0.0, 0.0)
        glVertex3f(200.0, 600.0, 0.0)
        glVertex3f(0.0, 600.0, 0.0)		
        glEnd()

	# Draw GLKolab Logo
	logoLabel.draw()

	# Draw Toolbox button (Y=500 until Y=340)
	y = 500
	for each in button:
		drawButton(100, y, each, each==selected_tool)
		y = y - 20
	
	# Draw Selected Color (Y = 320 until Y = 290)
	glColor3f(selected_color[0], selected_color[1], selected_color[2])
	glBegin(GL_POLYGON)
	glVertex2i(20, 320)
	glVertex2i(180, 320)
	glVertex2i(180, 290)
	glVertex2i(20, 290)
	glEnd()

	# Draw Color Selector (Y=280 until Y=240)
	# Each row with 4 color
	y = 280
	color_chunk = []
	for chunk_index in range(0, len(color), 4):
		color_chunk.append(color[chunk_index:chunk_index+4])
	
	for each in color_chunk:
		for i in range(0, 4):
			glColor3f(each[i][0], each[i][1], each[i][2])
			glBegin(GL_POLYGON)
			glVertex3f(50 * (i+1) - 50, y-10, 0.0)
			glVertex3f(50 * (i+1), y-10, 0.0)
			glVertex3f(50 * (i+1), y+10, 0.0)
			glVertex3f(50 * (i+1) - 50, y+10, 0.0) 
			glEnd()

		y = y - 20

def initToolLabel():
	global toolLabel
	y = 500
	for each in button:
		toolLabel[each] = pyglet.text.HTMLLabel('<font size=2 face="Helvetica" color="white"><strong>' + str(each) + '</font>', x=100, y=y, anchor_x='center', anchor_y='center')
		y = y - 20

### REDRAWING STUFF AND UTILITY
def redrawCanvas():
	map(drawAll, canvasDrawObject)

def redrawAll():
	window.clear()
	glColor3f(0.0, 0.0, 0.0)
	redrawCanvas()
	drawToolbox()
	cldis.draw()

def drawAll(drawObject):
	drawObject.draw()
	

### EVENT HANDLER	
@window.event
def on_mouse_motion(x, y, dx, dy):
	if(selected_tool == "Curve"):
		if(state == "Drawing"):
			drawedObject.vertex.pop()
			drawedObject.vertex.append((x, y, 0.0))
			
			redrawCanvas()
	elif(selected_tool == "Line"):
		if(state == "Drawing"):
			drawedObject.vertex.pop()
			drawedObject.vertex.append((x, y, 0.0))
			
			redrawCanvas()

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
	global state
	resizing = False
	if(button == pyglet.window.mouse.LEFT):
		if(selected_tool == "Select"):
			if(state == "Selecting"):
				if(drawedObject != -1):
					if(x in range(drawedObject.get_far_left()-20, drawedObject.get_far_left()+20) and y in range(drawedObject.get_far_top()-20, drawedObject.get_far_top()+20)):
						doResize(dx, dy, "TopLeft")
						resizing = True	
					elif(x in range(drawedObject.get_far_right()-20, drawedObject.get_far_right()+20) and y in range(drawedObject.get_far_top()-20, drawedObject.get_far_top()+20)):
						doResize(dx, dy, "TopRight")
						resizing = True
					elif(x in range(drawedObject.get_far_right()-20, drawedObject.get_far_right()+20) and y in range(drawedObject.get_far_bottom()-20, drawedObject.get_far_bottom()+20)):
						doResize(dx, dy, "BottomRight")
						resizing = True
					elif(x in range(drawedObject.get_far_left()-20, drawedObject.get_far_left()+20) and y in range(drawedObject.get_far_bottom()-20, drawedObject.get_far_bottom()+20)):
						doResize(dx, dy, "BottomLeft")
						resizing = True
					elif(resizing == False):
						doMovement(dx, dy)		
		elif(selected_tool == "Pencil"):
			drawedObject.vertex.append((x, y, 0.0))
			redrawCanvas()
			pass
		elif(selected_tool == "Curve"): 
			pass

@window.event
def on_mouse_release(x, y, button, modifiers):
	if(selected_tool == "Select"):
		pass
	elif(selected_tool == "Pencil"):
		state = "None"
		pass
	elif(selected_tool == "Curve"): 
		pass

@window.event
def on_mouse_press(x, y, button, modifiers):
	global state, selected_tool
	if(button == pyglet.window.mouse.LEFT):  
		# From what tools
		if(selected_tool == "Select"):
			getSelectedObject(x, y)
		elif(selected_tool == "Pencil"):
			# Just A DOT of drawing
			drawPencil(x, y)
			pass
		elif(selected_tool == "Curve"): 
			if(state == "None"):
				drawBezierCurve(x, y, False)
				
			if(state == "Drawing"):
				drawedObject.vertex.append((x, y, 0.0))
		elif(selected_tool == "Line"):
			if(state == "None"):
				drawLine(x, y, False)
				
			if(state == "Drawing"):
				drawedObject.vertex.append((x, y, 0.0))
						
	elif(button == pyglet.window.mouse.RIGHT):  # End Drawing
		if(state == "Drawing"):
			state = "None"
			drawedObject.selected = False

@window.event
def on_key_press(symbol, modifiers):
	global selected_tool, state, drawedObject
	
	# Tools changing
	if('drawedObject' in globals()):
		if(drawedObject != -1):
			drawedObject.selected = False
	state = "None"
	
	if symbol == pyglet.window.key._1:
		selected_tool = "Select"
	elif symbol == pyglet.window.key._2:
		selected_tool = "Vertex"
	elif symbol == pyglet.window.key._3:
		selected_tool = "Pencil"
	elif symbol == pyglet.window.key._4:
		selected_tool = "Line"
	elif symbol == pyglet.window.key._5:
		selected_tool = "Curve"
	elif symbol == pyglet.window.key._6:
		selected_tool = "Line P"
	elif symbol == pyglet.window.key._7:
		selected_tool = "Curve P"
	elif symbol == pyglet.window.key._8:
		selected_tool = "Text"
	
	print "Selected " + selected_tool

@window.event
def on_draw():
	redrawAll()

#patch_idle_loop()
glClearColor(1.0, 1.0, 1.0, 1.0)
initToolLabel()
pyglet.app.run()
