import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route("/parasite", methods=["POST"])
def resolve():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    output = []
    allPartsHelper(data, output)
    return json.dumps(output)


def allPartsHelper(data, output):
    for i in range(len(data)):
        currentRoomOutput = {}
        currentRoom = data[i]
        currentRoomOutput["room"] = currentRoom["room"]
        # part one logic
        currentRoomOutput["p1"] = partAFindPosition(currentRoom)
        # part two logic
        currentRoomOutput["p2"] = partBAndCFindPosition(currentRoom, True)
        # part three logic
        currentRoomOutput["p3"] = partBAndCFindPosition(currentRoom, False)
        # part four logic
        currentRoomOutput["p4"] = partDFindPosition(currentRoom)
        output.append(currentRoomOutput)


def partDFindPosition(roomEntry):
    energy = 0
    grid = [row[:] for row in roomEntry["grid"]]
    position = findStartingPosition(grid)
    if not gridContainsHealthyPerson(grid):
        return 0
    visited = [[float("inf") for _ in range(len(grid[0]))] for _ in range(len(grid))]
    calculateEnergyNeeded(position, grid, visited)
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == 1:
                energy = max(energy, visited[row][col])
    return energy


def gridContainsHealthyPerson(grid):
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == 1:
                return True
    return False


def calculateEnergyNeeded(position, grid, visited):
    startingRow, startingCol = position
    queue = [(startingRow, startingCol, 0)]  # the final is energy not time
    while queue:
        currentPerson = queue.pop()
        row, col, energy = currentPerson
        if row >= len(grid) or row < 0 or col >= len(grid[0]) or col < 0:
            continue
        currentEnergyAtPosition = visited[row][col]
        if (
            energy >= currentEnergyAtPosition
        ):  # the cell i am at now has either not been visited or it has been visited but with higher energy
            continue
        visited[row][col] = energy
        neighbours = getNeighboursWithEnergy(row, col, energy, grid)
        for n in neighbours:
            queue.append(n)


def getNeighboursWithEnergy(row, col, energy, grid):
    neighbours = []
    if row < len(grid) - 1:
        if grid[row + 1][col] == 0 or grid[row + 1][col] == 2:
            neighbours.append((row + 1, col, energy + 1))
        else:
            neighbours.append((row + 1, col, energy))
    if row > 0:
        if grid[row - 1][col] == 0 or grid[row - 1][col] == 2:
            neighbours.append((row - 1, col, energy + 1))
        else:
            neighbours.append((row - 1, col, energy))

    if col < len(grid[0]) - 1:
        if grid[row][col + 1] == 0 or grid[row][col + 1] == 2:
            neighbours.append((row, col + 1, energy + 1))
        else:
            neighbours.append((row, col + 1, energy))

    if col > 0:
        if grid[row][col - 1] == 0 or grid[row][col - 1] == 2:
            neighbours.append((row, col - 1, energy + 1))
        else:
            neighbours.append((row, col - 1, energy))

    return neighbours


def partBAndCFindPosition(roomEntry, partB):
    grid = [row[:] for row in roomEntry["grid"]]
    position = findStartingPosition(grid)
    answer = 0
    visited = {}
    if not gridContainsHealthyPerson(grid):
        return 0
    partBAndCFindInfectedPeople(position, grid, visited, partB)
    # check if there are healthy people still inside
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == 1:  # this guy could not be reached
                return -1
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == 3:
                answer = max(answer, visited[(row, col)])
    return answer


def partBAndCFindInfectedPeople(position, grid, visited, partB):
    startingRow, startingCol = position
    queue = [(startingRow, startingCol, 0)]
    while queue:
        currentPerson = queue.pop()  # use bfs
        row, col, steps = currentPerson
        if row >= len(grid) or row < 0 or col >= len(grid[0]) or col < 0:
            continue
        if grid[row][col] == 0 or grid[row][col] == 2:  # empty space or vacc person
            visited[(row, col)] = float("-inf")
            continue
        if (row, col) in visited and steps >= visited[(row, col)]:  # been visited before and no need to visit again
            continue
        visited[(row, col)] = steps
        grid[row][col] = 3
        if partB:
            neighbours = getNeighbours(row, col, steps)
        else:
            neighbours = getDiagonalNeighbours(row, col, steps)
        for neighbour in neighbours:
            queue.append(neighbour)


def partAFindPosition(roomEntry):
    outputDict = {}
    grid = [row[:] for row in roomEntry["grid"]]
    interestedIndividuals = roomEntry["interestedIndividuals"]
    position = findStartingPosition(grid)
    interestedIndividualsDict = {}
    for person in interestedIndividuals:
        personEntry = person.split(",")
        personRow, personCol = int(personEntry[0]), int(personEntry[1])
        interestedIndividualsDict[(personRow, personCol)] = -1
    visited = {}
    partAFindInfectedPeople(position, grid, interestedIndividualsDict, visited)
    for key, value in interestedIndividualsDict.items():
        row, col = key
        newKey = str(row) + "," + str(col)
        outputDict[newKey] = value
    return outputDict


def partAFindInfectedPeople(position, grid, interestedIndividualsDict, visited):
    startingRow, startingCol = position
    queue = [(startingRow, startingCol, 0)]
    while queue:
        currentPerson = queue.pop()  # use bfs
        row, col, steps = currentPerson
        if row >= len(grid) or row < 0 or col >= len(grid[0]) or col < 0:
            continue
        if grid[row][col] == 2 or grid[row][col] == 0:
            continue
        if (row, col) in visited and steps >= visited[(row, col)]:  # been visited before and no need to visit again
            continue
        visited[(row, col)] = steps
        if (row, col) in interestedIndividualsDict:
            interestedIndividualsDict[(row, col)] = visited[(row, col)] if grid[row][col] != 3 else -1
        neighbours = getNeighbours(row, col, steps)
        for neighbour in neighbours:
            queue.append(neighbour)


def getNeighbours(row, col, steps):
    neighbours = []
    neighbours.append((row - 1, col, steps + 1))
    neighbours.append((row + 1, col, steps + 1))
    neighbours.append((row, col + 1, steps + 1))
    neighbours.append((row, col - 1, steps + 1))
    return neighbours


def getDiagonalNeighbours(row, col, steps):
    neighbours = []
    neighbours.append((row - 1, col - 1, steps + 1))
    neighbours.append((row - 1, col, steps + 1))
    neighbours.append((row - 1, col + 1, steps + 1))
    neighbours.append((row, col - 1, steps + 1))
    neighbours.append((row, col + 1, steps + 1))
    neighbours.append((row + 1, col - 1, steps + 1))
    neighbours.append((row + 1, col, steps + 1))
    neighbours.append((row + 1, col + 1, steps + 1))
    return neighbours


def findStartingPosition(grid):
    position = (None, None)
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == 3:
                position = (row, col)
    return position
