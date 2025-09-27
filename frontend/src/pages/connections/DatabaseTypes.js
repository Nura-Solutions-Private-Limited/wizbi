import React, { useEffect, useRef, useState } from "react";
import Widget from "../../components/Widget/Widget";
import { fetchDatabaseTypes } from "../../api/databasesAPI";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch } from "react-redux";
import { v4 as uuidv4 } from "uuid";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";

const DatabaseTypes = ({ onSelection }) => {
  const toast = useRef(null);
  const dispatch = useDispatch();
  const [databaseTypes, setDatabaseTypes] = useState([]);

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
      }
    });
  };
  useEffect(() => {
    getDatabaseTypes();
  }, []);

  return (
    <div className="row w-100 d-flex align-content-center">
      {Array.isArray(databaseTypes) && databaseTypes.map((databaseItem) => {
        return (
          <div
            style={{ width: "250px", minHeight: "70px" }}
            className="py-0 px-0 mb-2 list-group"
            key={uuidv4()}
          >
            <Widget
              bodyClass="p-0 py-2 mx-2 d-flex align-items-center p-menuitem-link"
              className={`my-1 mx-3 list-group-item`}
              role="button"
              onClick={(evt) => {
                evt.preventDefault();
                onSelection(databaseItem);
              }}
            >
              <DatabaseIcon.Large database_type={databaseItem.connector_type} />
              <h6>
                {databaseItem.description}
                <small className="d-block" style={{ fontSize: "10px" }}>
                  {databaseItem.type}
                </small>
              </h6>
            </Widget>
          </div>
        );
      })}
    </div>
  );
};
export default DatabaseTypes;
