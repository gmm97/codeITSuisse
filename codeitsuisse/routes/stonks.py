import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route("/stonks", methods=["POST"])
def checkIfCanFindProfit():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    output = []
    allPartsHelper(data, output)
    return json.dumps(output), {"Content-Type": "application/json"}


def allPartsHelper(data, output):
    for i in range(len(data)):
        currentTestCase = data[i]
        op = testCaseHandler(currentTestCase)
        output.append(op)


def testCaseHandler(currentTestCase):
    energy = currentTestCase["energy"]
    capital = currentTestCase["capital"]
    timeline = currentTestCase["timeline"]  # this is how far we can go back
    profits = 0
    possibleTimeline = {}
    availableStocks = {}
    transactions = []
    answerList = []
    startingYear = 2037 - energy // 2
    for year in range(startingYear, 2038):
        if str(year) in timeline:
            possibleTimeline[year] = timeline[str(year)]
    for year in possibleTimeline:
        for stock in possibleTimeline[year]:
            availableStocks[stock] = []
    for year in possibleTimeline:
        for stock in possibleTimeline[year]:
            availableStocks[stock].append(
                [year, possibleTimeline[year][stock]["price"], possibleTimeline[year][stock]["qty"]]
            )
    while capital > 0:
        maxProfitPerUnitCapital = float("-inf")
        earlierStockInTransaction = None
        laterStockInTransaction = None
        purchasedStock = None
        for stock in availableStocks:
            for l in reversed(range(len(availableStocks[stock]))):
                laterStock = availableStocks[stock][l]
                for e in range(0, len(availableStocks[stock])):
                    earlierStock = availableStocks[stock][e]
                    if earlierStock[0] == laterStock[0]:  # not from same year
                        continue
                    profitPerUnitCapital = (laterStock[1] - earlierStock[1]) / earlierStock[1]
                    if profitPerUnitCapital > maxProfitPerUnitCapital:
                        maxProfitPerUnitCapital = profitPerUnitCapital
                        earlierStockInTransaction = earlierStock
                        laterStockInTransaction = laterStock
                        purchasedStock = stock
        if maxProfitPerUnitCapital <= 0:
            # do not buy anything so you dont make a loss
            break
        totalPriceOfStock = earlierStockInTransaction[1] * earlierStockInTransaction[2]
        # this wont work for all cases, but see how
        if totalPriceOfStock > capital:
            # not correct
            numberOfStockToBuy = capital // earlierStockInTransaction[1]
            pricePaid = capital
        else:
            numberOfStockToBuy = earlierStockInTransaction[2]
            pricePaid = numberOfStockToBuy * earlierStockInTransaction[2]
        capital -= pricePaid
        profits += (laterStockInTransaction[1] - earlierStockInTransaction[1]) * earlierStockInTransaction[2]
        availableStocks[purchasedStock] = list(
            filter(lambda entry: entry[0] != earlierStockInTransaction[0], availableStocks[purchasedStock])
        )
        # year, quantity,
        buyYear = earlierStockInTransaction[0]
        sellYear = laterStockInTransaction[0]
        oppositeDirection = True if buyYear > sellYear else False
        quantity = numberOfStockToBuy
        stockName = purchasedStock
        transactions.append([buyYear, oppositeDirection, quantity, stockName, True])  # last field true for buying
        transactions.append([sellYear, oppositeDirection, quantity, stockName, False])  # last field for buying

    backwardTransactions = list(filter(lambda transaction: transaction[1] == True, transactions))
    backwardTransactions.sort(key=lambda x: -x[0])  # sort based on year decreasing
    forwardTransactions = list(filter(lambda transaction: transaction[1] == False, transactions))
    forwardTransactions.sort(key=lambda x: x[0])  # sort based on year increasing
    totalTransactions = backwardTransactions + forwardTransactions
    if not backwardTransactions and not forwardTransactions:
        return []
    if not backwardTransactions:
        toAppend = "j" + "-" + "2037" + "-" + str(forwardTransactions[0][0])
        answerList.append(toAppend)
    for i in range(len(totalTransactions)):
        transactions = totalTransactions[i]
        if transactions[4]:
            toAppend = "b" + "-" + str(transactions[3]) + "-" + str(transactions[2])
            answerList.append(toAppend)
        else:
            toAppend = "s" + "-" + str(transactions[3]) + "-" + str(transactions[2])
            answerList.append(toAppend)
        if i != len(totalTransactions) - 1:
            if totalTransactions[i + 1][0] != totalTransactions[i][0]:
                toAppend = "j" + "-" + str(totalTransactions[i][0]) + "-" + str(totalTransactions[i + 1][0])
                answerList.append(toAppend)
            else:
                continue
        else:
            if totalTransactions[i][0] != 2037:
                toAppend = "j" + "-" + str(totalTransactions[i][0]) + "-" + "2037"
                answerList.append(toAppend)
    return answerList
