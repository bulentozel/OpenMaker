


# BokehControler:
# - At init: Initialize BOKEH ColumnDataSources.
# - Whenever scoreboard is updated update CDSes.

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


