import fileinput
from AndrewVerify.verifier import AndrewVerifier

if __name__=="__main__":
    batchLines = [line.rstrip() for line in fileinput.input()]
    verifier = AndrewVerifier(concurrent=12)
    result = verifier.concurrentBatchVerify(batchLines)
    print(AndrewVerifier.tabulateResults(result))




