#!/usr/bin/env python3


from bson import json_util
import argparse
import flask
import flask_cors as cors
import os
import pymongo
import utils


def create_app():
    """
    Defines routes and returns a Flask object.
    """

    conf = utils.load_configuration("drwatson.conf")

    app = flask.Flask(__name__)
    app.secret_key = os.urandom(128)
    cors.CORS(app)

    mongo = pymongo.MongoClient("localhost", 27017)
    db = mongo.drwatson

    # Watson = WatsonConnector(url=conf["watson"]["url"],
    #                          username=conf["watson"]["username"],
    #                          password=conf["watson"]["password"],
    #                          version=conf["watson"]["version"],
    #                          db_connector="test"
    # )

    @app.route('/feeds', methods=['GET'])
    def get_feeds():
        """
        Returns all available feeds.
        """

        feeds = db.feeds
        output = []

        for s in feeds.find():
            output.append(s)

        return json_util.dumps(output)

    @app.route('/feeds/<path:feed>', methods=['GET'])
    def get_feed(feed):
        """
        Returns info for specified feed.
        """

        feed = db.feeds.find({"key": feed})

        return json_util.dumps(feed)

    @app.route('/users', methods=['GET'])
    def get_users():
        """
        Returns all users.
        """

        users = db.users
        output = []

        for s in users.find():
            output.append(s)

        return json_util.dumps(output)

    @app.route('/users/<path:username>', methods=['GET'])
    def get_user(username):
        """
        Returns Profile for specified user.
        """

        user = db.users.find({"username": username})

        return json_util.dumps(user)

    @app.route('/reports/<path:username>/<path:date>', methods=['GET'])
    def get_user_report_date(username, date):
        """
        Returns specified report for specified user.
        """

        report = db.reports.find({"username": username, "date": date})

        return json_util.dumps(report)

    @app.route('/reports/<path:username>', methods=['GET'])
    @app.route('/users/<path:username>/reports', methods=['GET'])
    def get_user_reports(username):
        """
        Returns all reports for specified user.
        """

        reports = db.reports.find({"username": username})

        return json_util.dumps(reports)

    @app.route('/users/<path:username>/feeds', methods=['GET'])
    def get_feeds_for_user(username):
        """
        Returns all feeds for specified user.
        """

        user = db.users.find({"username": username})
        u = list(user)

        try:
            feeds = u[0]["feeds"]
        except IndexError as e:
            feeds = {}

        return json_util.dumps(feeds)

    @app.route('/users/<path:username>', methods=['POST'])
    def post_user(username):
        """
        Create a new user profile.
        """
        users = db.users
        user = users.find({"username": username})

        if user:
            flask.abort(409)

        # TODO: Validate request data
        username = request.json['username']
        password = request.json['password']
        mail = request.json['mail']
        feeds = request.json['feeds']

        new_user = { "username": username,
                     "mail": mail,
                     "password": password,
                     "feeds": feeds}

        users.insert_one(new_user)

        # TODO: Proper Return value
        return flask.jsonify({"result": []}, 201)

    @app.route('/users/<path:username>', methods=['DELETE'])
    def delete_user(username):
        """
        Delete a user profile.
        """
        users = db.users
        user = users.find({"username": username})

        if user:
            flask.abort(404)

        users.delete_one({"username": username})

        # TODO: Proper Return value
        return flask.jsonify({"result": []}, 200)

    return app
