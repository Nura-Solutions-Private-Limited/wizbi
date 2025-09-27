import React from "react";
import Widget from "../../components/Widget/Widget";
import s from "./Databases.module.scss";
import databaseTypes from "../../assets/data/databaseType.json";
import { Divider } from "primereact/divider";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";
const Databases = (props) => {
  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <Widget
            title={
              <>
                <div className="px-4 d-flex justify-content-between align-items-center">
                  <h5>
                    Databases
                    <small className="d-block" style={{ fontSize: "12px" }}>
                      Type of databases
                    </small>
                  </h5>
                </div>
                <Divider />
              </>
            }
            className={`mb-0`}
            bodyClass={`p-0 ${s.widgetBodyClass}`}
          >
            <div className={`w-100 h-100 `}>
              {databaseTypes.map((dbType) => {
                return (
                  <Widget
                    bodyClass={s.databseWidget}
                    className="bg-white text-black pull-left mx-4 mb-2"
                  >
                    <div className={`w-100 h-100`}>
                      <div className="d-flex align-items-center justify-content-center">
                        <DatabaseIcon.Large database_type={dbType.icon} />
                      </div>
                      <div className="mx-3 text-center my-2">{dbType.name}</div>
                    </div>
                  </Widget>
                );
              })}
            </div>
          </Widget>
        </div>
      </div>
    </>
  );
};

export default Databases;
