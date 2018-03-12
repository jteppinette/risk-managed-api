# Water Dragon API - *a Risk Managed backend rewrite*

## Development

### Required Software

* [docker](https://docs.docker.com/)
* [git](https://git-scm.com/)
* [virtualenv](https://virtualenv.pypa.io/en/stable/)

### Getting Started

```
$ git clone https://github.com/jteppinette/water-dragon-api.git && cd water-dragon-api
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ docker-compose up -d db minio
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createfixturedata
$ python manage.py runserver
```

### Testing

You will need to grant the `db` user `* . *` permissions to your PostgreSQL instance
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
* DB_PORT         `default: 5432`
* MINIO_ACCESSKEY `default: access-key`
* MINIO_BUCKET    `default: test`
* MINIO_SERVER    `default: 0.0.0.0:9000`
* MINIO_SECRET    `default: 'secret-key, insecure: true`
* MINIO_SECURE    `default: false`
* SESSION_SECRET  `defualt: secret, insecure: true`
