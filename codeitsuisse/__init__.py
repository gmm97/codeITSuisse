from flask import Flask

app = Flask(__name__)
import codeitsuisse.routes.square
import codeitsuisse.routes.parasite
import codeitsuisse.routes.opt
import codeitsuisse.routes.asteroid
import codeitsuisse.routes.stockhunter
import codeitsuisse.routes.stonks
