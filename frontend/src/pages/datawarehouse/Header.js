import { Divider } from "primereact/divider";
import { Tooltip } from "primereact/tooltip";
import { v4 as uuidv4 } from "uuid";
import { isDraftStatus } from "./Utils/utils";

const Title = ({ title, subTitle }) => {
  return (
    <h5>
      {title}
      <small className="d-block mx-1" style={{ fontSize: "10px", minWidth: "80px" }}>
        {subTitle}
      </small>
    </h5>
  );
};

const Header = ({ isStagingETL, pipelineInfo, tabsInfo, isDataLake }) => {
  let title = "Data Warehouse";
  let subTitle = "Create data warehouse to move data from any source";

  if(isDataLake){
    title = "Data Lake";
    subTitle = "Create data lake";
  } else if(isStagingETL){
    title = "Staging Database";
    subTitle = "Create and load data into cloud from any CSV sources";
  } 
  return (
    <div className="d-flex justify-content-between align-items-center">
        <Title
          title={title}
          subTitle={subTitle}
        />

      <Divider layout="vertical" />
      {pipelineInfo && pipelineInfo.name && (
        <>
          <Tooltip target=".custom-target-icon" />
          <h5
            style={{ width: "30%" }}
            className="text-truncate custom-target-icon"
            data-pr-tooltip={`${pipelineInfo.name}_(${pipelineInfo.id})`}
            data-pr-position="right"
            data-pr-at="right+5 top"
            data-pr-my="left center-2"
          >
            Name : {`${pipelineInfo.name}`}
            <small className="d-block my-1" style={{ fontSize: "12px" }}>
              ID : {pipelineInfo.id}
            </small>
            <small className="d-block my-1" style={{ fontSize: "12px" }}>
              Status :
              <span
                className={` badge ${
                  isDraftStatus(pipelineInfo)
                    ? "wizBi-bg-success"
                    : "wizBi-bg-pending"
                }`}
              >
                {pipelineInfo.status}
              </span>
            </small>
          </h5>
          <Divider layout="vertical" />
        </>
      )}

      {tabsInfo && (
        <div className="custom-stepper w-100">
          <div className="row mx-3">
            <ul className="breadcrumb m-0">
              {tabsInfo.map((tab) => {
                return (
                  <li
                    className={`${tab.active ? "active" : ""} ${
                      tab.completed ? "completed" : ""
                    }`}
                    key={uuidv4()}
                  >
                    <a href="javascript:void(0);">{tab.name}</a>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default Header;
