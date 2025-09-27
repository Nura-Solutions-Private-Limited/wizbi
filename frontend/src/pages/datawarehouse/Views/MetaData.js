import { Checkbox } from "primereact/checkbox";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import JSONEditorWithValidation from "../../JSONEditor/JSONEditorWithValidation";
import Widget from "../../../components/Widget/Widget";

const MetaData = ({
  metaData,
  setJsonData,
  setMetaData,
  setCloneMetaData,
  onTableSelectionChange,
  jsonData,
  isSaved,
  isExpanded,
  setAttribute,
  setTableDetails,
  setMetaDataValidationVisible,
  jsonView,
  selectedTablesInfo,
}) => {
  return jsonView ? (
    <JSONEditorWithValidation
      data={jsonData}
      onChange={(data) => {
        const response = data ? data : [];
        setJsonData(response);
        setMetaData(response);
        setCloneMetaData(response);
      }}
      isEditable={!isSaved}
    />
  ) : (
    <div className="p-4">
      <div className="row">
        {!!Object.keys(metaData).length &&
          !!Object.keys(metaData) &&
          Object.keys(metaData).map((mdata, index) => {
            return (
              <div
                className="col-lg-12 col-md-12"
                key={`${index}_${mdata}_${index}`}
              >
                <Widget
                  collapse
                  collapsed={isExpanded}
                  fullscreened={false}
                  title={
                    <div className="d-flex align-items-center">
                      <div style={{ width: "calc(100% - 50px)" }}>
                        <small
                          className={`text-muted ${!isSaved ? "mx-2" : ""}`}
                        >
                          Table Name
                        </small>
                        <h5 className="text-capitalize text-wizBi m-0 p-0">
                          {!isSaved && (
                            <span className="mx-2">
                              <Checkbox
                                inputId={mdata}
                                name={mdata}
                                value={mdata}
                                onChange={onTableSelectionChange}
                                checked={selectedTablesInfo.includes(mdata)}
                              />
                            </span>
                          )}
                          {mdata}
                        </h5>
                      </div>
                    </div>
                  }
                  bodyClass={`m-0 p-0 bg-white`}
                  className={`mb-0 bg-white my-2`}
                >
                  <div className="d-flex row p-3">
                    {Array.isArray(metaData[mdata]) &&
                      metaData[mdata].map((mInfo, mIndex) => {
                        return (
                          <div
                            className="col-lg-4 col-md-4 d-flex justify-content-center align-items-center"
                            key={`${mIndex}_${metaData[mdata]}_${mInfo.column_name}`}
                          >
                            {mInfo.type.length > 50 ? (
                              <WizBIInput
                                labelName={
                                  <span className="text-capitalize">
                                    {mInfo.column_name
                                      .match(/[A-Z]+[^A-Z]*|[^A-Z]+/g)
                                      .join(" ")}
                                  </span>
                                }
                                panelClass="my-2 w-100"
                                inputClass={`${isSaved ? "no-action" : ""}`}
                                controls={{
                                  value: mInfo.type,
                                  "data-name": mInfo.type,
                                  "data-table": mdata,
                                  onChange: (e) => {
                                    let wizInfo = { ...metaData };
                                    wizInfo[mdata][mIndex]["type"] =
                                      e.target.value;
                                    setMetaData({ ...wizInfo });
                                    setCloneMetaData({
                                      ...wizInfo,
                                    });
                                  },
                                  id: mInfo.column_name,
                                  type: "textarea",
                                }}
                              ></WizBIInput>
                            ) : (
                              <WizBIInput
                                labelName={
                                  <span className="text-capitalize">
                                    {mInfo.column_name
                                      .match(/[A-Z]+[^A-Z]*|[^A-Z]+/g)
                                      .join(" ")}
                                  </span>
                                }
                                panelClass="my-2 w-100"
                                inputClass={`${isSaved ? "no-action" : ""}`}
                                controls={{
                                  value: mInfo.type,
                                  "data-name": mInfo.type,
                                  "data-table": mdata,
                                  onChange: (e) => {
                                    let wizInfo = { ...metaData };
                                    wizInfo[mdata][mIndex]["type"] =
                                      e.target.value;
                                    setMetaData({ ...wizInfo });
                                    setCloneMetaData({
                                      ...wizInfo,
                                    });
                                  },
                                  id: mInfo.column_name,
                                  type: "text",
                                  style: {
                                    height: "45px",
                                  },
                                }}
                              />
                            )}
                            {!isSaved && (
                              <div
                                type="button"
                                name="delete"
                                className="mx-2"
                                onClick={() => {
                                  const usedIn = document.querySelectorAll(
                                    `[data-name*='${`${mdata}.${mInfo.column_name}`}']`
                                  );
                                  if (usedIn.length) {
                                    let tableDetails = [];
                                    for (let i = 0; i < usedIn.length; i++) {
                                      if (
                                        !tableDetails.includes(
                                          usedIn[i].dataset.table
                                        )
                                      ) {
                                        tableDetails.push(
                                          usedIn[i].dataset.table
                                        );
                                      }
                                    }
                                    setAttribute(mInfo.column_name);
                                    setTableDetails(tableDetails);
                                    setMetaDataValidationVisible(true);
                                    return;
                                  }
                                  const metaInfo = {
                                    ...metaData,
                                  };
                                  metaInfo[mdata].splice(mIndex, 1);
                                  setMetaData({ ...metaInfo });
                                  setCloneMetaData({
                                    ...metaInfo,
                                  });
                                }}
                              >
                                <i
                                  className="fa fa-trash text-black"
                                  role="button"
                                ></i>
                              </div>
                            )}
                          </div>
                        );
                      })}
                  </div>
                </Widget>
              </div>
            );
          })}
        {!Object.keys(metaData).length && (
          <h5 className="d-flex align-items-center justify-content-center">
            No Properties available
          </h5>
        )}
      </div>
    </div>
  );
};

export default MetaData;
