import turtle
wn=turtle.Screen()
wn.bgcolor ("lightgreen")
wn.title("Hello, Alex!")

alex=turtle.Turtle()
alex.color("blue")
alex.forward(50)

alex.left(120)
alex.color("red")
alex.forward(100)

alex.right(30)
alex.color("green")
alex.pensize(4)
alex.forward(100)

tess=turtle.Turtle()
tess.color("red")
tess.pensize(2)
tess.right(180)
tess.forward(50)

tess.left(120)
tess.color("green")
tess.forward(100)

tess.right(30)
tess.color("blue")
tess.pensize(4)
tess.forward(100)

def repeated_move(t,l,a,n):
	for i in range(n):
		t.forward(l)
		t.right(a)

alex.color("red")
repeated_move(alex,50,144,5)
	
tess.color("green")
repeated_move(tess,20,360/10,10)

def draw_multicolor_square(t,l):
	for c in ["red", "purple", "hotpink", "blue"]:
		t.color(c)
		t.forward(l)
		t.right(90)
		
for i in range(20):
	tess.forward(20)
	draw_multicolor_square(tess,i*10+10)
	tess.right(18)

wn.mainloop()
