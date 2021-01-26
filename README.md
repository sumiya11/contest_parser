# contest_parser

A parser for contest results with respect to custom deadlines. Takes external logs and deadlines as an input.

\
*Usage example:*

`$ python3 parser.py test/dump.xml test/deadlines.txt`

Output is stored in the `standings` folder in `json` format.

\
Contest dump file format is deafult.
\
Deadlines file contains some lines of the following format:\
`%m.%d.%y %h:%m:%s[ap]m=X`\
where X is the the multiplier for the score of solutions, submitted before this deadline.

One may check `test/dump.xml` and `test/deadlines.txt` for an illustration.
