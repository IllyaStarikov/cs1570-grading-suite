#!/bin/bash

# Usage: Run this in the cs1570 directory.
# run as ./grader.sh SECTION_TO_GRADE ENTIRE_CLASS

gradedFile="assessment.md"
violations="allViolations.csv"

shopt -s nullglob # disable returning *.cpp when can't find files

if [[ -n $(ls | grep "$violations") ]]; then
    rm "$violations"
fi

if [[ -n $(ls | grep "$gradedFile") ]]; then
    rm "$gradedFile"
fi

printf "Uploading To Moss... "

# Check against plagerism
printf "# Only Section\n\`\`\`\`" >> "$gradedFile"
#./moss.sh -d -l cc "$1"/*/*.cpp >> "$gradedFile"
printf "\`\`\`\`\n" >> "$gradedFile"

printf "Done.\n"
printf "Grading Student Files... "

# The first checks to see if the compilation process was sucessful
# Followed by checking to see if individual files broke coding standards
for path in "$1"/*; do
    [[ -d "${path}" ]] || continue # if not a directory, skip

    printedUser=false
    g++ -Wall -W -pedantic-errors "$path"/*.cpp -o testing > /dev/null 2>&1

    # if the last command (the compile) was successful, then skip
    # if not, log.
    if [[ $? -ne 0 ]]; then
        echo "# $(basename "${path}")" >> $gradedFile # insert filename into the file
        printedUser=true

        echo "### g++ Compilation Warnings/Errors" >> "$gradedFile"
        printf "\`\`\`\`\n" >> "$gradedFile"
        g++ -Wall -W -pedantic-errors "$path"/*.cpp 2>> "$gradedFile"
        printf "\`\`\`\`\n" >> "$gradedFile"
    fi
    

    # Style guide check every file
    if [[ -n $(python stylechecker.py $(basename "${path}") $path/*.cpp $path/*.hpp $path/*.h --csv) ]]; then
        if [[ "$printedUser" == false ]]; then
            echo "# $(basename "${path}")" >> $gradedFile # insert filename into the file
            printedUser=true
        fi
        
        python stylechecker.py $(basename "${path}") $path/*.cpp $path/*.hpp $path/*.h --csv >> "$gradedFile"
        cat violations.csv >> "$violations"
    else
        echo "$(basename "${path}")" >> "$violations"
    fi
done

printf "Done.\n"
rm testing violations.csv

shopt -u nullglob # re-enable returning *.cpp
