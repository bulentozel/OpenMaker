from LibOM.Tools import *
from LibOM.GuiControlers import *
from LibOM.GuiInterfaces import *

from bokeh.embed import components
from bokeh.models import ColumnDataSource, CustomJS, OpenURL,TapTool,HoverTool,LabelSet
from bokeh.plotting import figure
from bokeh.models.widgets import Div, AutocompleteInput
from bokeh.layouts import row, column, widgetbox
from bokeh.io import output_file, show

def display():
    output_file("spirometer.html")
    SB = ScoreBoard()
    MD = MakerDictionary()
    board = SB.import_board("./data/scoreboard.p")
    layout = bokehGUI(SB, MD, offlineboard=board)
    show(layout)

if __name__ == '__main__': display()

