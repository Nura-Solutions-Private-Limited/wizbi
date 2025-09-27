create database rebiz_test;

use rebiz_test;

CREATE TABLE user_group (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  description VARCHAR(255)
);
ALTER TABLE user_group AUTO_INCREMENT=1000;

CREATE TABLE user (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255),
  email VARCHAR(255),
  type ENUM('user', 'admin'),
  group_id INT,
  password VARCHAR(255),
  CONSTRAINT fk_user_group FOREIGN KEY (group_id) REFERENCES user_group(id),
  CONSTRAINT username_unique UNIQUE (username)
);
ALTER TABLE user AUTO_INCREMENT=1000;

CREATE TABLE pipeline (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  name VARCHAR(255),
  description VARCHAR(255),
  airflow_pipeline_name VARCHAR(255),
  airflow_pipeline_link VARCHAR(255),
  status VARCHAR(255),
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user(id)
);
ALTER TABLE pipeline AUTO_INCREMENT=1000;

CREATE TABLE db_conn (
  id INT PRIMARY KEY AUTO_INCREMENT,
  pipeline_id INT,
  user_id INT,
  db_conn_name VARCHAR(255),
  db_conn_type VARCHAR(255),
  db_host VARCHAR(255),
  db_username VARCHAR(255),
  db_password VARCHAR(255),
  destination_dw VARCHAR(255),
  CONSTRAINT fk_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id),
  CONSTRAINT fk_conn_user FOREIGN KEY (user_id) REFERENCES user(id)
);
ALTER TABLE db_conn AUTO_INCREMENT=1000;

CREATE TABLE source_db_mapping (
  id INT PRIMARY KEY AUTO_INCREMENT,
  db_conn_id INT,
  table_column VARCHAR(255),
  is_attr BOOLEAN,
  is_measure BOOLEAN,
  is_attr_direct BOOLEAN,
  attr_lookup_table VARCHAR(255),
  attr_lookup_column VARCHAR(255),
  time_lookup_table VARCHAR(255),
  time_lookup_key VARCHAR(255),
  time_column VARCHAR(255),
  measure_constant_value VARCHAR(255),
  CONSTRAINT fk_conn FOREIGN KEY (db_conn_id) REFERENCES db_conn(id)
);
ALTER TABLE source_db_mapping AUTO_INCREMENT=1000;

CREATE TABLE db_er (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  db_conn_id INT,
  source_er_image BLOB,
  destination_dw_image BLOB,
  CONSTRAINT fk_er_user FOREIGN KEY (user_id) REFERENCES user(id),
  CONSTRAINT fk_er_conn FOREIGN KEY (db_conn_id) REFERENCES db_conn(id)
);
ALTER TABLE db_er AUTO_INCREMENT=1000;

