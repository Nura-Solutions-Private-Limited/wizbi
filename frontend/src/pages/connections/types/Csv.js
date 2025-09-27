import React, { useEffect, useRef, useState, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import {
  addConnection,
  fetchFiles,
  fetchLocalFiles,
  updateConnection,
} from "../../../api/connection";
import { Toast } from "primereact/toast";
import { Button } from "primereact/button";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import _databaseTypes from "../../../assets/data/databaseType.json";
import { VirtualScroller } from "primereact/virtualscroller";
import debounce from "lodash.debounce";

import { validateKeyValueIgnoreCase as validateKeyValue } from "../../../utilities/validateKeyValueIgnoreCase";
import { useSearchParams } from "react-router-dom";
import { Checkbox } from "primereact/checkbox";
import classNames from "classnames";
import { resetConnectionDetails } from "../utilities";
import { createSearchParams, useNavigate } from "react-router-dom";  


const validateKeyValueIgnoreCase = (props, propertyName, value) => {
  if (typeof props === "object" && Object.keys(props).length) {
    return validateKeyValue(props, propertyName, value);
  }
  return props.toLowerCase() === value.toLowerCase();
};

const CSV = React.forwardRef(({ toast, callback, connectionDetails }, ref) => {

  const navigate = useNavigate();
  const childRef = useRef(null);
  //   const toast = useRef(null);
  const dispatch = useDispatch();
  const [isAddSelected, setIsAddSelected] = useState(!connectionDetails?.id);
  const [submitted, setSubmitted] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const dataType = searchParams.get("connector_type");
  const [connection, setConnection] = React.useState(
    connectionDetails || {
      ...resetConnectionDetails,
      db_type: dataType,
    }
  );

  React.useEffect(() => {
    if (connectionDetails) {
      setConnection(connectionDetails);
      if (connectionDetails.id) {
        setIsAddSelected(false);
      } else {
        setIsAddSelected(true);
      }
    }
  }, [connectionDetails]);

  const [filesList, setFilesList] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const isLoading = useSelector((state) => state.loader.loaderVisibility);

  React.useImperativeHandle(ref, () => ({
    createConnection,
  }));

  const createConnection = () => {
    if (validateKeyValueIgnoreCase(dataType, "database_type", "lfs")) {
      if (!connection.lfs_path || !connection.db_conn_name) {
        return setSubmitted(true);
      }
    } else if (
      validateKeyValueIgnoreCase(dataType, "database_type", "s3") &&
      (!connection.s3_access_key_id ||
        !connection.s3_secret_access_key ||
        !connection.s3_bucket ||
        !connection.s3_bucket_region ||
        !connection.db_conn_name)
    ) {
      return setSubmitted(true);
    }

    setSubmitted(false);
    if (isAddSelected) {
      if (!selectedOptions.length) {
        return toast.current.show({
          severity: "error",
          summary: "Error",
          detail:
            "Please select at least one file from the file list or fetch files from the given path",
          life: 5000,
        });
      }
      dispatch(showLoader());
      let connectionDetails = { ...connection };
      connectionDetails = {
        ...connectionDetails,
        db_type: dataType,
        connection_ext: selectedOptions.map((conExt) => {
          return {
            file_name: conExt.file_name,
            file_description: conExt.file_type,
          };
        }),
      };
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
          toast.current.show({
            severity: "success",
            summary: "Confirmed",
            detail: "The connection has been added successfully",
            life: 3000,
          });
          setFilesList([]);
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
    } else {
      let connectionDetails = { ...connection };
      dispatch(showLoader());
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
          setFilesList([]);
          if (callback) {
            callback();
          }
        }
      });
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };
  const debouncedResults = useMemo(() => {
    return debounce(handleSearch, 600);
  }, []);

  useEffect(() => {
    return () => {
      debouncedResults.cancel();
    };
  });

  const getS3FilesList = () => {
    if (
      !connection.s3_access_key_id ||
      !connection.s3_secret_access_key ||
      !connection.s3_bucket ||
      !connection.s3_bucket_region
    ) {
      return setSubmitted(true);
    }
    setSubmitted(false);
    dispatch(showLoader());
    fetchFiles(
      {
        s3_access_key_id: connection.s3_access_key_id,
        s3_secret_access_key: connection.s3_secret_access_key,
        s3_bucket: connection.s3_bucket,
        s3_bucket_path: connection.s3_bucket_path,
        s3_bucket_region: connection.s3_bucket_region,
      },
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
          setFilesList(resp);
        }
      }
    );
  };

  const getFilesList = () => {
    if (!connection.lfs_path) {
      return setSubmitted(true);
    }
    setSubmitted(false);
    dispatch(showLoader());
    fetchLocalFiles(
      {
        lfs_path: connection.lfs_path,
        lfs_prefix: connection.lfs_prefix,
        lfs_mount_point: connection.lfs_mount_point,
      },
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
          setFilesList(resp);
        }
      }
    );
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
  return (
    <>
      <div className={`w-100`}>
        <>
          {validateKeyValueIgnoreCase(dataType, "database_type", "s3") && (
            <>
              <div className="row">
                <div className="col col-md-6">
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Connection Name"
                      className={`${
                        submitted && !connection.db_conn_name
                          ? "is-invalid"
                          : ""
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
                  {isAddSelected && (
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Secret Acess Key"
                        className={`${
                          submitted && !connection.s3_secret_access_key
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          value: connection.s3_secret_access_key,
                          onChange: (e) => {
                            setConnection({
                              ...connection,
                              s3_secret_access_key: e.target.value,
                            });
                          },
                          id: "s3_secret_access_key",
                          tabindex: 3,
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid Secret Access Key is required!
                        </div>
                      </WizBIInput>
                    </div>
                  )}
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Path/Folder"
                      // className={`${(submitted && !connection.s3_bucket_path) ? 'is-invalid' : ''}`}
                      controls={{
                        value: connection.s3_bucket_path,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            s3_bucket_path: e.target.value,
                          });
                        },
                        id: "s3_bucket_path",
                        tabindex: 5,
                      }}
                    >
                      {/* <div className='invalid-feedback'>A valid user name is required!</div> */}
                    </WizBIInput>
                  </div>
                </div>
                <div className="col col-md-6">
                  {isAddSelected && (
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Access Key ID"
                        className={`${
                          submitted && !connection.s3_access_key_id
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          value: connection.s3_access_key_id,
                          onChange: (e) => {
                            setConnection({
                              ...connection,
                              s3_access_key_id: e.target.value,
                            });
                          },
                          id: "s3_access_key_id",
                          tabindex: 1,
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid access key id is required!
                        </div>
                      </WizBIInput>
                    </div>
                  )}
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Bucket"
                      className={`${
                        submitted && !connection.s3_bucket ? "is-invalid" : ""
                      }`}
                      controls={{
                        value: connection.s3_bucket,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            s3_bucket: e.target.value,
                          });
                        },
                        id: "s3_bucket",
                        tabindex: 3,
                      }}
                    >
                      <div className="invalid-feedback">
                        A valid bucket is required!
                      </div>
                    </WizBIInput>
                  </div>
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Bucket Region"
                      className={`${
                        submitted && !connection.s3_bucket_region
                          ? "is-invalid"
                          : ""
                      }`}
                      controls={{
                        value: connection.s3_bucket_region,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            s3_bucket_region: e.target.value,
                          });
                        },
                        id: "s3_bucket_region",
                        tabindex: 5,
                      }}
                    >
                      <div className="invalid-feedback">
                        A valid bucket region is required!
                      </div>
                    </WizBIInput>
                  </div>
                </div>
              </div>
              <div className="row">
                <div className="col-md-6 col-lg-6">
                  <h6 className="mx-3 text-wizBi">CSV files list</h6>
                  <VirtualScroller
                    items={
                      !isAddSelected && !!connection.connection_ext?.length
                        ? connection.connection_ext
                        : filesList
                    }
                    itemSize={50}
                    itemTemplate={itemTemplate}
                    className="surface-border border-round"
                    style={{ height: "150px" }}
                  />
                </div>

                {isAddSelected && (
                  <div className="col-md-6 col-lg-6">
                    <Button
                      severity="info"
                      className="mx-2 bg-wizBi p-2 pull-right"
                      onClick={getS3FilesList}
                    >
                      Get Files
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}

          {validateKeyValueIgnoreCase(dataType, "database_type", "GDRIVE") && (
            <div className="row">
              <div className="col-md-12 col-lg-12">
                <div className="form-group">
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
              </div>
              <div className="col col-md-6">
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Client ID"
                    className={`${
                      submitted && !connection.gdrive_client_id
                        ? "is-invalid"
                        : ""
                    }`}
                    controls={{
                      value: connection.gdrive_client_id,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_client_id: e.target.value,
                        });
                      },
                      id: "gdrive_client_id",
                      tabindex: 1,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid client ID is required!
                    </div>
                  </WizBIInput>
                </div>
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Access Token"
                    className={`${
                      submitted && !connection.gdrive_access_token
                        ? "is-invalid"
                        : ""
                    }`}
                    controls={{
                      value: connection.gdrive_access_token,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_access_token: e.target.value,
                        });
                      },
                      id: "gdrive_access_token",
                      tabindex: 5,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid access token is required!
                    </div>
                  </WizBIInput>
                </div>
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Token URI"
                    className={`${
                      submitted && !connection.gdrive_token_uri
                        ? "is-invalid"
                        : ""
                    }`}
                    controls={{
                      value: connection.gdrive_token_uri,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_token_uri: e.target.value,
                        });
                      },
                      id: "gdrive_token_uri",
                      tabindex: 3,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid token URI is required!
                    </div>
                  </WizBIInput>
                </div>
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Folder/Path"
                    className={`${
                      submitted && !connection.gdrive_path ? "is-invalid" : ""
                    }`}
                    controls={{
                      value: connection.gdrive_path,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_path: e.target.value,
                        });
                      },
                      id: "gdrive_path",
                      tabindex: 5,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid folder/path is required!
                    </div>
                  </WizBIInput>
                </div>
              </div>
              <div className="col col-md-6">
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Client Secret"
                    className={`${
                      submitted && !connection.gdrive_client_secret
                        ? "is-invalid"
                        : ""
                    }`}
                    controls={{
                      value: connection.gdrive_client_secret,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_client_secret: e.target.value,
                        });
                      },
                      id: "gdrive_client_secret",
                      tabindex: 1,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid client secret is required!
                    </div>
                  </WizBIInput>
                </div>
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Refresh token"
                    className={`${
                      submitted && !connection.gdrive_refresh_token
                        ? "is-invalid"
                        : ""
                    }`}
                    controls={{
                      value: connection.gdrive_refresh_token,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_refresh_token: e.target.value,
                        });
                      },
                      id: "gdrive_refresh_token",
                      tabindex: 3,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid refresh token is required!
                    </div>
                  </WizBIInput>
                </div>
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Scopes"
                    className={`${
                      submitted && !connection.gdrive_scopes ? "is-invalid" : ""
                    }`}
                    controls={{
                      value: connection.gdrive_scopes,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_scopes: e.target.value,
                        });
                      },
                      id: "gdrive_scopes",
                      tabindex: 5,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid scopes region is required!
                    </div>
                  </WizBIInput>
                </div>
                <div className="form-group mb-2">
                  <WizBIInput
                    labelName="Prefix"
                    className={`${
                      submitted && !connection.gdrive_prefix ? "is-invalid" : ""
                    }`}
                    controls={{
                      value: connection.gdrive_prefix,
                      onChange: (e) => {
                        setConnection({
                          ...connection,
                          gdrive_prefix: e.target.value,
                        });
                      },
                      id: "gdrive_prefix",
                      tabindex: 5,
                    }}
                  >
                    <div className="invalid-feedback">
                      A valid prefix is required!
                    </div>
                  </WizBIInput>
                </div>
              </div>
            </div>
          )}

          {validateKeyValueIgnoreCase(dataType, "database_type", "lfs") && (
            <>
              <div className="row">
                <div className="col col-md-6">
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Connection Name"
                      className={`${
                        submitted && !connection.db_conn_name
                          ? "is-invalid"
                          : ""
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
                      labelName="Prefix"
                      //  className={`${(submitted && !connection.lfs_prefix) ? 'is-invalid' : ''}`}
                      controls={{
                        value: connection.lfs_prefix,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            lfs_prefix: e.target.value,
                          });
                        },
                        id: "lfs_prefix",
                        tabindex: 3,
                      }}
                    >
                      {/* <div className='invalid-feedback'>A valid prefix is required!</div>  */}
                    </WizBIInput>
                  </div>
                </div>
                <div className="col col-md-6">
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Path"
                      className={`${
                        submitted && !connection.lfs_path ? "is-invalid" : ""
                      }`}
                      controls={{
                        value: connection.lfs_path,
                        disabled: !isAddSelected,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            lfs_path: e.target.value,
                          });
                        },
                        id: "lfs_path",
                        tabindex: 1,
                      }}
                    >
                      <div className="invalid-feedback">
                        A valid path is required!
                      </div>
                    </WizBIInput>
                  </div>
                  <div className="form-group mb-2">
                    <WizBIInput
                      labelName="Mount Point / Drive"
                      // className={`${(submitted && !connection.lfs_mount_point) ? 'is-invalid' : ''}`}
                      controls={{
                        value: connection.lfs_mount_point,
                        onChange: (e) => {
                          setConnection({
                            ...connection,
                            lfs_mount_point: e.target.value,
                          });
                        },
                        id: "lfs_mount_point",
                        tabindex: 3,
                      }}
                    >
                      {/* <div className='invalid-feedback'>A valid Mount Point / Drive is required!</div>  */}
                    </WizBIInput>
                  </div>
                </div>
              </div>
              <div className="row">
                <div className="col-md-6 col-lg-6">
                  <h6 className="mx-3 text-wizBi">CSV files list</h6>
                  <VirtualScroller
                    items={
                      !isAddSelected && !!connection.connection_ext?.length
                        ? connection.connection_ext
                        : filesList
                    }
                    itemSize={50}
                    itemTemplate={itemTemplate}
                    className="surface-border border-round"
                    style={{ height: "150px" }}
                  />
                </div>

                {isAddSelected && (
                  <div className="col-md-6 col-lg-6">
                    <Button
                      severity="info"
                      className="mx-2 bg-wizBi p-2 pull-right"
                      onClick={getFilesList}
                    >
                      Get Local Files
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}
        </>
      </div>
      <Toast ref={toast} />
    </>
  );
});

export default CSV;
