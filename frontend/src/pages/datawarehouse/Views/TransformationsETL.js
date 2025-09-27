import React, { useEffect, useState } from "react";
import { cloneDeep } from "lodash";
import {
  fetchDatabaseDatatypes,
  fetchFilePreview,
} from "../../../api/datawarehouse";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../../actions/loader";
import { DataTable } from "primereact/datatable";
import { TreeSelect } from "primereact/treeselect";
import { Column } from "primereact/column";
import { confirmDialog } from "primereact/confirmdialog";
import { isEmpty } from "lodash";
import { Checkbox } from "primereact/checkbox";
import s from "../DataWarehouse.module.scss";

const FilePreviewDatalakeTable = ({
  status,
  database_name,
  table_name,
  table_preview = [],
  selectedTypesDataLake = [],
  setSelectedTypesDataLake,
}) => {
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [group_by, setGroup_by] = useState([]);
  const [aggregate_function, setAggregate_function] = useState("");

  const updateSelectedTypesDataLake = (name, type, newAggregateFunction, newGroupBy) => {
    const newEntry = {
      table_name,
      database_name,
      table_preview: [{
        name,
        type,
        group_by: newGroupBy,
        is_selected: "y",
        aggregate_function: newAggregateFunction,
      }]
    };

    const findDatabaseIndex = selectedTypesDataLake.findIndex(
      (item) => item.database_name === database_name
    );

    const updatedSelectedTypesDataLake = cloneDeep(selectedTypesDataLake);

    if (findDatabaseIndex !== -1) {
        updatedSelectedTypesDataLake[findDatabaseIndex].table_preview[0] = {
          ...updatedSelectedTypesDataLake[findDatabaseIndex].table_preview[0],
          group_by: newGroupBy?.filter((item) => item !== name),
          aggregate_function: newAggregateFunction,
        }
    } else {
      updatedSelectedTypesDataLake.push(newEntry);
    }

    setSelectedTypesDataLake(updatedSelectedTypesDataLake);
  };

  const headers = table_preview.map((item) => item.name);

  const treeData = [
    { label: "Max", key: "max" },
    { label: "Min", key: "min" },
    { label: "Sum", key: "sum" },
    { label: "Average", key: "average" },
    { label: "Count", key: "count" },
  ];

  const handleNodeSelect = (e) => {
    setAggregate_function(e.value);
    updateSelectedTypesDataLake(name, type, e.value, group_by);
  };

  const handleGroupByChange = (column, e) => {
    const newGroupBy = e.checked ? [...group_by, column.name] : group_by.filter((item) => item !== column.name);
    setGroup_by(newGroupBy);
    updateSelectedTypesDataLake(column.name, column.type, aggregate_function, newGroupBy);
  };

  const handleAggregateChange = (column, e) => {
    if (e.checked) {
      setName(column.name);
      setType(column.type);
      updateSelectedTypesDataLake(column.name, column.type, aggregate_function, group_by);
    } else {
      setName("");
      setType("");
    }
  };

  useEffect(() => {
    if (table_preview?.length && !selectedTypesDataLake?.length) {
      table_preview.forEach((item) => {
        if (item?.is_selected) {
          handleAggregateChange(item, { checked: true });
        }
        if (item?.aggregate_function) {
          setAggregate_function(item.aggregate_function);
        }
        if (item?.group_by) {
          setGroup_by(item.group_by);
          updateSelectedTypesDataLake(name, type, item.aggregate_function, item.group_by);
        }
      });
    }
  }, [table_preview]);

  const columns = table_preview.map((column) => ({
    field: column.name,
    header: column.name,
    body: (rowData) => {
      const disabled = status === "Active";
      return (
        <div>
          <div className="d-flex flex-column align-items-center">
            <Checkbox
              inputId={`aggregateBy-${column.name}`}
              checked={name === column.name}
              onChange={(e) => handleAggregateChange(column, e)}
              className="mx-2"
              disabled={disabled}
            />
            <Checkbox
              inputId={`groupBy-${column.name}`}
              checked={group_by.includes(column.name)}
              onChange={(e) => handleGroupByChange(column, e)}
              className="mx-2 mt-2"
              disabled={disabled || (name && name === column.name)}
            />
          </div>
          <TreeSelect
            value={aggregate_function || ""}
            options={treeData}
            onChange={handleNodeSelect}
            style={{ width: "100%", marginTop: "1rem" }}
            placeholder="Select a type"
            disabled={disabled || (name && name !== column.name)}
          />
          <ul className="data-list" style={{ marginTop: "10px" }}>
            {column?.data?.length > 0 ? (
              column.data.map((item, index) => <li key={index}>{item}</li>)
            ) : (
              <li>No data available</li>
            )}
          </ul>
        </div>
      );
    },
  }));

  const customSidebarContent = (
    <div style={{ width: "7rem" }}>
      <div>Aggregate by</div>
      <div>Group By</div>
    </div>
  );

  return (
    <>
      <div>
        <h6>Database Name : {database_name}</h6>
        <h6>Table Name : {table_name}</h6>
      </div>
      <DataTable value={[headers]}>
        <Column
          field="customSidebar"
          header=""
          body={() => customSidebarContent}
          style={{ width: "300px" }}
        />
        {columns.map((col) => (
          <Column
            key={col.field}
            field={col.field}
            header={col.header}
            body={col.body}
          />
        ))}
      </DataTable>
    </>
  );
};

const FilePreviewTable = ({
  datatypes = [],
  file_columns = {},
  file_columns_data = {},
  file_name,
  handleDataTypeChange,
  status,
  deleteFileColumn,
  dateFormatTypes = [],
}) => {
  const headers = !isEmpty(file_columns) ? Object.keys(file_columns) : [];
  const [customDateFormat, setCustomDateFormat] = useState({});

  // Convert datatypes to tree structure with date formats as children
  const treeData = datatypes.map((type) => ({
    key: type.value,
    label: type.name,
    data: type,
    children:
      type.name === "Date" && dateFormatTypes?.length
        ? [
            ...dateFormatTypes.map((format) => ({
              key: format.date_format,
              label: format.date_format,
              data: { ...format, parentType: type.value },
            })),
            {
              key: "custom",
              label: "Custom",
              data: { parentType: type.value },
              button: {
                label: "Custom Button",
              },
            },
          ]
        : [],
  }));

  const columns = headers.map((header) => ({
    field: header,
    header: header,
    body: (rowData) => {
      const disabled = status === "Active";
      const value = file_columns[header];

      const handleNodeSelect = (e) => {
        handleDataTypeChange(
          e.value === "custom" ? "datetime64[s]" : e.value,
          header,
          file_name
        );
      };

      return (
        <div>
          <div className="d-flex">
            <TreeSelect
              value={value}
              options={treeData}
              onChange={handleNodeSelect}
              style={{ width: "100%" }}
              placeholder="Select a type"
              disabled={disabled}
            />
            <i
              className="pi pi-trash mx-2 mt-3"
              onClick={() => deleteFileColumn(header, file_name)}
              style={{ cursor: "pointer" }}
              disabled={disabled}
            ></i>
          </div>
          {value === "datetime64[s]" && (
            <div style={{ marginTop: "10px" }}>
              <input
                type="text"
                value={customDateFormat[header] || ""}
                onChange={(e) =>
                  setCustomDateFormat((prev) => ({
                    ...prev,
                    [header]: e.target.value,
                  }))
                }
                placeholder="Date Format"
                className="p-inputtext p-component"
                style={{ width: "100%" }}
              />
              <button
                className="p-button p-component"
                onClick={() =>
                  handleDataTypeChange(
                    customDateFormat[header],
                    header,
                    file_name
                  )
                }
                disabled={!customDateFormat[header] || disabled}
                style={{ marginTop: "0.5rem" }}
              >
                Apply
              </button>
            </div>
          )}
          <div style={{ marginTop: "10px" }}>
            <ul className="data-list">
              {file_columns_data[header] &&
              file_columns_data[header].length > 0 ? (
                file_columns_data[header].map((item, index) => (
                  <li key={index}>{item}</li>
                ))
              ) : (
                <li>No data available</li>
              )}
            </ul>
          </div>
        </div>
      );
    },
  }));

  return (
    <DataTable value={[headers]}>
      {columns.map((col) => (
        <Column
          key={col.field}
          field={col.field}
          header={col.header}
          body={col.body}
        />
      ))}
    </DataTable>
  );
};

const TransformationsETL = ({
  pipelineInfo,
  selectedTypesETL,
  setSelectedTypesETL,
  metaData,
  isDataLake,
  selectedTypesDataLake,
  setSelectedTypesDataLake,
}) => {
  const dispatch = useDispatch();
  const [dataTypes, setDatatypes] = useState([]);
  const [dateFormatTypes, setDateFormatTypes] = useState([]);
  const [filePreview, setFilePreview] = useState([]);
  const [isTypesLoaded, setIsTypesLoaded] = useState(false);
  const [isDateTypesLoaded, setIsDateFormatTypesLoaded] = useState(false);
  const [fetchedDataLakePreview, setFetchedDataLakePreview] = useState([]);
  const [fetchedPreview, setFetchedPreview] = useState([]);
  const [isLoaded, setIsLoaded] = useState(false);

  const fetchDatatypes = async () => {
    try {
      dispatch(showLoader());
      const response = await fetchDatabaseDatatypes();
      setDatatypes(response);
      setIsTypesLoaded(true);
    } catch (error) {
      console.error("Error fetching Datatypes:", error);
    } finally {
      isLoaded && dispatch(hideLoader());
    }
  };

  const fetchPreview = async () => {
    try {
      dispatch(showLoader());
      const response = await fetchFilePreview(pipelineInfo?.id, isDataLake);
      if (isDataLake) {
        dispatch(showLoader());
        setFetchedDataLakePreview(response || {});
      } else {
        setFetchedPreview(response || []);

        const updatedFilePreview = response?.length
          ? response.map(({ file_columns, file_name }, index) => {
              const columns = [];
              Object.entries(file_columns).map(([fileKey, fileValue]) => {
                columns.push({
                  column_name: fileKey,
                  data_type: fileValue,
                  format: fileValue,
                });
              });
              return {
                file_name,
                file_columns: columns,
              };
            })
          : [];
        setSelectedTypesETL(updatedFilePreview);
      }
    } catch (error) {
      console.error("Error fetching File Preview:", error);
    } finally {
      !isLoaded && dispatch(hideLoader());
      setIsLoaded(true);
    }
  };

  useEffect(() => {
    if (!isDataLake) {
      fetchDatatypes();
      pipelineInfo?.id && fetchPreview();
    }
  }, []);

  useEffect(() => {
    fetchDatatypes();
    pipelineInfo?.id && fetchPreview();
  }, []);

  const handleDataTypeChange = (
    value = "",
    header = "",
    file_name = "",
    deleteColumn = false
  ) => {
    if (!isDataLake) {
      let columnIndex = 0;
      const updatedFiles = selectedTypesETL.map((file) => {
        const { format = "" } =
          dataTypes.find((type) => type.value === value) || {};
        const { file_columns } = file;
        columnIndex =
          file_columns?.length &&
          file_columns.findIndex((column) => column?.column_name === header);

        if (file?.file_name === file_name) {
          if (deleteColumn) {
            file_columns.splice(columnIndex, 1);
          } else {
            if (file_columns?.length && columnIndex !== -1) {
              file_columns[columnIndex].data_type = format;
              file_columns[columnIndex].format = format;
            } else {
              file_columns.push({
                column_name: header,
                data_type: format,
                format,
              });
            }
          }
        }

        return {
          ...file,
          file_columns,
        };
      });

      const fileIndex = fetchedPreview.findIndex(
        (column) => column?.file_name === file_name
      );
      if (fileIndex !== -1) {
        const updatedFilePreview = [...fetchedPreview];
        updatedFilePreview[fileIndex].file_columns[header] = value;
        if (deleteColumn) {
          delete updatedFilePreview[fileIndex].file_columns?.[header];
        }
        setFetchedPreview(updatedFilePreview);
      }

      setSelectedTypesETL(updatedFiles);
    }
  };

  const deleteFileColumn = (header, file_name) => {
    confirmDialog({
      message: `Are you sure you want to delete the column ${header}?`,
      accept: () => handleDataTypeChange("", header, file_name, true),
    });
  };

  return (
    <div>
      {Boolean(pipelineInfo?.pipeline_type === "DATALAKE") &&
      fetchedDataLakePreview?.length
        ? fetchedDataLakePreview?.map((file, index) => (
            <FilePreviewDatalakeTable
              {...file}
              datatypes={dataTypes}
              dateFormatTypes={dateFormatTypes}
              handleDataTypeChange={handleDataTypeChange}
              status={pipelineInfo?.status}
              deleteFileColumn={deleteFileColumn}
              pipeline_type={pipelineInfo?.pipeline_type}
              selectedTypesDataLake={selectedTypesDataLake}
              setSelectedTypesDataLake={setSelectedTypesDataLake}
            />
          ))
        : ""}

      {Boolean(pipelineInfo?.pipeline_type !== "DATALAKE") &&
      fetchedPreview?.length
        ? fetchedPreview?.map((file) => (
            <FilePreviewTable
              {...file}
              datatypes={dataTypes}
              dateFormatTypes={dateFormatTypes}
              handleDataTypeChange={handleDataTypeChange}
              status={pipelineInfo?.status}
              deleteFileColumn={deleteFileColumn}
              pipeline_type={pipelineInfo?.pipeline_type}
            />
          ))
        : ""}
    </div>
  );
};

export default TransformationsETL;
