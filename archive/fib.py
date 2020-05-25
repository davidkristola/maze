import Tkinter

class FibApp(object):
    HEIGHT = 1200
    WIDTH = 800
    def __init__(self, master):
        self.frame = Tkinter.Frame(master)
        self.frame.pack()
        self.button_quit = Tkinter.Button(self.frame, text='Quit', command=self.frame.quit)
        self.button_quit.pack(side=Tkinter.LEFT)
        self.button_print = Tkinter.Button(self.frame, text='Print', command=self.print_window)
        self.button_print.pack(side=Tkinter.LEFT)
        self.button_draw = Tkinter.Button(self.frame, text='Draw', command=self.draw_next_box)
        self.button_draw.pack(side=Tkinter.RIGHT)
        self.area = Tkinter.Canvas(master, width=self.WIDTH, height=self.HEIGHT)
        self.area.pack(side=Tkinter.RIGHT)
        self.past = 0
        self.current = 1
        self.w = self.WIDTH/1.5
        self.h = self.HEIGHT/3.5
        self.d = 0 # direction

    def draw_next_box(self):
        l = self.past + self.current
        x = self.w + (-l, l, l, -l)[self.d]
        y = self.h + (l, l, -l, -l)[self.d]
        self.area.create_rectangle(self.w, self.h, x, y)
        self.w = x
        self.h = y
        self.past = self.current
        self.current = l
        self.d = (self.d+1)%4

    def print_window(self):
        self.area.postscript(file='tmp.ps')

root = Tkinter.Tk()
app = FibApp(root)
root.mainloop()
root.destroy()
