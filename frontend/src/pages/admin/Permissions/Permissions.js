import { useEffect, useRef, useState } from "react";
import Widget from "../../../components/Widget/Widget";
import s from "./Permissions.module.scss";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { ListBox } from "primereact/listbox";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import { hideLoader, showLoader } from "../../../actions/loader";
import {
  addPermission,
  deletePermissionById,
  fetchPermissions,
  updatePermissionById,
} from "../../../api/permissions";
import { confirmDialog } from "primereact/confirmdialog";
import { useDispatch } from "react-redux";
import { fetchRoles } from "../../../api/roles";
import { Toast } from "primereact/toast";
import WizBIDropDown from "../../../core/WizBIDropDown/WizBIDropDown";
import { Dropdown } from "primereact/dropdown";
import { Checkbox } from "primereact/checkbox";
import { fetchConnections } from "../../../api/connection";
import { fetchPipelines } from "../../../api/pipeLine";
import { fetchAudits } from "../../../api/auditsAPI";
import { fetchJobs } from "../../../api/jobsAPI";
import { fetchDashboards } from "../../../api/homeAPI";
import { getReports } from "../../../api/reportsAPI";

export const Permissions = () => {
  const [filterList, setFilterList] = useState([]);
  const [rolesList, setRolesList] = useState([]);
  const [selectedPermission, setSelectedPermission] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const toast = useRef(null);
  const dispatch = useDispatch();
  const [isRowSelected, setIsRowSelected] = useState(false);
  const [selectedRoleType, setSelectedRoleType] = useState(null);
  const [isAddSelected, setIsAddSelected] = useState(false);
  const resetPermissionDetails = {
    id: 0,
    role_id: 0,
    description: "",
    name: "",
    pipelines_allowed: false,
    etl_allowed: false,
    connections_allowed: false,
    dashboards_allowed: false,
    jobs_allowed: false,
    audits_allowed: false,
    reports_allowed: false,
    genai_allowed: false,
    dashboard_ids: [],
    report_ids: [],
    connection_ids: [],
    pipeline_ids: [],
  };
  const [permissionType, setPermission] = useState("");
  const [selectedItems, setSelectedItems] = useState([]);
  const [itemsList, setItemsList] = useState([]);
  const permissionsType = [
    {
      name: "Pipelines",
      id: 1000,
    },
    {
      name: "Dashboards",
      id: 1001,
    },
    {
      name: "Connections",
      id: 1002,
    },
    {
      name: "Reports",
      id: 1003,
    },
    {
      name: "Jobs",
      id: 1003,
    },
    {
      name: "Audits",
      id: 1003,
    },
    {
      name: "GenAi",
      id: 1003,
    },
  ];
  const accept = () => {
    dispatch(showLoader());
    deletePermissionById(selectedPermission.id, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp?.detail || !!resp?.message)) {
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
          detail: "The permission has been successfully deleted",
          life: 3000,
        });
        getPermissions();
        reset();
      }
    });
  };
  const deletePermission = () => {
    confirmDialog({
      message: "Do you want to delete this record?",
      header: "Delete Confirmation",
      icon: "pi pi-info-circle",
      acceptClassName: "p-button-danger",
      accept,
    });
  };
  const header = () => {
    return (
      <>
        <span>
          <Button
            severity="info"
            className="mx-2 bg-wizBi p-2"
            onClick={() => addPermissionEnabled()}
            disabled={isAddSelected || isRowSelected}
          >
            <i className="pi pi-plus mx-2"></i> Add
          </Button>
          <Button
            severity="danger"
            className="mx-2 p-2"
            onClick={() => deletePermission()}
            disabled={!isRowSelected}
          >
            <i className="pi pi-trash mx-2"></i> Delete
          </Button>
          <Button
            severity="success"
            className="mx-2 p-2 wizBi-bg-success"
            onClick={() => savePermission()}
            disabled={(!isRowSelected && !isAddSelected) || !selectedPermission}
          >
            <i className="pi pi-check mx-2"></i> Submit
          </Button>
          <Button
            severity="danger"
            className="mx-2 p-2"
            onClick={() => reset()}
          >
            <i className="pi pi-times mx-2"></i> Reset
          </Button>
        </span>
      </>
    );
  };
  const addPermissionEnabled = () => {
    setIsAddSelected(true);
    setSelectedPermission(resetPermissionDetails);
  };
  const reset = () => {
    setIsAddSelected(false);
    setIsRowSelected(false);
    setSubmitted(false);
    setSelectedPermission(null);
    setSelectedRoleType(null);
    setPermission("");
    setSelectedItems([]);
    setItemsList([]);
  };
  const savePermission = () => {
    if (!selectedPermission.name || !selectedPermission.description) {
      return setSubmitted(true);
    }
    setSubmitted(false);
    dispatch(showLoader());
    const permission = permissionType.toLowerCase();
    let permissionDetails = {
      ...selectedPermission,
      ...{
        pipelines_allowed: permission.includes("pipeline"),
        etl_allowed: permission.includes("etl"),
        connections_allowed: permission.includes("connections"),
        dashboards_allowed: permission.includes("dashboard"),
        jobs_allowed: permission.includes("jobs"),
        audits_allowed: permission.includes("audits"),
        reports_allowed: permission.includes("reports"),
        genai_allowed : permission.includes('genai'),
        ...(permission.includes("pipeline") && {
          pipeline_ids: selectedItems.map((item) => item.id),
        }),
        ...(permission.includes("reports") && {
          report_ids: selectedItems.map((item) => item.id),
        }),
        ...(permission.includes("dashboard") && {
          dashboard_ids: selectedItems.map((item) => item.id),
        }),
        ...(permission.includes("connections") && {
          connection_ids: selectedItems.map((item) => item.id),
        }),
      },
    };
    if (isAddSelected) {
      addPermission(permissionDetails, (resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp?.detail || !!resp?.message)) {
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
            detail: "The permission has been added successfully",
            life: 3000,
          });
          getPermissions();
        }
      });
    } else {
      updatePermissionById(permissionDetails, (resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp?.detail || !!resp?.message)) {
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
            detail: "The permission has been updated successfully",
            life: 3000,
          });
          getPermissions();
        }
      });
    }
  };
  const getPermissions = () => {
    dispatch(showLoader());
    fetchPermissions((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setFilterList(resp);
      }
    });
  };
  const getRoles = () => {
    dispatch(showLoader());
    fetchRoles((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setRolesList(resp);
      }
    });
  };
  useEffect(() => {
    getPermissions();
    getRoles();
  }, []);

  const fetchAllowedPermission = (pType, { role_type, info }) => {
    console.log(role_type, info);
    dispatch(showLoader());
    if (pType.includes("pipelines")) {
      fetchPipelines({}, (resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          const formatJson = resp.map((data) => {
            return { id: data.id, value: data.name };
          });
          formatData(
            formatJson,
            role_type ? { role: role_type, ids: info.pipeline_ids } : {}
          );
        }
      });
    } else if (pType.includes("dashboards")) {
      fetchDashboards((resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          const formatJson = resp.map((data) => {
            return { id: data.id, value: data.name };
          });
          formatData(
            formatJson,
            role_type ? { role: role_type, ids: info.dashboard_ids } : {}
          );
        }
      });
    } else if (pType.includes("connections")) {
      fetchConnections((resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          const formatJson = resp.map((data) => {
            return { id: data.id, value: data.db_conn_name };
          });
          formatData(
            formatJson,
            role_type ? { role: role_type, ids: info.connection_ids } : {}
          );
        }
      });
    } else if (pType.includes("reports")) {
      getReports("/rebiz/v1/reports-auto", (resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          const formatJson = resp.map((data) => {
            return { id: data.id, value: data.name };
          });
          formatData(
            formatJson,
            role_type ? { role: role_type, ids: info.report_ids } : {}
          );
        }
      });
    } else if (pType.includes("audits")) {
      fetchAudits((resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          const formatJson = resp.map((data) => {
            return { id: data.id, value: data.job_id };
          });
          formatData(
            formatJson,
            role_type ? { role: role_type, ids: info.audits_ids } : {}
          );
        }
      });
    } else if (pType.includes("jobs")) {
      fetchJobs((resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          const formatJson = resp.map((data) => {
            return { id: data.id, value: data.job_id };
          });
          formatData(
            formatJson,
            role_type ? { role: role_type, ids: info.job_ids } : {}
          );
        }
      });
    }
  };

  const formatData = (resp, { role, ids }) => {
    setItemsList(resp);
    if (role && role.toLowerCase().includes("component") && ids && ids.length) {
      setSelectedItems(resp.filter((data) => ids.includes(data.id)));
    }
  };
  const itemTemplate = (option) => {
    const isChecked = selectedItems.includes(option);
    const handleItemChange = (e) => {
      e.preventDefault();
      const { checked } = e.target;
      const _selectedItems = selectedItems.filter(
        (metric) => metric.id !== option.id
      );
      if (checked) {
        setSelectedItems([..._selectedItems, option]);
      } else {
        setSelectedItems([..._selectedItems]);
      }
    };

    return (
      <div className="d-flex align-items-center">
        <Checkbox
          inputId={`permission_${option.id}`}
          value={option.value}
          onChange={handleItemChange}
          checked={isChecked}
        />
        <label htmlFor={`permission_${option.id}`} className="mx-2">
          {option.value}
        </label>
      </div>
    );
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-5 col-lg-5 ${s.wrapper}`}>
          <Widget
            title={
              <div className="d-flex justify-content-between align-items-center py-2">
                <h5>Permissions</h5>
              </div>
            }
            className={`mb-0`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            <div
              className={`w-100 px-4 py-2 ${
                filterList.length === 0 ? "" : "h-100"
              }`}
            >
              <DataTable
                value={filterList}
                rowSelection
                selectionMode="single"
                emptyMessage={
                  false ? (
                    <h5 className="d-flex justify-content-center">
                      Loading ...
                    </h5>
                  ) : (
                    <h5 className="d-flex justify-content-center">
                      No data available
                    </h5>
                  )
                }
                // loadingIcon={<Loader />}
                onSelectionChange={(e) => {
                  setSelectedPermission(e.value);
                  setIsRowSelected(true);
                  const role = rolesList.find(
                    (role) => role.id === e.value.role_id
                  );
                  if (rolesList && rolesList.length) {
                    setSelectedRoleType(role);
                  }
                  const values = [
                    "pipelines_allowed",
                    "etl_allowed",
                    "connections_allowed",
                    "dashboards_allowed",
                    "jobs_allowed",
                    "audits_allowed",
                    "reports_allowed",
                    "genai_allowed"
                  ];

                  const val = values.filter((val) => {
                    if (e.value[val]) {
                      return val;
                    }
                  })[0];
                  if (val) {
                    const word = val?.split("_")[0];
                    const permission =
                      word.charAt(0).toUpperCase() + word.slice(1);
                    setPermission(permission);
                    if (role.role_type.toLowerCase().includes("component")) {
                      fetchAllowedPermission(permission.toLowerCase(), {
                        role_type: role.role_type,
                        info: e.value,
                      });
                    }
                  }
                }}
                tableStyle={{ minHeight: "200px" }}
              >
                <Column field="name" header="Name" sortable></Column>
                <Column field="description" header="Description"></Column>
              </DataTable>
            </div>
          </Widget>
        </div>
        <div className={`col-md-7 col-lg-7 ${s.wrapper}`}>
          <Widget
            title={
              <div className="d-flex justify-content-end align-items-center py-2">
                {header()}
              </div>
            }
            className={`mb-0`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            <div className="w-100 py-2 px-4 h-100">
              {!!selectedPermission ? (
                <div className="row">
                  <div className="col col-md-6">
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Permission Name"
                        className={`m-0 p-0 ${
                          submitted && !selectedPermission.name
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          value: selectedPermission.name,
                          onChange: (e) => {
                            setSelectedPermission({
                              ...selectedPermission,
                              name: e.target.value,
                            });
                          },
                          id: "name",
                          tabindex: 1,
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid permission name is required!
                        </div>
                      </WizBIInput>
                    </div>
                    <div className="form-group mb-2 position-relative">
                      <WizBIDropDown
                        labelName="Role"
                        panelClass="mb-2 w-100"
                        className={`${
                          submitted && !selectedPermission.role_id
                            ? "is-invalid"
                            : ""
                        }`}
                      >
                        <Dropdown
                          filter
                          value={selectedPermission.role_id}
                          style={{
                            height: "35px",
                          }}
                          className={`p-0 m-0 custom-conn-drop w-100 d-flex form-control active ${
                            submitted && !selectedPermission.role_id
                              ? "border border-danger"
                              : ""
                          }`}
                          options={rolesList}
                          optionLabel="name"
                          optionValue="id"
                          tabindex={2}
                          onChange={(e) => {
                            console.log(e);
                            setSelectedPermission({
                              ...selectedPermission,
                              role_id: e.value,
                            });
                            const roleType = rolesList.find(
                              (role) => role.id === e.value
                            );
                            setSelectedRoleType(roleType);
                            if (
                              roleType?.role_type.toLowerCase() ===
                                "component" &&
                              permissionType
                            ) {
                              const pType = permissionType.toLowerCase();
                              fetchAllowedPermission(pType, {});
                            } else {
                              setPermission("");
                            }
                          }}
                          placeholder="Please select a role"
                        />
                        <div
                          className={`invalid-feedback${
                            submitted && !selectedPermission.role_id
                              ? " d-block"
                              : ""
                          }`}
                        >
                          Please permission allowed type!
                        </div>
                      </WizBIDropDown>
                      {selectedRoleType?.role_type && (
                        <small
                          className="text-info position-absolute"
                          style={{
                            bottom: "-20px",
                          }}
                        >{`Role type:  ${selectedRoleType.role_type}`}</small>
                      )}
                    </div>

                    <div className="form-group my-5">
                      <WizBIInput
                        labelName="Permission Description"
                        className={`${
                          submitted && !selectedPermission.description
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          type: "textarea",
                          value: selectedPermission.description,
                          onChange: (e) => {
                            setSelectedPermission({
                              ...selectedPermission,
                              description: e.target.value,
                            });
                          },
                          id: "description",
                          tabindex: 1,
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid description is required!
                        </div>
                      </WizBIInput>
                    </div>
                  </div>
                  <div className="col col-md-6 my-4">
                    {selectedRoleType?.role_type.toLowerCase() !== "all" && (
                      <div className="form-group mb-2">
                        <WizBIDropDown
                          labelName="Permission Allowed"
                          panelClass="mb-2 w-100"
                          className={`${
                            submitted && !permissionType ? "is-invalid" : ""
                          }`}
                        >
                          <Dropdown
                            filter
                            value={permissionType}
                            style={{
                              height: "35px",
                            }}
                            className={`p-0 m-0 custom-conn-drop w-100 d-flex form-control active ${
                              submitted && !selectedPermission.role_type
                                ? "border border-danger"
                                : ""
                            }`}
                            options={permissionsType}
                            optionLabel="name"
                            optionValue="name"
                            tabindex={2}
                            onChange={(e) => {
                              setPermission(e.value);
                              if (
                                selectedRoleType?.role_type.toLowerCase() ===
                                "component"
                              ) {
                                fetchAllowedPermission(
                                  e.value.toLowerCase(),
                                  {}
                                );
                              }
                            }}
                            placeholder="Select a permission allowed"
                          />
                          <div
                            className={`invalid-feedback${
                              submitted && !permissionType ? " d-block" : ""
                            }`}
                          >
                            Please select allowed permissions!
                          </div>
                        </WizBIDropDown>
                      </div>
                    )}

                    {selectedRoleType?.role_type.toLowerCase() ===
                      "component" &&
                      permissionType && (
                        <div className="form-group mb-2">
                          <h6 className="mx-3 text-wizBi">{permissionType}</h6>
                          <div className="d-flex">
                            <ListBox
                              filter
                              value={selectedItems}
                              itemTemplate={itemTemplate}
                              options={itemsList}
                              optionLabel="value"
                              className="w-100"
                              listStyle={{ height: "150px", minWidth: "200px" }}
                            />
                          </div>
                        </div>
                      )}
                  </div>
                </div>
              ) : (
                <>
                  {!isAddSelected && (
                    <div className="d-flex justify-content-center align-items-center h-100">
                      <h5 className="text-center">
                        Please select a permission to see the details
                      </h5>
                    </div>
                  )}
                </>
              )}
            </div>
          </Widget>
        </div>
      </div>
      <Toast ref={toast} />
    </>
  );
};
