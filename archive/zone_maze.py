import Tkinter
import sys
import unittest
import random

from maze_lib import *

class MazeApp(object):
   HEIGHT = 1150
   WIDTH = 800
   X = 30
   Y = 40
   MOVES = 1100
   def __init__(self, master):
      self.frame = Tkinter.Frame(master)
      self.frame.pack()
      self.button_quit = Tkinter.Button(self.frame, text='Quit', command=self.frame.quit)
      self.button_quit.pack(side=Tkinter.LEFT)
      self.button_print = Tkinter.Button(self.frame, text='Print', command=self.print_window)
      self.button_print.pack(side=Tkinter.LEFT)
      self.button_draw = Tkinter.Button(self.frame, text='Draw', command=self.draw_next_maze)
      self.button_draw.pack(side=Tkinter.RIGHT)
      self.area = Tkinter.Canvas(master, width=self.WIDTH, height=self.HEIGHT)
      self.area.pack(side=Tkinter.RIGHT)
      self.s = self.WIDTH/(self.X+2)

   def clear_canvas(self):
      for i in self.area.find_all():
         self.area.delete(i)

   def prepare_maze(self):
      self.maze = Zone(6, 8, self.X//6, self.Y//8, False)
      self.maze.prepare(2) #(30)
      self.maze.open_outer_walls()

   def draw_next_maze(self):
      self.clear_canvas()
      self.prepare_maze()
      self.draw_maze()

   def draw_maze(self):
      for x in range(self.X):
         for y in range(self.Y):
            x1 = (x+1) * self.s
            y1 = (y+1) * self.s
            x2 = x1 + self.s
            y2 = y1 + self.s
            self.draw_cell_at(x1, y1, Coord(x, y))
            #self.area.create_rectangle(x1, y1, x2, y2)

   def draw_cell_at(self, x, y, coord):
      cell = self.maze.get(coord.x, coord.y)
      (x1, y1) = (x, y)
      for direction in range(4):
         (x2, y2) = self.step(direction, x1, y1)
         if not cell.has_door(direction):
            self.area.create_line(x1, y1, x2, y2) # wall
         else:
            pass # open, draw nothing
         (x1, y1) = (x2, y2)

   def step(self, direction, x, y):
      new_x = x + (0, self.s, 0, -self.s)[direction]
      new_y = y + (self.s, 0, -self.s, 0)[direction]
      return (new_x, new_y)

   def print_window(self):
      self.area.postscript(file='maze.ps')


def run_program():
   root = Tkinter.Tk()
   app = MazeApp(root)
   root.mainloop()
   root.destroy()

if __name__ == "__main__":
    run_program()
    #int(sys.argv[1])
