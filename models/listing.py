# coding: utf8
from datetime import datetime
from datetime import timedelta

db.define_table('listings',
    Field('user', db.auth_user, default=auth.user_id, required=True, readable=False, writable=False),
    Field('post_date', 'datetime', default=datetime.utcnow(), writable = False),
    Field('remove_date', 'datetime', default=datetime.utcnow() + timedelta(7,0), required=True, requires=IS_NOT_EMPTY()),
    Field('title', 'string', length=18, required=True, requires=[IS_NOT_EMPTY(), IS_LENGTH(18)]),
    Field('description', 'text', required=True, requires=IS_NOT_EMPTY()),
    Field('image', 'upload', uploadfield='image_file', required=False, requires=IS_NULL_OR([IS_IMAGE(), IS_LENGTH(maxsize=1048576, error_message='max file size is 1MB')])),
    Field('image_file', 'blob', required=False),
    Field('category', 'string', length=24, required=True, requires=IS_IN_SET(CATEGORIES), default=CATEGORIES[0]),
    Field('public', 'boolean', required=True, default=False),
    Field('content', 'text', readable=False, writable=False),
    )
    
db.listings.id.readable = False
