import { Dropdown } from "primereact/dropdown";
import WizBIDropDown from "../../../core/WizBIDropDown/WizBIDropDown";
import { TextWizBi } from "../Components/TextWizBi";

const extractDetails = (id, connectionResult = []) => {
  const connection = connectionResult.find((conn) => conn.id === id) ?? {
    db_conn_name: "",
  };
  return connection.db_conn_name;
};

const PipeLineTemplate = ({
  pipelinesResult,
  pipelineInfo,
  onPipelineChange,
}) => {
  return (
    <div className="row">
      <div className="col-5">
        <div className="form-group mb-2">
          <WizBIDropDown labelName="Pipeline">
            <Dropdown
              filter
              value={pipelineInfo}
              style={{ height: "35px" }}
              className="w-100 d-flex form-control active align-items-center"
              onChange={onPipelineChange}
              options={pipelinesResult}
              optionLabel="name"
              placeholder="Select a Pipeline"
            />
          </WizBIDropDown>
        </div>
      </div>
    </div>
  );
};

const Pipeline = ({
  pipelineInfo,
  isStagingETL,
  onPipelineChange,
  connectionResult,
  pipelinesResult,
}) => {
  return (
    <div className="p-4">
      <PipeLineTemplate
        pipelinesResult={pipelinesResult ?? []}
        pipelineInfo={pipelineInfo}
        onPipelineChange={onPipelineChange}
      />

      {isStagingETL ? (
        <div className="row">
          <div className="col-5">
            <TextWizBi
              label="Source DB Connection"
              value={extractDetails(
                pipelineInfo.db_conn_source_id,
                connectionResult
              )}
            />
            <TextWizBi
              label="Target DB Connection"
              value={extractDetails(
                pipelineInfo.db_conn_dest_id,
                connectionResult
              )}
            />
          </div>
        </div>
      ) : (
        <div className="row">
          <div className="col-5">
            <TextWizBi
              label="Source DB Connection"
              value={extractDetails(
                pipelineInfo.db_conn_source_id,
                connectionResult
              )}
            />
            <TextWizBi
              label="Target DB Connection"
              value={extractDetails(
                pipelineInfo.db_conn_dest_id,
                connectionResult
              )}
            />
            <TextWizBi label="Status" value={pipelineInfo.status} />
          </div>

          <div className="col-5">
            <TextWizBi
              label="Source DB Schema Name"
              value={pipelineInfo.source_schema_name}
            />
            <TextWizBi
              label="Target DB Schema Name"
              value={pipelineInfo.dest_schema_name}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Pipeline;
