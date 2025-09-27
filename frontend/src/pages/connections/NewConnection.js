import React from "react";

import { Toast } from "primereact/toast";
import Widget from "../../components/Widget/Widget";
import s from "./NewConnection.module.scss";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";

import { fetchDatabaseTypes } from "../../api/databasesAPI";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch } from "react-redux";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Database } from "./types/Database";
import RestAPI from "./RestAPI";
import DuckDBConnectionForm from "./DuckDBConnectionForm";
import IcebergConnectionForm from "./IcebergConnectionForm";
import { DataAnalytics } from "./types/DataAnalytics";
import CSV from "./types/Csv";
import SocialMedia from "./types/SocialMedia";

// Helper function to determine if a connector type is social media
const isSocialMediaConnection = (connectorType) => {
  const socialMediaTypes = ["X", "Facebook", "Instagram", "LinkedIn", "TikTok"];
  return socialMediaTypes.includes(connectorType);
};

export const NewConnection = () => {
  const childRef = React.useRef(null);
  const toast = React.useRef(null);
  const dispatch = useDispatch();
  const [databaseTypes, setDatabaseTypes] = React.useState([]);
  const [selectedDatabase, setSelectedDatabase] = React.useState(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [submitted, setSubmitted] = React.useState(false);
  const [selectedConnection, setSelectedConnection] = React.useState(null);
  const navigate = useNavigate();

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
        const db_type = searchParams.get("connector_type");
        const sub_type = searchParams.get("sub_type");

        const item = resp.find(
          (item) =>
            item.connector_type === db_type &&
            (sub_type ? item.sub_type === sub_type : true)
        );
        setSelectedDatabase(item);
      }
    });
  };
  React.useEffect(() => {
    getDatabaseTypes();
  }, []);

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
          {isSocialMediaConnection(selectedDatabase?.connector_type) 
            ? "Create Connection & Pipeline" 
            : "Create Connection"}
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
            <div className={`w-100`} style={{ height: "calc(100% + 100px)" }}>
              {selectedDatabase?.type.toLowerCase().includes("database") && (
                <Database
                  submitted={submitted}
                  connection={selectedConnection}
                  setSelectedConnection={setSelectedConnection}
                  ref={childRef}
                  toast={toast}
                  connection_id={selectedConnection?.id}
                />
              )}
              {selectedDatabase?.type.toLowerCase().includes("duckdb") && (
                <DuckDBConnectionForm
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connection_id={selectedConnection?.id}
                />
              )}

              {selectedDatabase?.type.toLowerCase().includes("iceberg") && (
                <IcebergConnectionForm
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connection_id={selectedConnection?.id}
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
                  connection_id={selectedConnection?.id}
                />
              )}
              {isSocialMediaConnection(selectedDatabase?.connector_type) && Array.isArray(databaseTypes) && (
                <SocialMedia
                  ref={childRef}
                  toast={toast}
                  callback={saveOrUpdateConnection}
                  connection_id={selectedConnection?.id}
                  databaseTypes={databaseTypes}
                />
              )}

              {["s3", "GDRIVE", "lfs", "LFS", "S3"].includes(db_type) && (
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
