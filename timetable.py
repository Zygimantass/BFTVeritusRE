#!/usr/bin/python
# -*- coding: utf-8 -*-

import config
import requests
from bs4 import BeautifulSoup as bs

def formatUrl(cmd):
    return config.MAIN_URL + "?cmd={0}".format(cmd)

def formatAdditionalArgs(url, args):
    if len(args) < 1:
        return url

    argList = ["{0}={1}".format(key, args[key]) for key in args]
    return url + "&" + "&".join(argList)

def get(cmd, additionalArgs={}):
    url = formatUrl(cmd)
    url = formatAdditionalArgs(url, additionalArgs)

    req = requests.get(url, headers={'User-Agent': config.USER_AGENT})
    return req.content

def post(cmd, additionalArgs={}):
    clientGroup = config.CLIENT_GROUP
    username = config.USERNAME
    password = config.PASSWORD

    url = formatUrl(cmd)
    url = formatAdditionalArgs(url, additionalArgs)

    req = requests.post(url, headers={'User-Agent': config.USER_AGENT}, data={"ClientGroup": clientGroup, "UserCode": username, "UserPass": password})
    return req.content

def parseClientGroups():
    clientGroupContent = get("clientgroups")
    cgSoup = bs(clientGroupContent, 'lxml')
    clientGroups = {}
    for clientGroup in cgSoup.root.client_groups.find_all("client_group"):
        clientGroups[clientGroup["id"]] = clientGroup["name"]
    return clientGroups

def parseTests():
    timeTableContent = post("timetable", {"fltNextWeek": 18, "fltUntillNextWeek": 1})
    ttSoup = bs(timeTableContent, 'xml')
    tests = {}

    root = ttSoup.find("ROOT")
    academic_year = root.find("ACADEMIC_YEAR")
    semester = academic_year.find("SEMESTER")
    timetable = semester.find("TIMETABLE")

    for lesson in timetable.find_all("NEXT_LESSON"):
        if lesson["IS_TEST_WORK"] == "1":
            date = lesson["DATE"]
            if not date in tests:
                tests[date] = []

            test = {"subject": lesson["SUBJECT"], "info": lesson["TEST_WORK_INFO"]}
            tests[date].append(test)
    return tests

def removeDupes(testList):
    subjects = []
    newTestList = []

    for test in testList:
        if not test["subject"] in subjects:
            newTestList.append(test)
            subjects.append(test["subject"])
    return newTestList

def countTests(upcoming_tests):
    cnt = 0

    for date in upcoming_tests:
        tests = removeDupes(upcoming_tests[date])
        cnt += len(tests)

    return cnt

def printUpcomingTests(upcoming_tests):
    testCount = countTests(upcoming_tests)

    if testCount == 0:
        color = "green"
    elif testCount == 1:
        color = "orange"
    elif testCount > 1:
        color = "red"

    print "{0} upcoming tests | color = {1}".format(testCount, color)

    print "---"

    for date in upcoming_tests:
        print "{0} | color = #0000ff".format(date)
        tests = removeDupes(upcoming_tests[date])
        for test in tests:
            test_string = test["subject"]
            if test["info"] != "":
                test_string += test["info"]
            print test_string + " | color = #ffffff"


upcoming_tests = parseTests()
printUpcomingTests(upcoming_tests)
