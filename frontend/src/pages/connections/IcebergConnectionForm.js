import React from "react";
import FormGroup from "./FormGroup";
import ConnectionField from "./ConnectionField";
import { VirtualScroller } from "primereact/virtualscroller";
import { useSearchParams } from "react-router-dom";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import classNames from "classnames";

import {
  addConnection,
  testConnection,
  updateConnection,
  v1Connection,
} from "../../api/connection";
import { Checkbox } from "primereact/checkbox";
import { resetConnectionDetails } from "./utilities";
import { createSearchParams, useNavigate } from "react-router-dom";  

const IcebergConnectionForm =
  // = ({
  //   itemTemplate,
  //   connection,
  //   setConnection,
  //   submitted,
  //   isAddSelected,
  //   filesList,
  //   connectionLoading,
  //   connectionTesting,
  //   metaLocationPath,
  // }) => (

  React.forwardRef(({ toast, callback, connectionDetails }, ref) => {
    const isAddSelected = !connectionDetails?.id;

    const navigate = useNavigate();
    const [connectionLoading, setConnectionLoading] = React.useState(false);
    const [connectionStatus, setConnectionStatus] = React.useState(null);
    const [selectedOptions, setSelectedOptions] = React.useState([]);
    const [filesList, setFilesList] = React.useState([]);
    const [searchParams, setSearchParams] = useSearchParams();
    const [metaLocationPath, setMetaLocationPath] = React.useState("");
    const db_type = searchParams.get("connector_type").toLowerCase();
    const [connection, setConnection] = React.useState(
      connectionDetails || {
        ...resetConnectionDetails,
        db_type,
      }
    );
    React.useEffect(() => {
      if (connectionDetails) {
        setConnection(connectionDetails);
      }
    }, [connectionDetails]);
    const [submitted, setSubmitted] = React.useState(false);
    const dispatch = useDispatch();
    const connectionTesting = (id, v1Connect = false, payload) => {
      setConnectionLoading(true);
      if (v1Connect) {
        v1Connection(payload, (resp) => {
          setConnectionLoading(false);
          if (!!resp && (!!resp.detail || !!resp.message)) {
            setConnectionStatus(false);
          } else {
            setConnectionStatus(true);
            // setMetaLocationPath(resp?.metadata_location || "");
          }
        });
      } else {
        testConnection(id, (resp) => {
          setConnectionLoading(false);
          if (!!resp && (!!resp.detail || !!resp.message)) {
            setConnectionStatus(false);
          } else {
            setConnectionStatus(true);
          }
        });
      }
    };

    const itemTemplate = (item, options) => {
      const className = classNames("flex align-items-center p-2", {
        "surface-hover": options.odd,
      });

      return (
        <div
          className={className}
          style={{ height: options.props.itemSize + "px" }}
        >
          <div key={item} className="d-flex align-items-center">
            {isAddSelected ? (
              <Checkbox
                inputId={item.file_name}
                name="item"
                value={item}
                onChange={onCheckBoxSelection}
                checked={selectedOptions.some(
                  (category) => item.file_name === category.file_name
                )}
              />
            ) : (
              <span
                className="db-icon csv-db"
                style={{ width: "30px", height: "30px" }}
              ></span>
            )}

            <label htmlFor={item.file_name} className="mx-2">
              {item.file_name}
            </label>
          </div>
        </div>
      );
    };

    const onCheckBoxSelection = (e) => {
      let _selectedOptions = [...selectedOptions];

      if (e.checked) _selectedOptions.push(e.value);
      else _selectedOptions = _selectedOptions.filter((val) => val !== e.value);

      setSelectedOptions(_selectedOptions);
    };

    React.useImperativeHandle(ref, () => ({
      createConnection,
    }));

    const createConnection = () => {
      if (
        !connection.s3_access_key_id ||
        !connection.s3_secret_access_key ||
        !connection.s3_bucket ||
        !connection.s3_bucket_region ||
        !connection.db_conn_name ||
        !connection.iceberg_table ||
        !connection.iceberg_database
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
        <div className="row">
          <FormGroup>
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
            {isAddSelected && (
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
                tabIndex={3}
              >
                <div className="invalid-feedback">
                  A valid Secret Access Key is required!
                </div>
              </ConnectionField>
            )}
            <ConnectionField
              labelName="Bucket Path"
              value={connection.s3_bucket_path}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  s3_bucket_path: e.target.value,
                });
              }}
              id="s3_bucket_path"
              submitted={submitted}
              isInvalid={false}
              tabIndex={5}
            />
            <ConnectionField
              labelName="Database Name"
              value={connection.iceberg_database}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  iceberg_database: e.target.value,
                });
              }}
              id="iceberg_database"
              submitted={submitted}
              isInvalid={submitted && !connection.iceberg_database}
              tabIndex={1}
            >
              <div className="invalid-feedback">
                A valid Database name is required!
              </div>
            </ConnectionField>
          </FormGroup>
          <FormGroup>
            {isAddSelected && (
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
                tabIndex={1}
              >
                <div className="invalid-feedback">
                  A valid access key id is required!
                </div>
              </ConnectionField>
            )}
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
              tabIndex={3}
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
              tabIndex={5}
            >
              <div className="invalid-feedback">
                A valid bucket region is required!
              </div>
            </ConnectionField>
            <ConnectionField
              labelName="Table Name"
              value={connection.iceberg_table}
              onChange={(e) => {
                setConnection({
                  ...connection,
                  iceberg_table: e.target.value,
                });
              }}
              id="iceberg_table"
              submitted={submitted}
              isInvalid={submitted && !connection.iceberg_table}
              tabIndex={1}
            >
              <div className="invalid-feedback">
                A valid table name is required!
              </div>
            </ConnectionField>
          </FormGroup>
        </div>

        {metaLocationPath && (
          <div style={{ marginBottom: "15px" }}>
            Meta Location Path : {metaLocationPath}
          </div>
        )}
        <div className="row">
          <div className="col">
            <button
              className="p-button p-component mx-2 bg-wizBi p-2 pull-right"
              disabled={
                connectionLoading ||
                !connection.s3_access_key_id ||
                !connection.s3_secret_access_key ||
                !connection.s3_bucket ||
                !connection.s3_bucket_region
              }
              onClick={() => {
                connectionTesting(connection.id, true, {
                  aws_access_key: connection.s3_access_key_id,
                  aws_secret_key: connection.s3_secret_access_key,
                  s3_bucket: connection.s3_bucket,
                  s3_bucket_path: connection.s3_bucket_path,
                  s3_region: connection.s3_bucket_region,
                  iceberg_table: connection.iceberg_table,
                  iceberg_database: connection.iceberg_database,
                });
              }}
            >
              {connectionLoading && (
                <span
                  className="spinner-border spinner-border-sm mx-2"
                  role="status"
                  aria-hidden="true"
                ></span>
              )}
              Test Connection
            </button>
          </div>
          {isAddSelected && !!filesList.length && (
            <div className="col-md-7 col-lg-7">
              <h6 className="mx-3 text-wizBi">CSV files list</h6>
              <VirtualScroller
                items={filesList}
                itemSize={50}
                itemTemplate={itemTemplate}
                className="surface-border border-round"
                style={{ height: "150px" }}
              />
            </div>
          )}
          {!isAddSelected && !!connection.connection_ext?.length && (
            <div className="col-md-5 col-lg-5">
              <h6 className="mx-3 text-wizBi">CSV files list</h6>
              <VirtualScroller
                items={connection.connection_ext}
                itemSize={50}
                itemTemplate={itemTemplate}
                className="surface-border border-round"
                style={{ height: "150px" }}
              />
            </div>
          )}
        </div>
      </>
    );
  });

export default IcebergConnectionForm;
