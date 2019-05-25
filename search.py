#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 17:58:28 2019

@author: francoischesnay, sebastianhurubaru
"""

from collections import defaultdict
from config import *
from rest import RESTClient
import json
from jsonpath_ng import jsonpath, parse


API_KEY="0K5Fn3TguQ_1OdFoSuzQREVG7aee1OKSYS5Mj5ns"
MAX_REQ_FOR_KEY=600
TIMEOUT=300 #seconds
BASE_URL="https://api.companieshouse.gov.uk/search"


restClient = RESTClient(API_KEY, MAX_REQ_FOR_KEY, TIMEOUT, BASE_URL)


log = logging.getLogger('search')


# Initialize global variable frontier with [(‘Cascado AG’,’Panama’)]
# where ‘Cascado AG’ is the name of the company to search
# and ‘Panama’ is the name of the country
frontier = [("Cascado AG","Panama")]

# Initialize global variable explored with an empty list
explored = []

# variable used to record the relationship between entities
# relationship are recorded through
# a list within relationship with
#  [[(entity1’, ’country entity1’), relationship, (entity2’, ’country entity2’)],
#     [(entity1’, ’country entity1’), relationship, (entity2’, ’country entity2’)]]
# and relationship can take the following two values for the moment:
#  “is an officer of”
#  “is a PSC of”
# at a later stage, we may decide to change the description of the relationship to include
# “is an officer (LLP Designated Member) of” and “is an officer (director) of”
relationship = []


# Create a dictionary to store the ranking of the various entities, that the ranking, may end up changing in time depending on new relationship being found.
# We initialize it with our first entity (‘Cascado AG’,’Panama’) with ranking 1
rank = defaultdict(lambda: 2147483647)
rank = {("Cascado AG","Panama"):1}

# Create a dictionary to store the list of entities who have a PSC
# for example, we could have:
# psc[(entity n’, ’country entity n’)] = ‘name of entity of significant control
# rationale to store is that it is not likely to be many PSC, and it is important
# to be able to retrieve the information when we need it.
psc = {}

# Create a list to store the entities who have financial statements
# available electronically, as this would be required for our project
financialStatements = []

# function searchTroikaEntities() used to build our database using
# public information available on CompaniesHouse website
# This function is a breadth search based on two search factors:
# the name of PSC (if it has been provided, therefore different from None), and
# the name of the officers of the entity
#
#
def searchTroikaEntities(K):
    # Take an entity out of the frontier if frontier is not empty
    if len(frontier)>0:
        entity = frontier.pop(0)
        # add the entity as explored
        explored.append(entity)

        # For all entities we call a procedure to obtain the list of appointments of
        # the entity in the company register
        # company register, as acting an director
        # Call a function, which will return the list of appointments
        # for an entity by connecting to Companies house
        # list of appointment return the information with format
        # [(‘name entity 1’, ’country entity 1’’),
        #  (‘name entity 2’, ’country entity 2’’)]

        secondEntities = getListOfAppointments(entity) # function to write defined below to extract information from Companies House
        for secondEntity in secondEntities:
            if secondEntity not in explored or secondEntity not in frontier:

                # Check that the rank of the new variable is within the threshold K
                if rank[entity]+1 <= K:
                    frontier.append((secondEntity, getcountry(secondEntity)))
                    rank[secondEntity]=rank[entity]+1

            # Add the relationship between entity and appointment
            #relationship.add([(entity1’, ’country entity1’), relationship,
            # (entity2’, ’country entity2’)]
            if min(rank[entity]+1, rank[secondEntity]) <= K:
                appendRelationship([entity, "is an officer of", (secondEntity)])


        if entity[1] == "UK":
            # If the entity is a UK entity, then there is more information to gather
            # and more work to do


            # call the function obtainPSC(entity)
            entityPSC = getPSC(entity)
            if entityPSC != None:
                psc[entity] = entityPSC
                if entityPSC not in explored or entityPSC not in frontier:

                    # Check that the rank of the new variable is within the threshold K
                    if rank[entity]+1 <= K:
                        frontier.append((entityPSC))
                        rank[entityPSC] = rank[entity]+1

                # Add the relationship between entity and appointment
                #relationship.add([(entity1’, ’country entity1’), relationship,
                # (entity2’, ’country entity2’)]
                if min(rank[entity]+1, rank[entityPSC]) <= K:
                    appendRelationship([entity, "is a PSC of", entityPSC])


            # call the function getOfficers(entity)
            officers = getOfficers(entity)
            if officers != None:
                for officer in officers:
                    if officer not in explored or officer not in frontier:

                        # Check that the rank of the new variable is within the threshold K
                        if rank[entity]+1 <= K:
                            frontier.append((officer))
                            rank[officer]=rank[entity]+1
                    # Add the relationship between the officer and the entity
                    #relationship.add([(entity1’, ’country entity1’), relationship,
                    # (entity2’, ’country entity2’)]
                    if min(rank[entity]+1, rank[officer]) <= K:
                        appendRelationship([officer, "is an officer of", entity])





#########################################################################################
# Functions requiring to be implemented to extract information from Companies House     #
#########################################################################################

# function to append the relationship between two entities
#relationship.add([(entity1’, ’country entity1’), relationship,  (entity2’, ’country entity2’)])
def appendRelationship(tupleEntity1, relationship, tupleEntity2):
    relationship.add([tupleEntity1, relationship, tupleEntity2])

# Return for an entity a list of its appointment in the UK based on the information extracted from Companies House website
def getListOfAppointments(entity):
    listNameCountryToReturn = []
    listOfAppointments = []
    #Search on CompaniesHouse the list of appointments based on the name of an entity
    # and append to listOfAppointments
    # I believe some work has been done already to program some functions
    # to access the company house website
    for appointment in listOfAppointments:
        listNameCountryToReturn.append((appointment,getcountry(appointment)))
    # return a list of tuple [(name1, xountry1), (name2, xountry2)]
    return listNameCountryToReturn


# Return for an entity the name of the country it is located in based on the information extracted from Companies House website
def getcountry(nameEntity):
    # Search on company house to return the country of the entity
    # return as a string the name of the country
    return nameOfCountry

#
def getPSC(entity):
    # obtain from company house, the PSC for an entity
    if PSCReturned == None:
        return None
    else:
        return (PSCReturned, getcountry(PSCReturned))

def getOfficers(entity):
    listofOfficers = []
    listOfOfficersAndCountries = []
    #Search on CompaniesHouse the list of officers for a company
    # and append to listofOfficers

    for officer in officerss:
        listOfOfficersAndCountries.append((officer,getcountry(officer)))
    # return a list of tuple [(officer1, xountry1), (officer2, xountry2)]
    return listOfOfficersAndCountries





