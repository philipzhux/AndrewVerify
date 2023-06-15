#
# Created on Fri Jun 16 2023
#
# Copyright (c) 2023 Philip Zhu Chuyan <me@cyzhu.dev>
#

import requests
from parse import *
from xpinyin import Pinyin
from tabulate import tabulate
from threading import Thread
from queue import Queue

'''
AndrewVerifier: a class that verifies a batch of names concurently
@usage:
from AndrewVerify.verifier import AndrewVerifier
verifier = AndrewVerifier()
result = verifier.verifyBatchString(\'''
1. 陈翔宇
2. 陆永忠
3. Philip Zhu
4. chuyanz
\''')
print(AndrewVerifier.tabulateResults(result))
'''
class AndrewVerifier:
    def __init__(self, concurrent = 15, url = "https://directory.andrew.cmu.edu/index.cgi"):
        self.url = url
        self.__results = []
        self.pinyin = Pinyin()
        self.concurrent = concurrent
        self.q = Queue(self.concurrent * 2)
        for _ in range(self.concurrent):
            t = Thread(target=lambda: self.__doWork())
            t.daemon = True
            t.start()

    '''
    tabulateResults: a static utility function that tabulates the results
    @param results: a list of dictionaries containing the result of verification
    @return: a string containing the tabulated results
    '''
    @staticmethod
    def tabulateResults(results):
        results.sort(key = lambda result: result["is_INI"])
        results.sort(key = lambda result: result["Verified"])
        if len(results)>0:
            header = results[0].keys()
            rows =  [x.values() for x in results]
            return tabulate(rows, header)
        else: return ""

    '''
    verifyBatchString: verify a batch of names in a string concurently
    @param verifiedString: a string containing names to be verified,
    acceptable format 1: "X. verifyingName1\nX. verifyingName2\nX. verifyingName3\n..."
    acceptable format 2: "verifyingName1\nverifyingName2\nverifyingName3\n..."
    verifying Name can be an andrew id or a full name in either Chinese or English
    @return: a list of dictionaries containing the result of verification
    '''
    def batchVerifyString(self,verifiedString):
        return self.concurrentBatchVerify(verifiedString.splitlines())

    '''
    verifyBatchLines: verify a batch of names in a list of strings concurently
    @param verifiedLines: a list of strings containing names to be verified,
    acceptable format 1: "X. verifyingName1\nX. verifyingName2\nX. verifyingName3\n..."
    acceptable format 2: "verifyingName1\nverifyingName2\nverifyingName3\n..."
    verifying Name can be an andrew id or a full name in either Chinese or English
    @return: a list of dictionaries containing the result of verification
    '''
    def concurrentBatchVerify(self, verifiedLines, verifiedBy = None):
        if verifiedBy == None: verifiedBy = self.singleNameVerify
        self.__results.clear()
        possibleParseRules = ["{:d}. {}","{:d}.{}","{:d} {}"]
        for line in verifiedLines:
            for parseRule in possibleParseRules:
                payload = parse(parseRule,line)
                if payload: 
                    payload = payload[1]
                    break
            else: payload = line
            self.q.put((payload, self.singleNameVerify))
        print("Verifying ...\n")
        self.q.join()
        return self.__results

    def __doWork(self):
        while True:
            name, action = self.q.get()
            result = action(name)
            self.__results.append(result)
            self.q.task_done()

    def __verifyData(self,dataToVerify):
        result = {"Declared_Keyword": dataToVerify, "Verified": False, "Display_Name": "", "CMU_Email": "", "is_INI": False}
        data = {
            'action': 'Search',
            'searchType': 'basic',
            'activetab': 'basic',
            'search': dataToVerify
        }
        response = requests.post(url = self.url, data=data)
        stringPayload = response.content.decode()
        parsed1 = parse("{}<b>Display Name:</b> {}<br /><b>Email:</b> {}<br /><b>Andrew UserID:</b> {}<br />{}",stringPayload)
        if parsed1:
            result["Display_Name"] = parsed1[1]
            result["Verified"] = True
            result["CMU_Email"] = parsed1[2]
            result["is_INI"] = stringPayload.find("Information Networking Institute")!=-1
        return result
    
    '''
    verifyById: verify a name by andrew id concurently
    @param andrewId: andrew id to be verified
    @return: a dictionary containing the result of verification
    '''
    def singleIdVerify(self,andrewId):
        return self.__verifyData(andrewId)
    
    '''
    verifyByName: verify a name by full name concurently
    @param name: full name to be verified, can be in either Chinese or English
    @return: a dictionary containing the result of verification
    '''
    def singleNameVerify(self, name):
        chinesePhontonic = self.pinyin.get_pinyin(name,' ')
        if name!=chinesePhontonic:
            chinesePhontonic = chinesePhontonic.split()
            lastName = chinesePhontonic[0].capitalize()
            firstName = "".join(chinesePhontonic[1:]).capitalize()
            name = f"{firstName} {lastName}"
        return self.__verifyData(name)

    '''
    verifyByKeyword: verify a name by keyword concurently
    @param keyword: keyword to be verified, raw keyword
    will be passed to CMU server directly to verify
    @return: a dictionary containing the result of verification
    '''
    def singleKeywordVerify(self, keyword):
        return self.__verifyData(keyword)