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

class SmokePuff:
    def __init__(self, size, positionY):
        self.size = size
        self.positionX = 0
        self.positionY = positionY
        self.opacity = SMOKE_MAX_OPACITY

    def move(self):
        self.positionX += MOVE_SPEED_PER_FRAME

    def draw(self):
        glBegin(GL_POLYGON)
        glColor4f(1, 1, 1, self.opacity)
        for vertex in range(0, 50):
            angle  = float(vertex) * 2.0 * numpy.pi / 50
            glVertex3f(
                self.positionX + numpy.cos(angle)*self.size,
                self.positionY + numpy.sin(angle)*self.size,
                0.0)
        glEnd()
        

class Smoke:
    def __init__(self, smoke_num, smoke_max_size, smoke_min_size):
        self.smoke_num = smoke_num
        self.smoke_max_size = smoke_max_size
        self.increment = (smoke_max_size - smoke_min_size) / smoke_num
        self.puffs = []

    def create_smoke_and_move(self):
        for puff in self.puffs:
            puff.size -= self.increment
            puff.opacity -= (SMOKE_MAX_OPACITY - SMOKE_MIN_OPACITY) / self.smoke_num
        if len(self.puffs) > 0 and self.puffs[0].size <= 0:
            self.puffs.pop(0)
        self.puffs.append(SmokePuff(self.smoke_max_size, ball.position))
        for puff in self.puffs:
            puff.move()

    def draw(self):
        for puff in self.puffs:
            puff.draw()

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
            self.position < rect.bottomY and self.position > rect.topY
            #self.position-self.radius < rect.bottomY and self.position+self.radius > rect.topY

    def possiblyBounce(self, rect):
        if self.intersects(rect) and not rect.has_bounced_already():
            rect.set_has_bounced()
            self.velocity *= -1 * DAMPING
            self.color = random.choice(COLORS)
            global frame_counter
            print(frame_counter)

class Rectangle:
    def __init__(self, topX, topY, bottomX, bottomY):
        self.topX = topX
        self.topY = topY
        self.bottomX = bottomX
        self.bottomY = bottomY
        self.bounced = False

    def copy(self):
        rect = Rectangle(self.topX, self.topY, self.bottomX, self.bottomY)
        return rect

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

def create_rectangles():
    frame_nums = []
    for time in TIMES:
        num_frames = int(time * FRAME_SPEED)
        if len(frame_nums) == 0:
            frame_nums.append(num_frames)
        else:
            frame_nums.append(num_frames + frame_nums[len(frame_nums)-1])
    print(frame_nums)

    frame_nums_copy = frame_nums.copy()

    rects = []
    for i in range(1, frame_nums[len(frame_nums)-1]+1):
        ball.drop()
        if i == frame_nums[0]:
            frame_num = frame_nums[0]
            frame_nums.pop(0)
            middleX = frame_num * -1 * MOVE_SPEED_PER_FRAME
            middleY = ball.position
            rect = Rectangle(middleX - RECT_WIDTH / 2, middleY - RECT_HEIGHT / 2, middleX + RECT_WIDTH / 2, middleY + RECT_HEIGHT / 2)
            if ball.velocity > 0:
                delta = 0.00001
            else:
                delta = -0.00001
            while True:
                intersects = ball.position < rect.bottomY and ball.position > rect.topY
                if not intersects:
                    rect.bottomY -= delta
                    rect.topY -= delta
                    break
                rect.bottomY += delta
                rect.topY += delta

            rects.append(rect)
            ball.velocity *= -1 * DAMPING

    for i in range(len(rects)-1):
        rect1 = rects[i]
        rect2 = rects[i+1]
        diff = rect2.topX - rect1.bottomX - SPACE_BETWEEN_RECTS
        rect2.topX -= diff/2
        rect1.bottomX += diff/2

    ball.position = 0
    ball.velocity = 0
    frame_nums = frame_nums_copy
    rect_index = 0
    rect_copies = [rect.copy() for rect in rects]
    for i in range(1, frame_nums[len(frame_nums)-1]+1):
        ball.drop()
        my_rect = rect_copies[rect_index]
        for rect in rect_copies:
            rect.move()

        if ball.intersects(my_rect):
            if i < frame_nums[rect_index]:
                delta = 0.00001
                while True:
                    my_rect.topX += delta
                    rects[rect_index].topX += delta
                    if not ball.intersects(my_rect):
                        break
            else:
                ball.velocity *= -1 * DAMPING
                rect_index += 1

    ball.position = 0
    ball.velocity = 0
    rect_index = 0
    already_intersected_rect = None
    last_frame_intersect = None
    rect_copies = [rect.copy() for rect in rects]
    for i in range(1, frame_nums[len(frame_nums)-1]+1):
        ball.drop()
        my_rect = rect_copies[rect_index]
        for rect in rect_copies:
            rect.move()

        if ball.intersects(my_rect):
            ball.velocity *= -1 * DAMPING
            rect_index += 1
            already_intersected_rect = my_rect
            last_frame_intersect = i

        if already_intersected_rect != None and ball.intersects(already_intersected_rect) and i - last_frame_intersect > 3:
            delta = 0.00001
            while True:
                already_intersected_rect.bottomX -= delta
                rects[rect_index-1].bottomX -= delta
                if not ball.intersects(already_intersected_rect):
                    if rects[rect_index-1].bottomX - rects[rect_index-1].topX > 3.0:
                        rects[rect_index-1].bottomX -= 3.0
                    else:
                        rects[rect_index-1].bottomX -= 0.2
                    break

    ball.position = 0
    ball.velocity = 0
    ball.color = (1, 1, 1)
    return rects

HEAVY_ROTATION = [0.831747, 0.4723451249999999, 0.44058133300000013, 0.9167322909999998, 0.4191738340000004, 0.44088695899999975, 0.895656792, 0.4210879580000002, 0.4480115000000007, 0.8720820420000006, 0.40821116600000007, 0.4553672080000002, 0.8517072910000003, 0.4328612079999985, 0.45225991699999923, 0.9180603339999998, 0.3946759999999987, 0.45451437500000047, 0.911510625, 0.3922679999999996, 0.4306693750000008, 0.8802875839999995, 0.89498575, 0.872889958, 0.9293627079999993, 0.8795086669999996, 0.45372995800000027, 0.4724472920000018, 0.42759120799999906, 0.4217895000000027, 0.4517409999999984, 0.4554057500000006, 0.42837916699999923, 0.45299541700000034, 0.4625650419999978, 0.4776142919999984, 1.2591257080000027, 0.4405655419999981, 0.9210330419999977, 0.8844226249999991, 0.451957084, 0.4342819579999997, 0.4033508329999975, 0.4485859170000026]
FUR_ELISE = [0.8065623749999999, 0.19952941600000007, 0.214801625, 0.20966975, 0.21847583300000006, 0.2350883749999999, 0.22159583299999985, 0.22888545800000015, 0.2879375000000004, 0.708770167, 0.23141870900000017, 0.20370450000000018, 0.21577925000000064, 0.7175689590000003, 0.23830216699999962, 0.19285200000000025, 0.23590695800000017, 0.7327296670000001, 0.2167441659999998, 0.20777025000000027, 0.22721679199999922, 0.2194567910000007, 0.2230312080000001, 0.2150672079999998, 0.21977200000000074, 0.22343795899999996, 0.2422378750000007, 0.6436360420000007, 0.22552754200000003, 0.20473570800000118, 0.22345087499999927, 0.6571020409999999, 0.22131704099999894, 0.25144591699999985, 0.2192649169999985, 0.6574829170000012, 0.23544020900000007, 0.20732416699999945, 0.2226001670000013, 0.7046048329999994, 0.22945533299999887, 0.19230320800000023, 0.24052233400000134, 0.6405874589999989, 0.22679637499999927, 0.20602612499999928, 0.23995658299999967, 0.6807038330000008, 0.21690516700000018, 0.21635300000000157, 0.2383426249999978, 0.2688506249999989, 0.23077604200000223, 0.22866550000000174, 0.21505125000000191, 0.20943091699999883, 0.22233729100000232, 0.22478075000000075, 0.22435520799999864, 0.38193774999999874, 0.20234675000000024, 0.19787649999999957, 0.2113263750000023, 0.21717883300000196, 0.20829520800000267, 0.24447145900000322, 0.22742408299999894, 0.22054250000000053, 0.28205954099999886, 0.7205094999999986, 0.20544274999999956, 0.20473924999999937, 0.21226416600000064, 0.7381736669999981, 0.21019370799999848, 0.1928499170000002, 0.23142899999999855, 0.7971946249999995, 0.21652179200000177, 0.19843770800000016, 0.2070598330000024, 0.20809962499999912, 0.2324099170000018, 0.23200691699999965, 0.2282810839999989, 0.23262062499999914, 0.2473659579999996, 0.7086759170000008, 0.2076703749999993, 0.1838699169999991, 0.27427550000000167, 0.641402541999998, 0.22622045800000024, 0.22601220800000021, 0.24047312500000118]
YOU_BELONG_WITH_ME = [0.682035708, 0.18617937500000004, 0.26861887500000003, 0.469261041, 0.23621754100000003, 0.6285487919999997, 0.22287991699999976, 0.467977125, 0.23308074999999961, 0.19354708300000034, 0.2444830419999997, 0.4447249580000001, 0.4630560829999997, 0.4603444999999997, 0.23203625000000017, 0.6270947499999995, 0.21339116700000016, 0.45874429199999955, 0.21311637499999936, 0.4401304159999997, 0.42705133300000053, 0.44279166699999983, 0.6670242080000008, 0.6353857919999992, 0.9067640420000007, 0.21963995800000014, 0.20112779199999942, 0.2068467500000004, 0.24002120799999993, 0.4355983750000014, 0.6351975420000002, 0.6526461250000004, 0.8180777499999987, 0.2021013749999998, 0.22205566599999926, 0.45493183299999984, 0.22165075000000023]
HEART_AND_SOUL = [0.9669582919999999, 0.8582358750000001, 0.20613570800000014, 0.8538766249999998, 0.20590470799999983, 0.8504604999999996, 0.21643837500000007, 0.26184520800000044, 0.23754883299999996, 0.22788604199999973, 0.2200627500000003, 0.23697516699999976, 0.24076641699999968, 0.8731236250000007, 0.2331899160000006, 0.8633240409999994, 0.21417283300000012, 0.5749813330000002, 0.541449042]
BIG_GAPS = [0.8731730000000001, 1.161972541, 2.1618007500000003, 0.22694579199999954, 0.29496858400000026, 0.5631486250000002, 0.5624361660000003, 1.0488539999999995, 3.1083484589999992, 0.23453529199999856, 0.2473194999999997, 0.4751829589999996, 1.9930087079999996, 0.24118295800000134, 0.23722324999999955, 0.4753922080000006, 2.953571666, 0.21261495799999963, 0.22047662499999987, 0.20541795799999818, 0.2376650840000032, 0.48298512500000257, 0.4798209590000013, 0.483948625]
STACYS_MOM = [0.6951244169999999, 0.20493716699999986, 0.505112834, 0.7535235420000002, 0.24843508400000003, 0.47697233299999997, 0.23262045799999997, 0.23703416700000002, 0.254080375, 0.7591922920000003, 0.25072229099999976, 0.23689499999999963, 0.4924977910000008, 0.504026584, 0.23375583300000002, 0.2513724590000006, 0.4781298749999996, 0.23138262500000017, 0.49005508299999967, 0.24485079200000115, 0.764994208000001, 0.23791650000000075, 0.23091312500000072, 0.23256537500000007, 0.2640055830000012, 0.48082916700000133, 0.22514266700000007, 0.24848275000000086, 0.3597500829999998, 0.35623949999999915, 0.24193379199999931, 0.24491479199999944, 0.5291844169999997, 0.21741179200000005, 0.2400361670000013, 0.23504387500000057, 0.22893454099999921, 0.2581752910000006, 0.49143312500000036, 0.5309363750000013, 0.23483916700000051, 0.22207420799999866, 0.23082512500000085, 0.23724504199999963, 0.23905750000000126, 0.4961019579999988]
GINGHAM_CHECK = [0.7105071249999999, 0.178874667, 0.618543042, 0.20172016700000017, 0.5919991249999998, 0.18565608300000003, 0.816467292, 0.38093212499999973, 0.39985120799999985, 1.2023649589999996, 0.18230099999999982, 0.1990077500000007, 1.2415024159999994, 0.20294224999999955, 0.6208247090000008, 0.20341941699999921, 0.5842127920000006, 0.19898262500000108, 0.7913095000000006, 0.40986129200000043, 0.40307537500000024, 1.2229379170000012, 0.18699375000000096, 0.20430237499999926, 1.256043, 0.1897210420000004, 0.18522787499999893, 1.0834720000000004, 0.20733058300000096, 0.19076491700000098, 1.0169465419999995, 0.19229899999999844, 0.1850532919999992, 0.7361664169999997, 0.7608582500000018, 1.714440916000001, 0.5596529169999975, 0.5264286250000012, 0.3753250829999999, 0.36511741600000036, 0.38142925000000005, 0.3695583330000005, 0.7413087910000016, 0.7066914580000017, 0.40118370800000136, 0.18503737500000028, 0.16589145800000082, 0.19873770799999946]
FUR_ELISE_2 = [0.2, 0.177534584, 0.14292191700000023, 0.1623037919999999, 0.15903554200000025, 0.1521868750000004, 0.13048733300000004, 0.15376845800000005, 0.12851037499999984, 0.5107198330000005, 0.16742504099999955, 0.16576583300000003, 0.16472683399999966, 0.41784354199999996, 0.19302612500000027, 0.15245154199999966, 0.18111937499999975, 0.6038324580000003, 0.1759285419999994, 0.15873724999999972, 0.16007204200000036, 0.16733920800000046, 0.16903325000000002, 0.17717041700000014, 0.16212525000000078, 0.17347820899999977, 0.13745116699999915, 0.4957678749999994, 0.1681015420000005, 0.1728205420000002, 0.1510328750000003, 0.5333030000000001, 0.18503545799999976, 0.1853847910000006, 0.17796441600000001, 0.9999128339999999, 0.23356191599999931, 0.2094360420000001, 0.16684616599999913, 0.1780479589999988, 0.1794515419999989, 0.16234970900000079, 0.1742880410000005, 0.1544512909999991, 0.47532279200000005, 0.19744712500000006, 0.1779358749999993, 0.15870091700000089, 0.5040370410000001, 0.17486225000000033, 0.16807975000000042, 0.16402854100000042, 0.5710088340000006, 0.18885587499999978, 0.15617116600000003, 0.18520299999999956, 0.16919566700000033, 0.17583162499999894, 0.1884586670000008, 0.136828916999999, 0.1808632089999982, 0.16516833300000044, 0.5022615830000028, 0.20494729199999995, 0.1687382080000006, 0.1577424590000014, 0.5316218329999991, 0.1963652499999995, 0.17133862500000063, 0.17952520900000124, 0.5642160000000018, 0.2044071669999994, 0.1639865829999998, 0.15322737500000017, 0.5574700000000021, 0.1860110000000006, 0.18848287499999827, 0.16998654200000018, 0.5103519580000011, 0.18166479200000296, 0.17049199999999942, 0.194571916000001, 0.5307495419999988, 0.19320237499999848, 0.18873691599999987, 0.18670045800000068, 0.2046980420000004, 0.2142621250000012, 0.19762408399999742, 0.199411542, 0.18813749999999985, 0.16975333299999917, 0.18133012500000234, 0.22599820900000012, 0.22644233300000138, 0.18442929100000072, 0.19149979199999834, 0.17959820799999804, 0.197167125, 0.18282233299999717, 0.18337100000000106, 0.17162641700000236, 0.1747082500000019, 0.1753423749999996, 0.1865224579999989, 0.18084520799999737, 0.1649598329999975, 0.18753729199999825, 0.18281800000000104, 0.5151562500000004, 0.18944662499999865, 0.16830670799999936, 0.19487541699999866, 0.45014020800000054, 0.1862354169999989, 0.1793484999999997, 0.1757493330000024, 0.5411194170000009, 0.20257195800000005, 0.19053779099999701, 0.15130587499999848, 0.16841458300000056, 0.18268741600000027, 0.1841841250000016, 0.15774654100000163, 0.19980570799999953, 0.1839615419999987, 0.43243662500000113, 0.18260287499999706, 0.16554283400000003, 0.16745712500000565, 0.4501085830000022, 0.19124029200000336, 0.21255250000000103, 0.18615670799999862]

TIMES = FUR_ELISE_2
GRAVITY = -15
FRAME_SPEED = 60
SPACE_BETWEEN_RECTS = 0.5
MOVE_SPEED_PER_FRAME = -0.12
RECT_WIDTH = 0.2
RECT_HEIGHT = 0.2
DAMPING = 0.85
SMOKE_NUM = 10
SMOKE_MAX_SIZE = 0.15
SMOKE_MIN_SIZE = 0.05
SMOKE_MAX_OPACITY = 0.8
SMOKE_MIN_OPACITY = 0.1

ball = Ball(50, 0.2)
smoke = Smoke(SMOKE_NUM, SMOKE_MAX_SIZE, SMOKE_MIN_SIZE)
rects = create_rectangles()

frame_counter = 0

def init(width, height):
    glViewport(0, 0, width, height)

    glClearColor(0.0, 0.0, 0.0, 1.0)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(135.0, 1.0, 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -5.0)

    glRotatef(0.0, 0.0, 0.0, 0.0)

    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

def display():
    start_time = time.perf_counter()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    global frame_counter
    frame_counter += 1

    ball.drop()
    smoke.create_smoke_and_move()
    smoke.draw()

    ball.draw()

    glTranslatef(0.0, -ball.velocity / FRAME_SPEED, 0.0)

    for rect in rects:
        rect.move()
        rect.draw()
        ball.possiblyBounce(rect)

    glutSwapBuffers()
    end_time = time.perf_counter()

    if 1/FRAME_SPEED > end_time - start_time:
        time.sleep(1/FRAME_SPEED - (end_time - start_time))
    
def resize(width, height):
    glViewport(0, 0, width, height)


if __name__ == "__main__":
    time.sleep(4.7)

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