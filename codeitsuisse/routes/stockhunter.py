import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route("/stock-hunter", methods=["POST"])
def checkIfWorks():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    output = []
    allPartsHelper(data, output)
    return json.dumps(output)


def allPartsHelper(data, output):
    for i in range(len(data)):
        currentTestCaseOutput = {}
        currentTestCase = data[i]
        currentTestCaseOutput["gridMap"] = constructGridMap(currentTestCase)
        currentTestCaseOutput["minimumCost"] = findMinimumCost(currentTestCaseOutput["gridMap"])
        output.append(currentTestCaseOutput)


def constructGridMap(currentTestCase):
    entryPoint = currentTestCase["entryPoint"]
    targetPoint = currentTestCase["targetPoint"]
    gridDepth = currentTestCase["gridDepth"]
    gridKey = currentTestCase["gridKey"]
    horizontalStepper = currentTestCase["horizontalStepper"]
    verticalStepper = currentTestCase["verticalStepper"]
    entryRow, entryCol = entryPoint["first"], entryPoint["second"]
    targetRow, targetCol = targetPoint["first"], targetPoint["second"]
    riskIndexMatrix = [[0 for _ in range(targetCol + 1)] for _ in range(targetRow + 1)]  # risk index
    riskLevelMatrix = [[0 for _ in range(targetCol + 1)] for _ in range(targetRow + 1)]
    for row in range(len(riskIndexMatrix)):
        for col in range(len(riskIndexMatrix[0])):
            if row == 0 and col == 0 or row == len(riskIndexMatrix) - 1 and col == len(riskIndexMatrix[0]) - 1:
                riskLevelMatrix[row][col] = (riskIndexMatrix[row][col] + gridDepth) % gridKey
                continue
            if row == 0:  # y coord 0
                riskIndexMatrix[row][col] = col * horizontalStepper
                riskLevelMatrix[row][col] = (riskIndexMatrix[row][col] + gridDepth) % gridKey
                continue
            if col == 0:
                riskIndexMatrix[row][col] = row * verticalStepper
                riskLevelMatrix[row][col] = (riskIndexMatrix[row][col] + gridDepth) % gridKey
                continue
            riskIndexMatrix[row][col] = riskLevelMatrix[row - 1][col] * riskLevelMatrix[row][col - 1]
            riskLevelMatrix[row][col] = (riskIndexMatrix[row][col] + gridDepth) % gridKey
    for row in range(len(riskLevelMatrix)):
        for col in range(len(riskLevelMatrix[0])):
            riskLevel = riskLevelMatrix[row][col]
            if riskLevel % 3 == 0:
                riskLevelMatrix[row][col] = "L"
            elif riskLevel % 3 == 1:
                riskLevelMatrix[row][col] = "M"
            else:
                riskLevelMatrix[row][col] = "S"
    return riskLevelMatrix


def findMinimumCost(gridMap):
    matrix = [[0 for _ in range(len(gridMap[0]))] for _ in range(len(gridMap))]
    costToReach = [[float("inf") for _ in range(len(gridMap[0]))] for _ in range(len(gridMap))]
    costToReach[0][0] = 0
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if gridMap[row][col] == "L":
                matrix[row][col] = 3
            elif gridMap[row][col] == "M":
                matrix[row][col] = 2
            else:
                matrix[row][col] = 1
    for row in range(1, len(matrix)):
        costToReach[row][0] = costToReach[row - 1][0] + matrix[row][0]
    for col in range(1, len(matrix[0])):
        costToReach[0][col] = costToReach[0][col - 1] + matrix[0][col]
    for row in range(1, len(matrix)):
        for col in range(1, len(matrix[0])):
            costToGetHereFromSides = min(costToReach[row][col - 1], costToReach[row - 1][col]) + matrix[row][col]
            costToReach[row][col] = min(costToReach[row][col], costToGetHereFromSides)
    return costToReach[-1][-1]
