# Store-Inventory-with-SQLAlchemy
Treehouse - Python Techdegree (Project 4)

This program uses the Peewee ORM to allow Python to create and manipulate an SQL database from a CSV file, and back up the database to another CSV file if requested.

Peewee 3.9.4 is required. A virtual env is not included.

The user can perform any of 4 actions:

- V: View an object inside the database using its ID (determined by the built-in `PrimaryKeyField()`)

- A: Add an object to the database. Names are unique, so if the user's chosen name for the object conflicts with an existing one, the newer one (the user's) will overwrite the old one.

- B: Back up the database to a CSV file. The contents of the database are preserved as completely as possible.

- Q: Quit the program after 3 seconds.
