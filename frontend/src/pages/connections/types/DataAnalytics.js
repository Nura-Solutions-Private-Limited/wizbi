import React from "react";
import { ListBox } from "primereact/listbox";
import { RadioButton } from "primereact/radiobutton";
import { Checkbox } from "primereact/checkbox";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import {
  addConnection,
  fetchDimensionMetrics,
  fetchDimensions,
  updateConnection,
} from "../../../api/connection";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import { useSearchParams } from "react-router-dom";
import { resetConnectionDetails } from "../utilities";

import { createSearchParams, useNavigate } from "react-router-dom";  

export const DataAnalytics = React.forwardRef(
  ({ toast, callback, connectionDetails }, ref) => {
    const navigate = useNavigate();
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
        setConnection({
          ...connectionDetails,
          ga_auth_json: JSON.stringify(connectionDetails.ga_auth_json),
        });
      }
    }, [connectionDetails]);

    const [submitted, setSubmitted] = React.useState(false);
    const dispatch = useDispatch();
    const [filesList, setFilesList] = React.useState([]);
    const [dimensions, setDimensions] = React.useState([]);
    const [metrics, setMetrics] = React.useState([]);
    const [selectedOptions, setSelectedOptions] = React.useState([]);
    const [selectedMetrics, setSelectedMetrics] = React.useState([]);
    const [selectedDimension, setSelectedDimension] = React.useState({});

    const isAddSelected = !connection.id;

    React.useImperativeHandle(ref, () => ({
      createConnection,
    }));

    const createConnection = () => {
      if (!connection.ga_property_id || !connection.db_conn_name) {
        return setSubmitted(true);
      }
      dispatch(showLoader());

      let parsedJson;
      try {
        parsedJson = JSON.parse(connection.ga_auth_json);
      } catch (error) {
        dispatch(hideLoader());
        return toast.current.show({
          severity: "error",
          summary: "Error",
          detail: "Invalid JSON from Auth JSON:" + error,
          life: 3000,
        });
      }

      const clonedConnection = {
        ...connection,
        ga_auth_json: parsedJson,
        connection_ext: [
          {
            dimension: selectedDimension.code,
            dimension_metric: selectedMetrics.map((metric) => metric.code),
          },
        ],
      };

      if (connectionDetails?.id) {
        return updateConnection(
          { id: connectionDetails?.id, ...clonedConnection },
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
      addConnection(clonedConnection, (resp) => {
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
        }
        if (callback) {
          callback();
        }
          navigate({
                    pathname: `/app/connections/${resp.id}`,
                    search: `?${createSearchParams({
                      connector_type: resp.db_type,
                    })}`,
                  });
      });
    };

    const dimensionsTemplate = (option) => {
      const isChecked = selectedDimension
        ? selectedDimension.code === option.code
        : false;
      const handleDimensionChange = (e) => {
        e.preventDefault();
        const collection = metrics.filter((metric) => {
          return metric.dimension_id === option.code;
        });
        if (!collection.length) {
          dispatch(showLoader());
          getDimensionsMetrics(option.code, connection);
        }
        setSelectedDimension(option);
      };

      return (
        <div className="d-flex align-items-center">
          <RadioButton
            name={`dimension${option.code}`}
            value={option.code}
            onChange={handleDimensionChange}
            checked={isChecked}
          />
          <label htmlFor={`dimension${option.id}`} className="mx-2">
            {option.name}
          </label>
        </div>
      );
    };

    const metricsTemplate = (option) => {
      const isChecked = selectedMetrics.includes(option);
      const handleMetricsChange = (e) => {
        e.preventDefault();
        const { checked } = e.target;
        const _selectedMetrics = selectedMetrics.filter(
          (metric) => metric.code !== option.code
        );
        if (checked) {
          setSelectedMetrics([...selectedMetrics, option]);
        } else {
          setSelectedMetrics([..._selectedMetrics]);
        }
      };

      return (
        <div className="d-flex align-items-center">
          <Checkbox
            inputId={`metrics_${option.code}`}
            value={option.code}
            onChange={handleMetricsChange}
            checked={isChecked}
          />
          <label htmlFor={`metrics_${option.code}`} className="mx-2">
            {option.name}
          </label>
        </div>
      );
    };

    const getDimensions = ({
      connection_ext,
      ga_property_id,
      ga_auth_json,
    }) => {
      setTimeout(() => {
        setMetrics([]);
        setSelectedDimension({});
      }, 0);
      fetchDimensions(
        {
          ga_property_id: ga_property_id,
          ga_auth_json:
            typeof ga_auth_json === "string"
              ? JSON.parse(ga_auth_json)
              : ga_auth_json,
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
            setDimensions(resp);
            if (!isAddSelected) {
              const _dimension = resp.find(
                (dim) => dim.code === connection_ext[0].dimension
              );
              setSelectedDimension(_dimension);
              dispatch(showLoader());
              getDimensionsMetrics(_dimension.code, {
                connection_ext,
                ga_property_id,
                ga_auth_json,
              });
            }
          }
        }
      );
    };

    const getDimensionsMetrics = (
      id,
      { connection_ext, ga_property_id, ga_auth_json }
    ) => {
      setTimeout(() => {
        setMetrics([]);
      }, 0);
      if (!id) {
        return;
      }
      fetchDimensionMetrics(
        {
          ga_property_id: ga_property_id,
          ga_auth_json:
            typeof ga_auth_json === "string"
              ? JSON.parse(ga_auth_json)
              : ga_auth_json,
        },
        id,
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
            const allData = [...resp];
            const existingIds = allData.map((data) => data.id);
            metrics.forEach((comb) => {
              if (!existingIds.includes(comb.id)) {
                allData.push(comb);
              }
            });

            if (
              !isAddSelected &&
              connection_ext &&
              id === connection_ext[0].dimension
            ) {
              const _metrics = resp.filter((metric) =>
                connection_ext[0].dimension_metric.includes(metric.code)
              );
              setSelectedMetrics(_metrics);
            } else {
              setSelectedMetrics([]);
            }
            setMetrics(allData);
          }
        }
      );
    };

    return (
      <>
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
                labelName="Auth JSON"
                className={`${
                  submitted && !connection.ga_auth_json ? "is-invalid" : ""
                }`}
                controls={{
                  value: connection.ga_auth_json,
                  disabled: !isAddSelected,
                  onChange: (e) => {
                    setConnection({
                      ...connection,
                      ga_auth_json: e.target.value,
                    });
                  },
                  onBlur: (e) => {
                    try {
                      const parsedJson = JSON.parse(e.target.value);
                      console.log(parsedJson);
                    } catch (error) {
                      toast.current.show({
                        severity: "error",
                        summary: "Error",
                        detail: "Invalid JSON from Auth JSON:" + error,
                        life: 3000,
                      });
                      console.error();
                    }
                  },
                  id: "ga_auth_json",
                  tabindex: 3,
                  type: "textarea",
                }}
              >
                <div className="invalid-feedback">
                  A valid auth JSON is required!
                </div>
              </WizBIInput>
            </div>
          </div>
          <div className="col col-md-6">
            <div className="form-group mb-2">
              <WizBIInput
                labelName="Property Id"
                className={`${
                  submitted && !connection.ga_property_id ? "is-invalid" : ""
                }`}
                controls={{
                  value: connection.ga_property_id,
                  disabled: !isAddSelected,
                  onChange: (e) => {
                    setConnection({
                      ...connection,
                      ga_property_id: e.target.value,
                    });
                  },
                  id: "ga_property_id",
                  tabindex: 2,
                }}
              >
                <div className="invalid-feedback">
                  A valid Property Id is required!
                </div>
              </WizBIInput>
            </div>
            {isAddSelected && (
              <div className="form-group mt-5">
                <button
                  className="btn bg-wizBi text-white"
                  disabled={!connection.ga_property_id}
                  style={{ width: "150px" }}
                  onClick={() => {
                    setSubmitted(false);
                    dispatch(showLoader());
                    getDimensions(connection);
                  }}
                >
                  Get Dimensions
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="row">
          <div className="d-flex">
            {!!dimensions.length && (
              <div className="py-2">
                <h6 className="mx-3 text-wizBi">Dimensions</h6>
                <div className="d-flex">
                  <ListBox
                    filter
                    value={selectedDimension}
                    itemTemplate={dimensionsTemplate}
                    options={dimensions}
                    optionLabel="name"
                    className="w-full md:w-14rem"
                    optionValue="code"
                    listStyle={{
                      height: "200px",
                      minWidth: "200px",
                    }}
                  />
                </div>
              </div>
            )}

            {!!metrics.length && (
              <div className="p-2">
                <h6 className="mx-3 text-wizBi">Metrics</h6>
                <div className="d-flex">
                  <ListBox
                    filter
                    value={selectedMetrics}
                    itemTemplate={metricsTemplate}
                    options={metrics}
                    optionLabel="metric"
                    className="w-full md:w-14rem"
                    listStyle={{
                      height: "200px",
                      minWidth: "200px",
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </>
    );
  }
);
