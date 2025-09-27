import { Dialog } from "primereact/dialog";
import { Link } from "react-router-dom";

const DataWareHousePopup = ({
  visible,
  onHide,
  response,
  pipelineId,
  tableDetails,
  attribute,
  componentName,
}) => {
  return (
    <Dialog
      header="Info"
      visible={visible}
      style={{ width: "50vw" }}
      resizable={false}
      draggable={false}
      onHide={onHide}
    >
      {attribute && (
        <p className="m-0">
          The "<span style={{ "font-weight": "bold" }}>{attribute}</span>"
          attribute is used in the following tables and cannot be deleted until
          it has no dependencies in other tables
          <ui className="font-weight-bold">
            {tableDetails.map((tName) => {
              return <li className="text-capitalize text-wizBi">{tName}</li>;
            })}
          </ui>
        </p>
      )}

      {componentName === "etl" && (
        <p className="m-0">
          To track the ETL running process, Please navigate to JOBS section by
          clicking on link JOB id
          <Link to={`/app/jobs?pipelineId=${pipelineId}`}>
            {response.job_id}
          </Link>
        </p>
      )}

      {componentName === "dataUpload" && (
        <p className="m-0">
          {response.status}, Please navigate to JOBS section by clicking on link
          JOB id
          <Link to={`/app/jobs?pipelineId=${pipelineId}`}>
            {response.job_id}
          </Link>
        </p>
      )}
    </Dialog>
  );
};

export default DataWareHousePopup;
