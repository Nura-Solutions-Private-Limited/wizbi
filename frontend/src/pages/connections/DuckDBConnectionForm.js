import React from "react";
import { addConnection, updateConnection } from "../../api/connection";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import { useSearchParams } from "react-router-dom";
import { RadioButton } from "primereact/radiobutton";
import ConnectionField from "./ConnectionField";
import s from "./Connections.module.scss";
import { resetConnectionDetails } from "./utilities";
import { createSearchParams, useNavigate } from "react-router-dom"; 

const DuckDBConnectionForm = React.forwardRef(
  ({ toast, callback, connectionDetails }, ref) => {
     const navigate = useNavigate();
    const [duckDBRadio, setDuckDBRadio] = React.useState("s3");
    const isAddSelected = !connectionDetails?.id;
    const [searchParams, setSearchParams] = useSearchParams();
    const db_type = searchParams.get("connector_type").toLowerCase();
    const [connection, setConnection] = React.useState(
      connectionDetails || {
        ...resetConnectionDetails,
        db_type
      }
    );
    React.useEffect(() => {
      if (connectionDetails) {
        setConnection(connectionDetails);
      }
    }, [connectionDetails]);

    const [submitted, setSubmitted] = React.useState(false);
    const dispatch = useDispatch();
    React.useImperativeHandle(ref, () => ({
      createConnection,
    }));

    const createConnection = () => {
      if (
        duckDBRadio === "s3" &&
        (!connection.duckdb_database ||
          !connection.db_conn_name ||
          !connection.s3_access_key_id ||
          !connection.s3_secret_access_key ||
          !connection.s3_bucket ||
          !connection.s3_bucket_path ||
          !connection.s3_bucket_region ||
          !connection.duckdb_database ||
          !connection.duckdb_lfs_path ||
          !connection.dbt_project_name)
      ) {
        return setSubmitted(true);
      } else if (
        !connection.db_conn_name ||
        !connection.duckdb_database ||
        !connection.dbt_project_name ||
        !connection.duckdb_lfs_path
      ) {
        return setSubmitted(true);
      }
      dispatch(showLoader());

      if (connectionDetails?.id) {
        return updateConnection(
          { id: connectionDetails?.id, ...connection },
          (resp) => {
            dispatch(hideLoader());
            if (!!resp && (!!resp.detail || !!resp.message)) {
              toast.current.show({
                severity: "error",
                summary: "Error",
                detail: resp.detail || resp.message,
                life: 3000,
              });
            } else {
              toast.current.show({
                severity: "success",
                summary: "Confirmed",
                detail: "The connection has been updated successfully",
                life: 3000,
              });
            }
          }
        );
      }
      addConnection(connection, (resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          toast.current.show({
            severity: "success",
            summary: "Confirmed",
            detail: "The connection has been added successfully",
            life: 3000,
          });
          navigate({
            pathname: `/app/connections/${resp.id}`,
            search: `?${createSearchParams({
              connector_type: resp.db_type,
            })}`,
          });
        }
        if (callback) {
          callback();
        }
      });
    };
    return (
      <>
        <ConnectionField
          labelName="Connection Name"
          value={connection.db_conn_name}
          onChange={(e) => {
            setConnection({
              ...connection,
              db_conn_name: e.target.value,
            });
          }}
          id="db_conn_name"
          submitted={submitted}
          isInvalid={submitted && !connection.db_conn_name}
          tabIndex={1}
        >
          <div className="invalid-feedback">
            A valid connection name is required!
          </div>
        </ConnectionField>

        <div className={s.dbheading}>Duck DB</div>
        <ConnectionField
          labelName="Duck DB Database Name"
          value={connection.duckdb_database}
          onChange={(e) => {
            setConnection({
              ...connection,
              duckdb_database: e.target.value,
            });
          }}
          id="duckdb_database"
          submitted={submitted}
          isInvalid={submitted && !connection.duckdb_database}
          tabIndex={2}
        >
          <div className="invalid-feedback">
            A valid database name is required!
          </div>
        </ConnectionField>

        <div className="d-flex">
          <div className="col-md-6 col-lg-6">
            <RadioButton
              inputId="s3"
              name="radio"
              value="s3"
              onChange={(e) => setDuckDBRadio(e.value)}
              checked={duckDBRadio === "s3"}
            />
            <label htmlFor="s3" className={s.radiolabel}>
              Place DuckDB Database on S3
            </label>
          </div>
          <div className={`col-md-6 col-lg-6 ${s.ml_20}`}>
            <RadioButton
              inputId="local"
              name="radio"
              value="local"
              onChange={(e) => setDuckDBRadio(e.value)}
              checked={duckDBRadio === "local"}
            />
            <label htmlFor="local" className={s.radiolabel}>
              Place DuckDB Database on Local Wizbi Server
            </label>
          </div>
        </div>

        {duckDBRadio === "s3" && isAddSelected && (
          <div className="row d-flex">
            <ConnectionField
              labelName="Access Key ID"
              value={connection.s3_access_key_id}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  s3_access_key_id: e.target.value,
                });
              }}
              id="s3_access_key_id"
              submitted={submitted}
              isInvalid={submitted && !connection.s3_access_key_id}
              tabIndex={3}
              className="col-md-6"
              panelClass="my-2"
            >
              <div className="invalid-feedback">
                A valid access key id is required!
              </div>
            </ConnectionField>
            <ConnectionField
              labelName="Secret Access Key"
              value={connection.s3_secret_access_key}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  s3_secret_access_key: e.target.value,
                });
              }}
              id="s3_secret_access_key"
              submitted={submitted}
              isInvalid={submitted && !connection.s3_secret_access_key}
              tabIndex={4}
              className="col-md-6"
              panelClass="my-2"
            >
              <div className="invalid-feedback">
                A valid secret access key is required!
              </div>
            </ConnectionField>
            <ConnectionField
              labelName="Bucket"
              value={connection.s3_bucket}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  s3_bucket: e.target.value,
                });
              }}
              id="s3_bucket"
              submitted={submitted}
              isInvalid={submitted && !connection.s3_bucket}
              tabIndex={5}
              className="col-md-6"
              panelClass="my-2"
            >
              <div className="invalid-feedback">
                A valid bucket is required!
              </div>
            </ConnectionField>
            <ConnectionField
              labelName="Bucket Region"
              value={connection.s3_bucket_region}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  s3_bucket_region: e.target.value,
                });
              }}
              id="s3_bucket_region"
              submitted={submitted}
              isInvalid={submitted && !connection.s3_bucket_region}
              tabIndex={6}
              className="col-md-6"
              panelClass="my-2"
            >
              <div className="invalid-feedback">
                A valid bucket region is required!
              </div>
            </ConnectionField>
          </div>
        )}

        <ConnectionField
          labelName="Path/Folder"
          value={connection.duckdb_lfs_path}
          onChange={(e) => {
            setConnection({
              ...connection,
              duckdb_lfs_path: e.target.value,
            });
          }}
          id="duckdb_lfs_path"
          submitted={submitted}
          isInvalid={false}
          tabIndex={7}
          className="col-md-6"
          panelClass="my-2"
        />

        <hr />

        <div className={s.dbheading}>DBT</div>
        <ConnectionField
          labelName="DBT Project Name"
          value={connection.dbt_project_name}
          onChange={(e) => {
            setConnection({
              ...connection,
              dbt_project_name: e.target.value,
            });
          }}
          id="dbt_project_name"
          submitted={submitted}
          isInvalid={submitted && !connection.dbt_project_name}
          tabIndex={8}
        >
          <div className="invalid-feedback">
            A valid DBT Project Name name is required!
          </div>
        </ConnectionField>
      </>
    );
  }
);

export default DuckDBConnectionForm;
