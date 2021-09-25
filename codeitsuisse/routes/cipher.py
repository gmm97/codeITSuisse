import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route("/cipher-cracking", methods=["POST"])
def thisBetterWork():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    output = []
    allPartsHelper(data, output)
    return json.dumps(output), {"Content-Type": "application/json"}


def allPartsHelper(data, output):
    for i in range(len(data)):
        currentTestCaseOutput = {}
        currentTestCase = data[i]
        testCaseHandler(currentTestCase, currentTestCaseOutput)
        output.append(currentTestCaseOutput)


def testCaseHandler(currentTestCase, currentTestCaseOutput):
    pass
