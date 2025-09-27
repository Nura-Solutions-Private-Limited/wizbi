import { useSelector } from "react-redux";
import {
  TRANSFORMATION_INDEX,
} from "./Constant";

const Footer = ({
  index,
  isStagingETL,
  isSaved,
  selectedTablesInfo,
  pipeLineId,
  deleteSelectedMetaDataTable,
  prevTabIndex,
  saveMetaInfo,
  proceedToDataWarehouse,
  isRunETL,
  getDataWarehousePhase,
  status,
  isDataLake,
  isSMA,
}) => {
  const isLoading = useSelector((state) => state.loader.loaderVisibility);

  const currentPhase = getDataWarehousePhase(index);

  if (isSMA) {
    return (
      <footer className={`popupFooter w-100 px-3`}>
        <div className="d-flex justify-content-end p-2">
          <button
            className="p-button p-component mx-2 bg-wizBi p-2"
            onClick={(evt) => proceedToDataWarehouse(evt)}
          >
            <i className="fa fa-arrow-right mx-2" />
            Run Pipeline
          </button>
        </div>
      </footer>
    );
  }
  return (
    <footer className={`popupFooter w-100 px-3`}>
      <div className="d-flex justify-content-end p-2">
        {isStagingETL ? (
          <>
            <button
              className="p-button p-component mx-2 bg-wizBi p-2"
              onClick={(evt) => {
                evt.preventDefault();
                prevTabIndex();
              }}
              disabled={currentPhase.pipelinePhase}
            >
              <i className="fa fa-arrow-left mx-2"> </i>Back
            </button>
            <button
              className="p-button p-component mx-2 bg-wizBi p-2"
              onClick={(evt) => {
                currentPhase.metaDataPhase && saveMetaInfo();
                currentPhase.pipelinePhase && proceedToDataWarehouse(evt);
              }}
              disabled={
                !pipeLineId ||
                isRunETL ||
                isLoading ||
                (!currentPhase.pipelinePhase && status === "Active")
              }
            >
              {currentPhase.pipelinePhase && (
                <i className="fa fa-arrow-right mx-2" />
              )}
              {currentPhase.pipelinePhase ? "Next" : "Save"}
            </button>
          </>
        ) : (
          <>
            {!!selectedTablesInfo.length && (
              <>
                <button
                  className="p-button p-component mx-2 bg-wizBi p-2"
                  onClick={(evt) => {
                    evt.preventDefault();
                    deleteSelectedMetaDataTable();
                  }}
                >
                  <i className="fa fa-trash mx-2"> </i>Delete
                  <span className="mx-2 badge badge-warning">
                    {selectedTablesInfo.length}
                  </span>
                </button>
              </>
            )}
            <button
              className="p-button p-component mx-2 bg-wizBi p-2"
              onClick={(evt) => {
                evt.preventDefault();
                prevTabIndex();
              }}
              disabled={currentPhase.pipelinePhase}
            >
              <i className="fa fa-arrow-left mx-2"> </i>Back
            </button>

            <button
              className="p-button p-component mx-2 bg-wizBi p-2"
              onClick={(evt) => {
                evt.preventDefault();
                saveMetaInfo();
              }}
              disabled={currentPhase.pipelinePhase || isSaved}
            >
              <i className="fa fa-save mx-2"> </i>Save
            </button>
          </>
        )}

        {((isStagingETL && index === 1) || !isStagingETL) && (
          <button
            className="p-button p-component mx-2 bg-wizBi p-2"
            onClick={(evt) => proceedToDataWarehouse(evt)}
            disabled={
              !pipeLineId ||
              isRunETL ||
              isLoading ||
              (isStagingETL && currentPhase.metaDataPhase && !isSaved)
            }
          >
            {isStagingETL ? (
              <i className="fa fa-upload mx-2" />
            ) : (
              <i className="fa fa-arrow-right mx-2" />
            )}
            {(currentPhase.pipelinePhase ||
              currentPhase.metaDataPhase ||
              (currentPhase.transformationPhase && isSaved)) &&
            !isStagingETL
              ? isDataLake && currentPhase.metaDataPhase
                ? "Setup Datalake"
                : "Continue"
              : isStagingETL
                ? "Create and Load Staging Database"
                : index === TRANSFORMATION_INDEX && !isSaved
                  ? "Create Data Warehouse"
                  : "Run Pipeline - Execute ETL ..."}
          </button>
        )}
      </div>
    </footer>
  );
};

export default Footer;
