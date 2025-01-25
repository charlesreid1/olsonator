# olsonator

![Lute Olson](img/olson.jpg)

This library contains a model for NCAA basketball,
tools to obtain the data the model needs via web scraping,
and tools to back-test the model against past games
to quantify how well a model performs.

This tool primarily uses <https://teamrankings.com> as a source of
data about possessions, offense, and defense. It uses 
<https://github.com/dcstats/CBBpy/> to interface with the NCAA
baskeball API and obtain schedule and spread odds data.


## Quick Start

There is no need to install this package, but you will need to install
dependencies. In a Python virtual environment:

```
pip install -r requirements.txt
```

Now you can run any of the example drivers in the `drivers/` folder.

To use the model to make a prediction about a single game:

```
python drivers/model.py
```

To backtest the model against several days of games:

```
python drivers/backtest.py
```


## Drivers

The `drivers/` folder contains examples and scripts used to drive
the model and model analysis.

* `model.py` - simple example of creating a model anad using it
  to make a prediction about a particular NCAAB game.
  Demonstrates use of a Model Data Harness.

* `backtest.py` - simple example of backtesting a model.

* `n_team_backtest.py` - example of backtesting a model against
  games specifically involving one or more teams.


## Core Package

The `pkg/` folder contains the core library for the model,
model backtester, model data harness, and web scrapers.

This is not a normal pip-installable package, it is intended
to be sdejacked into the drivers so that we can be lazy and
skip an extra build step every time we change the core library.

See lines 7-8 of [drivers/model.py](/drivers/model.py) for specifics.


## Data

The `data/` folder contains data used by the model,
plus any raw and processed data downloaded by web scrapers.


### Team Data

The `data/teams/` directory contains team name data.
This is largely hand-curated, with multiple verisons of team names
from the NCAA API, Kenpom, Sagarin, and others.

*Many Bothans died to bring us these names.*


### Rankings

The model uses several quantities for each team to make its prediction, including:

* Tempo
* Offensive efficiency
* Defensive efficiency

Different sites offer different rankings/values for these quantities:

* <https://teamrankings.com>:
    * [Offensive efficiency](https://www.teamrankings.com/ncaa-basketball/stat/offensive-efficiency/) for year, last 10, last 3, home, away, etc.
    * [Defensive efficiency](https://www.teamrankings.com/ncaa-basketball/stat/defensive-efficiency) 
    * [Possessions per game](https://www.teamrankings.com/ncaa-basketball/stat/possessions-per-game), same as tempo 
    * Can also obtain historical snapshots for doing backtesting of prior years

* TODO: <https://kenpom.com>:
    * Offers an adjusted offensive/defensive efficiency, and tempo
    * The catch: this data is updated each day, historical snapshots are not possible
    * These values are only useful if the model is predicting a game within ~90 days

## Acknowledgement

The author wishes to acknowledge <https://kenpom.com> for an explanation of
a version of the model implemented, <https://teamstats.com> for the NCAAB
statistics and schedule data, <https://github.com/dcstats/CBBpy/> for a
Python library to interface with the NCAA Basketball API, and all of the
hard-working men and women and the student athletes who make NCAA basketball
possible.

