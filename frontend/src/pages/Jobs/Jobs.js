import React, { useEffect, useRef, useState } from "react";
import Widget from "../../components/Widget/Widget";
import s from "./Jobs.module.scss";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch } from "react-redux";
import { createSchedule, getJobs } from "../../api/jobsAPI";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { usePipelines } from "../../hooks/usePipelines";
import { runPipeline } from "../../api/datawarehouse";
import { confirmDialog } from "primereact/confirmdialog";
import {
  NavLink,
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import WizBIInput from "../../core/WizBIInput/WizBIInput";
import { Toast } from "primereact/toast";
import AirflowIcon from "../../components/Icons/Global/AirflowIcon";
import config from "../../assets/data/settings.json";
import { getScheduleById, updateScheduleById } from "../../api/pipeLine";
import cronParser from "cron-parser";
import { useQuery, useQueryClient } from "@tanstack/react-query";

const Jobs = () => {
  const [pagination, setPagination] = useState({ page: 1, size: 50 }); // page = 1-based
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["jobs", pagination],
    queryFn: getJobs,
    keepPreviousData: true,
  });

  const onPage = (event) => {
    setPagination({
      page: event.page + 1, // PrimeReact is 0-based, your API is 1-based
      size: event.rows,
    });
  };

  const [loading, setLoading] = useState(true);
  const [jobsList, setJobsList] = useState([]);
  const [filterList, setFilterList] = useState([]);
  const toast = useRef(null);
  const dispatch = useDispatch();
  const [scheduleShow, setScheduleShow] = useState();
  const [submitted, setSubmitted] = useState();
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
  const [pipelineInfo, setPipeLineInfo] = useState(resetPipelineInfo);

  const [scheduleData, setScheduleData] = useState({});
  const [isCronValid, setIsCronValid] = useState(true);
  const [maxRows, setMaxRows] = useState(10);

  const handleResize = () => {
    const topPos = document
      .querySelector(".p-datatable-tbody")
      .getBoundingClientRect().top;
    const available = window.innerHeight - topPos;
    setMaxRows(Math.ceil(available / 50 - 2));
  };
  useEffect(() => {
    // Attach the event listener to the window object
    window.addEventListener("resize", handleResize);
    // Remove the event listener when the component unmounts
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

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

  const customBodyTemplate = (dTableInfo, props) => {
    let str = "";
    switch (props.field) {
      case "startDT":
        let startDT = new Date(dTableInfo.start_time);
        str =
          startDT.toLocaleString("en-GB", {
            weekday: "long",
            day: "numeric",
            month: "long",
          }) +
          " " +
          new Intl.DateTimeFormat("en-GB", {
            hour12: true,
            hour: "numeric",
            minute: "numeric",
          }).format(startDT);
        break;
      case "endDT":
        let endDT = new Date(dTableInfo.end_time);
        str =
          endDT.toLocaleString("en-GB", {
            weekday: "long",
            day: "numeric",
            month: "long",
          }) +
          " " +
          new Intl.DateTimeFormat("en-GB", {
            hour12: true,
            hour: "numeric",
            minute: "numeric",
          }).format(endDT);
        break;

      case "status":
        str =
          dTableInfo.status.toLowerCase().indexOf("success") !== -1 ? (
            <span className={`badge mx-4 wizBi-bg-success`}>
              {dTableInfo.status}
            </span>
          ) : (
            <span className={`badge mx-4 wizBi-bg-pending`}>
              {dTableInfo.status}
            </span>
          );
        break;
      // case "logs":
      //     str = <NavLink to={`/app/logs?pipelineId=${dTableInfo.pipeline_id}`}>Logs</NavLink>
      //     break;
      case "audits":
        str = (
          <NavLink to={`/app/audits?pipelineId=${dTableInfo.pipeline_id}`}>
            Audits
          </NavLink>
        );
        break;
      case "airflow":
        str = (
          <NavLink
            to={
              config.isProdAirflow ? config.prod_airflowURL : config.airflowURL
            }
            target="_blank"
            rel="Airflow"
            className={`d-inline-block jobs-airflow-icon d-flex justify-content-center align-items-center`}
            data-pr-tooltip="Navigate to airflow"
          >
            {/* <Tooltip target={`.pipeline-airflow-icon${index}`}> */}
            <AirflowIcon className={s.airflowIcon}></AirflowIcon>
            {/* </Tooltip> */}
          </NavLink>
        );
        break;
    }
    return str;
  };

  const setFilterListDetails = (id) => {
    const filterList = jobsList.filter((job) => job.pipeline_id === id);
    setFilterList(filterList);
    setTimeout(() => handleResize(), 100);
  };

  const navigate = useNavigate();

  const navToTarget = (url) => {
    navigate(url);
  };

  // const validateCronValue = (freq) => {
  //     var cronregex = new RegExp(/^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/);
  //     return cronregex.test(freq);
  // }

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
              detail: "Successfully updated and ran the schedule",
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
              detail: "The schedule has been successfully run",
              life: 3000,
            });
          }
        }
      );
    }
  };

  const footerScheduleContent = () => {
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

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <Widget
            title={
              <>
                <div className="d-flex justify-content-between align-items-center py-2">
                  <h5>Jobs</h5>
                  <Button
                    icon="pi pi-refresh"
                    className="p-button-text p-button-sm"
                    onClick={() => {
                      queryClient.invalidateQueries(["jobs"]);
                    }}
                    tooltip="Refresh data"
                    tooltipOptions={{ position: 'left' }}
                  />
                </div>
              </>
            }
            className={`mb-0`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            <div
              className={`w-100 px-4 py-2 h-100`}
            >
              <DataTable
                value={data?.items || []}
                lazy
                paginator
                totalRecords={data?.total || 0}
                first={(pagination.page - 1) * pagination.size}
                rows={pagination.size}
                onPage={onPage}
                loading={isLoading}
                // value={filterList}
                rowSelection
                selectionMode="single"
                emptyMessage={
                  loading ? (
                    <h5 className="d-flex justify-content-center">
                      Loading ...
                    </h5>
                  ) : (
                    <h5 className="d-flex justify-content-center">
                      No Jobs available
                    </h5>
                  )
                }
                // paginator
                // rows={maxRows}
                // loadingIcon={<Loader />}
                onSelectionChange={(e) => console.log(e.value)}
                tableStyle={{ minHeight: "200px", fontSize:'0.88rem' }}
              >
                <Column field="job_id" header="JOB ID" sortable></Column>
                <Column
                  field="startDT"
                  header="Start Time"
                  body={customBodyTemplate}
                ></Column>
                <Column
                  field="endDT"
                  header="End Time"
                  body={customBodyTemplate}
                ></Column>
                <Column
                  field="status"
                  header="Status"
                  body={customBodyTemplate}
                  sortable
                ></Column>
                <Column
                  field="airflow"
                  header="Airflow"
                  body={customBodyTemplate}
                ></Column>
                {/* <Column field="logs" header="Logs" body={customBodyTemplate}></Column> */}
                <Column
                  field="audits"
                  header="Audit"
                  body={customBodyTemplate}
                ></Column>
              </DataTable>
            </div>
          </Widget>
        </div>
      </div>

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
        <div className="form-group mb-2">
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
      <Toast ref={toast} />
    </>
  );
};

export default Jobs;
