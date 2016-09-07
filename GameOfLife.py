__author__ = "Nicholas O'Brien"
__email__  = "ndo9903@rit.edu"

from tkinter import Tk, Canvas, Entry
import random, sys


class GameOfLife(Tk):
    _cell_dim = 10
    _continue = False
    _primary_color = "black"
    _secondary_color = "lime green"
    _grid_lines_color = "dark slate gray"

    def __init__(self, dimension, refresh_rate, *args, **kwargs):
        """
        This function is used to inintialize all of the apps attributes:

        Args:
            dimension (int): The dimension of the grid that the user gave as input
                to the main program.
            refresh_rate (int): How much time in between refreshes when the
                simulation is running, this is an optional argument to the program
                and is in milliseconds.

        Returns:
            NoneType: None.

        """
        Tk.__init__(self, *args, **kwargs)
        self._dim = dimension
        self._refresh_rate = refresh_rate
        self._width = (self._dim*self._cell_dim)
        self._height = (self._dim*self._cell_dim) + 1 # 2nd term is padding
        self._board = self.blank_board()
        self.rect = {}
        self.lift()
        self.title("Conway's Game of Life - Nicholas O'Brien")
        self.canvas = Canvas(self, width=self._width, height=self._height+30, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.create_grid()

    def blank_board(self):
        """
        This function is used to initialize a blank board.

        Returns:
            Matrix - boolean: Matrix filled with False value, the size of the specified dimensions.

        """
        return [[False for x in range(self._dim)] for y in range(self._dim)]

    def create_grid(self):
        """
        This function is used to initialize the view on the canvas.

        Returns:
            NoneType: None.

        """
        row = 0
        col = 0
        for row in range(self._dim):
            for col in range(self._dim):
                x1 = col*self._cell_dim # bottom left
                y1 = row * self._cell_dim  # top left
                x2 = x1 + self._cell_dim   # bottom right
                y2 = y1 + self._cell_dim   # top right
                self.rect[row,col] = self.canvas.create_rectangle(x1,y1,x2,y2, fill=self._primary_color, outline=self._grid_lines_color, tags="rect")
                self.canvas.tag_bind(self.rect[row, col], '<ButtonPress-1>', self.change_cell)
        col = 0
        row += 1
        if self._dim < 50:
            button_size = int(80*(self._dim/50))
            font_size = int(22*(self._dim/50))
        else:
            button_size = 80
            font_size = 18
        x1 = col * self._cell_dim  + (((self._dim*self._cell_dim) - button_size*3)//2)
        y1 = row * self._cell_dim  + 5
        x2 = x1 + button_size
        y2 = y1 + 20
        self.canvas.create_oval(x1,y1,x2,y2, tags="toggle", fill=self._primary_color)
        self.canvas.create_text(x1+(button_size//2), y1+10, tags="toggle-text", fill=self._secondary_color, text="Start", font=("Courier", font_size))
        self.canvas.tag_bind("toggle", '<ButtonPress-1>', self.toggle_refresh)
        self.canvas.tag_bind("toggle-text", '<ButtonPress-1>', self.toggle_refresh)
        x1 = x2 + 5  # padding between buttons
        x2 = x1 + button_size
        self.canvas.create_oval(x1,y1,x2,y2, tags="next", fill=self._primary_color)
        self.canvas.create_text(x1+(button_size//2), y1+10, tags="next-text", fill=self._secondary_color, text="Next", font=("Courier", font_size))
        self.canvas.tag_bind("next", '<ButtonPress-1>', self.one_step)
        self.canvas.tag_bind("next-text", '<ButtonPress-1>', self.one_step)
        x1 = x2 + 5  # padding between buttons
        x2 = x1 + button_size
        self.canvas.create_oval(x1,y1,x2,y2, tags="clear", fill=self._primary_color)
        self.canvas.create_text(x1+(button_size//2), y1+10, tags="clear-text", fill=self._secondary_color, text="Clear", font=("Courier", font_size))
        self.canvas.tag_bind("clear", '<ButtonPress-1>', self.clear_board)
        self.canvas.tag_bind("clear-text", '<ButtonPress-1>', self.clear_board)
        self.model_refresh()

    def clear_board(self, event):
        """
        This function is used to clear the board.

        Args:
            event (Tk.Event): The Button click event that is generated to call this
                function.

        Returns:
            NoneType: None.

        """
        for row in range(self._dim):
            for col in range(self._dim):
                self._board[row][col] = False
        self.model_refresh()

    def change_cell(self, event):
        """
        This function is used to change the value of the clicked cell.

        Args:
            event (Tk.Event): The Button click event that is generated to call this
                function.

        Returns:
            NoneType: None.

        """
        try:
            (x, y) = self.get_id_from_coor(event.x, event.y)
            if self._board[x][y]:
                self._board[x][y] = False
            else:
                self._board[x][y] = True
            if self._board[x][y]:
                self.canvas.itemconfig(self.rect[y,x], fill=self._secondary_color)
            else:
                self.canvas.itemconfig(self.rect[y,x], fill=self._primary_color)
        except KeyError:
            pass  # tkinter bug

    def get_id_from_coor(self, x, y):
        """
        This function is used to get the grid coordinates of a cell from the pixel x,y value.

        Returns:
            Tuple - integer: The grid x,y values.

        """
        x_coor = x // self._cell_dim
        y_coor = y // self._cell_dim
        return (x_coor, y_coor)

    def one_step(self, event):
        """
        This function is used as a wrapper for a refresh call with only having one refresh occuring.

        Args:
            event (Tk.Event): The Button click event that is generated to call this
                function.

        Returns:
            NoneType: None.

        """
        self.refresh(self._refresh_rate, True)

    def toggle_refresh(self, event):
        """
        This function is used to start and stop the refreshing of the simulation.

        Args:
            event (Tk.Event): The Button click event that is generated to call this
                function.

        Returns:
            NoneType: None.

        """
        self._continue = not self._continue
        if self._continue:
            self.canvas.itemconfig("toggle-text", text="Stop")
            self.refresh(self._refresh_rate)
        else:
            self.canvas.itemconfig("toggle-text", text="Start")

    def refresh(self, delay, one_step=False):
        """
        This function is used to simulate a single refresh of the simulation. If
        the optional parameter is not set to True then it will call itself again
        when [delay] has passed.

        Args:
            delay (integer): The amount of time between refreshes, in milliseconds.
            one_step (boolean): If the function should call itself again when finished.

        Returns:
            NoneType: None.

        """
        self.canvas.itemconfig("rect", fill=self._primary_color)

        # complete a turn on a temp board
        temp_board = self.blank_board()
        for row in range(self._dim):
            for col in range(self._dim):
                temp_board[row][col] = self.live_or_die(row, col)

        # replace real board with new updated board
        self._board = temp_board


        # refresh UI
        self.model_refresh()


        if self._continue and not one_step:
            self.after(delay, lambda: self.refresh(delay))

    def live_or_die(self, x, y):
        """
        This function is used to analyze if a particular cell will live or die in the next refresh.

        Args:
            x (integer): The grid x coordinate of the cell.
            y (integer): The grid y coordinate of the cell.

        Returns:
            Boolean: True if the cell will be alive, False otherwise.

        """
        neighbors = self.get_neighbors(x, y)
        num_neighbors = 0
        for val in neighbors:
            if val:
                num_neighbors+=1


        # cell dies if less than 2 neighbors
        if num_neighbors < 2:
            return False

        # cell lives on if has 2 or 3 neighbors
        if (num_neighbors == 2 or num_neighbors == 3) and self._board[x][y]:
            return True

        # cell dies if more than 2 neighbors
        if num_neighbors > 3:
            return False

        # cell is born if has 3 neighbors
        if num_neighbors == 3 and not self._board[x][y]:
            return True

        # for consistency
        return False

    def get_neighbors(self, x, y):
        """
        This function is used to create an array of boolean values representing
        the 8 neighbors each cell could possible have.

        Args:
            x (integer): The grid x coordinate of the cell.
            y (integer): The grid y coordinate of the cell.

        Returns:
            Array - boolean: Each element will either be True if the neighbor is alive
                or False if not.

        """
        neighbors = [False]*8
        if x != 0 and y != 0:
            neighbors[0] = self._board[x-1][y-1]
        if y != 0:
            neighbors[1] = self._board[x][y-1]
        if x != (self._dim-1) and y != 0:
            neighbors[2] = self._board[x+1][y-1]
        if x != 0:
            neighbors[3] = self._board[x-1][y]
        if x != (self._dim-1):
            neighbors[4] = self._board[x+1][y]
        if y != (self._dim-1) and x != 0:
            neighbors[5] = self._board[x-1][y+1]
        if y != (self._dim-1):
            neighbors[6] = self._board[x][y+1]
        if x != (self._dim-1) and y != (self._dim-1):
            neighbors[7] = self._board[x+1][y+1]
        return neighbors


    def model_refresh(self):
        """
        This function is used to refresh the view based off of changes to the model of the simulation.

        Returns:
            NoneType: None.

        """
        for x in range(self._dim):
            for y in range(self._dim):
                if self._board[x][y]:
                    self.canvas.itemconfig(self.rect[y,x], fill=self._secondary_color)
                else:
                    self.canvas.itemconfig(self.rect[y,x], fill=self._primary_color)


if __name__ == "__main__":
    if (len(sys.argv) != 2 and len(sys.argv) != 3) or not sys.argv[1].isdigit():
        print("Usage: python HW1.py <dim : integer> [refresh : integer (milliseconds)]", file=sys.stderr)
    else:
        if len(sys.argv) == 3 and not sys.argv[2].isdigit():
            print("Usage: python HW1.py <dim : integer> [refresh : integer (milliseconds)]", file=sys.stderr)
        else:
            dim = int(sys.argv[1])
            if len(sys.argv) == 3:
                refresh = int(sys.argv[2])
            else:
                refresh = 800
            inf = 15
            sup = 60
            if inf < dim < sup:
                app = GameOfLife(dim, refresh)
                app.call('wm', 'attributes', '.', '-topmost', '1')
                app.mainloop()
            else:
                print("dim should be between %s and %s." % (str(inf), str(sup)), file=sys.stderr)
