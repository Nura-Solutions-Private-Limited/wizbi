import { useEffect, useRef, useState } from "react";
import Widget from "../../../components/Widget/Widget";
import s from "./Roles.module.scss";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import {
  addRole,
  deleteRoleById,
  fetchRoles,
  updateRoleById,
} from "../../../api/roles";
import { confirmDialog } from "primereact/confirmdialog";
import { Toast } from "primereact/toast";
import WizBIDropDown from "../../../core/WizBIDropDown/WizBIDropDown";
import { Dropdown } from "primereact/dropdown";
import { fetchUsers } from "../../../api/users";
import { Select } from "antd";
import { fetchGroups } from "../../../api/groups";
import React from "react";

const { Option } = Select;

export const Roles = () => {
  const resetRoleDetails = {
    id: 0,
    name: "",
    description: "",
    role_type: "",
  };
  const [filterList, setFilterList] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const toast = useRef(null);
  const dispatch = useDispatch();
  const [isRowSelected, setIsRowSelected] = useState(false);
  const [groupsList, setGroupsList] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [selectedGroupsList, setSelectedGroupsList] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const roleTypes = [
    {
      name: "Admin",
      id: 1000,
    },
    {
      name: "All",
      id: 1001,
    },
    {
      name: "Feature",
      id: 1002,
    },
    {
      name: "Component",
      id: 1003,
    },
  ];
  const [isAddSelected, setIsAddSelected] = useState(false);
  // const [selectedUsersInRole, setSelectedUsersInRole] = useState(null);
  const [selectedUsersList, setSelectedUsersList] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const accept = () => {
    dispatch(showLoader());
    deleteRoleById(selectedRole.id, (resp) => {
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
          detail: "The role has been successfully deleted",
          life: 3000,
        });
        getRoles();
        setSelectedRole(null);
      }
    });
  };

  const getGroups = () => {
    dispatch(showLoader());
    fetchGroups((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp?.detail || !!resp?.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setGroupsList(resp);
      }
    });
  };

  const handleGroupSelect = (values) => {
    setSelectedGroups(values);
    const users = Array.from(
      new Set(
        groupsList
          .filter((group) => values.includes(group.id))
          .flatMap((group) => group.users.map((user) => user.username))
      )
    );
    setSelectedGroupsList(
      groupsList.filter((group) => values.includes(group.id))
    );
    const list = Array.from(
      new Set(
        groupsList
          .filter((group) => values.includes(group.id))
          .flatMap((group) => group.users.map((user) => user))
      )
    );

    const roleList = filterList.filter((item) => users.includes(item.name));
    setSelectedUsersList([
      ...new Map(list.map((user) => [user.user_id, user])).values(),
    ]);
    setSelectedUsers(users);
    // setSelectedUsersInRole(roleList);
  };

  const handleUserSelect = (values) => {
    setSelectedUsers(values);
    setSelectedUsersList(
      filterList.filter((item) => values.includes(item.username))
    );
  };

  const deleteRole = () => {
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
            onClick={() => addRoleEnabled()}
            disabled={isAddSelected || isRowSelected}
          >
            <i className="pi pi-plus mx-2"></i> Add
          </Button>
          <Button
            severity="danger"
            className="mx-2 p-2"
            onClick={() => deleteRole()}
            disabled={!isRowSelected}
          >
            <i className="pi pi-trash mx-2"></i> Delete
          </Button>
          <Button
            severity="success"
            className="mx-2 p-2 wizBi-bg-success"
            onClick={() => saveRole()}
            disabled={(!isRowSelected && !isAddSelected) || !selectedRole}
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
  const addRoleEnabled = () => {
    setIsAddSelected(true);
    setSelectedRole(resetRoleDetails);
  };
  const reset = () => {
    setIsAddSelected(false);
    setIsRowSelected(false);
    setSubmitted(false);
    setSelectedRole(null);
    // setSelectedUsersInRole(null);
    setSelectedUsers([]);
    setSelectedUsersList([]);
    setSelectedGroups([]);
  };
  const saveRole = () => {
    if (!selectedRole.name || !selectedRole.description) {
      return setSubmitted(true);
    }

    const listOfGroups = selectedGroupsList.map((item) => {
      return { id: item.id, name: item.name };
    });
    const listOfUsers = selectedUsersList.map((user) => {
      return { id: user.user_id, name: user.username };
    });
    setSubmitted(false);
    let roleDetails = {
      ...selectedRole,
      rolepermissions: listOfGroups,
      roleusers: listOfUsers,
    };
    if (isAddSelected) {
      dispatch(showLoader());
      addRole(roleDetails, (resp) => {
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
            detail: "The role has been added successfully",
            life: 3000,
          });
          getRoles();
          setSelectedRole(resp);
        }
      });
    } else {
      dispatch(showLoader());
      updateRoleById(roleDetails, (resp) => {
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
            detail: "The role has been updated successfully",
            life: 3000,
          });
          getRoles();
        }
      });
    }
  };
  const getUsersList = () => {
    dispatch(showLoader());
    fetchUsers((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp?.detail || !!resp?.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setFilteredUsers(resp);
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
        setFilterList(resp);
      }
    });
  };
  useEffect(() => {
    getRoles();
    getUsersList();
    getGroups();
  }, []);

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-5 col-lg-5 ${s.wrapper}`}>
          <Widget
            title={
              <div className="d-flex justify-content-between align-items-center py-2">
                <h5>Roles</h5>
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
                onSelectionChange={(e) => {
                  setSelectedRole(e.value);
                  const { rolepermissions = [], roleusers } = e.value;
                  const userIds = roleusers.map((user) => user.id);
                  const filterUser = filteredUsers.filter((user) =>
                    userIds.includes(user.id)
                  );
                  setSelectedGroups(rolepermissions?.map((item) => item.id));
                  // setSelectedUsersInRole(filterUser);
                  setSelectedUsers(filterUser.map((user) => user.username));
                  setSelectedUsersList(filterUser);
                  setIsRowSelected(true);
                }}
                tableStyle={{ minHeight: "200px" }}
              >
                <Column field="name" header="Name" sortable></Column>
                <Column field="description" header="Description"></Column>
                <Column field="role_type" header="Role type"></Column>
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
              {!!selectedRole ? (
                <div className="row">
                  <div className="col col-md-6">
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Role Name"
                        className={`${
                          submitted && !selectedRole.name ? "is-invalid" : ""
                        }`}
                        controls={{
                          value: selectedRole.name,
                          onChange: (e) => {
                            setSelectedRole({
                              ...selectedRole,
                              name: e.target.value,
                            });
                          },
                          id: "name",
                          tabindex: 1,
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid role name is required!
                        </div>
                      </WizBIInput>
                    </div>
                    <div className="form-group mb-2">
                      <WizBIDropDown
                        labelName="Role Type"
                        panelClass="mb-2 w-100"
                      >
                        <Dropdown
                          filter
                          value={selectedRole.role_type}
                          style={{
                            height: "35px",
                          }}
                          className={`p-0 m-0 custom-conn-drop w-100 d-flex form-control active ${
                            submitted && !selectedRole.role_type
                              ? "border border-danger"
                              : ""
                          }`}
                          options={roleTypes}
                          optionLabel="name"
                          optionValue="name"
                          tabindex={2}
                          onChange={(e) => {
                            setSelectedRole({
                              ...selectedRole,
                              role_type: e.value,
                            });
                          }}
                          placeholder="Select a role type"
                        />
                      </WizBIDropDown>
                    </div>
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Role Description"
                        className={`${
                          submitted && !selectedRole.description
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          type: "textarea",
                          value: selectedRole.description,
                          onChange: (e) => {
                            setSelectedRole({
                              ...selectedRole,
                              description: e.target.value,
                            });
                          },
                          id: "description",
                          tabindex: 1,
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid role description is required!
                        </div>
                      </WizBIInput>
                    </div>
                  </div>
                  <div className="col col-md-6">
                    <div className="form-group mb-2 my-4">
                      {/* <MultiSelect
                        value={selectedUsersInRole}
                        onChange={(e) => setSelectedUsersInRole(e.value)}
                        options={filteredUsers}
                        optionLabel="username"
                        display="chip"
                        placeholder="Select Users"
                        maxSelectedLabels={10}
                        className="w-100 md:w-20rem"
                      /> */}
                      <div style={{ position: "relative" }}>
                        <div
                          style={{
                            zIndex: 10,
                            position: "absolute",
                            top: "-10px",
                            left: "10px",
                            fontSize: 11,
                            color: "#6c757d",
                            background: "white",
                            padding: "1px",
                            pointerEvents: "none",
                          }}
                        >
                          Select Groups
                        </div>
                        <Select
                          mode="multiple"
                          style={{ width: "100%" }}
                          placeholder="Select Groups"
                          onChange={handleGroupSelect}
                          value={selectedGroups}
                        >
                          {groupsList.map((group) => (
                            <Option key={group.id} value={group.id}>
                              {group.name}
                            </Option>
                          ))}
                        </Select>
                      </div>
                      <div style={{ position: "relative", marginTop: "16px" }}>
                        <div
                          style={{
                            zIndex: 10,
                            position: "absolute",
                            top: "-9px",
                            left: "10px",
                            fontSize: 11,
                            color: "#6c757d",
                            background: "white",
                            padding: "1px",
                            pointerEvents: "none",
                          }}
                        >
                          Select Users
                        </div>
                        <Select
                          mode="multiple"
                          style={{ width: "100%" }}
                          placeholder="Select Users"
                          onChange={handleUserSelect}
                          value={selectedUsers}
                        >
                          {selectedUsersList.map((user) => (
                            <Option key={user.username} value={user.username}>
                              {user.username}
                            </Option>
                          ))}
                        </Select>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {!isAddSelected && (
                    <div className="d-flex justify-content-center align-items-center h-100">
                      <h5 className="text-center">
                        Please select a role to see the details
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
