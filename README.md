# MessengerStats

A statistics generator for Facebook Messenger conversations.   

You'll need to get your conversations data from Facebook first:\
&nbsp;   &nbsp; &nbsp;   &nbsp; *facebook.com &#8594; Settings &#8594; Your Facebook information &#8594; Download your information*\
&nbsp;   &nbsp; &nbsp;   &nbsp; *(or https://www.facebook.com/dyi/?referrer=yfi_settings)*

There, select a date range and JSON as format. Below, you only need to pick "Messages".

Extract the JSON file(s) for the conversation you want to analyze, and place them in a directory.
Then, you can launch ```MessengerStats.py```, specifying the path to the directory:

```python3 MessengerStats.py  path/to/JSON/files```

Results tables are generated in an ```output/``` directory, created where scripts are located.
