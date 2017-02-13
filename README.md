# Water Dragon API - *a Risk Managed backend rewrite*

## Development

### Required Software

* [docker](https://docs.docker.com/)
* [git](https://git-scm.com/)
* [virtualenv](https://virtualenv.pypa.io/en/stable/)

### Getting Started

1. `git clone https://github.com/jteppinette/water-dragon.git`

2. `virtualenv venv`

3. `source venv/bin/activate`

4. `pip install -r requirements.txt`

5. `docker-compose up -d db`

6. `python manage.py migrate`

7. `python manage.py createfixturedata`

8. `python manage.py runserver`

### Testing

You will need to grant the `db` user `* . *` permissions to your MySQL instance
to allow the Django test runner to create and destroy test databases during testing.

Once this is complete, you can run the tests with `python manage.py test`.

## Usage

### Environment Variables

Any variables marked as `insecure: true` should be overriden before being added to a production system.

* DEBUG           `default: True`
* DB_NAME         `default: db`
* DB_USER         `default: db`
* DB_PASSWORD     `defualt: secret, insecure: true`
* DB_HOST         `default: 0.0.0.0`
* DB_PORT         `default: 3306`
* SESSION_SECRET  `defualt: secret, insecure: true`

### Docker

1. `docker build . -t app`

2. `docker run \
      -d
      -e MYSQL_DATABASE=db
      -e MYSQL_USER=db
      -e MYSQL_PASSWORD=db-secret
      -e MYSQL_RANDOM_ROOT_PASSWORD=yes
      --name db
      mysql`

3. `docker run
      -d
      -p 8000:80
      -e SESSION_SECRET=session-secret
      -e DB_NAME=db
      -e DB_USER=db
      -e DB_PORT=3306
      -e DB_PASSWORD=db-secret
      -e DB_HOST=db
      --link db
      --name app
      app`

4. `docker exec -it app python manage.py migrate`

5. `docker exec -it app python manage.py createfixturedata`
