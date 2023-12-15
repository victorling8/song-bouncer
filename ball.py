import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy
import time
import random

COLORS = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,1,0),
    (1,0,1),
    (0,1,1),
    (1,1,1),
)

class Ball:
    def __init__(self, side_num, radius):
        self.side_num = side_num
        self.radius = radius
        self.velocity = 0
        self.position = 0
        self.color = (1, 1, 1)

    def drop(self):
        self.velocity += GRAVITY / FRAME_SPEED
        self.position += self.velocity / FRAME_SPEED

    def draw(self):
        glBegin(GL_POLYGON)
        glColor3fv(self.color)
        for vertex in range(0, self.side_num):
            angle  = float(vertex) * 2.0 * numpy.pi / self.side_num
            glVertex3f(
                numpy.cos(angle)*self.radius,
                self.position + numpy.sin(angle)*self.radius,
                0.0)
        glEnd()
        glColor3fv((1, 1, 1))

    def intersects(self, rect):
        return rect.topX < 0 and rect.bottomX > 0 and \
            self.position-self.radius < rect.bottomY and self.position+self.radius > rect.topY

    def possiblyBounce(self, rect):
        if self.intersects(rect) and not rect.has_bounced_already():
            rect.set_has_bounced()
            self.velocity *= -1 * DAMPING
            self.color = random.choice(COLORS)

class Rectangle:
    def __init__(self, topX, topY, bottomX, bottomY):
        self.topX = topX
        self.topY = topY
        self.bottomX = bottomX
        self.bottomY = bottomY
        self.bounced = False

    def move(self):
        self.topX += MOVE_SPEED_PER_FRAME
        self.bottomX += MOVE_SPEED_PER_FRAME

    def draw(self):
        glBegin(GL_POLYGON)
        glVertex3f(self.bottomX, self.bottomY, 0.0)
        glVertex3f(self.bottomX, self.topY, 0.0)
        glVertex3f(self.topX, self.topY, 0.0)
        glVertex3f(self.topX, self.bottomY, 0.0)
        glEnd()

    def set_has_bounced(self):
        self.bounced = True

    def has_bounced_already(self):
        return self.bounced

def simulate_falling(num_frames):
    velocity = 0
    fall = 0
    for i in range(num_frames):
        velocity += GRAVITY / FRAME_SPEED
        fall += velocity / FRAME_SPEED
    return fall

def create_rectangles():
    lastMiddleX = 0
    lastBallY = 0
    lastBallVelocityY = 0
    rects = []
    for time in TIMES:
        num_frames = int(time * FRAME_SPEED)
        middleX = lastMiddleX + num_frames * -1 * MOVE_SPEED_PER_FRAME
        ballDisplacementY = lastBallVelocityY * (num_frames/FRAME_SPEED) + simulate_falling(num_frames)
        middleY = lastBallY + ballDisplacementY

        if lastBallVelocityY > 0:
            rects.append(Rectangle(middleX - RECT_WIDTH, middleY, middleX, middleY + RECT_HEIGHT))
        else:
            rects.append(Rectangle(middleX - RECT_WIDTH, middleY - RECT_HEIGHT, middleX, middleY))

        # rects.append(Rectangle(middleX - RECT_WIDTH, middleY - RECT_HEIGHT / 2, middleX, middleY + RECT_HEIGHT / 2))

        lastMiddleX = middleX - RECT_WIDTH / 2
        lastBallY = lastBallY + ballDisplacementY
        lastBallVelocityY = -(lastBallVelocityY + GRAVITY * (num_frames/FRAME_SPEED)) * DAMPING

    for i in range(len(rects)-1):
        rect1 = rects[i]
        rect2 = rects[i+1]
        diff = rect2.topX - rect1.bottomX - SPACE_BETWEEN_RECTS
        #rect2.topX -= diff/2
        #rect1.bottomX += diff/2

    return rects

TIMES = [0.8430445, 0.9670909999999997, 0.9905463750000001, 0.49809154200000005, 0.52056675, 1.010894125, 1.0611078330000003, 1.0316698330000005, 0.48712412500000024, 0.5013358329999988, 1.0440670829999998, 0.9729210410000011, 0.9815628329999999, 0.490127416, 0.5053051669999995]
GRAVITY = -5
FRAME_SPEED = 60
SPACE_BETWEEN_RECTS = 3.0
MOVE_SPEED_PER_FRAME = -0.08
RECT_WIDTH = 0.5
RECT_HEIGHT = 0.2
ball = Ball(50, 0.2)
DAMPING = 0.9
rects = create_rectangles()

def init(width, height):
    glViewport(0, 0, width, height)

    glClearColor(0.0, 0.0, 0.0, 1.0)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(100.0, 1.0, 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -5.0)

    glRotatef(0.0, 0.0, 0.0, 0.0)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    ball.drop()
    ball.draw()

    glTranslatef(0.0, -ball.velocity / FRAME_SPEED, 0.0)

    for rect in rects:
        rect.move()
        rect.draw()
        ball.possiblyBounce(rect)

    glutSwapBuffers()
    time.sleep(1/FRAME_SPEED)
    
def resize(width, height):
    glViewport(0, 0, width, height)


if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 640)
    glutInitWindowPosition(200, 200)

    glutCreateWindow(b"OpenGL")

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutReshapeFunc(resize)

    init(glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT))

    glutMainLoop()