CREATE TABLE user_group (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  description TEXT
);


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  email TEXT,
  type TEXT,
  group_id INTEGER,
  password TEXT,
  CONSTRAINT fk_user_group FOREIGN KEY (group_id) REFERENCES user_group(id),
  CONSTRAINT username_unique UNIQUE (username)
);


CREATE TABLE pipeline (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  name TEXT,
  description TEXT,
  airflow_pipeline_name TEXT,
  airflow_pipeline_link TEXT,
  status TEXT,
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE db_conn (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pipeline_id INTEGER,
  user_id INTEGER,
  db_conn_name TEXT,
  db_conn_type TEXT,
  db_host TEXT,
  db_username TEXT,
  db_password TEXT,
  destination_dw TEXT,
  CONSTRAINT fk_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id),
  CONSTRAINT fk_conn_user FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE source_db_mapping (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  db_conn_id INTEGER,
  table_column TEXT,
  is_attr BOOLEAN,
  is_measure BOOLEAN,
  is_attr_direct BOOLEAN,
  attr_lookup_table TEXT,
  attr_lookup_column TEXT,
  time_lookup_table TEXT,
  time_lookup_key TEXT,
  time_column TEXT,
  measure_constant_value TEXT,
  CONSTRAINT fk_conn FOREIGN KEY (db_conn_id) REFERENCES db_conn(id)
);


CREATE TABLE db_er (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  db_conn_id INTEGER,
  source_er_image BLOB,
  destination_dw_image BLOB,
  CONSTRAINT fk_er_user FOREIGN KEY (user_id) REFERENCES user(id),
  CONSTRAINT fk_er_conn FOREIGN KEY (db_conn_id) REFERENCES db_conn(id)
);

