# Smash Upset Distance - Backend

## Introduction

This repo objective is to provide an API backend to a front web app available [here](https://upsets.ssbapps.com/).
The front code repo is [also available](https://github.com/leopons/smash-upset-distance__frontend).

The web app goal is to allow any Super Smash Bros Ultimate competitive player to calculate what I call his 'upset distance' to the best player in the world at this day, MkLeo.

### The Upset Distance

What do I mean by that ?
Given all the sets that have been played in registered tournaments for this game, your upset distance to MkLeo is the minimal number of wins you need to go from you to him.

Which means :

- All the people that have won at least one time against MkLeo on a registered tournament have a distance of 1 from him. For exemple Glutonny has won against MkLeo at least one time, thus he has a distance of 1.
- All the people that have won at least one time against someone who has beaten MkLeo, have a distance of 2. Said differently, if you have beaten someone who is at a distance of 1 from MkLeo, you are yourself at a distance of 2. For exemple Raflow has won one time against Glutonny, thus he has a distance of 2.
- This goes on as many times as needed.
- Your final distance is your minimal distance, ie the shortest path of wins that lead from you to MkLeo.
- Some people may not have a score, if there is not any win path that can lead to MkLeo. This can happen for example with a player that has never won against anyone.

The app objective is to calculate this distance and the shortest win path associated, see the endpoint part for some examples.

_Disclaimer_ : I am very aware that "this means nothing" : a player true level can't be determined by this distance, as it is heavily influenced by one time out-performances, or one may even say luck. But this is fun.

### Data

I'm using data from [The Player Database](https://smashdata.gg/). Go check it out, it's a really nice website that aggregates and displays data about Smash players. They've done a really nice work of reconciliation of player ids from different sources like smash.gg or challonge, there was not point for me in trying to re-do it.

I'm accounting for all the Smash Ultimate sets on the Player Database, excepts for DQs. This means that some Online tournaments are used for the path calculation too. I may change this in the future, or make it an option. If this is important to you, don't hesitate to make yourself heard [on twitter](https://twitter.com/UnCalinSSB).

## Endpoints

The API production endpoint is : https://smash-upset-distance.ew.r.appspot.com/

There's throttling protection but the ratio isn't really severe, please do not flood it uselessly.

### Player Search

`/upsets/players/search/?term=<search_term>`

This gives a list of players whose tag matches the search term. On the front-end side, this is used for the player search autocomplete.

The results are ordered this way:

- First, players whose tag exactly matches the search term.
- Second, players whose tag begins with the search term.
- Finally, players whose tag contains the search term.
- The second ordering dimension is by total number of recorded sets (decreasing).

All matches are case insensitive and unaccentuated.
The number of results is limited to 20.

`/upsets/players/search/?term=calin`

```json
[
  {
    "id": "1693879",
    "tag": "Calin",
    "main_character": null,
    "last_tournament": {
      "name": "Smash in Class, SPS Super Smash Bros Fundraiser",
      "start_date": "2020-03-07"
    }
  },
  {
    "id": "1554284",
    "tag": "UnCalin",
    "main_character": "mario",
    "last_tournament": {
      "name": "WANTED SAISON 4 - 🎂 3 Years Anniversary 🎂",
      "start_date": "2020-10-10"
    }
  }
]
```

### Player Path

`/upsets/playerpath/<player_id>/`

This gives the shortest win path between the player requested and MkLeo, as well as details about each upset : tournament, scores, etc. When there is multiple sets possible that do not increase the overall distance, I choose the most recent sets. For example this is my personal path on this day :

`/upsets/playerpath/1554284/`

```json
{
  "player_tag": "UnCalin",
  "offline_only": false,
  "path_exist": true,
  "path": [
    {
      "node_depth": 5,
      "upset": {
        "tournament": {
          "name": "Show me your mask ! #3",
          "start_date": "2020-10-05",
          "online": false
        },
        "winner": {
          "id": "1554284",
          "tag": "UnCalin",
          "main_character": null
        },
        "loser": {
          "id": "993270",
          "tag": "Zenobia",
          "main_character": null
        },
        "winner_score": 2,
        "loser_score": 1,
        "round_name": "Losers Round 2",
        "best_of": 3,
        "winner_characters": [],
        "loser_characters": []
      }
    },
    {
      "node_depth": 4,
      "upset": {
        "tournament": {
          "name": "WANTED SAISON 3 - Chap 3 : Worlds of Wanted 1vs1 (main event)",
          "start_date": "2019-11-09",
          "online": false
        },
        "winner": {
          "id": "993270",
          "tag": "Zenobia",
          "main_character": null
        },
        "loser": {
          "id": "813046",
          "tag": "Jawkz",
          "main_character": null
        },
        "winner_score": 2,
        "loser_score": 1,
        "round_name": "Winners Round 1",
        "best_of": 3,
        "winner_characters": [],
        "loser_characters": []
      }
    },
    {
      "node_depth": 3,
      "upset": {
        "tournament": {
          "name": "WANTED Saison 3 - Chap 7 : Kirby c'est Top Tier",
          "start_date": "2020-02-22",
          "online": false
        },
        "winner": {
          "id": "813046",
          "tag": "Jawkz",
          "main_character": null
        },
        "loser": {
          "id": "173362",
          "tag": "Agito",
          "main_character": null
        },
        "winner_score": 2,
        "loser_score": 1,
        "round_name": "Winners Round 3",
        "best_of": 3,
        "winner_characters": [],
        "loser_characters": []
      }
    },
    {
      "node_depth": 2,
      "upset": {
        "tournament": {
          "name": "WANTED saison 2 Chapitre 8 : La moutarde lilloise The lost Maps",
          "start_date": "2019-05-11",
          "online": false
        },
        "winner": {
          "id": "173362",
          "tag": "Agito",
          "main_character": null
        },
        "loser": {
          "id": "6122",
          "tag": "Glutonny",
          "main_character": null
        },
        "winner_score": 2,
        "loser_score": 0,
        "round_name": "Winners Quarter-Final",
        "best_of": 3,
        "winner_characters": [],
        "loser_characters": []
      }
    },
    {
      "node_depth": 1,
      "upset": {
        "tournament": {
          "name": "2GG: Kickoff - Kongo Saga",
          "start_date": "2019-12-07",
          "online": false
        },
        "winner": {
          "id": "6122",
          "tag": "Glutonny",
          "main_character": null
        },
        "loser": {
          "id": "222927",
          "tag": "MkLeo",
          "main_character": null
        },
        "winner_score": 3,
        "loser_score": 0,
        "round_name": "Grand Final",
        "best_of": 3,
        "winner_characters": ["wario"],
        "loser_characters": ["joker"]
      }
    }
  ]
}
```

To get the path excluding online tournaments, just add an `offline_only` GET parameter:
`/upsets/playerpath/<player_id>/?offline_only=True`

### Twitter Tag

`/upsets/twittertag/player/<player_id>/`

This gives a valid twitter tag for the given player.

The source data sometimes present multiple twitter tags for a given player, and sometimes invalid ones.
I do not want to check for the validity of tags when importing the data because:

- Twitter api limit rates are pretty low, so it would take quite a long time to check for the whole DB.
- If a player changes his twitter tag, I do not want to display an invalid twitter tag (which would mean a broken link) on my app.

This is were this endpoint comes into play. I call it from the front end, player by player, after the loading of a path. The back end checks on the fly the validty of the tag candidates via the Twitter API, and returns the good one.
The tag is then 'cached' (it won't need another Twitter API call) for 24 hours.

I haven't embedded this data in the player path endpoint but made it a distinct endpoint so that the front calls could be asynchronous. Indeed, for long player paths, embedding the tags checks in the player path calculation could really delay the page loading.

`/upsets/twittertag/player/1554284/`

```json
{
  "player_id": "1554284",
  "twitter_tag": "UnCalinSSB"
}
```

If there is no valid twitter tag, the api just returns a null value.

`/upsets/twittertag/player/1641669/`

```json
{
  "player_id": "1641669",
  "twitter_tag": null
}
```

## Code Structure

I'm using Django, with a PostgreSQL DB.

The PostgreSQL choice is important : `ArrayField` is used on some models and it needs PostgreSQL, as well as the `unaccent` string search, which is used in the Player Search view.

Most of the data preparation and calculation logic can be found in `upsets/lib`.
Otherwise, this is a pretty standard Django codebase : model based structure with DRF handling the serialization, with a `requirements.txt` file for the dependencies, and some tests to run with `python manage.py test`.

There is a lot of DB queries optimisation going on. To ease the task, I've set up DB queries console logging when `DB_LOGS=True`. The log messages for these lines are limited to 120 characters to avoid console flooding. You can change that with `DB_LOGS_MAX_CHARS`, for example :
`DB_LOGS=True DB_LOGS_MAX_CHARS=200 python manage.py process_players`

## Setup

Steps to make the project work locally.

### Standard Django Setup

- Clone the repo
- Install the python dependencies which are in `requirements.txt`
- Setup your DB instance (remember that it is important that you use PostgreSQL).
- Setup your env variables, they should specify the classic `DEBUG` and `SECRET_KEY`, as well as a `LOCAL_DATABASE_URL` to access the DB and which should be formatted like this: `postgres://USER:PASSWORD@HOST/DBNAME` (I'm using `dj_database_url` to parse this.)
- Run the django migrations: `python manage.py migrate`

To run the local server : `python manage.py runserver`

### Data Setup

To initiate the data, download the last DB export for ultimate on [the player database Github repo](https://github.com/smashdata/ThePlayerDatabase).
Then simply run `python manage.py update_data path/to/the/db/file.db`. It could take a while depending on your local specs (like an hour), but there is some clear logging so you should be able to check it's progressing correctly. By default, it will only backfill the last 6 months of data. If you need a whole backfill, pass the `--full` or `-f` option.

If you need to update only some objects for dev purposes, you can : `python manage.py update_data file.db -o tournaments`.

You should also run `python manage.py process_players` which will update some info about the players (like their main character, or their last tournament played) based on the data you just loaded.

### Twitter API

If you want the Twitter Tag endpoint to work, you should also specify a valid `TWITTER_BEARER_TOKEN` in your env so that the app can use the Twitter API to check the tags validity.

## Production Environnement

For production I'm using Google App Engine Standard environnement with a Cloud SQL PostgreSQL instance.

### Run Django Commands

Standard GAE doesn't allow to ssh or run a command directly from the cloud. As described in the [docs](https://cloud.google.com/python/django/appengine?hl=en#macos-64-bit), database operations like migrations or the creation of a superuser have to be performed from your local setup:

- Ensure that your local code version corresponds to the code you actually want to run on the production DB.
- If not already done, install the Cloud SQL Proxy as described [here](https://cloud.google.com/python/django/appengine?hl=en#installingthecloudsqlproxy).
- Start the Cloud SQL Proxy : `./cloud_sql_proxy -instances="[YOUR_INSTANCE_CONNECTION_NAME]"=tcp:3306`
- Your local environment variables should include the prod DB logins : `DB_PROD_DATABASE`, `DB_PROD_USERNAME`, `DB_PROD_PASSWORD`
- The commands will run on prod if `DB_MODE=prod`, you can just specify the var before the command, like this : `DB_MODE=prod python manage.py showmigrations`

### Production Variables

GAE doesn't offer a built-in environment variables online interface.
The production variables are read from the `app.yaml` file on deployment.
As we want to track the app.yaml file with git, and in order to avoid to commit secrets, we define the variables in a `gae_env_variables.yaml` file which is not tracked, but which is included in the app.yaml for gae deployment.

Your `gae_env_variables.yaml` file should be placed at the root of the project with the app.yaml file, and should define the following variables:

```yaml
env_variables:
  DEBUG: "False"
  SECRET_KEY: "your-secret-key"
  DB_PROD_CONNECTION_NAME: "project-name:region-name:instance-name"
  DB_PROD_DATABASE: "database-instance-name"
  DB_PROD_USERNAME: "database-user-name"
  DB_PROD_PASSWORD: "database-user-password"
  TWITTER_BEARER_TOKEN: "twitter-api-bearer-token"
```

### Deployment

GAE deployment command :
`gcloud app deploy`

This wild deploy to prod, which means uploading the codebase and the environment variables from the `gae_env_variables.yaml` file. If needed, ensure to run `python manage.py collectstatic` before deploying as static files won't be updated otherwise: the deploy commands uploads the already collected static files and GAE directly uses them as is.

To deploy on the cloud without redirecting the traffic on the new version:
`gcloud app deploy --no-promote`

This will make the new version available at a specific url, and you will always be able to change traffic allocation to this new version from the GAE online console.
