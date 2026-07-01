import datetime
import json
import os
import random
from urllib.parse import urlparse

import pandas as pd
import redis
from celery import Celery

# We define our celery broker as well as our redis instance in the following lines.
# If the app is running on Workspaces, we connect to the same Redis instance as the deployed app but a different Redis
# database
if os.environ.get("DASH_ENTERPRISE_ENV") == "WORKSPACE":
    parsed_url = urlparse(os.environ.get("REDIS_URL"))
    if parsed_url.path == "" or parsed_url.path == "/":
        i = 0
    else:
        try:
            i = int(parsed_url.path[1:])
        except:
            raise Exception("Redis database should be a number")
    parsed_url = parsed_url._replace(path="/{}".format((i + 1) % 16))

    updated_url = parsed_url.geturl()
    REDIS_URL = "redis://%s" % (updated_url.split("://")[1])
else:
    REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")

celery_app = Celery("Celery App", broker=REDIS_URL)

redis_instance = redis.StrictRedis.from_url(REDIS_URL)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # This command invokes a celery task at an interval of every 1 second. You can change this.
    sender.add_periodic_task(1, update_data.s(), name="Update data")


@celery_app.task
def update_data():
    def generate_initial_dataframe(num_points=30, interval_seconds=1):
        dates = []
        values = []
        for i in range(num_points):
            new_date = datetime.datetime.now() + datetime.timedelta(
                seconds=-i * interval_seconds
            )
            dates.append(new_date.strftime("%Y-%m-%d %H:%M:%S"))
            values.append(random.randint(0, 50))
        return pd.DataFrame({"time": dates, "value": values})

    try:
        # Try to get existing data from Redis
        existing_data = redis_instance.hget("app-data", "DATASET")
        if existing_data:
            # Load existing dataframe
            data = json.loads(existing_data)
            df = pd.DataFrame(data=data)
        else:
            # If no existing data, create initial dataframe with some historical data
            df = generate_initial_dataframe()
    except (json.JSONDecodeError, TypeError):
        # If there's an issue with existing data, start fresh
        df = generate_initial_dataframe()

    # Prepend a new data point with current timestamp to the top (newest first)
    new_row = pd.DataFrame(
        {
            "time": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "value": [random.randint(0, 50)],
        }
    )
    df = pd.concat([new_row, df], ignore_index=True)

    # Prevent the dataframe from growing infinitely long - keep only first 100 points (newest)
    if len(df) > 100:
        df = df.head(100).reset_index(drop=True)

    # Save the updated dataframe to redis as a JSON string
    redis_instance.hset("app-data", "DATASET", json.dumps(df.to_dict("records")))
    return
