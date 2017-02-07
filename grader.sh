#!/bin/bash

extensions={cpp,h,hpp}
gradedFile="$1/assessment.md"

shopt -s nullglob # disable returning *.cpp when can't find files

# Check against plagerism
printf "\`\`\`\`" >> "$gradedFile"
#./moss.sh -d -l cc "$1"/*/*.cpp >> "$gradedFile"
printf "\`\`\`\`\n" >> "$gradedFile"

# The first checks to see if the compilation process was sucessful
# Followed by checking to see if individual files broke coding standards
for path in "$1"/*; do
    [[ -d "${path}" ]] || continue # if not a directory, skip

    printedUser=false
    g++ -Wall -W -pedantic-errors "$path"/*.cpp -o testing

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
    for file in "$path"/*.{cpp,h,hpp}; do
       if [[ -n "python stylechecker.py "$file"" ]]; then
            if [[ "$printedUser" == false ]]; then
                echo "# $(basename "${path}")" >> $gradedFile # insert filename into the file
                printedUser=true
            fi

            echo "## $(basename "${file}")" >> "$gradedFile"
            python stylechecker.py "$file" --csv >> "$gradedFile"
            echo "" >> "$gradedFile"

            cat violations.csv >> allViolations.csv
        fi
    done
done

rm testing allViolations.csv  

shopt -u nullglob # re-enable returning *.cpp
