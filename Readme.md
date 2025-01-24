# olsonator

![Lute Olson](img/olson.jpg)

This library contains a model for NCAA basketball,
tools to obtain the data the model needs via web scraping,
and tools to back-test the model against past games
to quantify how well a model performs.

It primarily uses <https://teamrankings.com> as a source of
data about possessions, offensive efficiency, and defensive
efficiency.

## Drivers

The `drivers/` folder contains examples and scripts used to drive
the model and model analysis.

* `model.py` - simple example of creating a model anad using it
  to make a prediction about a particular NCAAB game.
  Demonstrates use of a Model Data Harness.

* `backtest.py` - simple example of backtesting a model.


## Core Package

The `pkg/` folder contains the core library for the model
and model analysis.

This is not a normal pip-installable package, it is intended
to be sdejacked into the drivers so that we can be lazy and
skip an extra build step every time we change the core library.


## Data

The `data/` folder contains data used by the model,
plus any raw and processed data downloaded by web scrapers.


### Team Data

The `data/teams/` directory contains team name data.
This is largely hand-curated, with multiple verisons of team names
from the NCAA API, Kenpom, Sagarin, and others.

Many Bothans died to bring us these names.

That directory also contains latitude/longitude data
about each team's home city. That can be used to determine
distances traveled and account for travel and time zone
effects.


### Rankings

The `data/rankings/` directory contains data about team rankings,
scraped from the internet. Specifically, for each team:

* Tempo
* Offensive efficiency
* Defensive efficiency

These quantities are combined in the model to get predicted 
offensive output for each team (and a score).

Different sites offer different rankings for these quantities:

* <https://teamrankings.com>:
    * [Offensive efficiency](https://www.teamrankings.com/ncaa-basketball/stat/offensive-efficiency/) for year, last 10, last 3, home, away, etc.
    * [Defensive efficiency](https://www.teamrankings.com/ncaa-basketball/stat/defensive-efficiency) 
    * [Possessions per game](https://www.teamrankings.com/ncaa-basketball/stat/possessions-per-game), same as tempo 
    * Can also obtain historical snapshots for doing backtesting of prior years

* TODO: <https://kenpom.com>:
    * Offers an adjusted offensive/defensive efficiency, and tempo
    * The catch: this data is updated each day, historical snapshots are not possible
    * These values are only useful if the model is predicting a game within ~90 days

