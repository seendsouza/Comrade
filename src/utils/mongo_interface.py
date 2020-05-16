'''
Comrade - Python-MongoDB Interfacer
'''

from pymongo import MongoClient
import json
import os
import dotenv

dotenv.load_dotenv()
client = MongoClient(os.environ.get('MONGOKEY'))
print("Atlas Cluster Connected, Running Version {}.".format(
    client.server_info()['version']))


def getUser(userID: int, serverID: int):
    '''
    gets a user based on user ID and guild ID.
    '''
    users = client['Comrade']['UserData']
    return users.find_one({"user": userID, "server": serverID})


def getUserfromNick(nickname: str, serverID: int):
    '''
    gets a user based on server nickname
    '''
    users = client['Comrade']['UserData']
    return users.find_one({"nickname": nickname, "server": serverID})


def userQuery(query: dict):
    '''
    Returns a set of users given a query
    '''
    users = client['Comrade']['UserData']
    return users.find(query)

def cfgQuery(query:dict):
    '''
    Returns a set of cfgs given a query
    '''
    cfg = client['Comrade']['cfg']
    return cfg.find(query)

def customUserQuery(query:dict):
    '''
    Returns a set of custom users given a query
    '''
    customs = client.Comrade.CustomUsers
    return customs.find(query)


def getCFG(serverID: int):
    '''
    Returns a dictionary with the cfg values for Comrade in a given server
    '''
    cfg = client['Comrade']['cfg']
    return cfg.find_one({"_id": serverID})


def updateCFG(newCFG: dict):
    '''
    Updates configuration file for a given server based on the ID
    '''
    cfg = client['Comrade']['cfg']
    cfg.update({"_id": newCFG["_id"]}, newCFG, True)


def updateUser(userData: dict):
    '''
    Upserts user into userData collection
    '''
    users = client.Comrade.UserData
    users.update({
        "user": userData["user"],
        "server": userData["server"]
    }, userData, True)  # upsert


def addCustomUser(name, url, server):
    '''
    Adds a custom user to the CustomUsers collection, for use with echo command etc.
    '''
    customs = client.Comrade.CustomUsers
    customs.insert({"name": name, "url": url, "server": server})

def updateCustomUser(userData:dict):
    '''
    Updates a custom user.
    '''
    customs = client.Comrade.CustomUsers
    customs.update({
        "name": userData["name"],
        "server": userData["server"]
    }, userData, True)  # upsert


def getCustomUser(name, server):
    '''
    Gets a custom user from the database
    '''
    customs = client.Comrade.CustomUsers
    return customs.find_one({"name": name, "server": server})
