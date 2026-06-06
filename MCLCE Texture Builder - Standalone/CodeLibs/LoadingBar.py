import tkinter as tk
from tkinter import ttk
from sys import exit
import TextureLibs.Global as Global
from . import Logger as log
from CodeLibs.Logger import print

class LoadingBarExitException(Exception):
    pass

class bar():
    def __init__(self, totalWeight):
        # init main window
        self.main = tk.Tk() # window init
        def doNothing(): pass
        self.main.protocol("WM_DELETE_WINDOW", doNothing) # window when clicking X
        self.main.title("Loading... (this may take some time)") # window name
        self.main.geometry( "400x50+" + str(int((self.main.winfo_screenwidth() / 2) - 400 / 2)) + "+" + str(int((self.main.winfo_screenheight() / 2) - 50 / 2)) ) # window size and position
        self.main.iconbitmap(Global.getMainWorkingLoc() + "\\resources\\Re.ico") # window icon
        self.main.resizable(False, False)

        # add progress bar
        self.bar = ttk.Progressbar(maximum=totalWeight + 0.01, mode="determinate")
        self.bar.place(x=10, y=12.5, width=380, height=25)

    def step(self):
        self.bar.step(1) # rewrite for totalweight

    def stepCustom(self, amount):
        self.bar.step(amount)

    def run(self, func):
        # main loop, shows window
        self.main.after(0, func)
        self.main.mainloop()

    def testRun(self, func):
        self.main.protocol("WM_DELETE_WINDOW", self.main.quit)
        self.run(func)

    def close(self, message=None):
        if (message != None):
            print(message, log.EXIT)

        self.main.attributes("-topmost", True)
        self.main.focus()
        self.main.quit()
        try:
            exit()
        except SystemExit: # error that commonly occurs when trying to exit if things aren't completed
            raise LoadingBarExitException()

    def test(self):
        self.main.protocol("WM_DELETE_WINDOW", self.main.quit)
        self.main.mainloop()