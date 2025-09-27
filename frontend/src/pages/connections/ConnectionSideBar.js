import React from "react";
import { Button } from "primereact/button";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";
import { Sidebar } from "primereact/sidebar";
import DatabaseTypes from "./DatabaseTypes";
import { useNavigate } from "react-router-dom";
import { getDatabaseTypes } from "../../api/databasesAPI";
import { useQuery } from "@tanstack/react-query";

export const ConnectionSideBar = () => {
  const {
    data: databaseTypes,
    isLoading,
    error,
  } = useQuery({ queryKey: "databases", queryFn: getDatabaseTypes });
  const [visible, setVisible] = React.useState(false);
  const navigate = useNavigate();
  const itemRenderer = (item) => (
    <div className="p-menuitem-content">
      <a
        className="flex align-items-center p-menuitem-link"
        href={`/app/new_connection?database_type=${item.icon}`}
      >
        <DatabaseIcon.Small database_type={item.icon} />
        <h6>
          {item.label}
          <small className="d-block" style={{ fontSize: "10px" }}>
            {item.type}
          </small>
        </h6>
      </a>
    </div>
  );

  if (isLoading) {
    return (
      <div className="list-item d-flex justify-content-center mt-5">
        <h5>Loading ...</h5>
      </div>
    );
  }

  const items = databaseTypes?.map((item) => {
    return {
      label: item.description,
      icon: item.connector_type,
      type: item.type,
      template: itemRenderer,
    };
  });

  const handleDatabaseSelection = (information) => {
    const subTypeQueryParams = information.sub_type
      ? `&sub_type=${information.sub_type}`
      : "";
    navigate(
      `/app/new_connection?connector_type=${information.connector_type}${subTypeQueryParams}`
    );
  };

  return (
    <>
      <Button
        severity="info"
        className="mx-2 bg-wizBi p-2"
        onClick={(event) => setVisible(true)}
        aria-controls="popup_menu_left"
      >
        <i className="pi pi-plus mx-2"></i> New Connection
      </Button>

      <Sidebar
        visible={visible}
        position="right"
        onHide={() => setVisible(false)}
        style={{ width: "70%", color: "red" }}
        title="Select a connection type"
      >
        <DatabaseTypes onSelection={handleDatabaseSelection} />
      </Sidebar>
    </>
  );
};
