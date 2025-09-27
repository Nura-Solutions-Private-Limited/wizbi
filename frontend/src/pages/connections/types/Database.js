import React from "react";
import { Password } from "primereact/password";
import DatabaseIcon from "../../../components/Icons/Global/DatabaseIcon";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import WizBIDropDown from "../../../core/WizBIDropDown/WizBIDropDown";
import {
  addConnection,
  testConnection,
  updateConnection,
  v1Connection,
} from "../../../api/connection";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import { useSearchParams } from "react-router-dom";
import { resetConnectionDetails } from "../utilities";

import { createSearchParams, useNavigate } from "react-router-dom";

export const Database = React.forwardRef(
  ({ toast, callback, connectionDetails }, ref) => {
    const navigate = useNavigate();
    const [connectionLoading, setConnectionLoading] = React.useState(false);
    const [connectionStatus, setConnectionStatus] = React.useState(null);

    const [searchParams, setSearchParams] = useSearchParams();
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

    React.useImperativeHandle(ref, () => ({
      createConnection,
    }));

    const createConnection = () => {
      if (
        !connection.db_conn_name ||
        !connection.db_name ||
        !connection.db_type ||
        !connection.db_host ||
        !connection.db_username ||
        !connection.db_password ||
        !connection.db_port
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
        if (callback) {
          callback();
        }
        navigate({
          pathname: `/app/connections/${resp.id}`,
          search: `?${createSearchParams({
            connector_type: resp.db_type,
          })}`,
        });
      }
      });
    };

    return (
      <div className="row">
        <div className="col col-md-6">
          <div className="form-group mb-2">
            <WizBIInput
              labelName="Connection Name"
              className={`${
                submitted && !connection.db_conn_name ? "is-invalid" : ""
              }`}
              controls={{
                value: connection.db_conn_name,
                onChange: (e) => {
                  setConnection({
                    ...connection,
                    db_conn_name: e.target.value,
                  });
                },
                id: "db_conn_name",
                tabindex: 1,
              }}
            >
              <div className="invalid-feedback">
                A valid connection name is required!
              </div>
            </WizBIInput>
          </div>
          <div className="form-group mb-2">
            <WizBIInput
              labelName="Database Name"
              className={`${
                submitted && !connection.db_name ? "is-invalid" : ""
              }`}
              controls={{
                value: connection.db_name,
                onChange: (e) => {
                  setConnection({
                    ...connection,
                    db_name: e.target.value,
                  });
                },
                id: "db_conn_name",
                tabindex: 3,
              }}
            >
              <div className="invalid-feedback">
                A valid database name is required!
              </div>
            </WizBIInput>
          </div>
          <div className="form-group mb-2">
            <WizBIInput
              labelName="Database User"
              className={`${
                submitted && !connection.db_username ? "is-invalid" : ""
              }`}
              controls={{
                value: connection.db_username,
                onChange: (e) => {
                  setConnection({
                    ...connection,
                    db_username: e.target.value,
                  });
                },
                id: "db_username",
                tabindex: 5,
              }}
            >
              <div className="invalid-feedback">
                A valid user name is required!
              </div>
            </WizBIInput>
          </div>

          <div className="form-group mb-2">
            <WizBIInput
              labelName="Database Port"
              className={`${
                submitted && !connection.db_port ? "is-invalid" : ""
              }`}
              controls={{
                value: connection.db_port,
                onChange: (e) => {
                  setConnection({
                    ...connection,
                    db_port: e.target.value,
                  });
                },
                id: "db_port",
                type: "number",
                tabindex: 6,
              }}
            >
              <div className="invalid-feedback">A valid port is required!</div>
            </WizBIInput>
          </div>
        </div>
        <div className="col col-md-6">
          <div className="form-group mb-2">
            <WizBIInput
              labelName="Database Host"
              className={`${
                submitted && !connection.db_host ? "is-invalid" : ""
              }`}
              controls={{
                value: connection.db_host,
                onChange: (e) => {
                  setConnection({
                    ...connection,
                    db_host: e.target.value,
                  });
                },
                id: "db_host",
                tabindex: 2,
              }}
            >
              <div className="invalid-feedback">
                A valid database host is required!
              </div>
            </WizBIInput>
          </div>
          <div className="form-group mb-2">
            <WizBIDropDown labelName="Database Password">
              <Password
                autocomplete="off"
                value={connection.db_password}
                style={{ height: "35px" }}
                onChange={(e) => {
                  setConnection({
                    ...connection,
                    db_password: e.target.value,
                  });
                }}
                toggleMask
                className="p-0 m-0 w-100 form-control d-flex active align-items-center"
                inputClassName="form-control w-100 border-0 text-black"
                panelClassName="w-100"
                feedback={false}
                tabIndex={4}
              />
            </WizBIDropDown>
          </div>
        </div>

        <>
          <div className="col col-md-8">
            {connectionStatus === true && (
              <div className="alert alert-success">
                <strong>Success!</strong> Connection Passed
              </div>
            )}

            {connectionStatus === false && (
              <div className="alert alert-danger">
                <strong>Failed!</strong> Connection Failed! please check
                database connection properties
              </div>
            )}
          </div>
          <div className="col col-md-4">
            <button
              className="p-button p-component mx-2 bg-wizBi p-2 pull-right"
              disabled={!connection.id || connectionLoading}
              onClick={() => {
                connectionTesting(connection.id);
              }}
              tabIndex={7}
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
        </>
      </div>
    );
  }
);
