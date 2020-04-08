from redis import Redis
from io import StringIO
import os
import pickle

redis = Redis(host='redis_queue', port=6379)


def save_image_to_redis(eventset, key, image):
    directory = f'experiments/{eventset}/'
    filename = f'experiments/{eventset}/{key}.png'
    if not os.path.exists(directory):
        os.mkdir(directory)
    image.figure.savefig(filename)
    with open(filename, 'rb') as f:
        file = f.read()
        data = pickle.dumps(file)
    redis.set(eventset, data)
    os.remove(filename)

