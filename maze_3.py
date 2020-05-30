import Tkinter
import sys
import maze_lib
import random

class InfoProgressReporter(object):
   def __init__(self, msg):
      self.msg = msg
      self.hundredths = 0
   def report(self, x, out_of_y):
      percent = (x*100)//out_of_y
      if percent > self.hundredths:
         self.hundredths = percent
         self.msg.config(text="%d out of %d" % (x, out_of_y))
         self.msg.update()

class MazeApp(object):
   HEIGHT = 1150
   WIDTH = 800
   #X = 60
   #Y = 80
   X = 75 # multiples of 5
   Y = 100
   #X = 72
   #Y = 96
   NUDGE = 15
   def __init__(self, master, seed = None):
      #self.cell_size = self.WIDTH/(self.X+2) # cell size
      self.cell_size = 10
      self.next_seed = seed

      self.frame = Tkinter.Frame(master)
      self.frame.pack(side=Tkinter.TOP)

      self.button_quit = Tkinter.Button(self.frame, text='Quit', command=self.frame.quit)
      self.button_quit.pack(side=Tkinter.LEFT)

      self.button_print = Tkinter.Button(self.frame, text='Export', command=self.print_window)
      self.button_print.pack(side=Tkinter.LEFT)

      self.button_draw = Tkinter.Button(self.frame, text='Draw', command=self.draw_next_maze)
      self.button_draw.pack(side=Tkinter.LEFT)

      self.button_more = Tkinter.Button(self.frame, text='Complete', command=self.complete_split_tree)
      self.button_more.pack(side=Tkinter.LEFT)
      self.button_more.config(state=Tkinter.DISABLED)

      self.cell_opt = Tkinter.StringVar(self.frame)
      self.cell_opt.set('Traditional')
      self.cell_check = Tkinter.OptionMenu(self.frame, self.cell_opt, 'Traditional', 'Octagon', 'Inset', 'Wire', 'Wire2')
      self.cell_check.pack(side=Tkinter.LEFT)

      self.button_redraw = Tkinter.Button(self.frame, text='Redraw', command=self.redraw_maze)
      self.button_redraw.pack(side=Tkinter.LEFT)

      maze_styles = ['zigzag', 'zagzig', 'spiral', 'double-spiral', 'walk', 'run', 'random', 'kruskal', 'weaved', 'split_tree']
      shuffle_counts = ['0', '1', '2', '4', '8', '16', '24', '32', '48', '64', '128']

      self.outer_style = Tkinter.StringVar(self.frame)
      self.outer_style.set('zigzag')
      self.outer_style_menu = Tkinter.OptionMenu(self.frame, self.outer_style, *maze_styles)
      self.outer_style_menu.pack(side=Tkinter.LEFT)

      self.outer_count = Tkinter.StringVar(self.frame)
      self.outer_count.set('0')
      self.outer_count_menu = Tkinter.OptionMenu(self.frame, self.outer_count, *shuffle_counts)
      self.outer_count_menu.pack(side=Tkinter.LEFT)

      self.row_count = Tkinter.StringVar(self.frame)
      self.row_count.set('1')
      self.row_count_menu = Tkinter.OptionMenu(self.frame, self.row_count, *([str(x+1) for x in range(9)]))
      self.row_count_menu.pack(side=Tkinter.LEFT)

      self.col_count = Tkinter.StringVar(self.frame)
      self.col_count.set('1')
      self.col_count_menu = Tkinter.OptionMenu(self.frame, self.col_count, *([str(x+1) for x in range(9)]))
      self.col_count_menu.pack(side=Tkinter.LEFT)


      self.inner_style = Tkinter.StringVar(self.frame)
      self.inner_style.set('zigzag')
      self.inner_style_menu = Tkinter.OptionMenu(self.frame, self.inner_style, *maze_styles)
      self.inner_style_menu.pack(side=Tkinter.LEFT)

      self.inner_count = Tkinter.StringVar(self.frame)
      self.inner_count.set('0')
      self.inner_count_menu = Tkinter.OptionMenu(self.frame, self.inner_count, *shuffle_counts)
      self.inner_count_menu.pack(side=Tkinter.LEFT)

      self.button_test = Tkinter.Button(self.frame, text='Test', command=self.draw_test)
      self.button_test.pack(side=Tkinter.LEFT)

      #self.msg_text = Tkinter.StringVar(self.frame)
      #self.msg_text.set('information')
      #self.msg = Tkinter.Message(self.frame, textvariable=self.msg_text, relief=Tkinter.RAISED, width=200)
      self.msg = Tkinter.Message(self.frame, text='information', relief=Tkinter.RAISED, width=200)
      self.msg.pack(side=Tkinter.RIGHT)
      self.progress = InfoProgressReporter(self.msg)

      self.area = Tkinter.Canvas(master, width=self.WIDTH, height=self.HEIGHT, relief=Tkinter.RIDGE)
      self.area.pack(side=Tkinter.BOTTOM)

   def clear_canvas(self):
      for i in self.area.find_all():
         self.area.delete(i)
      #self.area.create_text(self.HEIGHT, self.NUDGE, text=str(self.seed))

   def get_outer_style(self):
      return self.decode_style(self.outer_style.get())

   def get_inner_style(self):
      return self.decode_style(self.inner_style.get())

   def decode_style(self, name):
      if name == 'random':
         return maze_lib.RANDOM
      elif name == 'zigzag':
         return maze_lib.ZIGZAG
      elif name == 'spiral':
         return maze_lib.SPIRAL
      elif name == 'zagzig':
         return maze_lib.ZAGZIG
      elif name == 'walk':
         return maze_lib.R_WALK
      elif name == "run":
          return maze_lib.RANRUN
      elif name == "kruskal":
          return maze_lib.KRUSKAL
      elif name == "weaved":
          return maze_lib.EXP_2
      elif name == "split_tree":
          return maze_lib.SPLIT_TREE
      else:
         return maze_lib.BI_SPI

   def get_outer_count(self):
      return int(self.outer_count.get())

   def get_inner_count(self):
      return int(self.inner_count.get())

   def prepare_mono_maze(self):
      self.effective_x = self.X
      self.effective_y = self.Y
      self.maze = maze_lib.Maze(self.X, self.Y, 'Spiral')
      self.maze.connect_all(self.get_outer_style(), self.progress)
      for i in range(self.get_outer_count()):
         self.maze.move_door()
      if self.outer_style.get() == "split_tree":
          self.button_more.config(state=Tkinter.NORMAL)
      else:
          self.maze.open_outer_walls()

   def prepare_zone_maze(self, x, y):
      self.effective_x = x * (self.X//x)
      self.effective_y = y * (self.Y//y)
      #print('self.X//x = %d, self.Y//y = %d' % (self.X//x, self.Y//y))
      print('outer style = %s' % (self.outer_style.get()))
      print('Zone maze zones (x, y) = (%d, %d)' % (x, y))
      print('effective (x, y) = (%d, %d)' % (self.effective_x, self.effective_y))
      print('self.X//x = %d, self.Y//y = %d' % (self.X//x, self.Y//y))
      print('EAST door (x, y) = (%d, %d)' % (self.X-1,self.Y-1))
      if self.outer_style.get() != "split_tree":
          self.maze = maze_lib.Zone(x, y, self.X//x, self.Y//y, False)
          self.maze.prepare(self.get_inner_count(), self.get_inner_style(), self.get_outer_count(), self.get_outer_style())
          self.maze.open_outer_walls()
      else:
          self.maze = maze_lib.Maze(self.X, self.Y, 'Spiral')
          self.maze.split_tree(x, y, self.X//x, self.Y//y, self.get_inner_style(), maze_lib.R_WALK, self.progress)
          self.maze.open_outer_walls()

   def prepare_maze(self):
      #description = '%s %s %d' % (self.zone_opt.get(), self.outer_style.get(), self.get_outer_count())
      if (self.row_count.get() == '1') and (self.col_count.get() == '1'):
         self.prepare_mono_maze()
      else:
         self.prepare_zone_maze(int(self.row_count.get()), int(self.col_count.get()))

   def print_window(self):
      self.area.postscript(file='maze.ps')

   def draw_next_maze(self):
      self.button_more.config(state=Tkinter.DISABLED)
      self.set_seed()
      self.clear_canvas()
      self.prepare_maze()
      self.draw_maze(self.cell_size, self.NUDGE)

   def set_seed(self):
      seed = self.next_seed
      # now get ready for the next maze
      self.next_seed = random.randint(0, (2**32)-1)
      if seed:
         print('random number seed set to %s' % (seed))
         self.seed = seed
         random.seed(seed)
      else:
         seed = random.randint(0, (2**32)-1)
         print('random generator being seeded with %s' % (seed))
         self.seed = seed
         random.seed(seed)

   def redraw_maze(self):
      self.clear_canvas()
      try:
          self.draw_maze(self.cell_size, self.NUDGE)
      except:
          pass

   def complete_split_tree(self):
       self.clear_canvas()
       self.maze.split_tree_again(self.progress)
       self.maze.open_outer_walls()
       self.draw_maze(self.cell_size, self.NUDGE)
       self.button_more.config(state=Tkinter.DISABLED)

   def draw_test(self):
       self.clear_canvas()
       self.area.create_rectangle(50, 50, 150, 100)
       self.area.create_arc(50, 50, 150, 100, extent=200.0, style=Tkinter.ARC)
       # stipple = 'gray50'
       self.area.create_rectangle(250, 250, 350, 300, fill = 'gray75')
       self.draw_seed()

   def draw_seed(self):
       self.area.create_text(70, self.HEIGHT-118, font="Times", text=str(self.seed))
       print('Seed = %d' % self.seed)

   def draw_maze(self, cell_size, maze_shift):
      #print('%s %d %d' % (self.zone_opt.get(), self.effective_x, self.effective_y))
      for x in range(self.effective_x):
         for y in range(self.effective_y):
            x1 = ((x+1) * cell_size) + maze_shift
            y1 = ((y+1) * cell_size) + maze_shift
            #self.draw_cell_at(x1, y1, Coord(x, y))
            tool = self.tool_factory(cell_size, x1, y1, maze_lib.Coord(x, y))
            tool.draw_cell()
      self.draw_seed()

   def tool_factory(self, cell_size, x, y, coord):
       cell = self.maze.get(coord)
       if self.cell_opt.get() == 'Octagon':
           return CellPainterOctagon(cell_size, self.area, x, y, cell)
       if self.cell_opt.get() == 'Inset':
           return CellPainterInset(cell_size, self.area, x, y, cell)
       if self.cell_opt.get() == 'Wire':
           return CellPainterWire(cell_size, self.area, x, y, cell)
       if self.cell_opt.get() == 'Wire2':
           return CellPainterWire2(cell_size, self.area, x, y, cell)
       return CellPainter(cell_size, self.area, x, y, cell)

class CellPainter(object):
    def __init__(self, cell_size, area, x, y, cell):
        self.cell_size = cell_size
        self.area = area
        self.cell = cell
        self.x = x
        self.y = y
        self.corners = []
        (x1, y1) = (self.x, self.y)
        for direction in range(4):
            self.corners.append( (x1, y1) )
            (x1, y1) = self.step(direction, x1, y1)
    def draw_cell(self):
        if self.cell.get_door_count() == 0:
            self.draw_empty()
        elif self.cell.has_under_cell():
            self.draw_over_under()
        else:
            self.draw_normal()
    def draw_normal(self):
        (x1, y1) = (self.x, self.y)
        for direction in range(4):
            (x2, y2) = self.step(direction, x1, y1)
            if self.cell.has_door(direction):
                pass # open, nothing to draw
            else:
                self.area.create_line(x1, y1, x2, y2) # wall
            (x1, y1) = (x2, y2)
    def draw_over_under(self):
        self.line(self.corners[0], self.corners[2])
        self.line(self.corners[1], self.corners[3])
    def draw_empty(self):
        #self.area.create_rectangle(self.corners[0][0]+2, self.corners[0][1]+2, self.corners[2][0]-2, self.corners[2][1]-2, fill='gray75', width=1)
        return
    def step(self, direction, x, y):
        new_x = x + (0, self.cell_size, 0, -self.cell_size)[direction]
        new_y = y + (self.cell_size, 0, -self.cell_size, 0)[direction]
        return (new_x, new_y)
    def x_delta(self, direction):
        return (0, 1, 0, -1)[direction]
    def y_delta(self, direction):
        return (1, 0, -1, 0)[direction]
    def pixel_step(self, d, xy, scale):
        x = xy[0] + (scale * self.x_delta(d))
        y = xy[1] + (scale * self.y_delta(d))
        return (x, y)
    def line(self, xy1, xy2):
        self.area.create_line(xy1[0], xy1[1], xy2[0], xy2[1])
    def bisect(self, xy1, xy2):
        #x = ((max(xy1[0], xy2[0]) - min(xy1[0], xy2[0])) // 2) + min(xy1[0], xy2[0])
        #y = ((max(xy1[1], xy2[1]) - min(xy1[1], xy2[1])) // 2) + min(xy1[1], xy2[1])
        #if xy1[0] > xy2[0]:
        #    x = ((xy1[0] - xy2[0]) // 2) + xy2[0]
        #else:
        #    x = ((xy2[0] - xy1[0]) // 2) + xy1[0]
        x = ((xy1[0] - xy2[0]) // 2) + xy2[0]
        y = ((xy1[1] - xy2[1]) // 2) + xy2[1]
        return (x, y)

class CellPainterOctagon(CellPainter):
    def draw_normal(self):
        has_wall = [(not self.cell.has_door(direction)) for direction in range(4)]
        s1 = int(self.cell_size//3)
        s3 = self.cell_size - s1
        (x1, y1) = (self.x, self.y)
        points_of_interest = []
        corner = True
        for direction in range(4):
            offset_1 = (s1 * self.x_delta(direction), s1 * self.y_delta(direction))
            offset_2 = (s3 * self.x_delta(direction), s3 * self.y_delta(direction))
            points_of_interest.append( (x1+offset_1[0], y1+offset_1[1]) )
            points_of_interest.append( (x1+offset_2[0], y1+offset_2[1]) )
            (x1, y1) = self.step(direction, x1, y1)
        for index in range(8):
            previous = index - 1
            p1 = points_of_interest[previous]
            p2 = points_of_interest[index]
            if corner:
                self.area.create_line(p1[0], p1[1], p2[0], p2[1])
            else:
                if has_wall[index//2]:
                    self.area.create_line(p1[0], p1[1], p2[0], p2[1])
            corner = not corner
    def draw_over_under(self):
        s1 = int(self.cell_size//3)
        s3 = self.cell_size - s1
        (x1, y1) = (self.x, self.y)
        points_of_interest = []
        for direction in range(4):
            offset_1 = (s1 * self.x_delta(direction), s1 * self.y_delta(direction))
            offset_2 = (s3 * self.x_delta(direction), s3 * self.y_delta(direction))
            points_of_interest.append( (x1+offset_1[0], y1+offset_1[1]) )
            points_of_interest.append( (x1+offset_2[0], y1+offset_2[1]) )
            (x1, y1) = self.step(direction, x1, y1)
        self.line(points_of_interest[0], points_of_interest[5])
        self.line(points_of_interest[1], points_of_interest[4])
        self.line(points_of_interest[2], points_of_interest[7])
        self.line(points_of_interest[3], points_of_interest[6])

class CellPainterInset(CellPainter):
    def draw_cell(self):
        if self.cell.get_door_count() == 0: return
        s1 = int(self.cell_size//6)
        s3 = self.cell_size - s1
        (x1, y1) = (self.x, self.y)

        for direction in range(4):
            (x2, y2) = self.step(direction, x1, y1)
            offset_1 = (s1 * self.x_delta(direction), s1 * self.y_delta(direction))
            offset_2 = (s3 * self.x_delta(direction), s3 * self.y_delta(direction))
            d_plus_1 = (direction+1)%4
            wall_p1 = (x1+offset_1[0], y1+offset_1[1])
            wall_p2 = (x1+offset_2[0], y1+offset_2[1])
            cent_p1 = (wall_p1[0]+(s1 * self.x_delta(d_plus_1)), wall_p1[1]+(s1 * self.y_delta(d_plus_1)))
            cent_p2 = (wall_p2[0]+(s1 * self.x_delta(d_plus_1)), wall_p2[1]+(s1 * self.y_delta(d_plus_1)))
            #arc_p1 = (wall_p1[0]-(s1 * self.x_delta(d_plus_1)), wall_p1[1]-(s1 * self.y_delta(d_plus_1)))
            arc_p2 = (wall_p2[0]-(s1 * self.x_delta(d_plus_1)), wall_p2[1]-(s1 * self.y_delta(d_plus_1)))

            if self.cell.has_door(direction) or self.cell.has_under_cell():
                # open, draw inset
                self.area.create_line(wall_p1[0], wall_p1[1], cent_p1[0], cent_p1[1])
                self.area.create_line(wall_p2[0], wall_p2[1], cent_p2[0], cent_p2[1])
            if not self.cell.has_door(direction):
                self.area.create_line(cent_p1[0], cent_p1[1], cent_p2[0], cent_p2[1]) # wall
                if self.cell.has_under_cell():
                    self.area.create_arc(cent_p1[0], cent_p1[1], arc_p2[0], arc_p2[1], start = (270.0, 0.0, 90.0, 180.0)[direction], extent=180.0, style=Tkinter.ARC)
                #self.area.create_rectangle(250, 250, 350, 300, fill = 'gray75')
            (x1, y1) = (x2, y2)

class CellPainterWire(CellPainter):
    def compute_mids(self):
        self.mids = []
        xy1 = (self.x, self.y)
        for direction in range(4):
            xy2 = self.step(direction, xy1[0], xy1[1])
            self.mids.append(self.bisect(xy1, xy2))
            xy1 = xy2
    def draw_normal(self):
        center = self.bisect(self.corners[0], self.corners[2])
        self.compute_mids()
        #xy1 = (self.x, self.y)
        for direction in range(4):
            #xy2 = self.step(direction, xy1[0], xy1[1])
            if self.cell.has_door(direction):
                self.line(self.mids[direction], center)
                #mid = self.bisect(xy1, xy2)
                #self.line(mid, center)
            #xy1 = xy2
        if self.cell.get_door_count() > 2:
            s1 = int(self.cell_size//8)
            self.area.create_oval(center[0]-s1, center[1]-s1, center[0]+s1, center[1]+s1, fill='black')
    def draw_over_under(self):
        self.compute_mids()
        s1 = int(self.cell_size//3)
        s3 = self.cell_size - s1
        c1 = (self.x + s1, self.y + s1)
        c2 = (self.x + s3, self.y + s3)
        self.line(self.mids[0], self.mids[2])
        self.area.create_arc(c1[0], c1[1], c2[0], c2[1], start = 90.0, extent=180.0, style=Tkinter.ARC)
        #self.line(self.mids[1], (self.mids[1][0], self.mids[1][1]+s2))
        #self.line((self.mids[3][0], self.mids[3][1]-s2), self.mids[3])
        cent_p1 = (self.mids[1][0]+(s1 * self.x_delta(2)), self.mids[1][1]+(s1 * self.y_delta(2)))
        self.line(self.mids[1], cent_p1)
        cent_p2 = (self.mids[3][0]+(s1 * self.x_delta(0)), self.mids[3][1]+(s1 * self.y_delta(0)))
        self.line(self.mids[3], cent_p2)

class CellPainterWire2(CellPainterWire):
    def draw_normal(self):
        if self.cell.get_door_count() != 2:
            CellPainterWire.draw_normal(self)
        else:
            self.draw_passage()
    def draw_passage(self):
        center = self.bisect(self.corners[0], self.corners[2])
        for direction in range(4):
            d_plus_1 = (direction+1)%4
            if self.cell.has_door(direction) and self.cell.has_door(d_plus_1):
                corner = self.hyper_corner(direction)
                #print('cell (%d,%d)(%d,%d), doors at %d and %d' % (self.x, self.y, center[0], center[1], direction, d_plus_1))
                self.area.create_arc(center[0], center[1], corner[0], corner[1], start = (0.0, 90.0, 180.0, 270.0)[direction], extent=90.0, style=Tkinter.ARC)
                return
        CellPainterWire.draw_normal(self)
    def hyper_corner(self, direction):
        d_plus_1 = (direction+1)%4
        d_minus_1 = (direction+3)%4
        start = self.corners[d_plus_1]
        step_1 = self.pixel_step(direction, start, self.cell_size//2)
        step_2 = self.pixel_step(d_minus_1, step_1, self.cell_size//2)
        return step_2

def run_program(seed):
   root = Tkinter.Tk()
   app = MazeApp(root, seed)
   print("running MazeApp (%dx%d)" % (app.X, app.Y))
   app.touch = 1
   root.mainloop()
   root.destroy()

if __name__ == "__main__":
    run_program(int(sys.argv[1]) if len(sys.argv) > 1 else None)
