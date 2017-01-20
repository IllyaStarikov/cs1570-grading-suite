import re
import sys

from itertools import islice


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


# If a new rule appears, simply add to the enum and the regex to the rules section
RuleTypes = enum('HEADER', 'DOCUMENTATION', 'FUNCTIONS', 'COLUMN', 'BRACES', 'TABS')

rules = {
        RuleTypes.HEADER: ("$a", "Missing Header"),
        RuleTypes.DOCUMENTATION: ("$a", "Missing Documentation"),
        RuleTypes.FUNCTIONS: ("$a", "Return Statements < Functions"),
        RuleTypes.COLUMN: (".{80}", "80 Column Rule"),
        RuleTypes.BRACES: ("[^\s].*({|}[^\s*while.*])", "Brace Not On Newline"),
	RuleTypes.TABS: ("\t", "Tabs")
        }


# Checks against all the regexes in the regex rules
# Args: Line (string) that is to be checked, and line number (int)
# Returns a list of the form (rule enum, line number)
# This list method is the standard for all violations
def checkAgainstRules(line, number):
    violations = []

    for rule, (regex, description) in rules.items():
        if re.search(regex, line):
            violations.append((rule, number + 1))
    
    return violations


# Arg: a string to specify the filename
# Return an array to be added to the list of the 
def checkHeaderComments(filename):
    authorFound = False
    filenameFound = False

    with open(filename) as fh:
        # We assume the header to be in the top 10 lines of the file
        for line in list(islice(fh, 6)):
            # The regex basically looks for something beginning with //,*, or a spaces
            
            if re.search("(\/\/|\*|\s)+.*(File|file|.hpp|.cpp|.h)", line):
                filenameFound = True
            if re.search("(Author|author)", line):
                authorFound = True

    if authorFound or filenameFound:
        return []
    else:
        return [(RuleTypes.HEADER, 0)]


# Arg: a string to specify the filename
# Will go through and attempt to count the number of lines in the file
# Uses heuristic to see if there are roughly enough comments to satisfy
# a decent description of the files
def checkForDocumentation(filename):
    if re.search(".*.cpp", filename):
        readingMultilineComment = False
        totalLinesOfComments = 0
        
        fh = open(filename)

        for line in fh:
            if readingMultilineComment:
                if re.search("\*/", line):
                    readingMultilineComment = False
                else:
                    totalLinesOfComments += 1
            
            else:
                # This covers the /* ... */ comments
                if re.search("/\*.*\*/", line):
                    totalLinesOfComments += 1
                # This covers /* \n .. \n */ comments
                elif re.search("/\*", line):
                    readingMultilineComment = True
                # This covers // comments
                elif re.search("\/\/", line):
                    totalLinesOfComments += 1
                       
        # A good hueristic for documentation is 3 lines of code for every function
        if 3*numberOfFunctions(filename) > totalLinesOfComments:
            newRule = "Missing Documentation ({functionCount} Functions, {commentCount} Lines of Comments)".format(functionCount=numberOfFunctions(filename), commentCount=totalLinesOfComments)
            rules[RuleTypes.DOCUMENTATION] = ("$a", newRule)
            return [(RuleTypes.DOCUMENTATION, 0)]
        else:
            return []

    else:
        return []


# Arg: a string to specify the filename
# Verifies every function has a return statement
def verifyReturnStatements(filename):
    if re.search(".*.cpp", filname):
        totalNumberOfReturnStatements = 0

        for line in fh:
            if re.search("\s*return\s*;\s*", line):
                totalNumberOfReturnStatements += 1

        if totalNumberOfReturnStatements < numberOfFunctions(filename):
            return [(RuleTypes.FUNCTIONS, 0)] 
    
    return []


# Arg: a string to specify the filename
# Counts and returns an integer for every function
def numberOfFunctions(filename):
    if re.search(".*.cpp", filename):
        
        totalNumberOfFunctions = 0
        fh = open(filename)

        for line in fh:
            if re.search("[a-zA-Z]([a-zA-Z]|[0-9]|_)*\s+([a-zA-Z]([a-zA-Z]|[0-9]|_)*\s*::\s*)*[a-zA-Z]([a-zA-Z]|[0-9]|_)*\(", line):
                totalNumberOfFunctions += 1
        
        return totalNumberOfFunctions
    else:
        return 0


# Args: a string filename and the line for which you want returned
# Navigates to the line, and returns the string up to and including \n
def getLine(filename, lineNumber):
    fh = open(filename)
    
    for index, line in enumerate(fh):
        if index + 1 == lineNumber:
            return line

    return ""


# Args: A string
# Will strip all special space characters (\n, \t, \r) from beginning and end
def stripExcessSpace(string):
    removedBeginningSpace = re.sub('^\s*', '', string)
    removedBeginningAndEndingSpace = re.sub('\s*$', '', removedBeginningSpace)
    return removedBeginningAndEndingSpace


# Args: a list of the form (rule enum, line number)
# Prints all violations in markdown form
def printOutViolations(filename, violations):
    violations.sort()
    
    keys = [i[0] for i in violations]
    violationsPrinted = {x: (0, False) for x in list(rules.keys())}

    for rule, line in violations:
        if keys.count(rule) > 10 and not violationsPrinted[rule][1]:
            print("\n**{violation}** *({count} Violations, Omitting After Five)*\n".format(count=keys.count(rule), violation=rules[rule][1]))
        elif not violationsPrinted[rule][1]:
            print("\n**{violation}**\n".format(violation=rules[rule][1]))
            
        if violationsPrinted[rule][0] < 5:
            print('- Line {line}: `{violatingLine}`\n'.format(line=line, violatingLine=stripExcessSpace(getLine(filename, line))))
        
        violationsPrinted[rule] = (violationsPrinted[rule][0] + 1, True)


def main():
    fh = open(sys.argv[1])
    nonLineByLineRules = [checkHeaderComments, checkForDocumentation]
    
    violations = [] 

    for function in nonLineByLineRules:
        additionalViolations = function(sys.argv[1])

        if additionalViolations != []:
            violations += additionalViolations

    for index, line in enumerate(fh):
        additionalViolations = checkAgainstRules(line, index)
        
        if additionalViolations != []:
            violations += additionalViolations
    
    
    printOutViolations(sys.argv[1], violations)
    fh.close()

if __name__ == "__main__":
    main()
