import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route("/asteroid", methods=["POST"])
def find():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    output = []
    answerHandler(data["test_cases"], output)
    return json.dumps(output)


def answerHandler(cases, output):
    for case in cases:
        caseOutput = {"input": case, "score": 1, "origin": 0}
        solveCase(case, caseOutput)
        output.append(caseOutput)


def solveCase(s, caseOutput):
    if len(s) == 1 or len(s) == 2:
        return
    pointsList = findPossibleBlastPoints(s)  # surrounded on both sides by the same letter
    if not pointsList:
        return  # must be surrounded on both sides
    for point in pointsList:
        # initially, the explosion expands out from the main character
        solveCaseHelper(s, caseOutput, 0, point - 1, point + 1, point, True)


def solveCaseHelper(s, caseOutput, score, leftPoint, rightPoint, beginIdx, isChar):
    if beginIdx == 8:
        print(s, leftPoint, rightPoint, score)
    if not s:
        updateScore(caseOutput, score, beginIdx)
        return
    if leftPoint < 0 or rightPoint > len(s) - 1:
        updateScore(caseOutput, score, beginIdx)
        return
    newString, addedScore, newLeftPoint, newRightPoint = calculateBlastPointsAndReturnString(
        s, leftPoint, rightPoint, isChar
    )
    score += addedScore
    if not newString or newString is None:
        updateScore(caseOutput, score, beginIdx)
        return
    return solveCaseHelper(newString, caseOutput, score, newLeftPoint, newRightPoint, beginIdx, False)


def updateScore(caseOutput, score, beginIdx):
    if score > caseOutput["score"]:
        caseOutput["score"] = score
        caseOutput["origin"] = beginIdx


def findPossibleBlastPoints(s):
    pointsList = []
    for i in range(1, len(s) - 1):  # except for the first and last index
        if s[i - 1] == s[i + 1]:
            pointsList.append(i)
    return pointsList


def calculateBlastPointsAndReturnString(s, leftPoint, rightPoint, isChar):
    rightSame = leftSame = 0
    if isChar and s[leftPoint] != s[leftPoint + 1]:  # the 2 sides are different from the middle
        return s[: leftPoint + 1] + s[rightPoint:], 1, leftPoint, leftPoint + 1
    if s[leftPoint] != s[rightPoint]:  # cannot destroy any more
        return None, 0, None, None
    for i in range(rightPoint, len(s)):
        if s[i] == s[rightPoint]:
            rightSame += 1
        else:
            break
    for i in reversed(range(0, leftPoint + 1)):
        if s[i] == s[leftPoint]:
            leftSame += 1
        else:
            break
    if leftSame == rightSame and leftSame == 0 and not isChar:  # cannot destroy any more
        return None, 0, None, None
    numberDestroyed = leftSame + rightSame + 1 if isChar else leftSame + rightSame
    score = calculateScore(numberDestroyed)
    rightString = s[rightPoint + rightSame :]
    leftString = s[: leftPoint - leftSame + 1]
    newString = leftString + rightString
    return newString, score, leftPoint - leftSame, leftPoint - leftSame + 1


def calculateScore(totalDestroyed):
    if totalDestroyed <= 6:
        multiplier = 1
    elif totalDestroyed >= 7 and totalDestroyed < 10:
        multiplier = 1.5
    else:
        multiplier = 2
    return multiplier * totalDestroyed
