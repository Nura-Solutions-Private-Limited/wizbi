import React, { useEffect, useRef, useState } from "react";
import Widget from "../../components/Widget/Widget";
import s from "./Logs.module.scss";
import { Divider } from "primereact/divider";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import { fetchJobs } from "../../api/jobsAPI";
import { usePipelines } from "../../hooks/usePipelines";
import { Dropdown } from "primereact/dropdown";
import WizBIDropDown from "../../core/WizBIDropDown/WizBIDropDown";

import { Skeleton } from "primereact/skeleton";
import { useSearchParams } from "react-router-dom";

const Logs = () => {
  const [jobsList, setJobsList] = useState([]);
  const [filterList, setFilterList] = useState([]);
  const [jobDetails, setJobDetails] = useState({});
  const toast = useRef(null);
  const dispatch = useDispatch();
  const { pipelinesResult } = usePipelines({pipeline_status: "active"});
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
  const [searchParams, setSearchParams] = useSearchParams();

  const getJobsInfo = () => {
    dispatch(showLoader());
    fetchJobs((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setJobsList(resp);
        setFilterList(resp);
      }
    });
  };

  useEffect(() => {
    if (searchParams.get("pipelineId") && pipelinesResult.length) {
      const info =
        pipelinesResult.find(
          (pInfo) => pInfo.id === parseInt(searchParams.get("pipelineId")),
        ) || pipelineInfo;
      setPipeLineInfo(info);
    }
  }, [pipelinesResult]);

  useEffect(() => {
    getJobsInfo();
  }, []);

  const filterPipelineInfo = (e) => {
    setPipeLineInfo(e.value);
    const filterList = jobsList.filter((job) => job.pipeline_id === e.value.id);
    setFilterList(filterList);
    setJobDetails({});
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <Widget
            title={
              <>
                <div className="d-flex justify-content-between align-items-center">
                  <h5>Logs</h5>
                </div>
                <Divider />
              </>
            }
            className={`mb-0`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            
            <div className={`w-100 h-100 px-4`}>
              <div className="row">
                <div className="d-flex py-2 px-4 justify-content-center">
                  <div className="col">
                    <div className="form-group my-4" style={{ width: "400px" }}>
                      <WizBIDropDown
                        labelName="Pipeline"
                        panelClass="mb-2 w-100"
                      >
                        <Dropdown
                          filter
                          value={pipelineInfo}
                          style={{ height: "35px" }}
                          className="w-100 d-flex form-control active align-items-center"
                          onChange={(e) => {
                            filterPipelineInfo(e);
                          }}
                          options={pipelinesResult}
                          optionLabel="name"
                          placeholder="Select a Pipeline"
                        />
                      </WizBIDropDown>
                    </div>
                    <div className="form-group my-4" style={{ width: "400px" }}>
                      <WizBIDropDown labelName="Job" panelClass="mb-2 w-100">
                        <Dropdown
                          filter
                          value={jobDetails}
                          style={{ height: "35px" }}
                          className="w-100 d-flex form-control active align-items-center"
                          onChange={(e) => {
                            setJobDetails(e.value);
                          }}
                          options={filterList}
                          optionLabel="job_id"
                          placeholder="Select a Job"
                          disabled={!pipelineInfo.name.length}
                        />
                      </WizBIDropDown>
                    </div>

                    <div className="form-group my-4" style={{ width: "400px" }}>
                      {jobDetails && jobDetails.status && (
                        <div className="d-flex align-items-center">
                          <label
                            className="mx-1"
                            style={{ color: "rgba(0, 0, 0, 0.6)" }}
                          >
                            Status :
                          </label>
                          <>
                            
                            {jobDetails.status
                              .toLowerCase()
                              .indexOf("success") != -1 ? (
                              <span className={`badge mx-4 wizBi-bg-success`}>
                                {jobDetails.status}
                              </span>
                            ) : (
                              <span className={`badge mx-4 wizBi-bg-pending`}>
                                {jobDetails.status}
                              </span>
                            )}
                          </>
                        </div>
                      )}

                      {/* <WizBIDropDown labelName='Status' panelClass='mb-2 w-100'>
                                                <Dropdown value={status} style={{ 'height': '45px' }} className='w-100 d-flex form-control active' onChange={(e) => { setStatus(e.value) }} options={jobStatus} optionLabel="name"
                                                    optionValue="id"
                                                    placeholder="Select a Status" disabled={!pipelineInfo.name.length} />
                                            </WizBIDropDown> */}
                    </div>
                  </div>
                  <div className="col">
                    <div className="d-flex justify-content-between">
                      <h5>Logs</h5>
                      <i className="fa fa-refresh mx-2" role="button"></i>
                    </div>
                    <div className="w-100 h-100">
                      <Skeleton className="mb-2 mt-4"></Skeleton>
                      <Skeleton width="10rem" className="mb-2"></Skeleton>
                      <Skeleton width="5rem" className="mb-2"></Skeleton>
                      <Skeleton height="2rem" className="mb-2"></Skeleton>
                      <Skeleton width="10rem" height="4rem"></Skeleton>
                    </div>
                    <div className="d-flex justify-content-end my-3">
                      <i className="fa fa-download" role="button"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Widget>
        </div>
      </div>
    </>
  );
};

export default Logs;
