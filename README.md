# Period Data Refresh with Celery

This app shows you how to run a task periodically to update data in your app on a defined schedule.

## Run the App on Your Workstation

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
2. Install & Run Redis. See [the Redis chapter](https://dash-temp.pmel.noaa.gov/docs/dash-enterprise/redis-database) for instructions on how to install & run Redis.

3. Run `export REDIS_URL="redis://127.0.0.1:6379"` to add an environment variable for your local instance of Redis.

4. In a terminal, run `celery -A tasks worker --loglevel=INFO --concurrency=2` to run a Celery worker.
5. In a another terminal, run `celery -A tasks beat --loglevel=INFO` to run the worker beat.

6. In a separate terminal, run the app:
   ```
   python app.py
   ```

## Run the App in a Workspace

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Add [Redis to your app](https://dash-temp.pmel.noaa.gov/docs/dash-enterprise/redis-database).

3. In a terminal, run `celery -A tasks worker --loglevel=INFO --concurrency=2` to run a Celery worker.
4. In a another terminal, run `celery -A tasks beat --loglevel=INFO` to run the worker beat.
5. In a separate terminal , run the app:
   ```
   python app.py
   ```


## Deploy the App From Your Workstation

To deploy this app to Dash Enterprise, [initialize an app](https://dash-temp.pmel.noaa.gov/docs/dash-enterprise/initialize), [add Redis to it](https://dash-temp.pmel.noaa.gov/docs/dash-enterprise/redis-database), and then follow [the steps for deployment](https://dash-temp.pmel.noaa.gov/docs/dash-enterprise/deployment).


## Deploy the App From a Workspace

If you're developing your app in a workspace, see [Deploying Changes](https://dash-temp.pmel.noaa.gov/docs/workspaces/deploying-changes) for more details on deploying from a workspace.