from redis import Redis
import os
import pickle
from PIL import Image

redis = Redis(host=os.environ.get("REDIS_HOST", 'redis'), port=os.environ.get("REDIS_PORT", 6379))


def save_image_to_redis(eventset, key, image):
    directory = f'experiments/{eventset}/'
    filename = f'experiments/{eventset}/{key}.png'
    if not os.path.exists(directory):
        os.makedirs(directory)
    image.figure.savefig(filename)
    im = Image.open(filename)
    data = pickle.dumps(im)
    redis_id = key + str(eventset)
    redis.set(redis_id, data)
    os.remove(filename)

    return redis_id


def save_html_to_redis(eventset, key, name, cluster):
    with open(name, 'r') as f:
        html = f.read()
    data = pickle.dumps(html)
    redis_id = key + str(eventset) + '_' + str(cluster)
    redis.set(redis_id, data)

    return redis_id


