# cs1570-grader
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

All these functions are encapsulated in Bash script, `grader.py`. The usage is as follows: `./grader.py DIRECTORY`.

## Regular Expressions
### Rules
- **Header, Documentation, Functions (`$a`)** `$` matches to the end of the line and `a` matches to *a* to an a after the end of the line --- if you think this is impossible, you'd be correct. This is a placeholder regex.
- **Column (`.{80}`)** Easy peasy. Match any character (`.`) for upto eighty characters (`{80}`).
- **Braces (`[^\s].*({|}[^\s*while.*])`)** Matches to any character doesn't begin with a space, maybe has a characters inbetween it, then has a either a closing or opening brace. If it's a closing brace, make sure not to have a while attached to it because that's valid syntax.
- **Tabs (`\t`)** Just look anywhere for the tab character (`\t`)

### Others
- **Number of Functions (`"[a-zA-Z]([a-zA-Z]|[0-1]|_)*\s+[a-zA-Z]([a-zA-Z]|[0-1]|_)*\(.*\)"`)** So this one's interesting. Anything that begins with a character, then followed by characters, numbers or underscores is a valid identifier. The first and second word are by nature identifiers (with, optionally, another identifier with `::` in between for scope). Then we match that to a parathesis, and that's the best we can do because sometimes parameters are forced to the next line because of the 80 columns rule.
