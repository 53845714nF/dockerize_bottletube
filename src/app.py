#!/usr/bin/python3

"""
Web service that allows to save images.
"""

from os import getenv, path, makedirs, chdir, stat
from time import strftime
from bottle import route, template, request, default_app
from psycopg2 import connect
from minio import Minio

HOSTNAME = getenv('HOSTNAME')

STORAGE_URL_IN = getenv('STORAGE_URL_IN')
STORAGE_URL_OUT = getenv('STORAGE_URL_OUT')
BUCKET = getenv('BUCKET')
SAVE_PATH = '/tmp/images/'

DB_USER = getenv('POSTGRES_USER')
DB_HOST = getenv('POSTGRES_HOST')
DB_PASSWORD = getenv('POSTGRES_PASSWORD')
DB_NAME = getenv('POSTGRES_DB')

@route('/home')
@route('/')
def home():
    """
    The start page of the web service
    """
    items = []
    cursor.execute('SELECT * FROM image_uploads ORDER BY id')

    for record in cursor.fetchall():
        url = STORAGE_URL_OUT + '/' + BUCKET + '/' + record[1]
        items.append({'id': record[0], 'url': url, 'category': record[2]})

    return template('home.tpl', name='Bottletube Home', items=items)

@route('/healthcheck', method='GET')
def healthcheck():
    """
    healthcheck can be used to check if the server is still alive.
    """
    return f'Here is {HOSTNAME}'

@route('/upload', method='GET')
def do_upload_get():
    """
    The Get uplode function show the Site for Uploade
    """
    return template('upload.tpl', name='Upload Image')

@route('/upload', method='POST')
def do_upload_post():
    """
    The Post uplode function stores images in object storage and in data bank.
    """
    category = request.forms.get('category')
    upload = request.files.get('file_upload')

    error_messages = []
    if not upload:
        error_messages.append('Please upload a file.')
    if not category:
        error_messages.append('Please enter a category.')

    try:
        name, ext = path.splitext(upload.filename)
        if ext not in ('.png', '.jpg', '.jpeg'):
            error_messages.append('File Type not allowed.')
    except: # pylint: disable=bare-except
        error_messages.append('Unknown error.')

    if error_messages:
        return template('upload.tpl', name='Upload Image', error_messages=error_messages)

    # Save to SAVE_PATH directory
    if not path.exists(SAVE_PATH):
        makedirs(SAVE_PATH)

    save_filename = f'{name}_{strftime("%Y%m%d-%H%M%S")}{ext}'
    with open(f'{SAVE_PATH}{save_filename}', 'wb') as open_file:
        open_file.write(upload.file.read())

    if ext == '.png':
        content_type = 'image/png'
    else:
        content_type = 'image/jpeg'

    uploade_file = str(SAVE_PATH) + str(save_filename)
    with open(uploade_file, 'rb') as file_data:
        file_stat = stat(uploade_file)
        resource.put_object(BUCKET,
                        f'user_uploads/{save_filename}',
                        file_data,
                        file_stat.st_size, content_type=content_type)

    # pylint: disable=line-too-long
    cursor.execute(f"INSERT INTO image_uploads (url, category) VALUES ('user_uploads/{save_filename}', '{category}');")
    connection.commit()

    return template('upload_success.tpl', name='Upload Image')

@route('/delete', method='GET')
def do_post_delete():
    """
    Can be used to delete images again.
    """
    items = []
    id = request.query['id']
    try:
        cursor.execute(f'SELECT * FROM image_uploads WHERE id = {id};')
        for record in cursor.fetchall():
            items.append({'id': record[0],
                          'filename': record[1],
                          'category': record[2]})

        resource.remove_object(BUCKET, items[0].get('filename'))

        cursor.execute(f'DELETE FROM image_uploads WHERE id = {id};')
        connection.commit()

        return template('delete.tpl', name='Delete Success')

    except: # pylint: disable=bare-except
        return template('delete.tpl', name='Delete Failed')

connection = connect(user=DB_USER, host=DB_HOST, password=DB_PASSWORD, database=DB_NAME)
cursor = connection.cursor()
cursor.execute("SET SCHEMA 'bottletube';")
connection.commit()

resource = Minio(STORAGE_URL_IN,secure=False)

chdir(path.dirname(__file__))
app = default_app()
