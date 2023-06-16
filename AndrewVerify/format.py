from xpinyin import Pinyin
from parse import *
from tabulate import tabulate

class NameFormater:
    @staticmethod
    def hybridAutoParser(name):
        if NameFormater.isChineseName(name):
            return NameFormater.chineseNameParser(name)
        return NameFormater.romanNameParser(name)
    @staticmethod
    def isChineseName(name):
        return Pinyin().get_pinyin(name,' ')!=name
    
    @staticmethod
    def chineseNameParser(name):
        chinesePhontonic = Pinyin().get_pinyin(name,' ')
        assert name!=chinesePhontonic, "Invalid chinese characters"
        chinesePhontonic = chinesePhontonic.split()
        lastName = chinesePhontonic[0].capitalize()
        firstName = "".join(chinesePhontonic[1:]).capitalize()
        name = f"{firstName} {lastName}"
        return name
        
    @staticmethod
    def romanNameParser(name):
        return name
    
class IOFormater:
    # statc formats
    andrewFormat = "{}<b>Display Name:</b> {}<br /><b>Email:</b> {}<br /><b>Andrew UserID:</b> {}<br />{}"
    inputFormats = ["{:d}. {}","{:d}.{}","{:d} {}"]
    
    @staticmethod
    def andrewResponseParser(andrewResponse):
        parsedVec = parse(IOFormater.andrewFormat,andrewResponse)
        entry = AndrewEntry()
        if parsedVec:
            entry.displayName = parsedVec[1]
            entry.CMUEmail = parsedVec[2]
            entry.verified = True
            entry.is_INI = andrewResponse.find("Information Networking Institute")!=-1
        return entry
    
    @staticmethod
    def inputLineParser(inputLine):
        for inputFormat in IOFormater.inputFormats:
            result = parse(inputFormat,inputLine)
            if result: 
                result = result[1]
                break
        else: result = inputLine
        return result
    
    @staticmethod
    def andrewRequestFormater(searchData):
        return {
            'action': 'Search',
            'searchType': 'basic',
            'activetab': 'basic',
            'search': searchData
        }
    
    '''
    tabulateResults: a static utility function that tabulates the results
    @param results: a list of dictionaries containing the result of verification
    @return: a string containing the tabulated results
    '''
    @staticmethod
    def tabulateResults(results):
        if len(results)==0: return ""
        assert "is_INI" in results[0] and "Verified" in results[0], "invalid Results"
        results.sort(key = lambda result: result["is_INI"])
        results.sort(key = lambda result: result["Verified"])
        header = results[0].keys()
        rows =  [x.values() for x in results]
        return tabulate(rows, header)



class AndrewEntry:
    def __init__(self, verified = False, is_INI = False, CMUEmail = "", displayName = ""):
        self.verified = verified
        self.CMUEmail = CMUEmail
        self.is_INI = is_INI
        self.displayName = displayName