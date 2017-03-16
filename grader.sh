#!/bin/bash

# Usage: Run this in the cs1570 directory.
# run as ./grader.sh SECTION_TO_GRADE

gradedFile="assessment.md"
violations="allViolations.csv"

# Basically, check to see the output files are in the
# directory and remove them. also
preperation() {
    printf "Removing Output Files... "

    if [[ -n $(ls | grep "$violations") ]]; then
        rm "$violations"
    fi

    if [[ -n $(ls | grep "$gradedFile") ]]; then
        rm "$gradedFile"
    fi

    shopt -s nullglob # disable returning *.cpp when can't find files

    printf "Done.\n"
}

plagerismChecker() {
    printf "Uploading To Moss... "

    printf "# Only Section\n\`\`\`\`" >> "$gradedFile"
    ./moss.sh -d -l cc "$1"/*/*.cpp >> "$gradedFile"
    printf "\`\`\`\`\n" >> "$gradedFile"

    printf "Done.\n"
}

grade() {
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
}

finish() {
    printf "Removing Temporary Files... "

    rm testing violations.csv
    shopt -u nullglob # re-enable returning *.cpp

    printf "Done.\n"
}

main() {
    plagerismChecker $1
    grade $1
    finish
}

main "$@"
