#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------
# change wordpress posts example
# ----------

db_url = 'mysql://weikanadmin:sniper@localhost:3306/weikan?charset=utf8'

file_name = '%(ID)s.%(post_name)s'
file_content = '%(post_content)s'
file_extension = 'txt'

sql_extract = '''
SELECT ID, post_name, post_content
FROM wk_posts
WHERE post_type in ("post", "page") AND post_name != ""
ORDER BY ID;
'''

sql_update = '''
UPDATE wk_posts SET post_content = :file_content
WHERE ID = :ID;
'''

