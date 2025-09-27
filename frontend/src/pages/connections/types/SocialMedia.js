import React, { useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import {
  addTwitterAPIConnection,
  getTwitterAPIConnection,
  updateTwitterAPIConnection,
  validateTwitterAPI,
  addConnection,
  getConnection,
  updateConnection,
} from "../../../api/connection";
import { createPipeline } from "../../../api/pipeLine";
import { Toast } from "primereact/toast";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";


import { useSearchParams } from "react-router-dom";
import { createSearchParams, useNavigate } from "react-router-dom";
import WizBIDropDown from "../../../core/WizBIDropDown/WizBIDropDown";
import { Dropdown } from "primereact/dropdown";


const reset_connection__details = {
  db_conn_name: "",
  db_type: "",
  sub_type: "",
  user_name: "",
  bearer_token: "",
  access_token: "",
  access_token_secret: "",
  client_id: "",
  client_secret: "",
};

const SocialMedia = React.forwardRef(
  ({ toast, callback, connection_id, databaseTypes = [] }, ref) => {
    const navigate = useNavigate();

    //   const toast = useRef(null);
    const dispatch = useDispatch();
    const [isAddSelected, setIsAddSelected] = useState(connection_id);
    const [submitted, setSubmitted] = useState(false);
    const [searchParams] = useSearchParams();
    const dataType = searchParams.get("connector_type");
    const [connection, setConnection] = React.useState({
      ...reset_connection__details,
      db_type: dataType,
    });

    const authTypes = [
      {
        name: "Bearer Token",
        id: 1000,
      },
      {
        name: "Access Token",
        id: 1001,
      },
    ];

    const [isBearerToken, setIsBearerToken] = React.useState(true);

    React.useEffect(() => {
      // if (connectionDetails) {
      //   setConnection(connectionDetails);
      if (connection_id) {
        setIsAddSelected(false);
      } else {
        setIsAddSelected(true);
      }
      // }
    }, [connection_id]);



    const [connectionLoading, setConnectionLoading] = React.useState(false);

    const [connectionStatus, setConnectionStatus] = React.useState({});

    React.useImperativeHandle(ref, () => ({
      createConnection,
    }));

    React.useEffect(() => {
      console.log('useEffect triggered - connection_id:', connection_id, 'dataType:', dataType); // Debug log
      if (connection_id) {
        dispatch(showLoader());
        if (dataType === "X") {
          getTwitterAPIConnection({ id: connection_id }, (resp) => {
            dispatch(hideLoader());
            if (!!resp && (!!resp.detail || !!resp.message)) {
              toast.current.show({
                severity: "error",
                summary: "Error",
                detail: resp.detail || resp.message,
                life: 3000,
              });
            } else {
              setConnection(resp);
              // Set isBearerToken based on whether bearer_token exists and is not empty
              setIsBearerToken(!!resp?.bearer_token && resp.bearer_token.trim() !== "");
            }
          });
        } else {
          getConnection(connection_id, (resp) => {
            dispatch(hideLoader());
            console.log('Non-Twitter connection response:', resp); // Debug log
            if (!!resp && (!!resp.detail || !!resp.message)) {
              toast.current.show({
                severity: "error",
                summary: "Error",
                detail: resp.detail || resp.message,
                life: 3000,
              });
            } else {
              setConnection(resp);
              // Set isBearerToken based on whether bearer_token exists and is not empty
              setIsBearerToken(!!resp?.bearer_token && resp.bearer_token.trim() !== "");
              console.log('Connection state set:', resp); // Debug log
              console.log('isBearerToken set to:', !!resp?.bearer_token && resp.bearer_token.trim() !== ""); // Debug log
            }
          });
        }
      }
    }, [connection_id, dataType, dispatch, toast]);

    // Update connection state when dataType changes
    React.useEffect(() => {
      if (dataType && !connection_id) {
        setConnection(prev => ({
          ...prev,
          db_type: dataType,
        }));
      }
    }, [dataType, connection_id]);

    const createConnection = () => {
      // Validation for Twitter/X
      if (dataType === "X") {
        if (
          !connection.db_conn_name ||
          !connection.user_name ||
          (isBearerToken && !connection.bearer_token) ||
          (!isBearerToken &&
            (!connection.access_token || !connection.access_token_secret))
        ) {
          return setSubmitted(true);
        }
      } 
      // Validation for other social media platforms
      else {
        if (
          !connection.db_conn_name ||
          !connection.user_name ||
          (isBearerToken && !connection.bearer_token) ||
          (!isBearerToken &&
            (!connection.access_token || !connection.access_token_secret))
        ) {
          return setSubmitted(true);
        }
      }

      setSubmitted(false);
      if (isAddSelected) {
        dispatch(showLoader());
        let connectionDetails = { ...connection };
        
        if (dataType === "X") {
          // Twitter/X specific field cleanup
          if (isBearerToken) {
            connectionDetails = {
              ...connectionDetails,
              db_type: dataType,
              access_token: "",
              access_token_secret: "",
              client_id: "",
              client_secret: "",
            };
          } else {
            connectionDetails = {
              ...connectionDetails,
              db_type: dataType,
              bearer_token: "",
              client_id: "",
              client_secret: "",
            };
          }
        } else {
          // Other social media platforms field cleanup
          connectionDetails = {
            ...connectionDetails,
            db_type: dataType,
            // Clear fields based on auth type, but keep user_name and client fields
            ...(isBearerToken ? {
              access_token: "",
              access_token_secret: "",
            } : {
              bearer_token: "",
            }),
          };
        }

        if (dataType === "X") {
          addTwitterAPIConnection(connectionDetails, (resp) => {
            dispatch(hideLoader());
            if (!!resp && (!!resp.detail || !!resp.message)) {
              toast.current.show({
                severity: "error",
                summary: "Error",
                detail: resp.detail || resp.message,
                life: 3000,
              });
            } else {
              // Create pipeline after successful connection creation
              createPipelineForSocialMedia(resp, connectionDetails.db_conn_name);
            }
          });
        } else {
          addConnection(connectionDetails, (resp) => {
            dispatch(hideLoader());
            if (!!resp && (!!resp.detail || !!resp.message)) {
              toast.current.show({
                severity: "error",
                summary: "Error",
                detail: resp.detail || resp.message,
                life: 3000,
              });
            } else {
              // Create pipeline after successful connection creation
              createPipelineForSocialMedia(resp, connectionDetails.db_conn_name);
            }
          });
        }
      } else {
        let connectionDetails = { ...connection };
        
        if (dataType === "X") {
          // Twitter/X specific field cleanup
          if (isBearerToken) {
            connectionDetails = {
              ...connectionDetails,
              access_token: "",
              access_token_secret: "",
              client_id: "",
              client_secret: "",
            };
          } else {
            connectionDetails = {
              ...connectionDetails,
              bearer_token: "",
              client_id: "",
              client_secret: "",
            };
          }
        } else {
          // Other social media platforms field cleanup
          if (isBearerToken) {
            connectionDetails = {
              ...connectionDetails,
              access_token: "",
              access_token_secret: "",
            };
          } else {
            connectionDetails = {
              ...connectionDetails,
              bearer_token: "",
            };
          }
        }
        dispatch(showLoader());
        if (dataType === "X") {
          updateTwitterAPIConnection(connectionDetails, (resp) => {
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
                detail: "The connection has been updated successfully ",
                life: 3000,
              });
              if (callback) {
                callback();
              }
            }
          });
        } else {
          updateConnection(connectionDetails, (resp) => {
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
                detail: "The connection has been updated successfully ",
                life: 3000,
              });
              if (callback) {
                callback();
              }
            }
          });
        }
      }
    };

    const createPipelineForSocialMedia = (connectionResponse, connectionName) => {
      // Using the same structure and validation logic as Pipeline.js for social media pipelines (isSMA)
      // This ensures consistency with the existing pipeline creation flow
      const pipelineInfo = {
        name: connectionName, // Pipeline name same as connection name
        description: `Pipeline for ${connectionName} social media connection`,
        airflow_pipeline_name: `${connectionName}_pipeline`,
        airflow_pipeline_link: "",
        status: "design", // Default status for social media pipelines
        source_schema_name: connectionName,
        dest_schema_name: connectionName,
        db_conn_source_id: connectionResponse.id,
        db_conn_dest_id: 0, // Will be set by backend for social media pipelines
        pipeline_type: "SOCIAL_MEDIA"
      };

      // Validation logic similar to Pipeline.js isSMA check
      if (!pipelineInfo.name || !pipelineInfo.db_conn_source_id) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: "Connection created successfully but pipeline validation failed: Name and source connection are required",
          life: 3000,
        });
        if (callback) {
          callback();
        }
        navigate({
          pathname: `/app/connections/${connectionResponse.id}`,
          search: `?${createSearchParams({
            connector_type: connectionResponse.db_type,
          })}`,
        });
        return;
      }

      createPipeline(pipelineInfo, (pipelineResp) => {
        if (!!pipelineResp && (!!pipelineResp.detail || !!pipelineResp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: `Connection created successfully but pipeline creation failed: ${pipelineResp.detail || pipelineResp.message}`,
            life: 3000,
          });
        } else {
          toast.current.show({
            severity: "success",
            summary: "Confirmed",
            detail: "Connection and pipeline have been created successfully",
            life: 3000,
          });
        }
        
        if (callback) {
          callback();
        }
        
        navigate({
          pathname: `/app/connections/${connectionResponse.id}`,
          search: `?${createSearchParams({
            connector_type: connectionResponse.db_type,
          })}`,
        });
      });
    };

    const connectionTesting = (id, v1Connect = false, payload) => {
      let body = {};
      
      if (dataType === "X") {
        const { user_name, bearer_token, access_token, access_token_secret } =
          connection;
        body = {
          user_name,
          ...(isBearerToken
            ? { bearer_token }
            : { access_token, access_token_secret }),
        };
      } else {
        const { user_name, bearer_token, access_token, access_token_secret, client_id, client_secret } = connection;
        body = {
          user_name,
          ...(isBearerToken
            ? { bearer_token }
            : { access_token, access_token_secret }),
          // Client ID and Client Secret are optional for now
          ...(client_id && { client_id }),
          ...(client_secret && { client_secret }),
        };
      }

      setConnectionLoading(true);
      // For now, all social media types use the Twitter API validation
      // This may need to be updated when specific APIs are available for other platforms
      validateTwitterAPI(body, (resp) => {
        setConnectionLoading(false);
        setConnectionStatus(
          !resp.status ? { status: false, message: resp.message } : resp
        );
      });
    };

    return (
      <>
        <div className={`w-100`}>
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
              {/* Auth Type dropdown - shown for all social media platforms */}
              <div className="form-group mb-2">
                <WizBIDropDown labelName="Auth Type" panelClass="mb-2 w-100">
                  <Dropdown
                    filter
                    value={isBearerToken ? "Bearer Token" : "Access Token"}
                    style={{
                      height: "35px",
                    }}
                    className={`p-0 m-0 custom-conn-drop w-100 d-flex form-control active`}
                    options={authTypes}
                    optionLabel="name"
                    optionValue="name"
                    tabindex={2}
                    onChange={(e) => {
                      setIsBearerToken(e.value === "Bearer Token");
                    }}
                    placeholder="Select a Auth type"
                  />
                </WizBIDropDown>
              </div>

              {/* Bearer Token field - shown for all platforms when Bearer Token is selected */}
              {isBearerToken && (
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Bearer Token"
                    className={`${
                      submitted && !connection.bearer_token ? "is-invalid" : ""
                    }`}
                    controls={{
                      value: connection.bearer_token,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          bearer_token: e.target.value,
                        });
                      },
                      id: "bearer_token",
                      tabindex: 3,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid Bearer Token is required!
                    </div>
                  </WizBIInput>
                </div>
              )}

              {/* Client ID field - shown for non-Twitter platforms */}
              {dataType !== "X" && (
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Client ID (Optional)"
                    className=""
                    controls={{
                      value: connection.client_id,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          client_id: e.target.value,
                        });
                      },
                      id: "client_id",
                      tabindex: 4,
                    }}
                  />
                </div>
              )}
            </div>
            <div className="col col-md-6">
              {/* User Name field - shown for all platforms */}
              <div className="form-group mb-2">
                <WizBIInput
                  labelName="User Name"
                  className={`${
                    submitted && !connection.user_name ? "is-invalid" : ""
                  }`}
                  controls={{
                    value: connection.user_name,
                    onChange: (e) => {
                      setConnection({
                        ...connection,
                        user_name: e.target.value,
                      });
                    },
                    id: "user_name",
                    tabindex: 1,
                  }}
                >
                  <div className="invalid-feedback">
                    A valid User Name is required!
                  </div>
                </WizBIInput>
              </div>

              {/* Access Token fields - shown for all platforms when Access Token is selected */}
              {!isBearerToken && (
                <>
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Access Token Secret"
                      className={`${
                        submitted && !connection.access_token_secret
                          ? "is-invalid"
                          : ""
                      }`}
                      controls={{
                        value: connection.access_token_secret,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            access_token_secret: e.target.value,
                          });
                        },
                        id: "access_token_secret",
                        tabindex: 5,
                      }}
                    >
                      <div className="invalid-feedback">
                        A valid Access Token Secret is required!
                      </div>
                    </WizBIInput>
                  </div>
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Access Token"
                      className={`${
                        submitted && !connection.access_token
                          ? "is-invalid"
                          : ""
                      }`}
                      controls={{
                        value: connection.access_token,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            access_token: e.target.value,
                          });
                        },
                        id: "access_token",
                        tabindex: 6,
                      }}
                    >
                      <div className="invalid-feedback">
                        A valid Access Token is required!
                      </div>
                    </WizBIInput>
                  </div>
                </>
              )}

              {/* Client Secret field - shown for non-Twitter platforms */}
              {dataType !== "X" && (
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Client Secret (Optional)"
                    className=""
                    controls={{
                      value: connection.client_secret,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          client_secret: e.target.value,
                        });
                      },
                      id: "client_secret",
                      tabindex: 7,
                    }}
                  />
                </div>
              )}
            </div>
          </div>

          <div className="row">
            {/* <div className="col col-md-6"> */}
            <div className="col col-md-8">
              {connectionStatus?.status && (
                <div className="alert alert-success">
                  <strong>Success!</strong>{" "}
                  {connectionStatus?.message
                    ? connectionStatus?.message
                    : "Connection Passed"}
                </div>
              )}

              {connectionStatus?.status === false && (
                <div className="alert alert-danger">
                  <strong>Failed!</strong>{" "}
                  {connectionStatus?.message
                    ? connectionStatus?.message
                    : `Connection Failed! please check
                  database connection properties`}
                </div>
              )}
            </div>
            <div className="col col-md-4">
              <button
                className="p-button p-component mx-2 bg-wizBi p-2 pull-right"
                disabled={
                  connectionLoading ||
                  !connection.db_conn_name ||
                  (dataType === "X" ? (
                    !connection.user_name ||
                    (isBearerToken && !connection.bearer_token) ||
                    (!isBearerToken &&
                      (!connection.access_token ||
                        !connection.access_token_secret))
                  ) : (
                    !connection.user_name ||
                    (isBearerToken && !connection.bearer_token) ||
                    (!isBearerToken &&
                      (!connection.access_token ||
                        !connection.access_token_secret))
                  ))
                }
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
          </div>
        </div>
        <Toast ref={toast} />
      </>
    );
  }
);

export default SocialMedia;
