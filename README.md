# cs1570 Grading Suite
cs1570-grader is a grader for introduction to programming at Missouri S&T. The programming lints student code for style guide violations, set by the course coordinator. Some of these rules include:

- Ensuring every `.hpp` files has a header
- All functions be properly documented
- All functions have a return statement
- Every `switch` statement has a default
- Code only goes up to the 80th column

And so forth. These functions are written entirely in python3. A markdown output is produced, and if the `--csv` option is passed, a CSV is produced of the form `username,type of violiation,type of violation,...`.

The linter file can be ran via `./stylechecker.py *.cpp *.hpp *.h`. The linting relies *heavily* on python's [Regular Expressions library](https://docs.python.org/2/library/re.html). The regexs are documented under the [Regular Expressions](#regular-expressions) section.

Along with said linting, the entire directory of homeworks is also checked for plagiarism via Stanford's [Moss](https://theory.stanford.edu/~aiken/moss/) program. Download it from the website, and put it in the same directory as the linter files.

For *all* of these program to work, there is an expected directory structure. That directory structure is thus:

````
DIRECTORY
|
|__ User #1
|__|__ File #1
|__|__ File #2
|__|__ File #3
|__|__ File #4
|
|__ User #2
|__|__ File #1
|__|__ File #2
|
|__ User #3
|__|__ File #1
|__|__ File #2
|__|__ File #3
|__|__ File #4
|__|__ File #5
|__|__ File #6
````

Essentially, the top level directory has all the homeworks, subsequent subdirectories are the user's files, and the user's subdirectories contain the code. The minimum and maximum depth of the folder structure is three.

All these functions are encapsulated in Bash script, `grader.py`. The usage is as follows: `./grader.py PATH/TO/DIRECTORY`. There are other files, which are described below.

## Other Files
Below are additional files added that can be an aid in grading.

### roster-checker.py
Usage: **python3 roster-checker.py PATH/TO/ROSTER/FILE PATH/TO/STUDENTS/DIRECTORY**

Roster checker provides a way to determine if there are either any faulty submission (i.e., a submission from a different class) or if a student forgot to submit an assignment.

The only requirements are a roster file, which lists all the students, seperated by a newline; like so:

````
User #1
User #2
User #3
````

It doesn't matter if there are subdirectories or files, the only requirements is *the username must be in the submission* of the top level. So if roster file is like the one above, then directory diagram at the beginning of the README would suffice.

## Regular Expressions
### Rules
- **Header, Documentation, Functions, Others (`$a`)** `$` matches to the end of the line and `a` matches to *a* to an "a" after the end of the line --- if you think this is impossible, you'd be correct. This is a placeholder regex.
- **Column (`.{80}\S"`)** Match any character (`.`) for upto eighty characters (`{80}`), followed by some sort of newline (`\S`). This is because some students would leave a spaces at the end of the file.
- **Braces (`[^\s].*([^\s*=\s*]{|}[^\s*while.)`)**  This one is currently being broken and is being fixed.
- **Tabs (`\t`)** Just look anywhere for the tab character (`\t`)
- **Constants** Just look for anything with the word `const` followed by an identifier for the type, then the name, and finally a `=` and a semicolon. These all have to be padded by spaces and what not because of different coding styles.

### Others
- **Number of Functions (`"[a-zA-Z]([a-zA-Z]|[0-1]|_)*\s+[a-zA-Z]([a-zA-Z]|[0-1]|_)*\(.*\)"`)** So this one's interesting. Anything that begins with a character, then followed by characters, numbers or underscores is a valid identifier. The first and second word are by nature identifiers (with, optionally, another identifier with `::` in between for scope). Then we match that to a parathesis, and that's the best we can do because sometimes parameters are forced to the next line because of the 80 columns rule.
