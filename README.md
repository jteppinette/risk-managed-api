# Water Dragon API - *a Risk Managed backend rewrite*

## Development

### Required Software

* [docker](https://docs.docker.com/)
* [git](https://git-scm.com/)
* [virtualenv](https://virtualenv.pypa.io/en/stable/)

### Getting Started

1. `git clone https://github.com/jteppinette/water-dragon-api.git`

2. `virtualenv venv`

3. `source venv/bin/activate`

4. `pip install -r requirements.txt`

5. `docker-compose up -d db minio`

6. `python manage.py migrate`

7. `python manage.py createfixturedata`

8. `python manage.py runserver`

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

### Docker

1. `docker build . -t app`

2. `docker run \
      -d
      -e POSTGRES_DB=db
      -e POSTGRES_USER=db
      -e POSTGRES_PASSWORD=db-secret
      --name db
      postgres:9.6`

3. `docker run
      -d
      -p 9000:9000
      -e MINIO_ACCESS_KEY=access-key
      -e MINIO_SECRET_KEY=secret-key
      -v ${PWD}/minio:/data
      --name minio
      minio server /data`

4. `docker run
      -d
      -p 8000:80
      -e SESSION_SECRET=session-secret
      -e DB_NAME=db
      -e DB_USER=db
      -e DB_PORT=5432
      -e DB_PASSWORD=db-secret
      -e DB_HOST=db
      -e MINIO_SERVER=minio:9000
      -e MINIO_BUCKET=water-dragon
      --link db
      --link minio
      --name app
      app`

4. `docker exec -it app python manage.py migrate`

5. `docker exec -it app python manage.py createfixturedata`
