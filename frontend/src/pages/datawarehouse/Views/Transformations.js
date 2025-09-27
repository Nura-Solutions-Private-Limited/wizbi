import { Dropdown } from "primereact/dropdown";
import ArrowRightIcon from "../../../components/Icons/Global/ArrowRightIcon";
import Widget from "../../../components/Widget/Widget";
import WizBIDropDown from "../../../core/WizBIDropDown/WizBIDropDown";
import WizBIInput from "../../../core/WizBIInput/WizBIInput";
import { PIPELINE_INDEX } from "../Constant";
import { useEffect, useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { Toast } from "primereact/toast";
import { fetchDataTypes } from "../../../api/datawarehouse";
import { hideLoader, showLoader } from "../../../actions/loader";

const Transformations = ({
  pipelineId,
  metaData,
  cloneMetaData,
  isExpanded,
  setCloneMetaData,
  submitted,
  isSaved,
}) => {
  const [dataTypes, setDataTypes] = useState([]);
  const dispatch = useDispatch();
  const toast = useRef(null);

  const fetchDTTypes = () => {
    dispatch(showLoader());
    fetchDataTypes(pipelineId, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        return toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      }
      if (resp.includes("int")) {
        resp[resp.indexOf("int")] = "integer";
      }
      setDataTypes(resp);
    });
  };

  useEffect(() => {
    fetchDTTypes();
  }, []);
  const selectedDatabaseTemplate = (option, props) => {
    if (option) {
      return (
        <div className="d-flex align-items-center">
          <div className="mx-3">{option}</div>
        </div>
      );
    }
    return <span>{props.placeholder}</span>;
  };

  const databaseOptionTemplate = (option) => {
    return (
      <div className="d-flex">
        <div className="d-flex align-items-center">
          <div className="mx-3">{option}</div>
        </div>
      </div>
    );
  };

  const selectMatchedDataType = (mdata, index) => {
    var typeof_data = cloneMetaData[mdata][index].datatype.toLowerCase();
    var dataType = typeof_data.split("(")[0];
    var size = cloneMetaData[mdata][index].length.length;
    if (
      dataType.length + size + 2 === typeof_data.length ||
      /\(([^)]+)\)/.exec(typeof_data) === null
    ) {
      return dataType;
    }
    return "";
  };
  return (
    <>
      <div className="p-4">
        <div className="row">
          {Object.keys(metaData).map((mdata, lindex) => {
            return (
              <div
                className="col-lg-12 col-md-12"
                key={`${lindex}_${cloneMetaData[mdata]}`}
              >
                <Widget
                  collapse
                  collapsed={isExpanded}
                  title={
                    <div className="pb-2 d-flex align-items-center justify-content-between text-black">
                      <h5
                        className="text-capitalize text-wizBi w-100 m-0 p-0"
                        style={{ width: "calc(100% - 50px)" }}
                      >
                        {mdata}
                      </h5>
                    </div>
                  }
                  bodyClass={`m-0 p-0 bg-white`}
                  className={`mb-0 bg-white my-2`}
                >
                  <div className="d-flex row px-3 py-2">
                    {Array.isArray(metaData[mdata]) &&
                      metaData[mdata].map((mInfo, index) => {
                        return (
                          <div
                            key={`${index}_${cloneMetaData[mdata][index].column_name}`}
                          >
                            {index === PIPELINE_INDEX && (
                              <div className="col-md-12 col-lg-12 row">
                                <div className="col-md-4 col-lg-4">
                                  <h5 className="my-0 p-0 text-center text-capitalize text-wizBi py-2">
                                    Source
                                  </h5>
                                </div>
                                <div className="col-md-2 col-lg-2"></div>
                                <div className="col-md-4 col-lg-4">
                                  <h5 className="my-0 p-0 text-center text-capitalize text-wizBi py-2">
                                    Destination DW
                                  </h5>
                                </div>
                              </div>
                            )}
                            <div className="col-md-12 col-lg-12 row">
                              <div className="col-md-4 col-lg-4">
                                <WizBIInput
                                  labelName={mInfo.column_name
                                    .match(/[A-Z]+[^A-Z]*|[^A-Z]+/g)
                                    .join(" ")}
                                  panelClass="my-2 w-100"
                                  controls={{
                                    value: `${
                                      mInfo.source_datatype
                                        ? mInfo.source_datatype
                                        : mInfo.datatype
                                    }`,
                                    disabled: true,
                                    id: mInfo.column_name,
                                  }}
                                />
                              </div>
                              <div className="col-md-2 col-lg-2 mt-3 align-items-center justify-content-center">
                                <ArrowRightIcon />
                              </div>
                              <div className="col-md-4 col-lg-4">
                                <div className="form-group mb-2 row">
                                  <div className="col-md-8 col-lg-8">
                                    <WizBIDropDown
                                      labelName={cloneMetaData[mdata][
                                        index
                                      ].column_name
                                        .match(/[A-Z]+[^A-Z]*|[^A-Z]+/g)
                                        .join(" ")}
                                      className={`${
                                        submitted &&
                                        !metaData[mdata]["data_type"]
                                          ? "is-invalid"
                                          : ""
                                      }`}
                                      panelClass="my-2"
                                      inputClass={`${
                                        isSaved ? "no-action" : ""
                                      }`}
                                    >
                                      <Dropdown
                                        filter
                                        value={selectMatchedDataType(
                                          mdata,
                                          index,
                                        )}
                                        style={{ height: "35px" }}
                                        panelClassName="text-black"
                                        className={`p-0 m-0 custom-conn-drop w-100 d-flex form-control active align-items-center ${
                                          submitted &&
                                          !metaData[mdata]["data_type"]
                                            ? " border border-danger"
                                            : ""
                                        }`}
                                        valueTemplate={selectedDatabaseTemplate}
                                        itemTemplate={databaseOptionTemplate}
                                        onChange={(e) => {
                                          let cloneMdata = {
                                            ...cloneMetaData,
                                          };
                                          if (
                                            !cloneMdata[mdata][index]
                                              .source_datatype
                                          ) {
                                            cloneMdata[mdata][
                                              index
                                            ].source_datatype =
                                              cloneMdata[mdata][index].datatype;
                                          }
                                          cloneMdata[mdata][index].datatype =
                                            !!cloneMetaData[mdata][index].length
                                              ? `${e.value}(${cloneMetaData[mdata][index].length})`
                                              : e.value;
                                          setCloneMetaData({
                                            ...cloneMdata,
                                          });
                                        }}
                                        disabled={isSaved}
                                        options={dataTypes}
                                        tabIndex={2}
                                        placeholder="Select a Datatype"
                                      />
                                      <div
                                        className={`invalid-feedback${
                                          submitted &&
                                          !metaData[mdata]["data_type"]
                                            ? " d-block"
                                            : ""
                                        }`}
                                      >
                                        Please select a datatype type!
                                      </div>
                                    </WizBIDropDown>
                                  </div>
                                  <div className="col-md-4 col-lg-4">
                                    <WizBIInput
                                      labelName=""
                                      panelClass="my-2 w-100"
                                      inputClass={`${
                                        isSaved ? "no-action" : ""
                                      }`}
                                      controls={{
                                        value:
                                          cloneMetaData[mdata][index].length,
                                        style: { width: "100px" },
                                        onChange: (e) => {
                                          let cloneMdata = {
                                            ...cloneMetaData,
                                          };
                                          if (
                                            !cloneMdata[mdata][index]
                                              .source_datatype
                                          ) {
                                            cloneMdata[mdata][
                                              index
                                            ].source_datatype =
                                              cloneMdata[mdata][index].datatype;
                                          }
                                          cloneMdata[mdata][index].length =
                                            e.target.value;
                                          cloneMdata[mdata][index].datatype =
                                            !!e.target.value
                                              ? `${
                                                  cloneMetaData[mdata][
                                                    index
                                                  ].datatype
                                                    .toLowerCase()
                                                    .split("(")[0]
                                                }(${e.target.value})`
                                              : cloneMetaData[mdata][
                                                  index
                                                ].datatype
                                                  .toLowerCase()
                                                  .split("(")[0];
                                          setCloneMetaData(cloneMdata);
                                        },
                                        id: cloneMetaData[mdata][index]
                                          .column_name,
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
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
      <Toast ref={toast} />
    </>
  );
};

export default Transformations;
