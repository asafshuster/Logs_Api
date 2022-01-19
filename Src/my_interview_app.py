"""
Python version: 3.8.5
Installed: flasgger

Description: This script runs an flask api which retrieve user's logs from a local json file.
OpenApi spacification file: OpenApiSpec.py (check-out at: http://localhost:5000/apidocs)
Main endpoint: http://localhost:5000/show-logs/
"""

# Imports
from flask import Flask, jsonify, request
from flasgger import Swagger
from Src.OpenApiSpec import api_spec
from datetime import datetime
import json
import os


# Constants
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SWAGGER'] = api_spec
swagger = Swagger(app)
working_dir = os.path.dirname(__file__)
log_file_path = rf"{working_dir}/events-sample.json"


def create_dataset():
    """Read the local json file, return list of dicts"""

    with open(log_file_path, "r") as events:
        logs_lst = [json.loads(log) for log in events.readlines()]
        return logs_lst


def get_user_logs(logs_lst, user_id):
    """Return a list which contains only logs contains user_id"""

    return [log for log in logs_lst if log["user_id"] == user_id]


def compare_timestamp(anchor_time, log_time):
    """Return True if the timestamp of the anchor is greater then the log timestamp"""

    date_time_anchor_obj = datetime.strptime(anchor_time, '%Y-%m-%d %H:%M:%S.%f')
    date_time_log_obj = datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S.%f')
    return date_time_anchor_obj > date_time_log_obj


def get_anchor_index(user_logs_lst, anchor_timestamp):
    """
    Runs over the range of the user_logs_lst, uses the compare_timestamp.
    Return the index of the anchor event in the user_log_lst.
    If anchor_timestamp greater then the first log timestamp, it will returns all logs at the list.

    :param user_logs_lst: A list of logs of specific user.
    :param anchor_timestamp: A str represent the timestamp which the user focused.
    :return: A int that represent the index of the anchor in the user_log_lst.
    """

    for i in range(len(user_logs_lst)):
        if compare_timestamp(anchor_timestamp, user_logs_lst[i]["timestamp"]):
            anchor_index = i - 1
            return anchor_index


def get_logs_by_limit(user_logs_lst, anchor_index, logs_limit):
    """
    Creates slice from user_logs_lst which determine by the logs_limit.

    :param user_logs_lst: List of logs of specific user
    :param anchor_index: The index of the anchor in the user_logs_lst
    :param logs_limit: The number of events that will appear upon and under the anchor
    :return: List of dictionaries of the limited logs.
    """

    anchor_index = int(anchor_index)
    logs_limit = int(logs_limit)
    under = anchor_index - logs_limit
    if under < 0:
        under = 0
    return user_logs_lst[under: (anchor_index + logs_limit) + 1]


@app.route('/tos')
def terms_of_service():
    """Returns a terms of service page"""

    return jsonify(massage="No terms of service")


logs_lst = create_dataset()


@app.route('/show-logs/', methods=['GET'])
def get_logs_page():
    """Api Endpoint: 'localhost:5000/testshow-logs/'.
    Return json which contains the logs around the anchor log according to the logs appearance limit.
    specification at: http://127.0.0.1:5000/apidocs
    ---
    Usage example: 'http://127.0.0.1:5000/show-logs/?anchor_timestamp=2021-01-09+23%3A01%3A59.140
                &user_id=31b20726-b870-47ba-bbcd-372b38527c89
                &log_appearance_limit=1
                &scrolling=0'
    """

    # get the query params (string is default)
    anchor_timestamp = request.args.get("anchor_timestamp")
    user_id = request.args.get("user_id")
    log_appearance_limit = int(request.args.get("log_appearance_limit"))
    scrolling = int(request.args.get("scrolling"))

    # To avoid unexciting configurable log limits.
    if log_appearance_limit < 0:
        return jsonify(error="log_appearance_limit < 0 is invalid"), 400

    user_logs_lst = get_user_logs(logs_lst, user_id)
    if len(user_logs_lst) == 0:
        return jsonify(error=f"Invalid user_id ({user_id})"), 400

    try:
        anchor_index = get_anchor_index(user_logs_lst, anchor_timestamp) + scrolling
    except (TypeError, ValueError):
        return jsonify(error=f"invalid anchor_timestamp ({anchor_timestamp})"), 400

    limited_logs = get_logs_by_limit(user_logs_lst, anchor_index, log_appearance_limit)

    len_user_logs_lst = len(user_logs_lst)
    scrolling_steps_to_end = len_user_logs_lst - (anchor_index + 1)
    scrolling_steps_to_start = len_user_logs_lst - scrolling_steps_to_end

    # limit the ability of the user the scroll to anchor which can't maintain the log_appearance_limit
    if scrolling > 0:
        if log_appearance_limit > scrolling_steps_to_end:
            return jsonify(error=f"Only {scrolling_steps_to_end} logs to scroll forward,"
                                 f" please decrease the log_appearance_limit",
                           user_logs_amount=len_user_logs_lst,
                           anchor_index=anchor_index), 400

    if scrolling < 0:
        if log_appearance_limit > scrolling_steps_to_start:
            return jsonify(error=f"Only {scrolling_steps_to_start} logs to scroll backward,"
                                 f" please decrease the log_appearance_limit",
                           user_logs_amount=len_user_logs_lst,
                           anchor_index=anchor_index), 400
    # valid params return
    return jsonify(user_id=user_id,
                   user_logs_amount=len_user_logs_lst,
                   anchor_index=anchor_index,
                   scrolling_steps_to_end=scrolling_steps_to_end,
                   scrolling_steps_to_start=scrolling_steps_to_start,
                   log_appearance_limit=log_appearance_limit,
                   current_scrolling=scrolling,
                   logs=limited_logs), 200


if __name__ == '__main__':
    app.run(debug=True)
