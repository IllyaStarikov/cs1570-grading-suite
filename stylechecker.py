#
#  main.py
#  cs1570-grader
#
#  Created by Illya Starikov on 06/04/2017
#  Copyright 2017. Illya Starikov. All rights reserved.
#

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
