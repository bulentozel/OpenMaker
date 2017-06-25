from LibOM.Tools import *
#from LibOM.GuiControlers import *

from bokeh.embed import components
from bokeh.models import ColumnDataSource, CustomJS,OpenURL,TapTool,HoverTool,LabelSet
from bokeh.plotting import figure
from bokeh.models.widgets import Div, AutocompleteInput
from bokeh.layouts import row, column, widgetbox


class BokehControler:

    def __init__(self, ScoreBoard, MakerDictionary):
        # influencers:
        self.SB = ScoreBoard
        self.MD = MakerDictionary
        self.Influencers = None
        self.Boards = None
        self.ActiveInfluencer = None
        self.ActiveBoard = None

    def populateInfluencers(self, names, categories,
                            stype = 'per_tweet',
                            origin={'x': 0, 'y': 0},
                            rotation= math.pi / 6):
        Xpoints = list()
        Ypoints = list()
        XSegments = list()
        YSegments = list()
        Colors = list()
        Memes = list()
        Names = list()
        Ntweets = list()
        Offsets = list()
        Sizes = list()
        Scores = list()
        for username in names:
            total = self.SB.get_score_one(username, 'all', stype)
            if not total: continue

            sub_scores = self.SB.get_scores(username, categories, stype)
            sub_scores = {k:v for k, v in sub_scores.items() if v}
            #sub_total = reduce(lambda x, y: x + y, [v for v in sub_scores.values() if v], 0.0)
            #sub_scores['making'] = total - sub_total if sub_total < total else 0
            ntweet = self.SB.table[username]['ntweets']
            scores = sub_scores
            scores[-1] = total

            sorted_scores = sorted(scores.items(), key=lambda x: x[1])
            memes = [self.MD.get_category_name(x[0]) for x in sorted_scores]
            npoints = len(memes)
            weights = [x[1] for x in sorted_scores]

            # rotate, this gets the total score at the head of the list:
            memes = memes[-1:] + memes[:-1]
            weights = weights[-1:] + weights[:-1]
            sizes = [round(w * 100 + 20) for w in weights]
            coordinates = get_spiral_locations(npoints, center=origin, diameters=sizes, teta=rotation)
            xpoints = [coord[0] for coord in coordinates]
            ypoints = [coord[1] for coord in coordinates]
            x_segments = [[origin['x'], x] for x in xpoints]
            y_segments = [[origin['y'], y] for y in ypoints]
            colors = ['olive'] * npoints

            Xpoints.extend(xpoints)
            Ypoints.extend(ypoints)
            Colors.extend(colors)
            Memes.extend(memes)
            Offsets.extend([x / 1.5 for x in sizes])
            Sizes.extend(sizes)
            Scores.extend(weights)
            XSegments.extend(x_segments)
            YSegments.extend(y_segments)
            Names.extend([username] * npoints)
            Ntweets.extend([ntweet] * npoints)

        source = ColumnDataSource(data=dict(
            x=Xpoints,
            y=Ypoints,
            colors=Colors,
            names=Names,
            sizes=Sizes,
            offsets=Offsets,
            memes=Memes,
            xsegments=XSegments,
            ysegments=YSegments ,
            tweets=Ntweets,
            scores=Scores
        ))
        self.Influencers = source

    def setActiveInfluencer(self, name, columns):
        indices = [i for i,x in enumerate(self.Influencers.data['names']) if x == name]
        if not indices: return

        influencer = BokehControler.getRows(self.Influencers, indices, columns)
        self.ActiveInfluencer = ColumnDataSource(influencer)

    def populateBoards(self,categories,
                       stype='per_tweet',
                       origin={'x': 0, 'y': 0},
                       rotation = math.pi / 6):
        Xpoints = list()
        Ypoints = list()
        Colors = list()
        Memes = list()
        Names = list()
        Sizes = list()
        Scores = list()
        Offsets = list()
        Tweets = list()
        categories.append(-1)
        for cat in categories:
            ranks = self.SB.get_rankings_one(category=cat, stype=stype)
            names = [x[0] for x in ranks]
            npoints = len(names)
            scores = [x[1] for x in ranks]
            #sizes = [20 for w in scores]
            sizes = [round(w * 50 + 10) for w in scores]
            offsets = [x / 1.8 for x in sizes]
            coordinates = get_spiral_locations(npoints, center=origin, diameters=sizes, teta=rotation)
            colors = ['turquoise'] * npoints
            memes = [self.MD.get_category_name(cat)] * npoints
            tweets = [self.SB.table[name]['ntweets'] for name in names]

            Names.extend(names)
            Scores.extend(scores)
            Sizes.extend(sizes)
            Xpoints.extend([coord[0] for coord in coordinates])
            Ypoints.extend([coord[1] for coord in coordinates])
            Colors.extend(colors)
            Memes.extend(memes)
            Offsets.extend(offsets)
            Tweets.extend(tweets)

        source = ColumnDataSource(data=dict(
            x=Xpoints,
            y=Ypoints,
            colors=Colors,
            names=Names,
            sizes=Sizes,
            offsets=Offsets,
            memes=Memes,
            scores=Scores,
            tweets=Tweets
        ))
        self.Boards = source

    def setActiveBoard(self, meme, columns):
        indices = [i for i,x in enumerate(self.Boards.data['memes']) if x == meme]
        #print("board: ", meme, columns, indices)
        if not indices: return
        board = BokehControler.getRows(self.Boards,indices,columns)
        self.ActiveBoard = ColumnDataSource(board)

    @staticmethod
    def getRows(CDS, indices, columns):
        """Returns a slice of a given ColumnDataSource.

            Args:
                CDS (ColumnDataSource) : Base data source.
                indices (list): The list of row indices (int) to be sliced out.
                columns (list): The list of column names (string) to be sliced out
            Returns:
                Dict: The new column data source in python dictionary format.
        """
        slice = dict()
        for column in columns:
            data = [CDS.data[column][i] for i in indices]
            slice[column] = data
        return slice


def bokehGUI(ScoreBoard, MakerDictionary,
             offlineboard='None',
             curMeme="sustainability",
             curInfluencer='mbanzi'
            ):
    
    MD = MakerDictionary
    SB = ScoreBoard
    if offlineboard: SB.import_board(offlineboard)
    BI = BokehControler(SB,MD)

    names = [k for k,v in SB.get_names().items()]
    category_codes = MD.categories.values()

    # make this more generic:
    if not curInfluencer: curInfluencer='mbanzi'
    if not curMeme: curMeme = 'sustainability'

    BI.populateInfluencers(names, category_codes)
    BI.populateBoards(category_codes)
    BI.setActiveBoard(curMeme,BI.Boards.data.keys())
    BI.setActiveInfluencer(curInfluencer, BI.Influencers.data.keys())

    boards = BI.Boards
    board = BI.ActiveBoard
    influencers = BI.Influencers
    influencer = BI.ActiveInfluencer

    boardatr = ColumnDataSource(data=dict(legend=[curMeme]))
    influenceratr = ColumnDataSource(data=dict(legend=[curInfluencer]))

    #for k in BI.Boards.data.keys(): print(k, BI.Boards.data[k])


    # Drawing:::::::::::::

    ## Commom Tools::
    TOOLS = "tap,pan,wheel_zoom,reset,save"

    ## The Influencer Canvas::
    title = "Influencer"
    fig_influencer = figure(plot_width=550, plot_height=350, title=title, tools=TOOLS, toolbar_location="above",
               toolbar_sticky=True, active_drag="pan", active_tap='tap', active_scroll='wheel_zoom', responsive=True)

    fig_influencer.axis.visible = False
    fig_influencer.border_fill_color = "whitesmoke"
    fig_influencer.border_fill_alpha = 0.3
    fig_influencer.min_border_top = 30
    fig_influencer.outline_line_width = 4
    fig_influencer.outline_line_alpha = 0.2
    fig_influencer.outline_line_color = "navy"
    fig_influencer.xgrid.visible = False
    fig_influencer.ygrid.visible = False

    ### Legend:::
    fig_influencer.circle(0, 0, alpha=0.8, color='olive', legend='legend', source=influenceratr)
    fig_influencer.legend.location = "top_left"
    fig_influencer.legend.label_text_font_size = "8pt"
    fig_influencer.legend.label_text_color = "red"

    ### Data:::
    fig_influencer.multi_line('xsegments', 'ysegments', color="colors", alpha=0.5, line_width=2, line_dash="dashed",
                 source=influencer)
    fig_influencer.circle('x', 'y', color='colors', size='sizes', alpha=1, source=influencer)
    labels = LabelSet(x='x', y='y', text='memes', text_font_size='9pt', level='glyph', x_offset="offsets", y_offset=0,
                      source=influencer,
                      render_mode='canvas')
    fig_influencer.add_layout(labels)

    ### Hover Tool:::
    infhover = HoverTool(tooltips=[
        ("Score", "@scores"),
        ("Type", "per_tweet"),
        ("Ntweets", "@tweets")
    ])
    fig_influencer.add_tools(infhover)


    ## The Board Canvas:::

    #for k in BI.ActiveBoard.data.keys(): print(k, BI.ActiveBoard.data[k])

    title_board = "Community Spirometer"
    fig_board = figure(plot_width=800, plot_height=500, title=title_board, tools=TOOLS, toolbar_location="above",
               toolbar_sticky=True, active_drag="pan", active_tap='tap', active_scroll='wheel_zoom', responsive=True)
    fig_board.axis.visible = False
    fig_board.border_fill_color = "whitesmoke"
    fig_board.border_fill_alpha = 0.2
    fig_board.min_border_top = 30
    fig_board.outline_line_width = 6
    fig_board.outline_line_alpha = 0.2
    fig_board.outline_line_color = "navy"
 
    ### Legend:::
    fig_board.circle(0,0,alpha=0.8,color='turquoise',legend='legend', source=boardatr)
    fig_board.legend.location = "top_left"
    fig_board.legend.label_text_font_size = "9pt"
    fig_board.legend.label_text_color = "red"

    ### Data:::
    fig_board.line('x','y', alpha=0.4, line_width=1, line_dash="dashed", source=board)
    fig_board.circle('x','y', color='colors', size='sizes', alpha=0.8, source=board)
    labels = LabelSet(x='x', y='y', text='names', text_font_size='7pt', level='glyph', x_offset='offsets', y_offset=0,
                      source=board, render_mode='canvas')
    fig_board.add_layout(labels)

    ### Hover Tool:::
    boardhover = HoverTool(tooltips=[
        ("Inf.", "@names"),
        ("Ntweets", "@tweets"),
        ("Score", "@scores"),
        ("Type", "per_tweet")
    ])
    fig_board.add_tools(boardhover)


    # JavaScript Callbacks:::

    board.callback = CustomJS(args=dict(source=influencers, display=influencer, atr=influenceratr), code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var d2 = source.data;
        var d3 = display.data;
        var d4 = atr.data;
        
        var ind = inds[0];
        console.log(ind);
        if (ind != null){
            d3['x'] = [];
            d3['y'] = [];
            d3['sizes'] = [];
            d3['scores'] = [];
            d3['names'] = [];
            d3['memes'] = [];
            d3['colors'] = [];
            d3['offsets'] = [];
            d3['xsegments'] = [];
            d3['ysegments'] = [];
            d3['tweets'] = [];
            d3_tags = [];
            
            var name = d1['names'][ind];
            console.log(name);
            d4['legend'] = [];
            d4['legend'].push(name);
            
            
            var start = d2['names'].indexOf(name);
            var end = d2['names'].lastIndexOf(name);
            
            console.log(start);
            console.log(end);

            for (var i = start; i <= end; i++) {
                d3['x'].push(d2['x'][i]);
                d3['y'].push(d2['y'][i]);
                d3['sizes'].push(d2['sizes'][i]);
                d3['scores'].push(d2['scores'][i]);
                d3['names'].push(d2['names'][i]);
                d3['memes'].push(d2['memes'][i]);
                d3['offsets'].push(d2['offsets'][i]);
                d3['colors'].push(d2['colors'][i]);
                d3['tweets'].push(d2['tweets'][i]);
                d3['xsegments'].push(d2['xsegments'][i]);
                d3['ysegments'].push(d2['ysegments'][i]);
            }
        }
        display.change.emit();
        atr.change.emit();
         """)

    influencer.callback = CustomJS(args=dict(source=boards, display=board, atr=boardatr), code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var d2 = source.data;
        var d3 = display.data;
        var d4 = atr.data;
        
        var ind = inds[0];
        console.log(ind)

        if (ind != null){
            d3['x'] = [];
            d3['y'] = [];
            d3['sizes'] = [];
            d3['scores'] = [];
            d3['names'] = [];
            d3['memes'] = [];
            d3['offsets'] = [];
            d3['colors'] = [];
            d3['tweets'] = [];
            
            var meme = d1['memes'][ind];
            d4['legend'] = [];
            d4['legend'].push(meme)
            console.log(meme)
            
            var name = d1['names'][ind];
            var color = d1['colors'][ind]
            
            var start = d2['memes'].indexOf(meme);
            var end = d2['memes'].lastIndexOf(meme);
            
            console.log(start);
            console.log(end);
            
            for (var i = start; i <= end; i++) {
                d3['x'].push(d2['x'][i]);
                d3['y'].push(d2['y'][i]);
                d3['sizes'].push(d2['sizes'][i]);
                d3['scores'].push(d2['scores'][i]);
                d3['names'].push(d2['names'][i]);
                d3['memes'].push(d2['memes'][i]);
                d3['offsets'].push(d2['offsets'][i]);
                d3['tweets'].push(d2['tweets'][i]);
                if (d2['names'][i] == name){
                    d3['colors'].push(color);
                }
                else {
                    d3['colors'].push(d2['colors'][i]);
                }
            }
        }
        display.change.emit();
        atr.change.emit();
         """)

    # Adding additional Widgets and their events:::::

    ## Info Box::
    div_title = Div(text="""
                <h3> OpenMaker Community Spirometer</h3>
                <p>The sprirometer is a way to observe opionion leaders and influencers of the community,
                those who promote values of the open making or open making friendly social values.
                
                <p><small>Influential actors are placed rather in the core of the spiral. See the lower interactive panel.
                An infleuncer's spiral profile, as of his/her contribution to the maker movement related debates,
                can be seen via the upper interactive panel.
                
                The data is collected from the tweets that are in the public domain.</small></p>
                """, width=750, height=120)
    title_box = widgetbox(div_title, sizing_mode='scale_both', responsive=True)

    ## Tips Box::
    div_tips = Div(text="""
            <small>
            <p>Hover over the nodes in order to see the details. <b>Ntweets</b>
             denotes the number of tweeters collected for the profiling, <b>per_tweet</b>
             denotes that scores are computed per tweet.</p>
      
            <p>A new influencer can be added. Address bar can be used to query an influencer
            whose profile is not analyzed yet. Note that a twitter user name is the part after @ sign.
            For instance, the Twitter user <i>@arduino</i> can be added by appaending <b>arduiono</b> to the URL:
            <i>BASE_URL/gui/arduino</i>
            </p>
            <p>To query the users whose profiling has already been included, the search bar below can be used. </p>
            </small>
            """, width=200, height = 260)
    tips_box = widgetbox(div_tips,sizing_mode='scale_both',responsive=True)

    ## Query Box::

    callback_search = CustomJS(args=dict(boardWin=board, infList=influencers, infWin=influencer, atr=influenceratr),
    code="""
        var bWin = boardWin.data;
        var iWin = infWin.data;
        var iL = infList.data;
        var query = cb_obj.value;
        var d4 = atr.data;
        
        console.log(query);
        
        var ind = iL['names'].indexOf(query);
        if (ind >= 0){
            var start = ind;
            var end = iL['names'].lastIndexOf(query);
            
            iWin['x'] = [];
            iWin['y'] = [];
            iWin['sizes'] = [];
            iWin['scores'] = [];
            iWin['names'] = [];
            iWin['memes'] = [];
            iWin['colors'] = [];
            iWin['offsets'] = [];
            iWin['xsegments'] = [];
            iWin['ysegments'] = [];
            iWin['tweets'] = [];
            
            for (var i = start; i <= end; i++) {
                iWin['x'].push(iL['x'][i]);
                iWin['y'].push(iL['y'][i]);
                iWin['sizes'].push(iL['sizes'][i]);
                iWin['scores'].push(iL['scores'][i]);
                iWin['names'].push(iL['names'][i]);
                iWin['memes'].push(iL['memes'][i]);
                iWin['offsets'].push(iL['offsets'][i]);
                iWin['colors'].push(iL['colors'][i]);
                iWin['tweets'].push(iL['tweets'][i]);
                iWin['xsegments'].push(iL['xsegments'][i]);
                iWin['ysegments'].push(iL['ysegments'][i]);
            }
            
            ind = bWin['names'].indexOf(query);
            if (ind > 0){
                var blength = bWin['colors'].length;
                bWin['colors'] = []
                for (i = 0; i < blength; i++) {
                    bWin['colors'].push('turquoise');
                }
                bWin['colors'][ind] = 'olive'
            }
            d4['legend'] = [];
            d4['legend'].push(query);
        }
        boardWin.change.emit();
        infWin.change.emit();
        atr.change.emit();
    """)
    text_input = AutocompleteInput(completions= names, title="Search an influencer:")
    text_input.js_on_change('value', callback_search)
    query_box = widgetbox(text_input,sizing_mode='stretch_both', responsive=True)

    # Overall Layout::::
    layout = column(title_box, row(fig_influencer, column(tips_box,query_box)), fig_board)

    return(layout)


def inf_OpenURL(name):
    print "GUI query for Influencer", name

    result = get_scores(name)

    scores = result['compositions']
    scores['overall'] = result['overall']

    ### Render Data
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    memes = [x[0] for x in sorted_scores]
    weights = [x[1] for x in sorted_scores]
    # rotate:
    memes = memes[-1:] + memes[:-1]
    weights = weights[-1:] + weights[:-1]

    npoints = len(memes)
    origin = {'x': 0, 'y': 0}
    rotation = math.pi / 3
    sizes = [round(w * 100 + 10) for w in weights]
    coordinates = get_spiral_locations(npoints, center=origin, diameters=sizes, teta=rotation)
    xpoints = [coord[0] for coord in coordinates]
    ypoints = [coord[1] for coord in coordinates]

    x_segments = [[origin['x'], x] for x in xpoints]
    y_segments = [[origin['y'], y] for y in ypoints]

    colors = ['olive'] * npoints

    source = ColumnDataSource(data=dict(
        x=xpoints,
        y=ypoints,
        color=colors,
        names=memes,
        weights=sizes,
        offset=[x / 2 for x in sizes]
    ))

    ### Drawing:::

    TOOLS = "tap,pan,wheel_zoom,box_zoom,reset,save"

    title = "Tap on the circles to see the diffusers of the respective Meme."
    p = figure(plot_width=750, plot_height=750, title=title, tools=TOOLS, toolbar_location="above",
               toolbar_sticky=True, responsive=False)

    p.axis.visible = False
    p.border_fill_color = "whitesmoke"
    p.border_fill_alpha = 0.3
    p.min_border_top = 30
    p.outline_line_width = 4
    p.outline_line_alpha = 0.2
    p.outline_line_color = "navy"

    p.multi_line(x_segments, y_segments, color="turquoise", alpha=0.5, line_width=2, line_dash="dashed")

    p.circle('x', 'y', color='color', size='weights', alpha=1, source=source)

    labels = LabelSet(x='x', y='y', text='names', level='glyph', x_offset="offset", y_offset=0, source=source,
                      render_mode='canvas')
    p.add_layout(labels)

    url = ROOT_URL + "gui/scoreboard/@names"
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url=url)

    header = "OpenMaking Memes :: " + name
    script, div = components(p)
    return render_template("gui.html", script=script, div=div, headline=header)

def board_OpenURL(category):
  code = get_category_code(category)
  if code == 'all': category = DEFAULT_CAT
  ranks = SB.get_rankings_one(code)
  ranks = map(lambda x: {"username":x[0], "score":x[1]}, ranks)

  ### Render Data

  if (len(ranks) > 16): ranks = [x for x in ranks if x['score'] >= 0.02]
  influencers = [x['username'] for x in ranks]
  weights = [x['score'] for x in ranks]
  npoints = len(influencers)
  origin = {'x': 0, 'y': 0}
  rotation = math.pi / 6
  sizes = [round(w * 100 + 10) for w in weights]
  coordinates = get_spiral_locations(npoints, center=origin, diameters=sizes, teta=rotation)
  xpoints = [coord[0] for coord in coordinates]
  ypoints = [coord[1] for coord in coordinates]
  colors = ['darkturquoise'] * npoints
  source = ColumnDataSource(data=dict(
      x=xpoints,
      y=ypoints,
      color=colors,
      names=influencers,
      weights=sizes,
      offset = [x/2 for x in sizes]
    ))

  ### Drawing:::
  TOOLS = "tap,pan,wheel_zoom,box_zoom,reset,save"
  title = "Tap on the circles to see the makership Memes of the respective influencer."
  p = figure(plot_width=740, plot_height=740, title=title, tools=TOOLS, toolbar_location="above",
           toolbar_sticky=True, responsive=False)
  p.axis.visible = False
  p.border_fill_color = "whitesmoke"
  p.border_fill_alpha = 0.2
  p.min_border_top = 30
  p.outline_line_width = 6
  p.outline_line_alpha = 0.2
  p.outline_line_color = "navy"

  p.line(xpoints,ypoints, color="turquoise", alpha=0.5, line_width=4, line_dash = "dashed")
  p.circle('x', 'y', color='color', size='weights', alpha=0.7, source=source)
  labels = LabelSet(x='x', y='y', text='names', text_font_size='8pt', level='glyph', x_offset=0, y_offset=0, source=source, render_mode='canvas')
  p.add_layout(labels)

  url = ROOT_URL + "gui/influencer/@names"
  taptool = p.select(type=TapTool)
  taptool.callback = OpenURL(url=url)


  script, div = components(p)
  header= "The Spiral of Influence :: " + category

  return render_template("gui.html", script=script, div=div, headline = header)

if __name__ == '__main__': pass
