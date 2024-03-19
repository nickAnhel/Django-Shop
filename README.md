# Shop

Study project from the book "Django 4 by Example" by Antonio Mele

# Local Launcing

First of all you need to create python virtual environment. You can do this by running
the following command in your terminal.

```console
python -m venv "your-venv-name"
```

Next you need to install all third-party modules.

```console
pip install -r requirements.txt
```

Now you can run local server.

```console
python3 manage.py runserver
```

Install and run docker images for redis and rabbitmq.

```console
docker pull rabbitmq
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

```console
docker pull redis
docker run -it --rm --name redis -p 6379:6379 redis
```

Run Celery worker.

```console
celery -A myshop worker -l info
```

After this you can optional run Flower tool for Celery.

```console
celery -A myshop flower
```

Ultimatelly, you need to login in the Stripe CLI and run listener for payment webhook.

```console
stripe login
stripe listen --forward-to localhost:8000/payment/webhook
```

