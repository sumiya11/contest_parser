# contest_parser

Two files:
1. `parser.py` - parses contest results with respect to custom deadlines. Takes external logs and deadlines as an input.
2. `uploader.py` - uploads contest results to a Google Table. Takes output of `parser.py` as an input.

\
*Usage example:*

`$ python3 parser.py -i test/dump.xml -d test/deadlines.txt -o test`\

`$ python3 uploader.py -i standings/test.json -n 1`

\
Contest dump file format is deafult(external logs). Deadlines file contains some lines of the following format:
\
`%m.%d.%y %h:%m:%s[ap]m=X`\
where X is the the multiplier for the score of solutions, submitted before this deadline. One may check `test/dump.xml` and `test/deadlines.txt` for an illustration.
\\

`uploader.py` needs `credentials.json` file to be present in the same folder in order to authentify in Tables.


