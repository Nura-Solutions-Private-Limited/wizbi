import React, { useEffect, useRef, useState } from "react";
import Widget from "../../components/Widget/Widget";
import s from "./DataWarehouse.module.scss";
import { usePipelines } from "../../hooks/usePipelines";
import { useConnections } from "../../hooks/useConnections";
import { getMetaData } from "../../api/pipeLine";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch } from "react-redux";
import { Toast } from "primereact/toast";
import {
  genDWFromSource,
  runPipeline,
  saveMetaData,
} from "../../api/datawarehouse";
import {
  Link,
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { confirmDialog } from "primereact/confirmdialog";
import { RadioButton } from "primereact/radiobutton";
import FileHandler from "../JSONEditor/FileHandler";
import tabsInfoCollection from "./data/tabsData.json";
import Header from "./Header";
import { isDraftStatus } from "./Utils/utils";
import {
  METADATA_INDEX,
  PIPELINE_INDEX,
  SUMMARY_VIEW_INDEX,
  TRANSFORMATION_INDEX,
} from "./Constant";
import { useActiveTab } from "./useActiveTab";
import Footer from "./Footer";
import Pipeline from "./Views/Pipeline";
import Summary from "./Views/Summary";
import MetaData from "./Views/MetaData";
import Transformations from "./Views/Transformations";
import DataWareHousePopup from "./Views/DataWareHousePopup";
import TransformationsETL from "./Views/TransformationsETL";
import { cloneDeep } from "lodash";
import RestAPIMetaData from "./Views/RestAPIMetaData";

const DataWarehouse = () => {
  const [submitted, setSubmitted] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const resetPipelineInfo = {
    name: "",
    description: "description",
    airflow_pipeline_name: "airflow_pipeline_name",
    airflow_pipeline_link: "airflow_pipeline_link",
    status: "",
    source_schema_name: "",
    dest_schema_name: "",
    db_conn_source_id: 0,
    db_conn_dest_id: 0,
  };
  const [tabsInfo, setTabInfo] = useState(tabsInfoCollection);
  const [pipelineInfo, setPipeLineInfo] = useState(resetPipelineInfo);
  const [metaData, setMetaData] = useState([]);
  const [cloneMetaData, setCloneMetaData] = useState([]);
  const { pipelinesResult } = usePipelines({ pipeline_status: "" });
  const { connectionResult } = useConnections();
  const dispatch = useDispatch();
  const toast = useRef(null);
  const [index, setIndex] = useState(0);
  const [searchParams, setSearchParams] = useSearchParams();
  const [isSaved, setIsSaved] = useState(false);
  const [isRunETL, setIsRunETL] = useState(false);

  const [isRestAPI, setIsRestAPI] = useState(false);

  const [metaDataValidationVisible, setMetaDataValidationVisible] =
    useState(false);
  const [isETLRunning, setIsETLRunning] = useState(false);
  const [tableDetails, setTableDetails] = useState([]);
  const [attribute, setAttribute] = useState("");
  const [isStagingETL, setIsStagingETL] = useState(false);
  const [isDataLake, setIsDatalake] = useState(false);
  const [isDataUploadStarted, setIsDataUploadStarted] = useState(false);

  const [selectedTablesInfo, setSelectedTablesInfo] = useState([]);

  const navigate = useNavigate();
  const [response, setResponse] = useState({});
  const navToTarget = (url) => {
    navigate(url);
  };

  // Data Lake
  const [selectedTypesDataLake, setSelectedTypesDataLake] = useState([]);

  // ETL
  const [selectedTypesETL, setSelectedTypesETL] = useState([]);

  const etlCollection = tabsInfoCollection.reduce(
    (acc, td) => (!td.isStaging ? [...acc, { ...td, index: acc.length }] : acc),
    []
  );

  const smaCollection = tabsInfoCollection.reduce(
    (acc, td) => (!td.isSMA ? [...acc, { ...td, index: acc.length }] : acc),
    []
  );

  const [jsonView, setJsonView] = useState(false);

  const [jsonData, setJsonData] = useState({});

  const { activeTabIndex, prevTabIndex } = useActiveTab(
    tabsInfo,
    setTabInfo,
    setIndex,
    index
  );

  const handleFileUpload = (data) => {
    setJsonData(data);
    setMetaData(data);
    setCloneMetaData(data);
  };

  const handleRestAPI = ({ db_conn_source_id }) => {
    const conn = extractDetails(db_conn_source_id, connectionResult);
    if (conn && conn?.db_type?.length) {
      setIsRestAPI(conn.db_type.toLowerCase().includes("restapi"));
    }
  };

  useEffect(() => {
    if (searchParams.get("pipelineId") && pipelinesResult.length) {
      const info = pipelinesResult.find(
        (pInfo) => pInfo.id === parseInt(searchParams.get("pipelineId"))
      );
      const pipelineDetails = info ?? pipelineInfo;
      setPipeLineInfo(pipelineDetails);
      handleRestAPI(pipelineDetails);
      setIsRunETL(false);
      setIsSaved(isDraftStatus(info));
      if (
        info.pipeline_type &&
        (info.pipeline_type.toLocaleLowerCase().includes("elt") ||
          info.pipeline_type.toLocaleLowerCase().includes("datalake"))
      ) {
        setIsDatalake(
          info.pipeline_type.toLocaleLowerCase().includes("datalake")
        );
        setIsStagingETL(info.pipeline_type.toLocaleLowerCase().includes("elt"));
        setTabInfo(etlCollection);
      } else {
        setIsStagingETL(false);
        setIsDatalake(false);

        const isSMA = info.pipeline_type === "SOCIAL_MEDIA";
        if (isSMA) {
          setTabInfo(smaCollection);
        } else {
          setTabInfo(tabsInfoCollection);
        }
      }
    }
  }, [pipelinesResult, connectionResult]);

  const ativeTabIndex = () => {
    const dataInfo = cloneDeep(tabsInfo);
    const currentIndex = tabsInfo.findIndex((info) => {
      return info.index === index + 1;
    });
    if (currentIndex != -1) {
      dataInfo[currentIndex].active = true;
      dataInfo[currentIndex].completed = false;
      setIndex(index + 1);
    }

    const prevIndex = tabsInfo.findIndex((info) => {
      return info.index === index;
    });

    if (prevIndex != -1) {
      dataInfo[prevIndex].active = false;
      dataInfo[prevIndex].completed = true;
    }
    setTabInfo(dataInfo);
  };

  const getDataWarehousePhase = (index) => {
    return {
      pipelinePhase: index === PIPELINE_INDEX,
      metaDataPhase: index === METADATA_INDEX,
      transformationPhase: index === TRANSFORMATION_INDEX,
      summaryPhase: index === SUMMARY_VIEW_INDEX,
    };
  };

  const currentPhase = getDataWarehousePhase(index);

  const saveMetaInfo = () => {
    //ativeTabIndex();
    dispatch(showLoader());
    const params = index === METADATA_INDEX ? metaData : cloneMetaData;

    let body = params;
    if (isStagingETL && !isRestAPI) {
      body = { files: selectedTypesETL };
    }

    if (isDataLake) {
      body = { model_mappings: selectedTypesDataLake };
    }
    saveMetaData(pipelineInfo.id, body, (resp) => {
      handleAPIResponse(
        resp,
        "The pipeline metadata has been saved successfully",
        () => {
          setIsSaved(isStagingETL && currentPhase.metaDataPhase);
        }
      );
    });
  };

  const fetchMetaData = () => {
    dispatch(showLoader());
    getMetaData(pipelineInfo.id, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        const message = resp.detail || resp.message;
        handleError(message);
      } else {
        setMetaData({ ...resp });
        setCloneMetaData(JSON.parse(JSON.stringify(resp)));
      }
    });
  };

  const handleError = (message) => {
    toast.current.show({
      severity: "error",
      summary: "Error",
      detail: message,
      life: 3000,
    });
  };

  const handleAPIResponse = (response, message, successCallback) => {
    dispatch(hideLoader());
    const isFailed = !!response && (!!response?.detail || !!response?.message);
    const text = isFailed ? response.detail || response.message : message;
    if (isFailed) {
      handleError(text);
    } else {
      toast.current.show({
        severity: "success",
        summary: "Success",
        detail: text,
        life: 3000,
      });
      if (successCallback) {
        successCallback();
      }
    }
  };

  const proceedToDataWarehouse = (evt) => {
    evt.preventDefault();
    const isSMA = pipelineInfo.pipeline_type === "SOCIAL_MEDIA";
    if (isSMA) {
      return confirmDialog({
        message:
          "This action will start the ETL data load, do you want to continue?",
        header: "Are you sure you want to proceed ?",
        icon: "pi pi-info-circle",
        acceptClassName: "p-button-danger",
        accept: () => {
          dispatch(showLoader());
          runPipeline(pipelineInfo.id, (resp) => {
            handleAPIResponse(
              resp,
              "Successfully started the ETL execution",
              () => {
                dispatch(hideLoader());
                setIsRunETL(true);
                // ativeTabIndex();
                const info = pipelineInfo;
                info.status = "running";
                setPipeLineInfo(info);
                setIsSaved(isDraftStatus(info));
                setIsETLRunning(true);
                setResponse(resp);
              }
            );
          });
        },
        reject: () => {
          return "";
        },
      });
    }

    if (index === TRANSFORMATION_INDEX && !isSaved) {
      confirmDialog({
        message:
          "Once the data warehouse is created, associated pipelines, database connections, and the data warehouse itself cannot be modified!",
        header: "Are you sure you want to proceed?",
        icon: "pi pi-info-circle",
        acceptClassName: "p-button-danger",
        accept: () => {
          dispatch(showLoader());
          genDWFromSource(pipelineInfo.id, cloneMetaData, (resp) => {
            handleAPIResponse(
              resp,

              "The Data Warehouse has been successfully created",
              () => {
                const clonePipelineInfo = { ...pipelineInfo };
                clonePipelineInfo.status = "Ready for ETL";
                setPipeLineInfo(clonePipelineInfo);
                setIsSaved(isDraftStatus(clonePipelineInfo));
                ativeTabIndex();
              }
            );
          });
        },
        reject: () => {
          return "";
        },
      });
    } else if (index === PIPELINE_INDEX) {
      ativeTabIndex();

      if ((!isStagingETL && !isDataLake) || isRestAPI) {
        fetchMetaData();
      }
    } else if (index === METADATA_INDEX) {
      ativeTabIndex();
    } else if (index === SUMMARY_VIEW_INDEX) {
      confirmDialog({
        message:
          "This action will start the ETL data load, do you want to continue?",
        header: "Are you sure you want to proceed ?",
        icon: "pi pi-info-circle",
        acceptClassName: "p-button-danger",
        accept: () => {
          dispatch(showLoader());
          runPipeline(pipelineInfo.id, (resp) => {
            handleAPIResponse(
              resp,
              "Successfully started the ETL execution",
              () => {
                setIsRunETL(true);
                ativeTabIndex();
                const info = pipelineInfo;
                info.status = "running";
                setPipeLineInfo(info);
                setIsSaved(isDraftStatus(info));
                setIsETLRunning(true);
                setResponse(resp);
              }
            );
          });
        },
        reject: () => {
          return "";
        },
      });
    } else if (
      (isSaved && !isStagingETL) ||
      (isStagingETL && index === PIPELINE_INDEX)
    ) {
      ativeTabIndex();
    }
    if (
      (isStagingETL || isDataLake) &&
      index === 1 &&
      currentPhase.metaDataPhase
    ) {
      confirmDialog({
        message: `Once the ${
          isDataLake ? "datalake" : "staging database"
        } is created or updated, exist data can be replaced!`,
        header: "Are you sure you want to proceed?",
        icon: "pi pi-info-circle",
        acceptClassName: "p-button-danger",
        accept: () => {
          dispatch(showLoader());
          runPipeline(
            pipelineInfo.id,
            (resp) => {
              handleAPIResponse(resp, resp.status, () => {
                const clonePipelineInfo = { ...pipelineInfo };
                setPipeLineInfo(clonePipelineInfo);
                setIsSaved(isDraftStatus(clonePipelineInfo));
                ativeTabIndex();
                setIsDataUploadStarted(true);
                setResponse(resp);
              });
            },
            isDataLake
          );
        },
        reject: () => {
          return "";
        },
      });
    }
  };

  const deleteSelectedMetaDataTable = () => {
    confirmDialog({
      message: "Do you want to delete these selected Table?",
      header: "Delete Confirmation",
      icon: "pi pi-info-circle",
      acceptClassName: "p-button-danger",
      accept: () => {
        const metaInfo = { ...metaData };
        let flag = true;
        selectedTablesInfo.forEach((mdata) => {
          metaInfo[mdata].forEach((item) => {
            const usedIn = document.querySelectorAll(
              `[data-name*='${`${mdata}.${item.column_name}`}']`
            );
            if (usedIn.length) {
              let tableDetails = [];
              for (let i = 0; i < usedIn.length; i++) {
                if (
                  !tableDetails.includes(usedIn[i].dataset.table) &&
                  !selectedTablesInfo.includes(usedIn[i].dataset.table)
                ) {
                  tableDetails.push(usedIn[i].dataset.table);
                }
              }
              if (tableDetails.length) {
                setTableDetails(tableDetails);
                setAttribute(item.column_name);
                setMetaDataValidationVisible(true);
                flag = false;
                return;
              }
            }
          });
        });

        if (flag) {
          selectedTablesInfo.forEach((mdata) => {
            delete metaInfo[mdata];
          });
          setMetaData({ ...metaInfo });
          setCloneMetaData({ ...metaInfo });
          setSelectedTablesInfo([]);
        }
      },
    });
  };

  const onTableSelectionChange = (e) => {
    let _selectedTablesInfo = [...selectedTablesInfo];
    if (e.checked) _selectedTablesInfo.push(e.value);
    else _selectedTablesInfo.splice(_selectedTablesInfo.indexOf(e.value), 1);
    setSelectedTablesInfo(_selectedTablesInfo);
  };

  const extractDetails = (id, connectionResult = []) => {
    const connection = connectionResult.find((conn) => conn.id === id) ?? {
      db_conn_name: "",
    };
    return connection;
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <Widget
            title={
              <>
                <Header
                  isStagingETL={isStagingETL}
                  pipelineInfo={pipelineInfo}
                  tabsInfo={tabsInfo}
                  isDataLake={isDataLake}
                />
                <div className="d-flex justify-content-end">
                  {index === METADATA_INDEX && !isStagingETL && !isDataLake && (
                    <div className="d-flex align-items-center my-3">
                      <div className="d-flex align-items-center">
                        <RadioButton
                          inputId="formView"
                          name="format"
                          value="formView"
                          onChange={(e) => setJsonView(false)}
                          checked={!jsonView}
                        />
                        <label htmlFor="formView" className="mx-2">
                          Form View
                        </label>
                      </div>
                      <div className="d-flex align-items-center">
                        <RadioButton
                          inputId="jsonVIew"
                          name="format"
                          value="jsonVIew"
                          onChange={(e) => {
                            setJsonView(true);
                            setJsonData({ ...metaData });
                          }}
                          checked={jsonView}
                        />
                        <label htmlFor="jsonVIew" className="mx-2">
                          JSON View
                        </label>
                      </div>
                      {jsonView && (
                        <FileHandler
                          onUpload={handleFileUpload}
                          data={metaData}
                          isEditable={isSaved}
                        />
                      )}
                    </div>
                  )}

                  {[METADATA_INDEX, TRANSFORMATION_INDEX].includes(index) &&
                    !jsonView &&
                    !isDataLake &&
                    !isStagingETL && (
                      <div className="d-flex align-items-center my-3 space-evenly">
                        <button
                          className="p-button p-component mx-2 bg-wizBi p-2"
                          onClick={(evt) => {
                            evt.preventDefault();
                            setIsExpanded(!isExpanded);
                          }}
                        >
                          {isExpanded ? (
                            <>
                              <i className="fa fa-angle-up mx-2"> </i>Expand All
                            </>
                          ) : (
                            <>
                              <i className="fa fa-angle-down mx-2"> </i>
                              Collapse All
                            </>
                          )}
                        </button>
                      </div>
                    )}
                </div>
              </>
            }
            className={`mb-0`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass} ${s.adjustHeight}`}
          >
            <div className={`w-100 h-100`}>
              {/* Pipeline View */}
              {index === PIPELINE_INDEX && (
                <Pipeline
                  pipelineInfo={pipelineInfo}
                  isStagingETL={isStagingETL}
                  onPipelineChange={(e) => {
                    handleRestAPI(e.value);
                    setPipeLineInfo(e.value);
                    setIsSaved(isDraftStatus(e.value));
                    setIsRunETL(false);
                    if (isStagingETL) {
                      setMetaData([]);
                      setCloneMetaData([]);
                      setJsonView(false);
                      setJsonData([]);
                    } else {
                      navToTarget({
                        pathname: "/app/datawarehouse",
                        search: `?${createSearchParams({
                          pipelineId: e.value.id,
                        })}`,
                      });
                    }
                    if (
                      e.value.pipeline_type &&
                      e.value.pipeline_type.toLocaleLowerCase().includes("elt")
                    ) {
                      setIsStagingETL(true);
                      setTabInfo(etlCollection);
                    } else {
                      setIsStagingETL(false);
                      setTabInfo(tabsInfoCollection);
                    }
                    if (isStagingETL) {
                      navToTarget({
                        pathname: "/app/datawarehouse",
                        search: `?${createSearchParams({
                          pipelineId: e.value.id,
                        })}`,
                      });
                    } else {
                      setMetaData([]);
                      setCloneMetaData([]);
                    }
                  }}
                  connectionResult={connectionResult}
                  pipelinesResult={pipelinesResult}
                />
              )}
              {/* Metadata View */}
              {index === METADATA_INDEX &&
                (!isStagingETL && !isDataLake ? (
                  <MetaData
                    metaData={metaData}
                    setJsonData={setJsonData}
                    setMetaData={setMetaData}
                    setCloneMetaData={setCloneMetaData}
                    onTableSelectionChange={onTableSelectionChange}
                    jsonData={jsonData}
                    isSaved={isSaved}
                    isExpanded={isExpanded}
                    setAttribute={setAttribute}
                    setTableDetails={setTableDetails}
                    setMetaDataValidationVisible={setMetaDataValidationVisible}
                    jsonView={jsonView}
                    selectedTablesInfo={selectedTablesInfo}
                  />
                ) : isRestAPI ? (
                  <RestAPIMetaData
                    // setJsonData={setJsonData}
                    setMetaData={setMetaData}
                    // setCloneMetaData={setCloneMetaData}
                    metaData={metaData}
                    isSaved={isSaved}
                    toast={toast}
                  />
                ) : (
                  <TransformationsETL
                    pipelineInfo={pipelineInfo}
                    selectedTypesETL={selectedTypesETL}
                    setSelectedTypesETL={setSelectedTypesETL}
                    selectedTypesDataLake={selectedTypesDataLake}
                    setSelectedTypesDataLake={setSelectedTypesDataLake}
                    metaData={metaData}
                    isDataLake={isDataLake}
                  />
                ))}
              {/* Transformation View */}
              {index === TRANSFORMATION_INDEX && (
                <Transformations
                  pipelineId={pipelineInfo.id}
                  metaData={metaData}
                  cloneMetaData={cloneMetaData}
                  isExpanded={isExpanded}
                  setCloneMetaData={setCloneMetaData}
                  submitted={submitted}
                  isSaved={isSaved}
                />
              )}
              {/* Summary View */}
              {index === SUMMARY_VIEW_INDEX && (
                <Summary pipelineInfo={pipelineInfo} />
              )}

              <Footer
                index={index}
                isStagingETL={isStagingETL}
                isSMA={pipelineInfo.pipeline_type === "SOCIAL_MEDIA"}
                isDataLake={isDataLake}
                isSaved={isSaved}
                selectedTablesInfo={selectedTablesInfo}
                pipeLineId={pipelineInfo.id}
                deleteSelectedMetaDataTable={deleteSelectedMetaDataTable}
                prevTabIndex={prevTabIndex}
                saveMetaInfo={saveMetaInfo}
                proceedToDataWarehouse={proceedToDataWarehouse}
                isRunETL={isRunETL}
                getDataWarehousePhase={getDataWarehousePhase}
                status={pipelineInfo?.status}
              />
            </div>
          </Widget>
        </div>
      </div>
      <Toast ref={toast} />

      <DataWareHousePopup
        visible={metaDataValidationVisible}
        onHide={() => {
          setMetaDataValidationVisible(false);
        }}
        tableDetails={tableDetails}
        attribute={attribute}
      />
      <DataWareHousePopup
        visible={isETLRunning}
        onHide={() => {
          setIsETLRunning(false);
        }}
        response={response}
        pipelineId={pipelineInfo.id}
        componentName="etl"
      />
      <DataWareHousePopup
        visible={isDataUploadStarted}
        onHide={() => {
          setIsDataUploadStarted(false);
        }}
        response={response}
        pipelineId={pipelineInfo.id}
        componentName="dataUpload"
      />
    </>
  );
};

export default DataWarehouse;
