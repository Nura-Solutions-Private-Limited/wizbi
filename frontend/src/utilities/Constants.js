export const BASE = "/rebiz/v1";
export const LOGIN = BASE + "/login";
export const REGISTER = BASE + "/register";

export const FETCH_CONNECTIONS = BASE + "/connections";
export const DELETE_CONNECTION = BASE + "/connection";
export const ADD_CONNECTION = BASE + "/connection";
export const UPDATE_CONNECTION = BASE + "/connection";
export const TEST_CONNECTION = BASE + "/databases";
export const V1_CONNECTION = BASE + "/connection";
export const ICEBERG_CONNECTION_VALIDATE = BASE + "/validate-iceberg-table";

export const FETCH_PIPELINES = BASE + "/pipelines";
export const DELETE_PIPELINE = BASE + "/pipeline";
export const CREATE_PIPELINE = BASE + "/pipeline";
export const PIPELINE_TYPE = BASE + "/pipelinetype";

export const GET_META_DATA = BASE + "/metadata";
export const GEN_DW_FROM_SOURCE = BASE + "/gen-dw-from-source";
export const FETCH_ER_DIAGRAM = BASE + "/erdiagram";

export const FETCH_ER_SOURCE_DIAGRAM = BASE + "/source-erdiagram";
export const FETCH_ER_DEST_DIAGRAM = BASE + "/dest-erdiagram";

export const FETCH_ER_SOURCE_DIAGRAM_DATA = BASE + "/source-diagram-json";
export const FETCH_ER_DEST_DIAGRAM_DATA = BASE + "/dest-diagram-json";

export const SAVE_METADATA = BASE + "/metadata";
export const RUN_PIPELINE = BASE + "/run-pipeline";
export const SETUP_DATALAKE = BASE + "/setup-dbt-project";
export const RUN_ETL = BASE + "/run-etl";

export const FETCH_REPORTS = BASE + "/reports";
export const SHOW_REPORT = BASE + "/showreport";
export const CREATE_REPORTS = BASE + "/reports/{pipeline_id}";

export const FETCH_AUDITS = BASE + "/audits";

export const FETCH_PAGINATED_AUDITS = BASE + "/audits-paginated";

export const FETCH_PAGINATED_JOBS = BASE + "/jobs-paginated";

export const FETCH_JOBS = BASE + "/jobs";
export const CREATE_SCHEDULE = BASE + "/schedule";

export const GET_SCHEDULES_BY_ID = BASE + "/schedules";

export const UPDATE_SCHEDULE_BY_ID = BASE + "/schedules";

export const FETCH_DATATYPES = BASE + "/datatypes";

export const FETCH_DATABASE_DATATYPES = BASE + "/database-datatypes";

export const FETCH_DATE_FORMAT_TYPES = BASE + "/dateformat";

export const FETCH_FILE_PREVIEW = BASE + "/filepreview";

export const FETCH_ICEBERG_FILE_PREVIEW = BASE + "/iceberg-table-preview";

export const FETCH_FILES = BASE + "/s3files";

export const S3_DATA_LOAD = BASE + "/s3dataload";

export const FETCH_LOCAL_FILES = BASE + "/localfiles";

export const FETCH_DIMENSIONS = BASE + "/dimensions";

export const FETCH_DIMENSION_METRICS = BASE + "/metrics";

export const LOCAL_DATA_LOAD = BASE + "/localdataload";

export const FETCH_DASHBOARDS = BASE + "/dashboard";
export const DELETE_DASHBOARD = BASE + "/dashboard";
export const ADD_DASHBOARD = BASE + "/dashboard";
export const UPDATE_DASHBOARD = BASE + "/dashboard";
export const ACTIVE_DASHBOARD = BASE + "/activedashboard";

// Admin - GROUPS

export const FETCH_GROUPS = BASE + "/groups";
export const ADD_GROUP = BASE + "/group";
export const DELETE_GROUP = BASE + "/group";
export const UPDATE_GROUP = BASE + "/group";

// Admin - ROles

export const FETCH_ROLES = BASE + "/roles";
export const DELETE_ROLE = BASE + "/role";
export const ADD_ROLE = BASE + "/role";
export const UPDATE_ROLE = BASE + "/role";

// Admin Permissions

export const FETCH_PERMISSIONS = BASE + "/permissions";
export const DELETE_PERMISSION = BASE + "/permission";
export const ADD_PERMISSION = BASE + "/permission";
export const UPDATE_PERMISSION = BASE + "/permission";

export const FETCH_USERS = BASE + "/users";

// Gen AI
export const GENAI_FACT_QUESTION = BASE + "/factquestion";
export const GENAI_OTHER_QUESTION = BASE + "/otherquestion";
export const GENAI_FOLLOWUP_QUESTION = BASE + "/followup-question";
export const CONNECTION_QUESTION = BASE + "/connection/question";

export const GENAI_DASHBOARD_FACT_QUESTION = BASE + "/gen-dashboard";
export const GENAI_DASHBOARD_OTHER_QUESTION = BASE + "/otherquestion";

// databasetype

export const DATABASE_TYPES = BASE + "/connection/connector-type";

export const CONNECTION_REST_API = BASE + "/connection/restapi/validate";

export const REST_API_CONNECTION = BASE + "/connection/restapi";


export const VALIDATE_TWITTER_API = BASE + "/connection/x/validate";

export const TWITTER_API_CONNECTION = BASE + "/connection/x";

export const FETCH_NOTIFICATIONS = BASE + '/notifications';