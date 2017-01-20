#!/bin/bash

extensions={cpp,h,hpp}
gradedFile="$1/assessment.md"

rm "$gradedFile"

shopt -s nullglob # disable returning *.cpp when can't find files

# Check against plagerism
printf "\`\`\`\`" >> "$gradedFile"
./moss.sh -d -l cc "$1"/*/*.cpp >> "$gradedFile"
printf "\`\`\`\`\n" >> "$gradedFile"

# The first checks to see if the compilation process was sucessful
# Followed by checking to see if individual files broke coding standards
for path in "$1"/*; do
    [ -d "${path}" ] || continue # if not a directory, skip
    echo "# $(basename "${path}")" >> $gradedFile # insert filename into the file

    g++ -Wall -W -pedantic-errors "$path"/*.cpp -o testing

    # if the last command (the compile) was successful, then skip
    # if not, log.
    if [ $? -ne 0 ]; then
        echo "### g++ Compilation Warnings/Errors" >> "$gradedFile"
        printf "\`\`\`\`\n" >> "$gradedFile"
        g++ -Wall -W -pedantic-errors "$path"/*.cpp 2>> "$gradedFile"
        printf "\`\`\`\`\n" >> "$gradedFile"
    fi

    # Style guide check every file
    for file in "$path"/*.{cpp,h,hpp}; do
        echo "## $(basename "${file}")" >> "$gradedFile"

       if [ -n "python grader.py "$file"" ]; then
            python grader.py "$file" >> "$gradedFile"
            echo "" >> "$gradedFile"
        fi
    done
done

rm testing # from the compilation process
shopt -u nullglob # re-enable returning *.cpp
