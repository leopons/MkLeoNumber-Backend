# smash-upset-distance

For production we're using Google App Engine Standard environnement with a Cloud SQL Postgres instance.

## Run Django Commands

Standard GAE doesn't allow to ssh or run a command directly from the cloud. As described in the [docs](https://cloud.google.com/python/django/appengine?hl=en#macos-64-bit), database operations like migrations or the creation of a superuser have to be performed from your local setup:

- Ensure that your local code version corresponds to the code you actually want to run on the production DB.
- If not already done, install the Cloud SQL Proxy as described [here](https://cloud.google.com/python/django/appengine?hl=en#installingthecloudsqlproxy).
- Start the Cloud SQL Proxy : `./cloud_sql_proxy -instances="[YOUR_INSTANCE_CONNECTION_NAME]"=tcp:3306`
- Your local environment variables should include the prod DB logins : `DB_PROD_DATABASE`, `DB_PROD_USERNAME`, `DB_PROD_PASSWORD`
- The commands will run on prod if `DB_MODE=prod`, you can just specify the var before the command, like this : `DB_MODE=prod python manage.py showmigrations`

## Production Variables

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
```

## Deployment

GAE deployment command :
`gcloud app deploy`

This wild deploy to prod, which means uploading the codebase and the environment variables from the `gae_env_variables.yaml` file. If needed, ensure to run `python manage.py collectstatic` before deploying as static files won't be updated otherwise: the deploy commands uploads the already collected static files and GAE directly uses them as is.

To deploy on the cloud without redirecting the traffic on the new version:
`gcloud app deploy --no-promote`

This will make the new version available at a specific url, and you will always be able to change traffic allocation to this new version from the GAE online console.
