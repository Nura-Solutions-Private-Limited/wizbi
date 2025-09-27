import prettyBytes from "pretty-bytes";
// import setupEditors from "./setupEditor";
import React from "react";
import debounce from "lodash.debounce";
import { TabView, TabPanel } from "primereact/tabview";
import { InputSwitch } from "primereact/inputswitch";
import WizBIInput from "../../core/WizBIInput/WizBIInput";
import {
  addRestAPIConnection,
  getRestAPIConnection,
  updateConnection,
  updateRestAPIConnection,
  validateRestAPI,
} from "../../api/connection";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch } from "react-redux";
import JsonEditor from "./JsonEditor";
import { Button } from "primereact/button";
import { useSearchParams } from "react-router-dom";
import { Dialog } from "primereact/dialog";
import { createSearchParams, useNavigate } from "react-router-dom";

const RestAPI = React.forwardRef(
  ({ toast, callback, connection_id, databaseTypes }, ref) => {
    const navigate = useNavigate();

    const [paramsKeyValuePairs, setParamsKeyValuePairs] = React.useState([
      { id: 1, key: "", value: "" },
    ]);

    const [authKeyValuePairs, setAuthKeyValuePairs] = React.useState([
      { id: 1, key: "", value: "" },
    ]);

    const [headersKeyValuePairs, setHeadersKeyValuePairs] = React.useState([
      { id: 1, key: "", value: "" },
    ]);

    const [bodyKeyValuePairs, setBodyKeyValuePairs] = React.useState([
      { id: 1, key: "", value: "" },
    ]);

    const [paramsChecked, setParamsChecked] = React.useState(false);
    const [authChecked, setAUthChecked] = React.useState(false);
    const [headersChecked, setHeadersChecked] = React.useState(false);
    const [bodyChecked, setBodyChecked] = React.useState(false);

    const [queryJSONData, setQueryJSONData] = React.useState({});
    const [authJSONData, setAuthJSONData] = React.useState({});
    const [headersJSONData, setHeadersJSONData] = React.useState({});
    const [bodyJSONData, setBodyJSONData] = React.useState({});

    const [currentConnectorType, setCurrentConnectorType] =
      React.useState(null);

    const [showStructure, setShowStructure] = React.useState(false);

    const [restAPIResponse, setRestAPIResponse] = React.useState({
      body: {},
      headers: {},
    });

    const [searchParams, setSearchParams] = useSearchParams();

    const db_type = searchParams.get("connector_type").toLowerCase();
    const sub_type = searchParams.get("sub_type");
    const defaultValues = {
      db_conn_name: "",
      db_type,
      method: "GET",
      url: "",
      params: null,
      authorization: null,
      headers: null,
      body: null,
    };

    const [connection, setConnection] = React.useState(defaultValues);
    const [submitted, setSubmitted] = React.useState(false);
    const dispatch = useDispatch();

    React.useImperativeHandle(ref, () => ({
      createConnection,
    }));

    function transformInput(input) {
      return Object.entries(input).map(([key, value]) => ({
        key: key,
        value: value,
      }));
    }

    React.useEffect(() => {
      const connectorType = databaseTypes.find((database) => {
        return (
          database.type.toLowerCase().includes(db_type) &&
          (sub_type ? database.sub_type === sub_type : true)
        );
      });

      setCurrentConnectorType(connectorType?.extra ?? null);
      // console.log(connectorType)
    }, []);

    React.useEffect(() => {
      if (connection_id) {
        dispatch(showLoader());
        getRestAPIConnection({ id: connection_id }, (resp) => {
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

            if (resp.params) {
              setParamsKeyValuePairs(transformInput(resp.params));
            }

            if (resp.authorization) {
              setAuthKeyValuePairs(transformInput(resp.authorization));
            }

            if (resp.headers) {
              setHeadersKeyValuePairs(transformInput(resp.headers));
            }

            if (resp.body) {
              setBodyKeyValuePairs(transformInput(resp.body));
            }
          }
        });
      }
    }, [connection_id]);

    const handleAddQueryParamAction = ({ props }) => {
      // const queryParamsContainer = document.querySelector("[data-query-params]");
      // queryParamsContainer.append(createKeyValuePair());
      if (props === "params") {
        setParamsKeyValuePairs([
          ...paramsKeyValuePairs,
          { id: paramsKeyValuePairs.length, key: "", value: "" },
        ]);
      }
      if (props === "auth") {
        setAuthKeyValuePairs([
          ...authKeyValuePairs,
          { id: authKeyValuePairs.length, key: "", value: "" },
        ]);
      }
      if (props === "headers") {
        setHeadersKeyValuePairs([
          ...headersKeyValuePairs,
          { id: headersKeyValuePairs.length, key: "", value: "" },
        ]);
      }
      if (props === "body") {
        setBodyKeyValuePairs([
          ...bodyKeyValuePairs,
          { id: bodyKeyValuePairs.length, key: "", value: "" },
        ]);
      }
    };

    const createConnection = () => {
      if (!connection?.db_conn_name?.length) {
        return setSubmitted(true);
      }
      dispatch(showLoader());
      const params = arrayToObject(paramsKeyValuePairs);
      const authorization = arrayToObject(authKeyValuePairs);
      const headers = arrayToObject(headersKeyValuePairs);
      const body = arrayToObject(bodyKeyValuePairs);
      const connectionDetails = {
        db_conn_name: connection.db_conn_name,
        db_type: searchParams.get("connector_type"),
        sub_type: searchParams.get("sub_type") ?? "",
        url: connection.url,
        method: connection.method,
        ...(Object.keys(params).length && { params }),
        ...(Object.keys(authorization).length && { authorization }),
        ...(Object.keys(headers).length && { headers }),
        ...(Object.keys(body).length && { body }),
      };

      if (connection_id) {
        return updateRestAPIConnection(
          { id: connection_id, ...connectionDetails },
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
            callback();
          }
        );
      }
      addRestAPIConnection(connectionDetails, (resp) => {
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
        callback();
      });
    };

    // const { requestEditor, updateResponseEditor } = setupEditors();

    const onSubmit = (e) => {
      e.preventDefault();
      const params = paramsChecked
        ? queryJSONData
        : arrayToObject(paramsKeyValuePairs);
      const authorization = authChecked
        ? authJSONData
        : arrayToObject(authKeyValuePairs);
      const headers = headersChecked
        ? headersJSONData
        : arrayToObject(headersKeyValuePairs);
      const body = bodyChecked
        ? bodyJSONData
        : arrayToObject(bodyKeyValuePairs);

      dispatch(showLoader());

      validateRestAPI(
        {
          url: connection.url,
          method: connection.method,

          ...(Object.keys(params).length && { params }),
          ...(Object.keys(authorization).length && { authorization }),
          ...(Object.keys(headers).length && { headers }),
          ...(Object.keys(body).length && { body }),
        },
        async (response) => {
          dispatch(hideLoader());
          document
            .querySelector("[data-response-section]")
            .classList.remove("d-none");
          const body = await response.json();
          updateResponseDetails({
            status: response.status,
            body,
            headers: response.headers,
          });

          setRestAPIResponse({
            body: body,
            header: response.header,
          });
        }
      );
    };

    function updateResponseDetails({ status, body, headers }) {
      document.querySelector("[data-status]").textContent = status;
      // document.querySelector("[data-time]").textContent =
      //   response.customData.time;
      document.querySelector("[data-size]").textContent = prettyBytes(
        JSON.stringify(body).length + JSON.stringify(headers).length
      );
    }

    function arrayToObject(inputArray) {
      return inputArray.reduce((acc, item) => {
        if (item.key) {
          // Only add if the key is not empty
          acc[item.key] = item.value;
        }
        return acc;
      }, {});
    }

    const updateKeyValue = React.useCallback(
      debounce((index, field, newValue, section) => {
        if (section === "params") {
          setParamsKeyValuePairs((prevState) => {
            const updatedPairs = [...prevState];
            updatedPairs[index] = { ...updatedPairs[index], [field]: newValue };
            return updatedPairs;
          });
        }
        if (section === "auth") {
          setAuthKeyValuePairs((prevState) => {
            const updatedPairs = [...prevState];
            updatedPairs[index] = { ...updatedPairs[index], [field]: newValue };
            return updatedPairs;
          });
        }
        if (section === "headers") {
          setHeadersKeyValuePairs((prevState) => {
            const updatedPairs = [...prevState];
            updatedPairs[index] = { ...updatedPairs[index], [field]: newValue };
            return updatedPairs;
          });
        }
        if (section === "body") {
          setBodyKeyValuePairs((prevState) => {
            const updatedPairs = [...prevState];
            updatedPairs[index] = { ...updatedPairs[index], [field]: newValue };
            return updatedPairs;
          });
        }
      }, 100),
      []
    );

    // Handle input changes
    const handleInputChange = (index, field, event, section) => {
      const { value } = event.target;
      updateKeyValue(index, field, value, section); // Call debounced update function
    };

    const handleChange = (event) => {
      const { name, value } = event.target;
      setConnection((prevState) => ({
        ...prevState,
        [name]: value,
      }));
    };

    const handleJsonChange = ({ key, updatedJson }) => {
      if (key === "params") {
        setQueryJSONData(updatedJson);
      } else if (key === "auth") {
        setAuthJSONData(updatedJson);
      } else if (key === "headers") {
        setHeadersJSONData(updatedJson);
      } else if (key === "body") {
        setBodyJSONData(updatedJson);
      }
    };

    const footerStructureContent = () => {
      return (
        <div>
          <Button
            label="Cancel"
            icon="pi pi-times"
            className="p-button-text text-wizBi mx-2"
            onClick={() => {
              setShowStructure(false);
            }}
          />
        </div>
      );
    };

    return (
      <>
        <div class="p-2">
          <form data-form>
            <WizBIInput
              labelName="Connection Name"
              panelClass="my-2"
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

            <div class="input-group mb-4">
              <select
                class="form-select flex-grow-0 w-auto"
                name="method"
                value={connection.method}
                onChange={handleChange}
              >
                <option value="GET" selected>
                  GET
                </option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="PATCH">PATCH</option>
                <option value="DELETE">DELETE</option>
              </select>
              <input
                required
                class="form-control"
                type="url"
                placeholder="https://example.com"
                style={{ color: "#000" }}
                name="url"
                value={connection.url}
                onChange={handleChange}
              />
              <button
                onClick={onSubmit}
                class="p-button p-component p-2 bg-wizBi text-white"
              >
                Test Connection
              </button>
            </div>

            {currentConnectorType && (
              <div className="row my-2">
                <div className="col-md-12">
                  <button
                    class="p-button p-component p-2 bg-wizBi text-white pull-right"
                    onClick={(event) => {
                      event.preventDefault();
                      setShowStructure(true);
                    }}
                  >
                    <i className="fa fa fa-code mx-2" />
                    See Structure
                  </button>
                </div>
              </div>
            )}
            <TabView>
              <TabPanel header="Params">
                <div
                  class="tab-pane fade show active"
                  id="query-params"
                  role="tabpanel"
                  aria-labelledby="query-params-tab"
                >
                  <div className="d-flex align-items-center gap-1">
                    <span>JSON View</span>
                    <InputSwitch
                      checked={paramsChecked}
                      onChange={(e) => {
                        if (e.value) {
                          const jsonBody = arrayToObject(paramsKeyValuePairs);
                          setQueryJSONData(jsonBody);
                        }
                        setParamsChecked(e.value);
                      }}
                    />
                  </div>

                  {paramsChecked ? (
                    <>
                      <JsonEditor
                        data={queryJSONData}
                        setData={setQueryJSONData}
                        isEditable={true}
                        toast={toast}
                        onChange={(updatedJson) => {
                          handleJsonChange({ key: "params", updatedJson });
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <div data-query-params>
                        {paramsKeyValuePairs.map((item, index) => (
                          <div class="input-group my-2" data-key-value-pair>
                            <input
                              type="text"
                              data-key
                              class="form-control"
                              placeholder="Key"
                              value={item.key}
                              onChange={(e) =>
                                handleInputChange(index, "key", e, "params")
                              }
                              style={{ color: "#000" }}
                            />
                            <input
                              type="text"
                              data-value
                              class="form-control"
                              placeholder="Value"
                              value={item.value}
                              onChange={(e) =>
                                handleInputChange(index, "value", e, "params")
                              }
                              style={{ color: "#000" }}
                            />

                            <Button
                              icon="pi pi-trash"
                              severity="danger"
                              aria-label="Delete"
                              onClick={(e) => {
                                e.preventDefault();
                                const cloneItems = [...paramsKeyValuePairs];
                                cloneItems.splice(index, 1);
                                setParamsKeyValuePairs(cloneItems);
                              }}
                            />
                          </div>
                        ))}
                      </div>

                      <Button
                        className="bg-wizBi pull-right"
                        label="Add"
                        icon="pi pi-plus"
                        onClick={(event) => {
                          event.preventDefault();
                          handleAddQueryParamAction({ props: "params" });
                        }}
                        aria-label="Add"
                      />
                    </>
                  )}
                </div>
              </TabPanel>
              <TabPanel header="Auth">
                <div
                  class="tab-pane fade show active"
                  id="query-params"
                  role="tabpanel"
                  aria-labelledby="query-params-tab"
                >
                  <div className="d-flex align-items-center gap-1">
                    <span>JSON View</span>
                    <InputSwitch
                      checked={authChecked}
                      onChange={(e) => {
                        if (e.value) {
                          const jsonBody = arrayToObject(authKeyValuePairs);
                          setAuthJSONData(jsonBody);
                        }
                        setAUthChecked(e.value);
                      }}
                    />
                  </div>
                  {authChecked ? (
                    <>
                      <JsonEditor
                        data={authJSONData}
                        setData={setAuthJSONData}
                        isEditable={true}
                        toast={toast}
                        onChange={(updatedJson) => {
                          handleJsonChange({ key: "auth", updatedJson });
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <div data-query-auth>
                        {authKeyValuePairs.map((item, index) => (
                          <div class="input-group my-2" data-key-value-pair>
                            <input
                              type="text"
                              data-key
                              class="form-control"
                              placeholder="Key"
                              value={item.key}
                              onChange={(e) =>
                                handleInputChange(index, "key", e, "auth")
                              }
                              style={{ color: "#000" }}
                            />
                            <input
                              type="text"
                              data-value
                              class="form-control"
                              placeholder="Value"
                              value={item.value}
                              onChange={(e) =>
                                handleInputChange(index, "value", e, "auth")
                              }
                              style={{ color: "#000" }}
                            />

                            <Button
                              icon="pi pi-trash"
                              severity="danger"
                              aria-label="Delete"
                              onClick={(e) => {
                                e.preventDefault();
                                const cloneItems = [...authKeyValuePairs];
                                cloneItems.splice(index, 1);
                                setAuthKeyValuePairs(cloneItems);
                              }}
                            />
                          </div>
                        ))}
                      </div>

                      <Button
                        className="bg-wizBi  pull-right"
                        label="Add"
                        icon="pi pi-plus"
                        onClick={(event) => {
                          event.preventDefault();
                          handleAddQueryParamAction({ props: "auth" });
                        }}
                        aria-label="Add"
                      />
                    </>
                  )}
                </div>
              </TabPanel>
              <TabPanel header="Headers">
                <div
                  class="tab-pane fade show active"
                  id="query-params"
                  role="tabpanel"
                  aria-labelledby="query-params-tab"
                >
                  <div className="d-flex align-items-center gap-1">
                    <span>JSON View</span>
                    <InputSwitch
                      checked={headersChecked}
                      onChange={(e) => {
                        if (e.value) {
                          const jsonBody = arrayToObject(headersKeyValuePairs);
                          setHeadersJSONData(jsonBody);
                        }
                        setHeadersChecked(e.value);
                      }}
                    />
                  </div>
                  {headersChecked ? (
                    <>
                      <JsonEditor
                        data={headersJSONData}
                        setData={setHeadersJSONData}
                        isEditable={true}
                        toast={toast}
                        onChange={(updatedJson) => {
                          handleJsonChange({ key: "headers", updatedJson });
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <div data-query-headers>
                        {headersKeyValuePairs.map((item, index) => (
                          <div class="input-group my-2" data-key-value-pair>
                            <input
                              type="text"
                              data-key
                              class="form-control"
                              placeholder="Key"
                              value={item.key}
                              onChange={(e) =>
                                handleInputChange(index, "key", e, "headers")
                              }
                              style={{ color: "#000" }}
                            />
                            <input
                              type="text"
                              data-value
                              class="form-control"
                              placeholder="Value"
                              value={item.value}
                              onChange={(e) =>
                                handleInputChange(index, "value", e, "headers")
                              }
                              style={{ color: "#000" }}
                            />

                            <Button
                              icon="pi pi-trash"
                              severity="danger"
                              aria-label="Delete"
                              onClick={(e) => {
                                e.preventDefault();
                                const cloneItems = [...headersKeyValuePairs];
                                cloneItems.splice(index, 1);
                                setHeadersKeyValuePairs(cloneItems);
                              }}
                            />
                          </div>
                        ))}
                      </div>
                      <Button
                        className="bg-wizBi pull-right"
                        label="Add"
                        icon="pi pi-plus"
                        onClick={(event) => {
                          event.preventDefault();
                          handleAddQueryParamAction({ props: "headers" });
                        }}
                        aria-label="Add"
                      />
                    </>
                  )}
                </div>
              </TabPanel>
              <TabPanel header="Body">
                <div
                  class="tab-pane fade show active"
                  id="query-body"
                  role="tabpanel"
                  aria-labelledby="query-body
                -tab"
                >
                  <div className="d-flex align-items-center gap-1">
                    <span>JSON View</span>
                    <InputSwitch
                      checked={bodyChecked}
                      onChange={(e) => {
                        if (e.value) {
                          const jsonBody = arrayToObject(bodyKeyValuePairs);
                          setBodyJSONData(jsonBody);
                        }
                        setBodyChecked(e.value);
                      }}
                    />
                  </div>
                  {bodyChecked ? (
                    <>
                      <JsonEditor
                        data={bodyJSONData}
                        setData={setBodyJSONData}
                        isEditable={true}
                        toast={toast}
                        onChange={(updatedJson) => {
                          handleJsonChange({ key: "body", updatedJson });
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <div data-query-body>
                        {bodyKeyValuePairs.map((item, index) => (
                          <div class="input-group my-2" data-key-value-pair>
                            <input
                              type="text"
                              data-key
                              class="form-control"
                              placeholder="Key"
                              value={item.key}
                              onChange={(e) =>
                                handleInputChange(index, "key", e, "body")
                              }
                              style={{ color: "#000" }}
                            />
                            <input
                              type="text"
                              data-value
                              class="form-control"
                              placeholder="Value"
                              value={item.value}
                              onChange={(e) =>
                                handleInputChange(index, "value", e, "body")
                              }
                              style={{ color: "#000" }}
                            />

                            <Button
                              icon="pi pi-trash"
                              severity="danger"
                              aria-label="Delete"
                              onClick={(e) => {
                                e.preventDefault();
                                const cloneItems = [...bodyKeyValuePairs];
                                cloneItems.splice(index, 1);
                                setBodyKeyValuePairs(cloneItems);
                              }}
                            />
                          </div>
                        ))}
                      </div>
                      <Button
                        className="bg-wizBi pull-right"
                        label="Add"
                        icon="pi pi-plus"
                        onClick={(event) => {
                          event.preventDefault();
                          handleAddQueryParamAction({ props: "body" });
                        }}
                        aria-label="Add"
                      />
                    </>
                  )}
                </div>
              </TabPanel>
            </TabView>
          </form>

          <div class="mt-5 d-none" data-response-section>
            <h3>Response</h3>
            <div class="d-flex my-2">
              <div class="me-3">
                Status: <span data-status></span>
              </div>
              <div class="me-3">
                Time: <span data-time></span>ms
              </div>
              <div class="me-3">
                Size: <span data-size></span>
              </div>
            </div>
            <TabView>
              <TabPanel header="Body">
                <div
                  class="tab-pane fade show active"
                  id="body-params"
                  role="tabpanel"
                  aria-labelledby="body-params-tab"
                >
                  <JsonEditor
                    data={{ ...restAPIResponse.body }}
                    setData={setBodyJSONData}
                    isEditable={false}
                    theme="dark"
                    toast={toast}
                  />
                </div>
              </TabPanel>

              <TabPanel header="Headers">
                <div
                  class="tab-pane fade show active"
                  id="headers-params"
                  role="tabpanel"
                  aria-labelledby="headers-params-tab"
                >
                  <JsonEditor
                    data={{ ...restAPIResponse.headers }}
                    setData={setBodyJSONData}
                    isEditable={false}
                    theme="dark"
                    toast={toast}
                  />
                </div>
              </TabPanel>
            </TabView>
          </div>
        </div>

        <Dialog
          header={
            <div className="d-flex align-items-center" draggable={false}>
              <small className="mx-1 px-1">Schedule</small>
            </div>
          }
          visible={showStructure}
          style={{ width: "50vw" }}
          onHide={() => setShowStructure(false)}
          footer={footerStructureContent()}
        >
          <div className="form-group mb-2 m-1">
            <JsonEditor
              data={currentConnectorType}
              setData={setBodyJSONData}
              isEditable={false}
              theme="dark"
              toast={toast}
            />
          </div>
        </Dialog>
      </>
    );
  }
);

export default RestAPI;
