# Smash Upset Distance - Backend

## Introduction

This repo objective is to provide an API backend to a front web app which is coming soon.

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

*Disclaimer* : I am very aware that "this means nothing" : a player true level can't be determined by this distance, as it is heavily influenced by one time out-performances, or one may even say luck. But this is fun.

### Data

I'm using data from [The Player Database](https://smashdata.gg/). Go check it out, it's a really nice website that aggregates and displays data about Smash players. They've done a really nice work of reconciliation of player ids from different sources like smash.gg or challonge, there was not point for me in trying to re-do it.

I'm accounting for all the Smash Ultimate sets on the Player Database, excepts for DQs. This means that some Online tournaments are used for the path calculation too. I may change this in the future, or make it an option. If this is important to you, don't hesitate to make yourself heard [on twitter](https://twitter.com/UnCalinSSB).

## Endpoints

The API isn't available in production yet.

There is only one endpoint for now : `/upsets/playerpath/<player_id>/`

This gives the shortest win path between the player requested and MkLeo, as well as details about each upset : tournament, scores, etc. When there is multiple sets possible that do not increase the overall distance, I choose the most recent sets. For example this is my personal path on this day :

```json
{
    "player_tag": "UnCalin",
    "path_exist": true,
    "path": [
        {
            "node_depth": 5,
            "upset": {
                "tournament": {
                    "name": "Show me your mask ! #2",
                    "start_date": "2020-09-21"
                },
                "winner": "UnCalin",
                "loser": "Ukiyo",
                "winner_score": 2,
                "loser_score": 1,
                "round_name": "Losers Round 2",
                "best_of": 3
            }
        },
        {
            "node_depth": 4,
            "upset": {
                "tournament": {
                    "name": "Cycom Weekly S2 #3",
                    "start_date": "2019-11-08"
                },
                "winner": "Ukiyo",
                "loser": "Amiin",
                "winner_score": 2,
                "loser_score": 1,
                "round_name": "Losers Round 2",
                "best_of": 3
            }
        },
        {
            "node_depth": 3,
            "upset": {
                "tournament": {
                    "name": "Show me your mask ! #2",
                    "start_date": "2020-09-21"
                },
                "winner": "Amiin",
                "loser": "Tag",
                "winner_score": 2,
                "loser_score": 0,
                "round_name": "Losers Round 5",
                "best_of": 3
            }
        },
        {
            "node_depth": 2,
            "upset": {
                "tournament": {
                    "name": "Ultimate WANTED #1 Side Event #2 : Squad Battle / Smash en Bande",
                    "start_date": "2018-12-28"
                },
                "winner": "Tag",
                "loser": "Glutonny",
                "winner_score": 2,
                "loser_score": 1,
                "round_name": "Winners Round 4",
                "best_of": 3
            }
        },
        {
            "node_depth": 1,
            "upset": {
                "tournament": {
                    "name": "2GG: Kickoff - Kongo Saga",
                    "start_date": "2019-12-07"
                },
                "winner": "Glutonny",
                "loser": "MkLeo",
                "winner_score": 3,
                "loser_score": 0,
                "round_name": "Grand Final",
                "best_of": 3
            }
        },
        {
            "node_depth": 0,
            "upset": null
        }
    ]
}
```

## Code Structure

I'm using Django.

Most of the data preparation and calculation logic can be found in `upsets/lib`.
Otherwise, this is a pretty standard Django codebase : model based structure with DRF handling the serialization, with a `requirements.txt` file for the dependencies, and some tests to run with `python manage.py test`.

There is a lot of DB queries optimisation going on. To ease the task, I've set up DB queries console logging when `DB_LOGS=True`. The log messages for these lines are limited to 120 characters to avoid console flooding. You can change that with `DB_LOGS_MAX_CHARS`, for example :
`DB_LOGS=True DB_LOGS_MAX_CHARS=200 python manage.py process_players`

## Production Environnement

For production I'm using Google App Engine Standard environnement with a Cloud SQL Postgres instance.

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
  DEBUG: 'False'
  SECRET_KEY: 'your-secret-key'
  DB_PROD_CONNECTION_NAME: 'project-name:region-name:instance-name'
  DB_PROD_DATABASE: 'database-instance-name'
  DB_PROD_USERNAME: 'database-user-name'
  DB_PROD_PASSWORD: 'database-user-password'
  TWITTER_BEARER_TOKEN: 'twitter-api-bearer-token'
```

### Deployment

GAE deployment command :
`gcloud app deploy`

This wild deploy to prod, which means uploading the codebase and the environment variables from the `gae_env_variables.yaml` file. If needed, ensure to run `python manage.py collectstatic` before deploying as static files won't be updated otherwise: the deploy commands uploads the already collected static files and GAE directly uses them as is.

To deploy on the cloud without redirecting the traffic on the new version:
`gcloud app deploy --no-promote`

This will make the new version available at a specific url, and you will always be able to change traffic allocation to this new version from the GAE online console.
