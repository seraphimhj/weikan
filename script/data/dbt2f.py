#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------
# dbt2f stand for "database text to file", a simple script to extract database
# text content to files for maintain.
# ----------

import os
import re
import sys
import json
from argparse import ArgumentParser
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text as SQL

CONFIG_TEMPLATE = """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------
# change wordpress posts example
# ----------

db_url = 'mysql://username:password@host:port/database_name?charset=utf8'

file_name = '%(ID)s.%(post_name)s'
file_content = '%(post_content)s'
file_extension = 'txt'

sql_extract = '''
SELECT ID, post_name, post_content
FROM wp_posts
WHERE post_type in ("post", "page") AND post_name != ""
ORDER BY ID;
'''

sql_update = '''
UPDATE wp_posts SET post_content = :file_content
WHERE ID = :ID;
'''

"""

def output_metadata(fields, values):
    filename = 'metadata.json'
    metadata = [fields, values]
    text = json.dumps(metadata)

    # petty look format
    text = text.replace('], ', '], \n')
    text = text.replace('[[', '[\n[')
    text = text.replace(']]]', ']\n]\n]')

    with open(filename, 'w') as outfile:
        outfile.write(text)

def do_config():
    filename = 'config.py'
    if os.path.exists(filename):
        print "there a config.py in current folder, please delete first."
        return

    with open(filename, 'w') as outfile:
        outfile.write(CONFIG_TEMPLATE)
    print "config template 'config.py' has been created."

def do_extract(config):
    db = create_engine(config.db_url).connect()
    rows = db.execute(config.sql_extract);

    # don't write the field value in config.file_content in metadata
    string_holders = re.findall(
        r'%\([0-9a-zA-Z_]+\)s', config.file_content)
    ignore_fields = [e[2:-2] for e in string_holders] # remove "%s(" & ")s"
    keep_fields = [e for e in rows.keys() if e not in ignore_fields]

    metadata_fields = ['rowid', 'filename', 'mtime'] + keep_fields
    metadata_values = []

    for rowid, row in enumerate(rows):
        filename = '%s.%s' % (
                config.file_name % row,
                config.file_extension)

        if os.path.exists(filename):
            print 'skip: %s' % filename
        else:
            print 'create: %s' % filename
            with open(filename, 'w') as outfile:
                file_content = config.file_content % row
                outfile.write(file_content.encode('utf-8'))

        mtime = os.path.getmtime(filename)
        values = [rowid, filename, mtime]
        values.extend([row[field] for field in keep_fields])
        metadata_values.append(values)

    output_metadata(metadata_fields, metadata_values)

def do_update(config):
    metadata = json.loads(open('metadata.json').read())
    metadata_fields, metadata_values = metadata

    db = create_engine(config.db_url).connect()
    for metadata_value in metadata_values:
        kwargs = dict(zip(metadata_fields, metadata_value))
        filename = kwargs['filename']

        if not os.path.exists(filename):
            continue
        if os.path.getmtime(filename) == kwargs['mtime']:
            continue

        kwargs['file_content'] = open(filename).read()
        print 'update %s' % filename
        sql = SQL(config.sql_update)
        db.execute(sql, kwargs)
        metadata_value[2] = os.path.getmtime(filename)

    output_metadata(metadata_fields, metadata_values)


def get_commandline_arguments():
    parser = ArgumentParser(
        description='database text to file, ' +
                    'extract database text content to files for maintain')
    subparsers = parser.add_subparsers(
        dest='command', title='avaiable commands')
    subparsers.add_parser(
        'config', help="output the config template 'config.py'")
    subparsers.add_parser(
        'extract', help='extract database content to files')
    subparsers.add_parser(
        'update', help='update database content from files')
    return parser

def main():
    args = get_commandline_arguments().parse_args()
    if args.command == 'config':
        do_config()
        return

    sys.path.insert(0, os.getcwd())
    try:
        import config
    except ImportError:
        print "error: can't find config.py"

    if args.command == 'extract':
        do_extract(config)
    elif args.command == 'update':
        do_update(config)

if __name__ == '__main__':
    main()
