import React, { useState } from "react";
import Widget from "../../components/Widget/Widget";
import s from "./Audits.module.scss";
import { getAudits } from "../../api/auditsAPI";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { NavLink, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "primereact/button";
const Audits = (props) => {
  const [pagination, setPagination] = useState({ page: 1, size: 50 }); // page = 1-based
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["audits", pagination],
    queryFn: getAudits,
    keepPreviousData: true,
  });

  const onPage = (event) => {
    setPagination({
      page: event.page + 1, // PrimeReact is 0-based, your API is 1-based
      size: event.rows,
    });
  };

  const customBodyTemplate = (dTableInfo, props) => {
    let str = "";
    switch (props.field) {
      case "name":
        str = (
          <NavLink
            to={`/app/datawarehouse?pipelineId=${dTableInfo.pipeline_id}`}
          >
            <span className="font-bold">{`${dTableInfo.pipeline.name} _ ${dTableInfo.pipeline.id}`}</span>
          </NavLink>
        );
        break;
      case "startDT":
        let startDT = new Date(dTableInfo.job.start_time);
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
        let endDT = new Date(dTableInfo.job.end_time);
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
          dTableInfo.job.status.toLowerCase().indexOf("success") !== -1 ? (
            <span className={`badge mx-4 wizBi-bg-success`}>
              {dTableInfo.job.status}
            </span>
          ) : (
            <span className={`badge mx-4 wizBi-bg-pending`}>
              {dTableInfo.job.status}
            </span>
          );
        break;
      case "jobs":
        str = (
          <NavLink
            to={`/app/jobs?pipelineId=${dTableInfo.pipeline_id}&jobId=${dTableInfo.job_id}`}
          >
            {dTableInfo.job_id}
          </NavLink>
        );
        break;
    }
    return str;
  };
  const navigate = useNavigate();

  const navToTarget = (url) => {
    navigate(url);
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <Widget
            title={
              <>
                <div className="d-flex justify-content-between align-items-center">
                  <h5>Audits</h5>
                  <Button
                    icon="pi pi-refresh"
                    className="p-button-text p-button-sm"
                    onClick={() => {
                      queryClient.invalidateQueries(["audits"]);
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
            <div className={`w-100 h-100 p-4`}>
              <DataTable
                value={data?.items || []}
                lazy
                paginator
                totalRecords={data?.total || 0}
                first={(pagination.page - 1) * pagination.size}
                rows={pagination.size}
                onPage={onPage}
                loading={isLoading}
                rowSelection
                selectionMode="single"
                data-pr-classname="h-100"
                emptyMessage={
                  <h5 className="d-flex justify-content-center">
                    No Audits available
                  </h5>
                }
                tableStyle={{ minHeight: "200px", fontSize: "0.88rem" }}
              >
                <Column
                  field="name"
                  header="Pipeline / name"
                  body={customBodyTemplate}
                  sortable
                  sortField="pipeline.name"
                ></Column>
                <Column
                  field="jobs"
                  header="Job ID"
                  body={customBodyTemplate}
                  sortable
                  sortField="job_id"
                ></Column>
                <Column
                  field="startDT"
                  header="Start Date Time"
                  body={customBodyTemplate}
                ></Column>
                <Column
                  field="endDT"
                  header="End Date Time"
                  body={customBodyTemplate}
                ></Column>
                <Column
                  field="status"
                  header="Status"
                  body={customBodyTemplate}
                  sortable
                  sortField="job.status"
                ></Column>
                <Column field="duplicates" header="Duplicates"></Column>
                <Column field="inserts" header="Inserts"></Column>
                <Column field="errors" header="Errors"></Column>
                <Column field="warnings" header="Warnings"></Column>
              </DataTable>
            </div>
          </Widget>
        </div>
      </div>
    </>
  );
};

export default Audits;
