ac2884 adl55

Allen Chun
Annette Lee
4

"Using an API: Bonus Activity"

The application is slow because because we front load all of the course information (which is a considerably large volume of data) by making API calls on every subject code and inserting the data into a list object, before performing searches on the data.

We could use multi-threading to make many different API calls by running multiple processes in parallel.

Querying only the cached data is problematic because the data may become outdated. If some data were updated, inserted, or removed, the cached data would not reflect these changes. We could use a write-behind cache to mitigate this problem by updating the cache only at first, then updating the Yale API later
asynchronously when it is a more optimal time to do so. By doing this, we don't have to perform two costly writes to the cache and the Yale system at the same time.

We had to replace all of our database SQL queries with searches that involved nested for loops on a front loaded set of course data. We also had to add API calls to our regapp.py file before the HTML pages were rendered. To reduce the scope of this change, we could have just converted the API data into a database initially.

The non-relational data JSON data is preferred because it gives more flexibility
in being able to retreive many different types of data through a simple search, whereas a relational database requires specific queries to extract particular categories of data.

Allen worked on regapp.py, getting the request.get functions to access the subject codes
and courses from the Yale CoursesWebServicev3 API. He also worked on search.py to search 
through all the frontloaded data as well as sort them according to the spec. He modified 
files from pset 3 by switching out all the code involving database calls to
functions that accomodated the API implementation. He also added a progress bar to inform
the user why the server was taking a while to load.

Annette worked on regapp.py, getting the request.get functions to access the subject codes
and courses from the Yale CoursesWebServicev3 API. She also worked on search.py to search 
through all the frontloaded data as well as sort them according to the spec. She modified 
files from pset 3 by switching out all the code involving database calls to
functions that accomodated the API implementation. She also added a progress bar to inform
the user why the server was taking a while to load.

We worked on every part of the pset together. 

We didn't receive help from anybody.

We referenced the PennyFlaskJinja code from the examples shown in class and listed 
under canvas files.

Estimated time spent on pset: 15 hours

This assignment helped us get familiar with using the request and json package. It
gave us practice on python functionality as we had to switch our implementation
from database querying to brute searching on frontloaded data in Python. 
It would've been a lot more helpful if this pset was more clear on the differences 
between the regsqlite databases in the previous psets and the Yale API data on this pset.

For Pylint, with runserver.py, we could not resolve the general exceptions error
because we did not know what specific error to use for giving a positive integer
value for the port number. We also used a general exception to catch any other
errors that could have come up. Course.py was also weird because we received a
9.51 on it in pset3 but we got a 9.47 for too many arguments and local variables
when we actually decreased the number of arguments, local variables, and functions. 
We needed all those attributes in the class for our implementation to work.

The grader should generate their own API key and put it in a `.env` file in the 
project root with the format API_KEY=<value>