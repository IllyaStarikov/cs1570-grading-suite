import re
import sys
import csv

from itertools import islice

extensions = ["hpp", "cpp", "h"]

# These sections specify what the rules are and how the work
# Every rule is specified as an enum, then stored in a dictionary
# The enum is the key, and a (regular expression, description) is the value
# A regular expression is used to specify how to match against the enum,
# a description is used to print out what the violation is

# Note if the regex is $a, this is a character after the end of the line
# If you think that's impossible, you're correct. This is used to specify
# a rule that's too complicated to be checked line by line (further in the script)
# and has it's own dedicated function.


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


# If a new rule appears, simply add to the enum and the regex to the rules section
RuleTypes = enum('HEADER', 'DOCUMENTATION', 'HEADER_GAURDS_MATCHING', 'HEADER_GAURDS_NAMING', 'SWITCH_DEFAULT', 'FUNCTIONS', 'COLUMN', 'BRACES', 'TABS', "CONSTANTS")


rules = {
    RuleTypes.HEADER: ("$a", "Missing Header"),
    RuleTypes.DOCUMENTATION: ("$a", "Missing Documentation"),
    RuleTypes.FUNCTIONS: ("$a", "Return Statements < Functions"),
    RuleTypes.HEADER_GAURDS_MATCHING: ("$a", "Header Gaurds Don't Match"),
    RuleTypes.HEADER_GAURDS_NAMING: ("$a", "Header Gaurds Are Incorrect Format"),
    RuleTypes.SWITCH_DEFAULT: ("$a", "No Default in Switch Case"),
    RuleTypes.COLUMN: (".{80}\S", "80 Column Rule"),
    RuleTypes.BRACES: ("[^\s].*([^\s*=\s*]{|}[^\s*while.*])", "Brace Not On Newline"),
    RuleTypes.TABS: ("\A\t", "Tabs"),
    RuleTypes.CONSTANTS: ("const\s+([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*\s+(([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*|\s*,\s*)*([a-zA-Z]|_)([A-Z]|[0-9]|_)*[a-z]+([A-Z]|[0-9]|_)*(\s*=\s*.+)*;", "Non-Uppercase Constants")
}


# Args: a list of the form (rule enum, line number)
# Prints all violations in markdown form. Why markdown?
# Easily exportable to other formats.
def printOutViolations(filename, violations):
    violations.sort()

    keys = [i[0] for i in violations]
    violationsPrinted = {x: (0, False) for x in list(rules.keys())}

    print("## {filename}".format(filename=basename(filename)))

    for rule, line in violations:
        if keys.count(rule) > 10 and not violationsPrinted[rule][1]:
            print("\n**{violation}** *({count} Violations, Omitting After Five)*\n".format(count=keys.count(rule), violation=rules[rule][1]))
        elif not violationsPrinted[rule][1]:
            print("\n**{violation}**\n".format(violation=rules[rule][1]))

        if violationsPrinted[rule][0] < 5:
            print('- Line {line}: `{violatingLine}`\n'.format(line=line, violatingLine=stripExcessSpace(getLine(filename, line))))

        violationsPrinted[rule] = (violationsPrinted[rule][0] + 1, True)


def exportToCSV(filename, violations):
    violations.sort()

    keys = [i[0] for i in violations]
    keys = removeDuplicates(keys)

    toExport = [filename]
    toExport += [rules[i][1] for i in keys]

    csvFile = open("violations.csv", 'w')
    wr = csv.writer(csvFile)
    wr.writerow(toExport)


# Checks against all the regexes in the regex rules
# Args: Line (string) that is to be checked, and line number (int)
# Returns a list of the form (rule enum, line number)
# This list method is the standard for all violations
def checkAgainstRules(line, number):
    violations = []

    for rule, (regex, description) in rules.items():
        pattern = re.compile(regex)

        if pattern.search(line):
            violations.append((rule, number + 1))

    return violations


# Arg: a string to specify the filename
# Return an array to be added to the list of the
def checkHeaderComments(filename):
    authorFound = False
    filenameFound = False

    with open(filename) as fh:
        # We assume the header to be in the top 10 lines of the file
        for line in list(islice(fh, 8)):
            # The regex basically looks for something beginning with //,*, or a spaces

            if re.search("(\/\/|\*|\s)+.*(File|file|.hpp|.cpp|.h)", line):
                filenameFound = True
            if re.search("(Author|author)", line):
                authorFound = True

    fh.close()
    if authorFound or filenameFound:
        return []
    else:
        return [(RuleTypes.HEADER, 0)]


# Arg: a string to specify the filename
# Will go through and attempt to count the number of lines in the file
# Uses heuristic to see if there are roughly enough comments to satisfy
# a decent description of the files
def checkForDocumentation(filename):
    totalLinesOfComments = 0

    entireFile = getEntireFile(filename)
    # This covers the /* ... */ comments
    allCommentPattern = re.compile('\/\*[\S\s]*\*\/')
    comments = allCommentPattern.findall(entireFile)

    if comments != []:
        for comment in comments:
            if comment.count('\n') == 0:
                totalLinesOfComments += 1
            else:
                # Just a simple check to see if there's comments preceding */ or after /*
                if re.search("\/\*\S+", comment):
                    totalLinesOfComments += 1
                if re.search("\S+\*\/", comment):
                    totalLinesOfComments += 1

                # We subtract one empty lines after * (this also matches the /* \n)
                totalLinesOfComments += comment.count('\n') - len(re.findall('\*\s*\n', comment))

    # This covers // comments
    allSingleLineComments = re.compile('\/\/.+')
    totalLinesOfComments += len(allSingleLineComments.findall(entireFile))

    # A good hueristic for documentation is 3 lines of code for every function
    if 3 * (numberOfFunctions(filename))[1] > totalLinesOfComments:
        newRule = "Missing Documentation ({functionCount} Functions, {commentCount} Lines of Comments)".format(functionCount=numberOfFunctions(filename)[1], commentCount=totalLinesOfComments)
        rules[RuleTypes.DOCUMENTATION] = ("$a", newRule)
        return [(RuleTypes.DOCUMENTATION, 0)]
    else:
        return []


# Arg: a string to specify the filename
# Verifies every function has a return statement
def verifyReturnStatements(filename):
    if re.search(".*.cpp", filename):
        fh = open(filename)
        totalNumberOfReturnStatements = 0

        for line in fh:
            if re.search("\s*return\s*;\s*", line):
                totalNumberOfReturnStatements += 1

        fh.close()

        if totalNumberOfReturnStatements < numberOfFunctions(filename):
            return [(RuleTypes.FUNCTIONS, 0)]

    return []


# Args: a string to specify the filename
# Verifies that every switch has a default case
# as specified in the styleguide
def checkForDefaultInSwitch(filename):
    entireFile = getEntireFile(filename)
    violations = []

    pattern = re.compile('switch\s*\(.*\)\s*\{[^\{;]+\}')
    switchCases = pattern.findall(entireFile)
    lineNumbers = [m.start(0) for m in pattern.finditer(entireFile)]

    for switch, line in zip(switchCases, lineNumbers):
        if not re.search('\s*default:\s+', switch):
            # the line of Nth character is used because the iterator returns what character
            # number is in the file. There should be a more effecient way, but Meh
            violations.append((RuleTypes.SWITCH_DEFAULT, lineOfNthCharacter(filename, line)))

    return violations


# Args: a string to specify the filename
# Verifies that header gaurds both:
# 1) are named the same
# 2) have the format of FILENAME_EXTENSION
def checkHeaderGaurds(filename):
    entireFile = getEntireFile(filename)
    violations = []

    # If not a header, disregard
    if re.search(".*.(h|hpp)", filename):
        # Match against the header gaurds, assuming there are only one
        pattern = re.compile('#ifndef\s*(.*)\n#define\s*(.*)')
        headerGaurds = pattern.search(entireFile)

        if headerGaurds:
            ifNotDefine = headerGaurds.group(1)
            define = headerGaurds.group(2)

            # If not defined the same
            if ifNotDefine != define:
                violations.append((RuleTypes.HEADER_GAURDS_MATCHING, findFirstOccurenceInFile(filename, ifNotDefine)))

            # If not in the format FILENAME_EXTENSION
            if stripExcessSpace(define) not in stripExcessSpace(filename.replace(".", "_").upper()):
                violations.append((RuleTypes.HEADER_GAURDS_NAMING, findFirstOccurenceInFile(filename, define)))

    return violations


# Args: someTuple is, well, a tuple
# Returns te last element in the said tuple
def lastElement(someTuple):
    return someTuple[len(someTuple) - 1]


# Args: a string to specify the filename
# Returns what line the Nth character in the string is
# This is literally going to hurt python coders
# but I have no idea of a better way to do it
def lineOfNthCharacter(filename, characterCount):
    entireFile = getEntireFile(filename)

    if len(entireFile) < characterCount:
        return None

    count = 1

    for index, character in enumerate(entireFile):
        if character == '\n':
            count += 1
        if index + 1 >= characterCount:
            return count


# Args: string for filename, string token
# Searches in the file line by line and returns
# The first occurence of said token is returned
def findFirstOccurenceInFile(filename, token):
    fh = open(filename)

    for index, line in enumerate(fh):
        if token in line:
            fh.close()
            return index + 1

    fh.close()
    return None


# Arg: a string to specify the filename
# Counts and returns an integer specifying how many function there are in said file
def numberOfFunctions(filename):
    entireFile = getEntireFile(filename)

    pattern = re.compile(
        '(([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*)\s+(([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*\s*::\s*)?([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*\(([a-zA-Z]|[0-9]|_|\[.*|\]|\&|\s|,)*\)\s*(.)'
    )
    allFunctions = pattern.findall(entireFile)

    definitions = list(filter(lambda x: lastElement(x) == '{', allFunctions))
    prototypes = list(filter(lambda x: lastElement(x) == ';', allFunctions))

    return (len(definitions), len(prototypes))


# Args: a string filename and the line for which you want returned
# Navigates to the line, and returns the string up to and including \n
def getLine(filename, lineNumber):
    fh = open(filename)

    for index, line in enumerate(fh):
        if index + 1 == lineNumber:
            fh.close()
            return line

    fh.close()
    return ""


# Args: A string
# Will strip all special space characters (\n, \t, \r) from beginning and end
def stripExcessSpace(string):
    removedBeginningSpace = re.sub('^\s*', '', string)
    removedBeginningAndEndingSpace = re.sub('\s*$', '', removedBeginningSpace)
    return removedBeginningAndEndingSpace


# http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-whilst-preserving-order
def removeDuplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# Args: a string to specify the filename
# gets the entirety of a the file, and returns said file as a string
def getEntireFile(filename):
    fh = open(filename)
    fileAsString = ""

    for line in fh:
        fileAsString += line

    fh.close()
    return fileAsString


def filesToGrade():
    files = []

    for argument in sys.argv:
        if re.search(".+\.(.+)", argument):
            pattern = re.compile(".+\.(.+)")
            extension = pattern.search(argument).group(1)

            if extension in extensions:
                files.append(argument)

    return files


def basename(filename):
    pattern = re.compile("(.*\/)*(.+.)")
    return pattern.search(filename).group(2)


def main():
    nonLineByLineRules = [checkHeaderComments, checkForDocumentation, checkHeaderGaurds, checkForDefaultInSwitch]
    allViolations = []

    for fileToGrade in filesToGrade():
        fh = open(fileToGrade)

        violations = []

        for function in nonLineByLineRules:
            additionalViolations = function(fileToGrade)

            if additionalViolations != []:
                violations += additionalViolations

        for index, line in enumerate(fh):
            additionalViolations = checkAgainstRules(line, index)

            if additionalViolations != []:
                violations += additionalViolations

        allViolations += violations

        if violations != []:
            printOutViolations(fileToGrade, violations)

    if "--csv" in sys.argv:
        exportToCSV(sys.argv[1], allViolations)


if __name__ == "__main__":
    main()
