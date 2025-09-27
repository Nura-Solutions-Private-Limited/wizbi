import { useEffect, useRef, useState } from "react";
import Widget from "../../../components/Widget/Widget";
import s from "./Groups.module.scss";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import {
  addGroup,
  deleteGroupById,
  fetchGroups,
  updateGroupById,
} from "../../../api/groups";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import { Toast } from "primereact/toast";
import { fetchUsers } from "../../../api/users";
import { confirmDialog } from "primereact/confirmdialog";
import { MultiSelect } from "primereact/multiselect";

export const Groups = () => {
  const toast = useRef(null);
  const dispatch = useDispatch();
  const [isRowSelected, setIsRowSelected] = useState(false);
  const [isAddSelected, setIsAddSelected] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [groupsList, setGroupsList] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const resetGroupDetails = {
    name: "",
    id: 0,
    description: "",
    userlist: [],
  };
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [selectedUsersInGroup, setSelectedUsersInGroup] = useState(null);

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
  useEffect(() => {
    getGroups();
    getUsersList();
  }, []);

  const addGroupEnabled = () => {
    setIsAddSelected(true);
    setSelectedGroup(resetGroupDetails);
  };
  const accept = () => {
    dispatch(showLoader());
    deleteGroupById(selectedGroup.id, (resp) => {
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
          detail: "The group has been successfully deleted",
          life: 3000,
        });
        getGroups();
        reset();
      }
    });
  };
  const deleteGroup = () => {
    confirmDialog({
      message: "Do you want to delete this record?",
      header: "Delete Confirmation",
      icon: "pi pi-info-circle",
      acceptClassName: "p-button-danger",
      accept,
    });
  };

  const reset = () => {
    setIsAddSelected(false);
    setIsRowSelected(false);
    setSubmitted(false);
    setSelectedGroup(null);
    setSelectedUsersInGroup(null);
  };
  const saveGroup = () => {
    if (!selectedGroup.name || !selectedGroup.description) {
      return setSubmitted(true);
    }
    setSubmitted(false);
    dispatch(showLoader());
    let groupDetails = {
      ...selectedGroup,
      userlist: selectedUsersInGroup.map((user) => user.id),
    };
    if (isAddSelected) {
      addGroup(groupDetails, (resp) => {
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
            detail: "The group has been added successfully",
            life: 3000,
          });
          getGroups();
          reset();
        }
      });
    } else {
      updateGroupById(groupDetails, (resp) => {
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
            detail: "The group has been updated successfully",
            life: 3000,
          });
          getGroups();
          reset();
        }
      });
    }
  };

  const header = () => {
    return (
      <>
        <span>
          <Button
            severity="info"
            className="mx-2 bg-wizBi p-2"
            onClick={() => addGroupEnabled()}
            disabled={isAddSelected || isRowSelected}
          >
            <i className="pi pi-plus mx-2"></i> Add
          </Button>
          <Button
            severity="danger"
            className="mx-2 p-2"
            onClick={() => deleteGroup()}
            disabled={!isRowSelected}
          >
            <i className="pi pi-trash mx-2"></i> Delete
          </Button>
          <Button
            severity="success"
            className="mx-2 p-2 wizBi-bg-success"
            onClick={() => saveGroup()}
            disabled={(!isRowSelected && !isAddSelected) || !selectedGroup}
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

  const customBodyTemplate = (dTableInfo, props) => {
    if (props.field === "users") {
      return dTableInfo.users?.map((user) => user.username).join(",");
    }
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-5 col-lg-5 ${s.wrapper}`}>
          <Widget
            title={
              <div className="d-flex justify-content-between align-items-center py-2">
                <h5>Groups</h5>
              </div>
            }
            className={`mb-0`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            <div
              className={`w-100 px-4 py-2 ${
                groupsList.length === 0 ? "" : "h-100"
              }`}
            >
              <DataTable
                value={groupsList}
                rowSelection={true}
                selectionMode="single"
                selection={selectedGroup}
                onSelectionChange={(e) => {
                  setSelectedGroup(e.value);
                  const userIds = e.value.users.map((user) => user.user_id);
                  const filterUser = filteredUsers.filter((user) =>
                    userIds.includes(user.id),
                  );
                  setSelectedUsersInGroup(filterUser);
                  setIsRowSelected(true);
                }}
                dataKey="id"
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
                tableStyle={{ minHeight: "200px" }}
                rowHeight={10}
              >
                <Column field="name" header="Name" sortable></Column>
                <Column field="description" header="Description"></Column>
                <Column
                  field="users"
                  header="Users"
                  body={customBodyTemplate}
                ></Column>
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
              {!!selectedGroup ? (
                <div className="row">
                  <div className="col col-md-6">
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Group Name"
                        className={`${
                          submitted && !selectedGroup.name ? "is-invalid" : ""
                        }`}
                        controls={{
                          value: selectedGroup.name,
                          onChange: (e) => {
                            setSelectedGroup({
                              ...selectedGroup,
                              name: e.target.value,
                            });
                          },
                          id: "name",
                          tabindex: 1,
                        }}
                      >
                        
                        <div className="invalid-feedback">
                          A valid group name is required!
                        </div>
                      </WizBIInput>
                    </div>
                    <div className="form-group mb-2">
                      <WizBIInput
                        labelName="Group Description"
                        className={`${
                          submitted && !selectedGroup.description
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          type: "textarea",
                          value: selectedGroup.description,
                          onChange: (e) => {
                            setSelectedGroup({
                              ...selectedGroup,
                              description: e.target.value,
                            });
                          },
                          id: "description",
                          tabindex: 1,
                        }}
                      >
                        
                        <div className="invalid-feedback">
                          A valid group description is required!
                        </div>
                      </WizBIInput>
                    </div>
                  </div>
                  <div className="col col-md-6">
                    <div className="form-group mb-2 my-4">
                      <MultiSelect
                        value={selectedUsersInGroup}
                        onChange={(e) => setSelectedUsersInGroup(e.value)}
                        options={filteredUsers}
                        optionLabel="username"
                        display="chip"
                        placeholder="Select Users"
                        maxSelectedLabels={10}
                        className="w-100 md:w-20rem"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {!isAddSelected && (
                    <div className="d-flex justify-content-center align-items-center h-100">
                      <h5 className="text-center">
                        
                        Please select a group to see the details
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
