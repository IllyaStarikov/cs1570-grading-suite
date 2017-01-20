# CS1570 Grader

## Regular Expressions
### Rules 
- **Header, Documentation, Functions (`$a`)** `$` matches to the end of the line and `a` matches to *a* to an a after the end of the line --- if you think this is impossible, you'd be correct. This is a placeholder regex.
- **Column (`.{80}`)** Easy peasy. Match any character (`.`) for upto eighty characters (`{80}`).
- **Braces (`[^\s].*({|}[^\s*while.*])`)** Matches to any character doesn't begin with a space, maybe has a characters inbetween it, then has a either a closing or opening brace. If it's a closing brace, make sure not to have a while attached to it because that's valid syntax.
- **Tabs (`\t`)** Just look anywhere for the tab character (`\t`)

### Others
- **Number of Functions (`"[a-zA-Z]([a-zA-Z]|[0-1]|_)*\s+[a-zA-Z]([a-zA-Z]|[0-1]|_)*\(.*\)"`)** So this one's interesting. Anything that begins with a character, then followed by characters, numbers or underscores is a valid identifier. The first and second word are by nature identifiers (with, optionally, another identifier with `::` in between for scope). Then we match that to a parathesis, and that's the best we can do because sometimes parameters are forced to the next line because of the 80 columns rule.
