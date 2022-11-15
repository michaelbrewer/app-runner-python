from flask import Flask
import boto3
import os

app = Flask(__name__)
session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


@app.route("/")
def hello():
    return table.get_item(Key={"PK": "100"})["Item"]["value"]


if __name__ == "__main__":
    from waitress import serve

    serve(app, port=8080)
