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
$ docker-compose up -d db minio mail
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createfixturedata
$ python manage.py runserver
```

### Testing

After setting up the development environment with the steps above, you can run the following command to execute the test suite.

```
$ python manage.py test
```

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
* MAIL_FROM       `default: notifications@water-dragon-api.localhost`
* MAIL_HOST       `default: 0.0.0.0`
* MAIL_PORT       `default: 1025`
* MAIL_PASSWORD   `default: `
* MAIL_USER       `default: `
* MAIL_USE_TLS    `default: False`
* MAIL_USE_SSL    `default: False`
