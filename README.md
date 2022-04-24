
# REST Library inventory management

This is a simple library management app that allows the owner to:

- Keep a list of all books
```/books```

- Listing details for a single book 
```/books/int```

- Creating a book in the DB manually
```/add/book```

- updating the details of a single book / deleting book is available in the detail view
```/books/int```

- importing new books from the Google Book Api
```/import/book```

## Technology used

Python3, Django, REST, HTML, SQL
## Installation

- Fork and clone the repo
- Source a virtual environment
- Pip install requirements.txt
- Obtain access_token and secret_key and store in secrets.sh
- Setup a Postgres DB, create user & database
- Migrate
    
## Deployment

Project is deployed on Heroku and can be found under this url:

```bash
  https://evening-reef-62982.herokuapp.com/
```

