from celery import Celery

print(__name__)

celery_app = Celery(__name__ #'tasks'
                    , broker='amqp://guest@localhost//')

@celery_app.task
def add(x, y):
    return x + y