# olsonator

This library contains a model for NCAA basketball,
tools to obtain the data the model needs via web scraping,
and tools to back-test the model against past games
to quantify how well a model performs.

## Drivers

The `drivers/` folder contains the scripts used to drive
the model and model analysis.

## Core package

The `pkg/` folder contains the core library for the model
and model analysis.

This is not a normal pip-installable package, it is intended
to be sdejacked into the drivers so that we can be lazy and
skip an extra build step every time we change the core library.

## Data

The `data/` folder contains data used by the model,
plus any raw and processed data downloaded by web scrapers.

The `data/teams/` directory contains team name data.
Many Bothans died to bring us these names.

