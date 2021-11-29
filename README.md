This mini-project is composed of a single python script `cron.py` and a test
file `test_parser.py` that contains some unit-tests. The script parses a string
representing standard cron arguments.

>Note:
The code is written in Python 3.8, however the minimal version it can run on is Python 3.5
(_the code makes use of type hints which were introduced in 3.5_).


#### Running the script
The script, `cron.py`, is executed with the following command:

    python3 cron.py "<cron-string>",

where `cron-string` consists of exactly 5 parts (enclosed by `""`) in the following order:

`"minute hour day-of-month month day-of-week command"`.


**Example**:

    python3 cron.py "*/15 0 1,15 * 1-5 /usr/bin/find"

_Refer to this [link](https://www.ibm.com/docs/en/db2oc?topic=task-unix-cron-format) for
more information about the standard cron format._


#### Running unit-tests
From the project's root folder execute the following:

    python3 -m unittest tests/test*

