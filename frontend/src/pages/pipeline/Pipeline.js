import React, { useEffect, useMemo, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import {
  createPipeline,
  deletePipeLineById,
  fetchPipelines,
  getPipelineType,
  getScheduleById,
  updateScheduleById,
} from "../../api/pipeLine";
import Widget from "../../components/Widget/Widget";
import s from "./Pipeline.module.scss";
import { confirmDialog } from "primereact/confirmdialog";
import { Toast } from "primereact/toast";
import { Button } from "primereact/button";
import { Dropdown } from "primereact/dropdown";
import ArrowRightIcon from "../../components/Icons/Global/ArrowRightIcon";
import { InputText } from "primereact/inputtext";
import config from "../../assets/data/settings.json";
import WizBIInput from "../../core/WizBIInput/WizBIInput";
import { testConnection } from "../../api/connection";
import {
  NavLink,
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useConnections } from "../../hooks/useConnections";
import { runPipeline } from "../../api/datawarehouse";
import { Sidebar } from "primereact/sidebar";
import { Tooltip } from "primereact/tooltip";
import WizBIDropDown from "../../core/WizBIDropDown/WizBIDropDown";
import debouce from "lodash.debounce";
import { v4 as uuidv4 } from "uuid";
import LogsIcon from "../../components/Icons/Global/LogsIcon";
import AirflowIcon from "../../components/Icons/Global/AirflowIcon";
import { DataView } from "primereact/dataview";
import { createSchedule } from "../../api/jobsAPI";
import { Dialog } from "primereact/dialog";
import cronParser from "cron-parser";
import capitalize from "lodash/capitalize";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";

const Pipeline = () => {
  const isLoading = useSelector((state) => state.loader.loaderVisibility);
  const toast = useRef(null);
  const [visible, setVisible] = useState(false);
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const searchRef = useRef("");
  const resetPipelineInfo = {
    name: "",
    description: "description",
    airflow_pipeline_name: "",
    airflow_pipeline_link: "",
    status: "design",
    source_schema_name: "",
    dest_schema_name: "",
    db_conn_source_id: 0,
    db_conn_dest_id: 0,
    pipeline_type: "ETL",
  };
  const [pipelineInfo, setPipeLineInfo] = useState(resetPipelineInfo);
  const { connectionResult } = useConnections();
  const [sourceSchemaOptions, setSourceSchemaOptions] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [isPipelineCreated, setIsPipelineCreated] = useState(false);
  const [isTargetSchemaNameValid, setIsTargetSchemaNameValid] = useState(false);
  const [scheduleData, setScheduleData] = useState({});
  const [maxRows, setMaxRows] = useState(5);
  const footerContent = (
    <div className="pull-right">
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={(evt) => {
          evt.preventDefault();
          setVisible(false);
        }}
        className="p-button p-component p-button-text text-wizBi mx-2 p-2"
      />
      <Button
        label="Save"
        icon="pi pi-check"
        onClick={(evt) => {
          evt.preventDefault();
          addPipeLine();
        }}
        autoFocus
        badgeClassName={s.sbtBtn}
        className={`p-button p-component mx-2 bg-wizBi p-2 ${s.sbtBtn}`}
        disabled={isPipelineCreated}
      />
    </div>
  );

  const [pipelinesList, setPipeLinesList] = useState([]);
  const [filterPipelinesList, setFilterPipelinesList] = useState([]);
  const [categories, setCategoriest] = useState({});
  const [searchParams, setSearchParams] = useSearchParams();
  const [scheduleShow, setScheduleShow] = useState();
  const [isCronValid, setIsCronValid] = useState(true);
  const [pipelineType, setPipelineType] = useState([]);
  const [isStagingETL, setIsStagingETL] = useState(false);
  const [isDataLake, setIsDataLake] = useState(false);

  const [isSMA, setIsSMA] = React.useState(false);

  const dispatch = useDispatch();

  useEffect(() => {
    if (searchParams.get("filterId") && filterPipelinesList.length) {
      let cKey = searchParams.get("filterId").toLocaleLowerCase();
      filterPipelines(cKey);
      selectCategories(cKey);
    } else {
      setPipeLinesList([]);
      setCategoriest({});
    }
  }, [filterPipelinesList]);

  const navToTarget = (url) => {
    navigate(url);
  };

  const selectCategories = (cKey) => {
    const categoryItems = { ...categories };
    Object.keys(categoryItems).forEach((key) => {
      categories[key].selected = cKey === key ? true : false;
    });
    setCategoriest(categoryItems);
  };

  const filterPipelines = (argVal) => {
    let info = filterPipelinesList;
    if (argVal !== "all") {
      info =
        filterPipelinesList.filter(
          (pInfo) => pInfo.status.toLowerCase().replace(/ /g, "") === argVal
        ) || [];
    }
    setPipeLinesList(info);
  };

  const getPipeLines = () => {
    dispatch(showLoader());
    fetchPipelines(
      { pipeline_type: searchParams.get("pipelineType") },
      (resp) => {
        dispatch(hideLoader());
        if (!!resp && (!!resp.detail || !!resp.message)) {
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          if (resp && resp.length) {
            const categoriesList = {
              all: {
                name: "All",
                count: resp.length,
                selected: true,
              },
            };
            resp.forEach((element) => {
              let objVal = element.status.toLowerCase().replace(/ /g, "");
              if (!categoriesList[objVal]) {
                categoriesList[objVal] = {
                  name: element.status,
                  count: resp.filter(
                    (res) =>
                      res.status.toLowerCase().replace(/ /g, "") === objVal
                  ).length,
                  selected: false,
                };
              }
            });
            setCategoriest(categoriesList);
            return setFilterPipelinesList(resp);
          }
          setFilterPipelinesList([]);
        }
      }
    );
  };

  useEffect(() => {
    getPipeLines();
    const pipelineType = searchParams.get("pipelineType");
    setIsSMA(pipelineType === "SOCIAL_MEDIA");
  }, [searchParams.get("pipelineType")]);

  const handleResize = () => {
    if (document.querySelector("tbody")) {
      const topPos = document
        .querySelector("tbody")
        .getBoundingClientRect().top;
      const available = window.innerHeight - topPos;
      setMaxRows(Math.ceil(available / 145 - 3));
    }
  };
  useEffect(() => {
    // Attach the event listener to the window object
    window.addEventListener("resize", handleResize);

    // Remove the event listener when the component unmounts
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const fetchScheduleById = (item) => {
    dispatch(showLoader());
    setScheduleData({});
    setSubmitted(false);
    getScheduleById(item.id, (response) => {
      dispatch(hideLoader());
      (!response.message || !response.stack) && setScheduleData(response);
      setScheduleShow(true);
    });
  };

  const addPipeLine = () => {
    if (isSMA) {
      if (!pipelineInfo.name || !pipelineInfo.db_conn_source_id) {
        return setSubmitted(true);
      }
    } else {
      if (
        !isStagingETL &&
        !isDataLake &&
        (!pipelineInfo.name ||
          !pipelineInfo.db_conn_dest_id ||
          !pipelineInfo.db_conn_source_id ||
          !pipelineInfo.dest_schema_name ||
          !pipelineInfo.source_schema_name)
      ) {
        return setSubmitted(true);
      }
      if (
        (isStagingETL || isDataLake) &&
        (!pipelineInfo.name ||
          !pipelineInfo.db_conn_dest_id ||
          !pipelineInfo.db_conn_source_id)
      ) {
        return setSubmitted(true);
      }
    }
    if (containsSpecialCharacters(pipelineInfo.name)) {
      return setSubmitted(true);
    }

    setSubmitted(false);
    dispatch(showLoader());
    createPipeline(pipelineInfo, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setIsPipelineCreated(true);
        setIsStagingETL(false);
        toast.current.show({
          severity: "success",
          summary: "Confirmed",
          detail: "The pipeline has been successfully added.",
          life: 3000,
        });
        getPipeLines();
        // setVisible(false);
        setPipeLineInfo(resp);
      }
    });
  };

  const deletePipeLine = (id) => {
    let pipelineId = id;
    confirmDialog({
      message: "Do you want to delete this pipeline?",
      header: "Delete Confirmation",
      icon: "pi pi-info-circle",
      acceptClassName: "p-button-danger",
      accept: () => {
        dispatch(showLoader());
        deletePipeLineById(pipelineId, (resp) => {
          dispatch(hideLoader());
          if (!!resp && (!!resp.detail || !!resp.message)) {
            toast.current.show({
              severity: "error",
              summary: "Error",
              detail: resp.detail || resp.message,
              life: 3000,
            });
          } else {
            toast.current.show({
              severity: "success",
              summary: "Confirmed",
              detail: `The pipeline with the specified ID ${id} has been successfully deleted`,
              life: 3000,
            });
            getPipeLines();
            setVisible(false);
            setPipeLineInfo(resetPipelineInfo);
            setIsStagingETL(false);
          }
        });
      },
    });
  };

  const getSchemas = () => {
    dispatch(showLoader());
    testConnection(pipelineInfo.db_conn_source_id, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setSourceSchemaOptions(resp.databases);
      }
    });
  };

  const getDataTypes = () => {
    dispatch(showLoader());
    getPipelineType((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setPipelineType(resp);
      }
    });
  };

  const getStatusValue = (info) => {
    return ["saved", "design"].includes(info.status.toLowerCase());
  };
  const getSourceDestTemplate = (pipeline, isSource) => {
    if (!connectionResult.length) {
      return <></>;
    }
    const conn =
      connectionResult.find((item) => {
        return (
          item.id ===
          (isSource
            ? pipeline["db_conn_source_id"]
            : pipeline["db_conn_dest_id"])
        );
      }) || null;
    return (
      <>
        <div className="mx-1 d-flex align-items-center">
          <DatabaseIcon.Large database_type={setDTtype(conn)} />
          <p className="mx-2 text-truncate">
            {isSource ? pipeline.source_schema_name : pipeline.dest_schema_name}
            <small className="d-block text-gray" style={{ fontSize: "10px" }}>
              {conn?.db_conn_name}
            </small>
            <small
              className="d-block text-wizBi text-uppercase"
              style={{ fontSize: "10px" }}
            >
              {conn?.db_type}
            </small>
            <small
              className="badge badge-secondary text-center my-2"
              style={{ fontSize: "10px" }}
            >
              {isSource ? "Source System" : "Destination System"}
            </small>
          </p>
        </div>
      </>
    );
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  let filterBySearch = pipelinesList;
  if (searchTerm !== "") {
    filterBySearch = pipelinesList.filter((item) => {
      const value = searchTerm.toLowerCase();
      if (
        item.id.toString().toLowerCase().includes(value) ||
        item.source_schema_name.toLowerCase().includes(value) ||
        item.dest_schema_name.toLowerCase().includes(value) ||
        item.name.toLowerCase().includes(value)
      ) {
        return item;
      }
    });
    dispatch(hideLoader());
    // setPipeLinesList(filterBySearch);
    setTimeout(() => handleResize(), 100);
  }

  const dblActionOnPipelineitem = (evt, item) => {
    evt.preventDefault();
    navigate({
      pathname: "/app/datawarehouse",
      search: `?${createSearchParams({
        pipelineId: item.id,
      })}`,
    });
  };

  const runSchedule = () => {
    dispatch(showLoader());
    if (scheduleData && scheduleData.id) {
      updateScheduleById(
        pipelineInfo.id,
        {
          schedule: scheduleData.schedule,
        },
        (resp) => {
          dispatch(hideLoader());
          if (!!resp && (!!resp.detail || !!resp.message)) {
            toast.current.show({
              severity: "error",
              summary: "Error",
              detail: resp.detail || resp.message,
              life: 3000,
            });
          } else {
            setScheduleShow(false);
            toast.current.show({
              severity: "success",
              summary: "Confirmed",
              detail: "The schedule has been successfully updated and executed",
              life: 3000,
            });
          }
        }
      );
    } else {
      createSchedule(
        {
          pipeline_id: pipelineInfo.id,
          ...scheduleData,
        },
        (resp) => {
          dispatch(hideLoader());
          if (!!resp && (!!resp.detail || !!resp.message)) {
            toast.current.show({
              severity: "error",
              summary: "Error",
              detail: resp.detail || resp.message,
              life: 3000,
            });
          } else {
            setScheduleShow(false);
            toast.current.show({
              severity: "success",
              summary: "Confirmed",
              detail: "The schedule has been successfully executed ",
              life: 3000,
            });
          }
        }
      );
    }
  };

  const runPipelineHandler = (pipeline) => {
    confirmDialog({
      message: `Are you sure you want to run the ETL pipeline "${pipeline.name}"? This action will start the data processing workflow.`,
      header: "Confirm ETL Pipeline Execution",
      icon: "pi pi-exclamation-triangle",
      acceptClassName: "p-button-danger",
      accept: () => {
        dispatch(showLoader());
        const isDatalake = pipeline.pipeline_type
          ?.toLowerCase()
          .includes("spark");

        runPipeline(
          pipeline.id,
          (resp) => {
            dispatch(hideLoader());
            if (!!resp && (!!resp.detail || !!resp.message)) {
              toast.current.show({
                severity: "error",
                summary: "Error",
                detail: resp.detail || resp.message,
                life: 3000,
              });
            } else {
              toast.current.show({
                severity: "success",
                summary: "Success",
                detail: `Pipeline "${pipeline.name}" has been started successfully.`,
                life: 3000,
              });
            }
          },
          isDatalake
        );
      },
      reject: () => {
        // User cancelled - no action needed
      },
    });
  };

  const validateCronExpression = (cronExpression) => {
    try {
      cronParser.parseExpression(cronExpression);
      return true;
    } catch (error) {
      console.error(`Invalid cron expression: ${cronExpression}`);
      console.error(error.message);
      return false;
    }
  };

  const footerScheduleContent = (type) => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text text-wizBi mx-2"
          onClick={() => {
            setScheduleShow(false);
          }}
        />
        <Button
          label="Save"
          icon="pi pi-check"
          badgeClassName={s.sbtBtn}
          className={`bg-wizBi mx-2 ${s.sbtBtn}`}
          autoFocus
          onClick={() => {
            if (
              !scheduleData.schedule ||
              !validateCronExpression(scheduleData.schedule)
            ) {
              setIsCronValid(false);
              return setSubmitted(true);
            }
            setSubmitted(false);
            setIsCronValid(true);
            runSchedule();
          }}
        />
      </div>
    );
  };

  const renderPipeline = (item, index) => {
    //return filterBySearch.map((item, index) => {
    return (
      <Widget
        bodyClass="p-0 py-2"
        className={`my-1 mx-2 ${s.pipelineItem}`}
        key={uuidv4()}
        onDoubleClick={(evt) => {
          dblActionOnPipelineitem(evt, item);
        }}
      >
        <div>
          <div className="d-flex flex-column">
            <h6 className="text-wizBi text-truncate m-0 mx-2 p-2">
              {item.name}
              {
                <span
                  className={`badge mx-4 pull-right ${
                    getStatusValue(item)
                      ? "wizBi-bg-pending"
                      : "wizBi-bg-success"
                  }`}
                >
                  {capitalize(item.status)}
                </span>
              }
            </h6>
            <div className="d-flex align-items-center flex-nowrap justify-content-between">
              <div
                className="d-flex align-items-center justify-content-between"
                style={{ width: "70%" }}
              >
                <div
                  className="mx-2 text-truncate flex-column"
                  style={{ width: "40%" }}
                >
                  {getSourceDestTemplate(item, true)}
                </div>
                <div
                  className="d-flex text-truncate flex-column align-items-center justify-content-center"
                  style={{ width: "20%" }}
                >
                  <small
                    className="text-wizBi text-truncate mx-1"
                    style={{ fontSize: "11px" }}
                  >
                    Pipeline Id : {item.id}
                  </small>
                  <ArrowRightIcon />
                  <small
                    className="text-wizBi mx-1"
                    style={{ fontSize: "11px" }}
                  >
                    {item?.pipeline_type_description || ""}
                  </small>
                </div>
                <div
                  className="mx-2 text-truncate flex-column"
                  style={{ width: "40%" }}
                >
                  {getSourceDestTemplate(item, false)}
                </div>
              </div>
              <div className="d-flex align-items-center justify-content-between">
                <NavLink
                  to={
                    config.isProdAirflow
                      ? config.prod_airflowURL
                      : config.airflowURL
                  }
                  target="_blank"
                  rel="Airflow"
                  className={`d-inline-block pipeline-airflow-icon${index}`}
                  data-pr-tooltip="Navigate to airflow"
                >
                  <Tooltip target={`.pipeline-airflow-icon${index}`} />
                  <AirflowIcon className={s.airflowIcon}></AirflowIcon>
                  {/* </Tooltip> */}
                </NavLink>

                <i
                  className="fa fa-calendar mx-3 schedule-jobs-icon"
                  role="button"
                  onClick={() => {
                    setPipeLineInfo(item);
                    fetchScheduleById(item);
                  }}
                  data-pr-tooltip="Schedule"
                >
                  <Tooltip target=".schedule-jobs-icon" />
                </i>

                <i
                  className={`fa fa-play mx-3 pipeline-run-icon${index}`}
                  role="button"
                  onClick={() => {
                    runPipelineHandler(item);
                  }}
                  data-pr-tooltip="Run Pipeline"
                >
                  <Tooltip target={`.pipeline-run-icon${index}`} />
                </i>

                <i
                  className={`fa fa-cogs mr-3 pipeline-jobs-icon${index}`}
                  role="button"
                  onClick={() => {
                    navToTarget({
                      pathname: "/app/jobs",
                      search: `?${createSearchParams({
                        pipelineId: item.id,
                      })}`,
                    });
                  }}
                  data-pr-tooltip="Jobs"
                >
                  <Tooltip target={`.pipeline-jobs-icon${index}`} />
                </i>
                <span
                  onClick={() => {
                    navToTarget({
                      pathname: "/app/audits",
                      search: `?${createSearchParams({
                        pipelineId: item.id,
                      })}`,
                    });
                  }}
                  role="button"
                  className={`mx-3 pipeline-audits-icon${index}`}
                  data-pr-tooltip="Audits"
                >
                  <Tooltip target={`.pipeline-audits-icon${index}`} />
                  <LogsIcon className={s.menuIcon}></LogsIcon>
                </span>

                <i
                  className={`fa fa-trash mx-3 pipeline-delete-icon${index}`}
                  role="button"
                  onClick={() => {
                    deletePipeLine(item.id);
                  }}
                  data-pr-tooltip="Delete"
                >
                  <Tooltip target={`.pipeline-delete-icon${index}`} />
                </i>

                <i
                  className="fa fa-angle-right fa-2x mx-3"
                  role="button"
                  onClick={(evt) => {
                    evt.preventDefault();
                    navigate({
                      pathname: "/app/datawarehouse",
                      search: `?${createSearchParams({
                        pipelineId: item.id,
                      })}`,
                    });
                  }}
                ></i>
              </div>
            </div>
          </div>
        </div>
      </Widget>
    );

    // })
  };

  const noPipelineMessage = () => {
    return (
      !!filterBySearch.length === 0 &&
      (isLoading ? (
        <li className="list-item d-flex justify-content-center mt-5">
          <h3>Loading ...</h3>
        </li>
      ) : (
        <li className="list-item d-flex justify-content-center mt-5 flex-column align-items-center">
          <span>
            <i className="fa-solid fa-print-magnifying-glass"></i>
          </span>
          <h5>No data available</h5>
          <span>
            Sorry, we couldn't find any results for the search {searchTerm}
          </span>
        </li>
      ))
    );
  };

  // const validateCronValue = (freq) => {
  //     var cronregex = new RegExp(/^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/);
  //     return cronregex.test(freq);
  // }

  const debouncedResults = useMemo(() => {
    return debouce(handleSearch, 600);
  }, []);

  useEffect(() => {
    return () => {
      debouncedResults.cancel();
    };
  });

  const setDTtype = (conn) => {
    let dTYpe = conn.db_type;
    if (conn.db_type) {
      if (conn.db_type.toLowerCase().includes("local")) {
        dTYpe = "lfs";
        return dTYpe;
      }
      if (conn.db_type.toLowerCase().includes("analytics")) {
        dTYpe = "ga";
      }
      if (conn.db_type.toLowerCase().includes("amazon")) {
        dTYpe = "s3";
      }
    }
    return dTYpe;
  };

  const selectedPipelineTemplate = (option, props) => {
    if (option) {
      return (
        <div className="d-flex align-items-center">
          <DatabaseIcon.Small database_type={setDTtype(option)} />
          <div className="mx-3">{option.db_conn_name}</div>
        </div>
      );
    }

    return <span>{props.placeholder}</span>;
  };

  const containsSpecialCharacters = (input) => {
    // Regular expression to match any special characters
    const regex = /[!@#$%^&*()+\-=\[\]{};':"\\|,.<>\/?]/;
    return regex.test(input);
  };
  const pipelineOptionTemplate = (option) => {
    return (
      <div className="d-flex">
        <div className="d-flex align-items-center">
          <DatabaseIcon.Small database_type={setDTtype(option)} />
          <div className="mx-3">{option.db_conn_name}</div>
        </div>
      </div>
    );
  };

  const filterConnections = (connections, criteria, include = true) => {
    return connections.filter((conn) => {
      const dbType = conn.db_type ? conn.db_type.toLowerCase() : "";
      const matches = criteria.some((criterion) =>
        dbType.includes(criterion.toLowerCase())
      );
      return include ? matches || !conn.db_type : !matches;
    });
  };

  const sourceConnectionList = (
    flag,
    criteria = ["amazon", "local", "analytics", "restapi", "LFS", "S3", "GA"]
  ) => {
    return flag
      ? filterConnections(connectionResult, criteria, true)
      : filterConnections(connectionResult, criteria, false);
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <Widget
            title={
              <div className="d-flex align-items-center justify-content-between pb-2">
                <h5 className="py-0">Pipelines</h5>
                <div>
                  <Button
                    severity="info"
                    className="mx-2 bg-wizBi p-2"
                    onClick={(event) => {
                      event.preventDefault();
                      getDataTypes();
                      setSubmitted(false);
                      setVisible(true);
                      setIsPipelineCreated(false);

                      const value = searchParams.get("pipelineType");
                      setPipeLineInfo({
                        ...pipelineInfo,
                        pipeline_type: value,
                        ...(isSMA && { status: "active" }),
                      });
                      setIsDataLake(value.toLowerCase().includes("spark"));
                      setIsStagingETL(value.toLowerCase().includes("elt"));
                    }}
                    aria-controls="popup_menu_left"
                  >
                    <i className="pi pi-plus mx-2"></i> New Pipeline
                  </Button>
                </div>
              </div>
            }
            className={`mb-0 pb-3`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            <div className={`w-100 overflow-auto h-100 px-3`}>
              <div className="p-input-icon-left w-100">
                <i className="pi pi-search global-search-icon" />
                <InputText
                  placeholder="Search for pipeline Id, name, source schema name, destination schema name"
                  style={{ width: "100%", height: "30px" }}
                  onChange={debouncedResults}
                  ref={searchRef}
                />
              </div>
              {Object.keys(categories).length ? (
                <>
                  <div className="col-md-12">
                    {/* <h6 className="font-weight-bold my-2">Categories</h6> */}
                    <ul className="list-group d-flex flex-row flex-wrap gap-1">
                      {Object.keys(categories).map((cKey) => {
                        return (
                          <li
                            className={`list-group-item flex-fill d-flex flex-column align-items-center border-0 my-1 text-capitalize ${
                              categories[cKey].selected ? "" : "bg-none"
                            }`}
                            style={{ width: "150px" }}
                            role="button"
                            key={uuidv4()}
                            onClick={() => {
                              selectCategories(cKey);
                              filterPipelines(cKey);
                              setSearchTerm("");
                              searchRef.current.value = "";
                              navigate({
                                pathname: "/app/pipelines",
                                search: `?${createSearchParams({
                                  filterId: cKey,
                                  pipelineType:
                                    searchParams.get("pipelineType"),
                                })}`,
                              });
                            }}
                          >
                            <small className="d-block text-muted">
                              {categories[cKey].name}
                            </small>
                            <span>{categories[cKey].count}</span>
                          </li>
                        );
                      })}
                    </ul>
                  </div>

                  <div className="col-md-12">
                    <DataView
                      value={filterBySearch}
                      itemTemplate={renderPipeline}
                      paginator
                      rows={maxRows}
                      emptyMessage={noPipelineMessage}
                    />
                  </div>
                </>
              ) : isLoading ? (
                <div className="list-item d-flex justify-content-center mt-5">
                  <h5>Loading ...</h5>
                </div>
              ) : (
                <div className="list-item d-flex justify-content-center mt-5 flex-column align-items-center">
                  <span>
                    <i className="fa-solid fa-print-magnifying-glass"></i>
                  </span>
                  <h5>No data available</h5>
                  <span>Please create a new pipeline to proceed</span>
                </div>
              )}
            </div>
          </Widget>
        </div>
      </div>
      <Toast ref={toast} />
      <Sidebar
        visible={visible}
        position="right"
        onHide={() => setVisible(false)}
        style={{ width: "70%" }}
      >
        {isPipelineCreated ? (
          <div className="list-group">
            <h3 className="text-center d-flex align-items-center justify-content-center text-wizBi my-3">
              <i className="fa fa-code-fork fa-2x mx-2"></i>Pipeline Created
            </h3>
            <Widget
              bodyClass="p-0 py-2"
              className={`my-3 ${s.pipelineItem}`}
              onDoubleClick={(evt) => {
                dblActionOnPipelineitem(evt, pipelineInfo);
              }}
            >
              <div className="d-flex flex-column">
                <h6 className="text-wizBi text-truncate m-0 mx-2 p-2">
                  {pipelineInfo.name}
                  {!pipelineInfo.pipeline_type
                    .toLowerCase()
                    .includes("elt") && (
                    <span
                      className={`badge mx-4 pull-right ${
                        getStatusValue(pipelineInfo)
                          ? "wizBi-bg-pending"
                          : "wizBi-bg-success"
                      }`}
                    >
                      {pipelineInfo.status}
                    </span>
                  )}
                </h6>
                <div className="d-flex align-items-center flex-nowrap justify-content-between">
                  <div
                    className="d-flex align-items-center justify-content-between"
                    style={{ width: "70%" }}
                  >
                    <div className="d-flex mx-2" style={{ width: "40%" }}>
                      {getSourceDestTemplate(pipelineInfo, true)}
                    </div>
                    <div
                      className="d-flex text-truncate flex-column"
                      style={{ width: "20%" }}
                    >
                      {/* <small className="text-wizBi text-truncate">ID : {pipelineInfo.id}</small> */}
                      <small
                        className="text-wizBi text-truncate mx-2"
                        style={{ fontSize: "10px" }}
                      >
                        Pipeline Id : {pipelineInfo.id}
                      </small>
                      <ArrowRightIcon />
                    </div>
                    <div className="d-flex mx-2" style={{ width: "40%" }}>
                      {getSourceDestTemplate(pipelineInfo, false)}
                    </div>
                  </div>
                  <div className="d-flex align-items-center justify-content-between">
                    <NavLink
                      to={
                        config.isProdAirflow
                          ? config.prod_airflowURL
                          : config.airflowURL
                      }
                      target="_blank"
                      rel="Airflow"
                      className="new_pipeline-airflow-icon"
                      data-pr-tooltip="Navigate to airflow"
                    >
                      {/* <Tooltip target='.new_pipeline-airflow-icon'> */}
                      <AirflowIcon className={s.airflowIcon}></AirflowIcon>
                      {/* </Tooltip> */}
                    </NavLink>

                    <i
                      className="fa fa-calendar mx-3 schedule-jobs-icon"
                      role="button"
                      onClick={() => {
                        setPipeLineInfo(pipelineInfo);
                        fetchScheduleById(pipelineInfo);
                      }}
                      data-pr-tooltip="Schedule"
                    >
                      <Tooltip target=".schedule-jobs-icon" />
                    </i>

                    <i
                      className="fa fa-cogs mx-3 new_pipeline-jobs-icon"
                      role="button"
                      onClick={() => {
                        navToTarget({
                          pathname: "/app/jobs",
                          search: `?${createSearchParams({
                            pipelineId: pipelineInfo.id,
                          })}`,
                        });
                      }}
                      data-pr-tooltip="Jobs"
                    >
                      <Tooltip target=".new_pipeline-jobs-icon" />
                    </i>
                    <span
                      onClick={() => {
                        navToTarget("/app/audits");
                      }}
                      role="button"
                      className="new_pipeline-audits-icon mx-3"
                      data-pr-tooltip="Audits"
                    >
                      <Tooltip target=".new_pipeline-audits-icon" />
                      <LogsIcon className={s.menuIcon}></LogsIcon>
                    </span>

                    <i
                      className="fa fa-trash mx-3 new_pipeline-delete-icon"
                      role="button"
                      onClick={() => {
                        deletePipeLine(pipelineInfo.id);
                      }}
                      data-pr-tooltip="Delete"
                    >
                      <Tooltip target=".new_pipeline-delete-icon" />
                    </i>

                    <i
                      className="fa fa-angle-right fa-2x mx-3"
                      role="button"
                      onClick={(evt) => {
                        evt.preventDefault();
                        navigate({
                          pathname: "/app/datawarehouse",
                          search: `?${createSearchParams({
                            pipelineId: pipelineInfo.id,
                          })}`,
                        });
                      }}
                    ></i>
                  </div>
                </div>
              </div>
            </Widget>

            <div className="d-flex justify-content-end mt-5">
              <Button
                icon="pi pi-arrow-left"
                label="Back to Pipelines"
                onClick={(evt) => {
                  evt.preventDefault();
                  setVisible(false);
                  getPipeLines();
                }}
                autoFocus
                badgeClassName={s.sbtBtn}
                className={`bg-wizBi mx-2 w-50`}
              />
            </div>
          </div>
        ) : (
          <>
            {!isSMA ? (
              <>
                <h5 className="mx-4">Create Pipeline</h5>
                <form>
                  <div className="row mt-1 mx-2">
                    {/* <div className="col-md-3 col-lg-3">
                  <div className="form-group mb-2">
                    <WizBIDropDown
                      labelName="Pipeline Type"
                      className={`${
                        submitted && !pipelineInfo.pipeline_type
                          ? "is-invalid"
                          : ""
                      }`}
                    >
                      <Dropdown
                        value={pipelineInfo.pipeline_type}
                        style={{ height: "35px" }}
                        className={`w-100 d-flex form-control custom-conn-drop active  align-items-center ${
                          submitted && !pipelineInfo.pipeline_type
                            ? " border border-danger"
                            : ""
                        }`}
                        onChange={(e) => {
                          const { value = "" } = e || {};
                          setPipeLineInfo({
                            ...pipelineInfo,
                            pipeline_type: value,
                          });
                          setIsDataLake(
                            value.toLowerCase().includes("datalake")
                          );
                          setIsStagingETL(value.toLowerCase().includes("elt"));
                        }}
                        options={pipelineType}
                        optionLabel="description"
                        optionValue="pipeline_type"
                        placeholder="Select a Pipeline Type"
                      />
                      <div
                        className={`invalid-feedback${
                          submitted && !pipelineInfo.pipeline_type
                            ? " d-block"
                            : ""
                        }`}
                      >
                        Please select a pipeline type!
                      </div>
                    </WizBIDropDown>
                  </div>
                </div> */}
                    <div className="col-md-12 col-lg-12">
                      <WizBIInput
                        labelName="Pipeline Name"
                        className={`${
                          submitted &&
                          (!pipelineInfo.name ||
                            containsSpecialCharacters(pipelineInfo.name))
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          value: pipelineInfo.name,
                          onChange: (e) => {
                            setPipeLineInfo({
                              ...pipelineInfo,
                              name: e.target.value,
                            });
                          },
                          id: "name",
                          type: "type",
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid pipeline name is required!
                        </div>
                      </WizBIInput>
                    </div>
                  </div>
                  {!isStagingETL && !isDataLake && (
                    <div className="row  mx-2">
                      <div className="col">
                        <div className="form-group mb-2">
                          <WizBIDropDown
                            labelName="Source DB Connection"
                            className={`${
                              submitted && !pipelineInfo.db_conn_source_id
                                ? "is-invalid"
                                : ""
                            }`}
                          >
                            <Dropdown
                              filter
                              value={pipelineInfo.db_conn_source_id}
                              style={{ height: "35px" }}
                              className={`w-100 d-flex custom-conn-drop form-control active  align-items-center ${
                                submitted && !pipelineInfo.db_conn_source_id
                                  ? " border border-danger"
                                  : ""
                              }`}
                              onChange={(e) =>
                                setPipeLineInfo({
                                  ...pipelineInfo,
                                  db_conn_source_id: e.value,
                                })
                              }
                              options={connectionResult}
                              optionLabel="db_conn_name"
                              optionValue="id"
                              placeholder="Select a Source DB Connection"
                              valueTemplate={selectedPipelineTemplate}
                              itemTemplate={pipelineOptionTemplate}
                            />
                            <div
                              className={`invalid-feedback${
                                submitted && !pipelineInfo.db_conn_source_id
                                  ? " d-block"
                                  : ""
                              }`}
                            >
                              Select a Source DB Connection!
                            </div>
                          </WizBIDropDown>
                        </div>
                      </div>
                      <div className="col">
                        <div className=" row m-0 p-0">
                          <div className="col-md-5 col-lg-5 mt-4 p-0">
                            <Button
                              icon="pi pi-angle-double-right"
                              className="p-button p-component mx-2 bg-wizBi p-2"
                              label="Get Schemas"
                              raised
                              disabled={pipelineInfo.db_conn_source_id === 0}
                              onClick={(evt) => {
                                evt.preventDefault();
                                getSchemas();
                              }}
                            />
                          </div>
                          <div className="col-md-7 col-lg-7 mt-1 p-0">
                            <div className="form-group mb-2">
                              <WizBIDropDown
                                labelName="Source DB Schema"
                                className={`${
                                  submitted && !pipelineInfo.source_schema_name
                                    ? "is-invalid"
                                    : ""
                                }`}
                              >
                                <Dropdown
                                  filter
                                  value={pipelineInfo.source_schema_name}
                                  style={{ height: "35px" }}
                                  className={`w-100 d-flex form-control custom-conn-drop active  align-items-center ${
                                    submitted &&
                                    !pipelineInfo.source_schema_name
                                      ? " border border-danger"
                                      : ""
                                  }`}
                                  onChange={(e) =>
                                    setPipeLineInfo({
                                      ...pipelineInfo,
                                      source_schema_name: e.value,
                                    })
                                  }
                                  options={sourceSchemaOptions}
                                  disabled={!sourceSchemaOptions}
                                  placeholder="Select a source DB Schema"
                                />
                                <div
                                  className={`invalid-feedback${
                                    submitted &&
                                    !pipelineInfo.source_schema_name
                                      ? " d-block"
                                      : ""
                                  }`}
                                >
                                  A valid Source DB Schema is required!
                                </div>
                              </WizBIDropDown>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  {!isStagingETL && !isDataLake && (
                    <div className="row  mx-2">
                      <div className="col">
                        <div className="form-group mb-2">
                          <WizBIDropDown
                            labelName="Target DB Connection"
                            className={`${
                              submitted && !pipelineInfo.db_conn_dest_id
                                ? "is-invalid"
                                : ""
                            }`}
                          >
                            <Dropdown
                              filter
                              value={pipelineInfo.db_conn_dest_id}
                              style={{ height: "35px" }}
                              className={`w-100 d-flex form-control custom-conn-drop active  align-items-center ${
                                submitted && !pipelineInfo.db_conn_dest_id
                                  ? " border border-danger"
                                  : ""
                              }`}
                              onChange={(e) =>
                                setPipeLineInfo({
                                  ...pipelineInfo,
                                  db_conn_dest_id: e.value,
                                })
                              }
                              options={connectionResult}
                              optionLabel="db_conn_name"
                              optionValue="id"
                              placeholder="Select a Target DB Connection"
                              valueTemplate={selectedPipelineTemplate}
                              itemTemplate={pipelineOptionTemplate}
                            />
                            <div
                              className={`invalid-feedback${
                                submitted && !pipelineInfo.db_conn_dest_id
                                  ? " d-block"
                                  : ""
                              }`}
                            >
                              Please select a Target DB connection!
                            </div>
                          </WizBIDropDown>
                        </div>
                      </div>
                      <div className="col">
                        <WizBIInput
                          labelName="Target DB Schema Name"
                          className={`${
                            submitted &&
                            (!pipelineInfo.dest_schema_name ||
                              !isTargetSchemaNameValid)
                              ? "is-invalid"
                              : ""
                          }`}
                          controls={{
                            value: pipelineInfo.dest_schema_name,
                            onChange: (e) => {
                              const re = /^[a-zA-Z0-9_]+$/;
                              setIsTargetSchemaNameValid(
                                re.test(e.target.value)
                              );
                              setPipeLineInfo({
                                ...pipelineInfo,
                                dest_schema_name: e.target.value,
                              });
                            },
                            id: "dest_schema_name",
                            type: "type",
                          }}
                        >
                          <div className="invalid-feedback">
                            A valid Target DB Schema Name is required!
                          </div>
                        </WizBIInput>
                      </div>
                    </div>
                  )}

                  {(isStagingETL || isDataLake) && (
                    <div className="row  mx-2">
                      <div className="col">
                        <div className="form-group mb-2">
                          <WizBIDropDown
                            labelName={
                              isDataLake
                                ? "Apache Iceberg on S3"
                                : "Source Connection (S3, Google, Local FS, Rest API)"
                            }
                            className={`${
                              submitted && !pipelineInfo.db_conn_source_id
                                ? "is-invalid"
                                : ""
                            }`}
                          >
                            <Dropdown
                              filter
                              value={pipelineInfo.db_conn_source_id}
                              style={{ height: "35px" }}
                              className={`w-100 custom-conn-drop d-flex form-control active  align-items-center ${
                                submitted && !pipelineInfo.db_conn_source_id
                                  ? " border border-danger"
                                  : ""
                              }`}
                              onChange={(e) =>
                                setPipeLineInfo({
                                  ...pipelineInfo,
                                  db_conn_source_id: e.value,
                                })
                              }
                              options={
                                isDataLake
                                  ? sourceConnectionList(true, ["iceberg"])
                                  : sourceConnectionList(true)
                              }
                              optionLabel="db_conn_name"
                              optionValue="id"
                              placeholder="Select a Source Connection"
                              valueTemplate={selectedPipelineTemplate}
                              itemTemplate={pipelineOptionTemplate}
                            />
                            <div
                              className={`invalid-feedback${
                                submitted && !pipelineInfo.db_conn_source_id
                                  ? " d-block"
                                  : ""
                              }`}
                            >
                              Please select a source connection!
                            </div>
                          </WizBIDropDown>
                        </div>
                      </div>
                      <div className="col">
                        <div className="form-group mb-2">
                          <WizBIDropDown
                            labelName={
                              isDataLake
                                ? "DuckDB/DBT"
                                : "Staging MySql DB connection"
                            }
                            className={`${
                              submitted && !pipelineInfo.db_conn_dest_id
                                ? "is-invalid"
                                : ""
                            }`}
                          >
                            <Dropdown
                              filter
                              value={pipelineInfo.db_conn_dest_id}
                              style={{ height: "35px" }}
                              className={`w-100 d-flex custom-conn-drop form-control active  align-items-center ${
                                submitted && !pipelineInfo.db_conn_dest_id
                                  ? " border border-danger"
                                  : ""
                              }`}
                              onChange={(e) =>
                                setPipeLineInfo({
                                  ...pipelineInfo,
                                  db_conn_dest_id: e.value,
                                })
                              }
                              options={
                                isDataLake
                                  ? sourceConnectionList(true, ["duckdb"])
                                  : sourceConnectionList(false)
                              }
                              optionLabel="db_conn_name"
                              optionValue="id"
                              placeholder="Select a MySql DB Connection"
                              valueTemplate={selectedPipelineTemplate}
                              itemTemplate={pipelineOptionTemplate}
                            />
                            <div
                              className={`invalid-feedback${
                                submitted && !pipelineInfo.db_conn_dest_id
                                  ? " d-block"
                                  : ""
                              }`}
                            >
                              Please select a MySql DB connection!
                            </div>
                          </WizBIDropDown>
                        </div>
                      </div>
                    </div>
                  )}
                  <footer className={`${s.popupFooter} w-100 px-4`}>
                    <div className="d-flex justify-content-end p-4">
                      {footerContent}
                    </div>
                  </footer>
                </form>
              </>
            ) : (
              <>
                <h5 className="mx-4">Create Pipeline</h5>
                <form>
                  <div className="row mt-1 mx-2">
                    <div className="col-md-12 col-lg-12">
                      <WizBIInput
                        labelName="Pipeline Name"
                        className={`${
                          submitted &&
                          (!pipelineInfo.name ||
                            containsSpecialCharacters(pipelineInfo.name))
                            ? "is-invalid"
                            : ""
                        }`}
                        controls={{
                          value: pipelineInfo.name,
                          onChange: (e) => {
                            setPipeLineInfo({
                              ...pipelineInfo,
                              name: e.target.value,
                            });
                          },
                          id: "name",
                          type: "type",
                        }}
                      >
                        <div className="invalid-feedback">
                          A valid pipeline name is required!
                        </div>
                      </WizBIInput>
                    </div>
                  </div>
                  <div className="row  mx-2">
                    <div className="col">
                      <div className="form-group mb-2">
                        <WizBIDropDown
                          labelName="Source DB Connection"
                          className={`${
                            submitted && !pipelineInfo.db_conn_source_id
                              ? "is-invalid"
                              : ""
                          }`}
                        >
                          <Dropdown
                            filter
                            value={pipelineInfo.db_conn_source_id}
                            style={{ height: "35px" }}
                            className={`w-100 d-flex custom-conn-drop form-control active  align-items-center ${
                              submitted && !pipelineInfo.db_conn_source_id
                                ? " border border-danger"
                                : ""
                            }`}
                            onChange={(e) =>
                              setPipeLineInfo({
                                ...pipelineInfo,
                                db_conn_source_id: e.value,
                              })
                            }
                            options={connectionResult}
                            optionLabel="db_conn_name"
                            optionValue="id"
                            placeholder="Select a Source DB Connection"
                            valueTemplate={selectedPipelineTemplate}
                            itemTemplate={pipelineOptionTemplate}
                          />
                          <div
                            className={`invalid-feedback${
                              submitted && !pipelineInfo.db_conn_source_id
                                ? " d-block"
                                : ""
                            }`}
                          >
                            Select a Source DB Connection!
                          </div>
                        </WizBIDropDown>
                      </div>
                    </div>
                    <div className="col">
                      <h6>
                        <span style={{ fontWeight: "bold" }}>Note:</span>
                        The destination for all the social media connection will
                        be WizBI social Media Analytics Platform.
                      </h6>
                    </div>
                  </div>

                  <footer className={`${s.popupFooter} w-100 px-4`}>
                    <div className="d-flex justify-content-end p-4">
                      {footerContent}
                    </div>
                  </footer>
                </form>
              </>
            )}
          </>
        )}
      </Sidebar>
      <Dialog
        header={
          <div className="d-flex align-items-center" draggable={false}>
            <small className="mx-1 px-1">Schedule</small>
          </div>
        }
        visible={scheduleShow}
        style={{ width: "50vw" }}
        onHide={() => setScheduleShow(false)}
        footer={footerScheduleContent()}
      >
        <div className="form-group mb-2 m-1">
          <div className="fs-0.2">Cron Job Format String</div>
          <WizBIInput
            labelName="Schedule Value"
            className={`${
              submitted && (!scheduleData.schedule || !isCronValid)
                ? "is-invalid"
                : ""
            }`}
            controls={{
              value: scheduleData.schedule,
              onChange: (e) => {
                setScheduleData({ schedule: e.target.value });
              },
              id: "scheduleVal",
            }}
          >
            <div className="invalid-feedback">
              A valid schedule value is required!
            </div>
          </WizBIInput>
        </div>
      </Dialog>
    </>
  );
};

export default Pipeline;
