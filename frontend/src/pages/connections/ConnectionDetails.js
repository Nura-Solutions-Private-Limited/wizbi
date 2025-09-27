import React from "react";
import Widget from "../../components/Widget/Widget";
import s from "./NewConnection.module.scss";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";

import { fetchDatabaseTypes } from "../../api/databasesAPI";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch } from "react-redux";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Database } from "./types/Database";
import RestAPI from "./RestAPI";
import DuckDBConnectionForm from "./DuckDBConnectionForm";
import IcebergConnectionForm from "./IcebergConnectionForm";
import { DataAnalytics } from "./types/DataAnalytics";
import { fetchConnections } from "../../api/connection";
import { Toast } from "primereact/toast";
import CSV from "./types/Csv";
import SocialMedia from "./types/SocialMedia";

export const ConnectionDetails = () => {
  const childRef = React.useRef(null);
  const toast = React.useRef(null);
  const dispatch = useDispatch();
  const [databaseTypes, setDatabaseTypes] = React.useState([]);
  const [selectedDatabase, setSelectedDatabase] = React.useState(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedConnection, setSelectedConnection] = React.useState(null);
  const navigate = useNavigate();
  const { id } = useParams();
  const db_type = searchParams.get("connector_type");
  const getDatabaseTypes = () => {
    dispatch(showLoader());
    fetchDatabaseTypes((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp?.detail || !!resp?.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setDatabaseTypes(Array.isArray(resp) ? resp : []);

        const db_type = searchParams.get("connector_type").toLowerCase();
        const sub_type = searchParams.get("sub_type");
        const item = resp.find(
          (database) =>
            database.connector_type.toLowerCase().includes(db_type) &&
            (sub_type ? database.sub_type === sub_type : true)
        );
        setSelectedDatabase(item);
        getConnections();
      }
    });
  };
  React.useEffect(() => {
    getDatabaseTypes();
  }, []);


  const getConnections = () => {
    dispatch(showLoader());
    fetchConnections((resp) => {
      dispatch(hideLoader());
      // setLoading(false);
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        // setConnectionsList(resp);
        // setSelectedConnection(null);
        const findConnection = resp.find(
          (connection) => connection.id === parseInt(id)
        );
        setSelectedConnection(findConnection);
      }
    });
  };

  const header = (
    <div className="d-flex align-items-center">
      <button
        className="p-button p-component mx-2 bg-none p-2 text-black  border-0"
        onClick={(evt) => {
          evt.preventDefault();
          navigate("/app/connections");
        }}
      >
        <i className="fa  fa-angle-left mx-2"> </i>Back
      </button>
      <DatabaseIcon.Large database_type={selectedDatabase?.connector_type} />
      <h5>
        {selectedDatabase?.description}
        <small className="d-block" style={{ fontSize: "10px" }}>
          {selectedDatabase?.type}
        </small>
      </h5>
    </div>
  );

  const footer = (
    <footer className={`popupFooter w-100 px-3`}>
      <div className="d-flex justify-content-end p-2">
        <button
          className="p-button p-component mx-2 bg-wizBi p-2"
          onClick={(evt) => {
            evt.preventDefault();
            childRef.current.createConnection();
          }}
        >
          Update Connection
        </button>
      </div>
    </footer>
  );

  const saveOrUpdateConnection = () => {
    navigate("/app/connections");
  };
  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 p-0 px-3 m-0 ${s.wrapper}`}>
          <Widget
            title={header}
            className={`mb-0 background-white pb-3`}
            bodyClass={`m-0 pt-0 ${s.widgetBodyClass}`}
          >
            {/* <DatabaseTypes onSelection={handleDatabaseSelection} /> */}
            <div className={`w-100 h-100`}>
              {selectedDatabase?.type.toLowerCase().includes("database") && (
                <Database
                  connectionDetails={selectedConnection}
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                />
              )}
              {selectedDatabase?.type.toLowerCase().includes("duckdb") && (
                <DuckDBConnectionForm
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connectionDetails={selectedConnection}
                  // toast={toast}
                  // filesList={filesList}
                  // fetchFiles={fetchFiles}
                  // dispatch={dispatch}
                  // connectionLoading={connectionLoading}
                  // connectionTesting={connectionTesting}
                />
              )}

              {selectedDatabase?.type.toLowerCase().includes("iceberg") && (
                <IcebergConnectionForm
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connectionDetails={selectedConnection}
                />
              )}
              {selectedDatabase?.type.toLowerCase().includes("restapi") && (
                <RestAPI
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connection_id={selectedConnection?.id}
                  databaseTypes={databaseTypes}
                />
              )}

              {selectedDatabase?.type
                .toLowerCase()
                .includes("data analytics") && (
                <DataAnalytics
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connectionDetails={selectedConnection}
                />
              )}

              {(selectedDatabase?.connector_type === "X" || 
                selectedDatabase?.connector_type === "Facebook" || 
                selectedDatabase?.connector_type === "Instagram" || 
                selectedDatabase?.connector_type === "LinkedIn" || 
                selectedDatabase?.connector_type === "TikTok") && Array.isArray(databaseTypes) && (
                <SocialMedia
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connection_id={selectedConnection?.id}
                  databaseTypes={databaseTypes}
                />
              )}

              {["s3", "GDRIVE", "lfs", "LFS"].includes(db_type) && (
                <CSV
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connectionDetails={selectedConnection}
                />
              )}
            </div>

            {footer}
          </Widget>
        </div>
      </div>
      <Toast ref={toast} />
    </>
  );
};
