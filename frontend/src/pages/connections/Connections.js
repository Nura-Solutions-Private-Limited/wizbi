import React, { useEffect, useRef, useState, useMemo } from "react";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import {
  deleteConnectionById,
  fetchConnections,
  getAllConnections,
} from "../../api/connection";
import Widget from "../../components/Widget/Widget";
import s from "./Connections.module.scss";
import { Toast } from "primereact/toast";
import { v4 as uuidv4 } from "uuid";
import debounce from "lodash.debounce";
import { InputText } from "primereact/inputtext";
import DatabaseIcon from "../../components/Icons/Global/DatabaseIcon";
import { confirmDialog } from "primereact/confirmdialog";

import { ConnectionSideBar } from "./ConnectionSideBar";
import { createSearchParams, useNavigate } from "react-router-dom";

import { useQuery } from "@tanstack/react-query";

const Connections = () => {
  const navigate = useNavigate();
  const toast = useRef(null);
  const dispatch = useDispatch();
  const [isRowSelected, setIsRowSelected] = useState(false);
  const [isAddSelected, setIsAddSelected] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [dataType, setDataType] = useState(null);
  const [filesList, setFilesList] = useState([]);
  const [dimensions, setDimensions] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const searchRef = useRef("");
  // const [loading, setLoading] = useState(true);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: "connections",
    queryFn: getAllConnections,
    staleTime: 0, // Always consider data stale to ensure fresh data
    cacheTime: 0, // Don't cache to ensure fresh data
  });

  // Debug log to see when data changes
  React.useEffect(() => {
    console.log('Connections data updated:', data);
  }, [data]);

  // const getDatabaseTypes = () => {
  //   dispatch(showLoader());
  //   fetchDatabaseTypes((resp) => {
  //     dispatch(hideLoader());
  //     if (!!resp && (!!resp?.detail || !!resp?.message)) {
  //       toast.current.show({
  //         severity: "error",
  //         summary: "Error",
  //         detail: resp.detail || resp.message,
  //         life: 3000,
  //       });
  //     } else {
  //       setDatabaseTypes(resp);
  //     }
  //   });
  // };
  // useEffect(() => {
  //   getDatabaseTypes();
  // }, []);

  // const getConnections = () => {
  //   dispatch(showLoader());
  //   fetchConnections((resp) => {
  //     dispatch(hideLoader());
  //     // setLoading(false);
  //     if (!!resp && (!!resp.detail || !!resp.message)) {
  //       toast.current.show({
  //         severity: "error",
  //         summary: "Error",
  //         detail: resp.detail || resp.message,
  //         life: 3000,
  //       });
  //     } else {
  //       setConnectionsList(resp);
  //     }
  //   });
  // };

  // useEffect(() => {
  //   getConnections();
  // }, []);

  const setDTtype = (conn) => {
    let type = conn.db_type;
    if (conn.db_type) {
      if (conn.db_type.toLowerCase().includes("local")) {
        type = "lfs";
        return type;
      }
      if (conn.db_type.toLowerCase().includes("analytics")) {
        type = "ga";
      }
      if (conn.db_type.toLowerCase().includes("amazon")) {
        type = "s3";
      }
    }
    return type;
  };

  const navigateToConnectionDetails = (conn) => {
    // const subTypeQueryParams = conn.sub_type
    //   ? `&sub_type=${conn.sub_type}`
    //   : "";

    navigate({
      pathname: `/app/connections/${conn.id}`,
      search: `?${createSearchParams({
        connector_type: setDTtype(conn),
        ...(conn.sub_type && { sub_type: conn.sub_type }),
      })}`,
    });
  };

  const resetForm = () => {
    setIsAddSelected(false);
    setIsRowSelected(false);
    setDataType(null);
    setSubmitted(false);
    setFilesList([]);
    setDimensions({});
    setMetrics([]);
    setSelectedOptions();
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };
  const debouncedResults = useMemo(() => {
    return debounce(handleSearch, 600);
  }, []);

  useEffect(() => {
    return () => {
      debouncedResults.cancel();
    };
  });

  let filterBySearch = data ?? [];
  if (searchTerm !== "") {
    filterBySearch = data.filter((item) => {
      const value = searchTerm.toLowerCase();
      console.log(item);
      if (
        (item.db_conn_name &&
          item.db_conn_name.toString().toLowerCase().includes(value)) ||
        (item.db_type && item?.db_type.toLowerCase().includes(value))
      ) {
        return item;
      }
    });
  }

  const accept = (connectionId) => {
    console.log('Deleting connection with ID:', connectionId); // Debug log
    dispatch(showLoader());
    deleteConnectionById(connectionId, (resp) => {
      dispatch(hideLoader());
      console.log('Delete response:', resp); // Debug log
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        const { deleted } = resp;
        console.log('Deleted status:', deleted); // Debug log
        if (deleted) {
          toast.current.show({
            severity: "success",
            summary: "Confirmed",
            detail: "The connection has been successfully deleted",
            life: 3000,
          });
          console.log('Calling refetch to refresh connection list'); // Debug log
          refetch().then(() => {
            console.log('Refetch completed');
          }).catch((error) => {
            console.error('Refetch error:', error);
          });
        } else {
          toast.current.show({
            severity: "warn",
            summary: "Warning",
            detail:
              "The connection is having a dependency in Pipeline. Cannot be deleted!",
            life: 3000,
          });
        }
      }
    });
  };

  const deleteConnection = (connection) => {
    confirmDialog({
      message: "Do you want to delete this record?",
      header: "Delete Confirmation",
      icon: "pi pi-info-circle",
      acceptClassName: "p-button-danger",
      accept: () => {
        accept(connection.id);
      },
    });
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 p-0 px-3 m-0 ${s.wrapper}`}>
          <Widget
            title={
              <div className="d-flex align-items-center justify-content-between pb-2">
                <h5 className="py-0">Connections</h5>
                <div>
                  <ConnectionSideBar />
                  <i
                    className="fa fa-refresh"
                    onClick={() => {
                      // getConnections();
                      refetch();
                    }}
                    role="button"
                  ></i>
                </div>
              </div>
            }
            className={`mb-0 background-white pb-3`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            <div
              className={`w-100 overflow-auto h-100 ${
                !!filterBySearch.length ? "h-100" : ""
              } px-3`}
            >
              <div className="p-input-icon-left w-100">
                <i className="pi pi-search global-search-icon" />
                <InputText
                  placeholder="Search for connection name, db type"
                  style={{ width: "100%", height: "30px" }}
                  onChange={debouncedResults}
                  ref={searchRef}
                />
              </div>
              {!!filterBySearch.length ? (
                filterBySearch.map((conn) => {
                  return (
                    <div>
                      <Widget
                        className={`${s.connectionItem} my-2 p-0`}
                        key={uuidv4()}
                      >
                        <div
                          className={`w-100 h-100 m-2 p-2`}
                          role="button"
                          onDoubleClick={(evt) => {
                            evt.preventDefault();
                            navigateToConnectionDetails(conn);
                            // navigate({
                            //   pathname: `/app/connections/${conn.id}`,
                            //   search: `?${createSearchParams({
                            //     connector_type: setDTtype(conn),
                            //   })}`,
                            // });
                          }}
                        >
                          <div className="d-flex align-items-center text-truncate">
                            <DatabaseIcon.Large
                              database_type={setDTtype(conn)}
                            />
                            <div className="flex-grow-1">
                              <h6 className="mx-2 text-wizBi text-capitalize p-0 my-0">
                                {conn.db_conn_name}
                              </h6>
                              <div className="row m-0 p-0 text-truncate">
                                {/* <div className="col text-black px-1 text-truncate">
                                  <small className="text-black text-capitalize p-0 my-0">
                                    <label className="mx-2">Name :</label>
                                    {conn.db_name}
                                  </small>
                                </div> */}
                              </div>
                              <div className="row m-0 p-0 text-truncate">
                                <div className="col text-black px-1 text-truncate">
                                  <small className="d-flex">
                                    <label className="mx-2">Type :</label>
                                    {conn.db_type}
                                  </small>
                                </div>
                                {/* <div className="col text-black px-1 text-truncate">
                                  <small
                                    className="d-flex text-truncate"
                                    style={{ width: "100px" }}
                                  >
                                    <label className="mx-2">Host :</label>
                                    {conn.db_host}
                                  </small>
                                  <small className="d-flex">
                                    <label className="mx-2">Port :</label>
                                    {conn.db_port}
                                  </small>
                                </div> */}
                              </div>
                            </div>
                            <div className="d-flex align-items-center justify-content-between">
                              <i
                                className="fa fa-trash mx-3 new_pipeline-delete-icon"
                                role="button"
                                onClick={() => {
                                  deleteConnection(conn);
                                }}
                                data-pr-tooltip="Delete"
                              />

                              <i
                                className="fa fa-angle-right fa-2x mx-3"
                                role="button"
                                onClick={(evt) => {
                                  evt.preventDefault();
                                  navigateToConnectionDetails(conn);
                                  // const subTypeQueryParams = conn.sub_type
                                  //   ? `&sub_type=${conn.sub_type}`
                                  //   : "";

                                  // // const subTypeQueryParams = information.sub_type
                                  // // ? `&sub_type=${information.sub_type}`
                                  // // : "";
                                  // navigate(
                                  //   `/app/connections/${conn.id}/connector_type=${conn.connector_type}${subTypeQueryParams}`
                                  // );

                                  // navigate({
                                  //   pathname: `/app/connections/${conn.id}`,
                                  //   search: `?${createSearchParams({
                                  //     connector_type: conn.db_type,
                                  //   })}`,
                                  // });
                                }}
                              />
                            </div>
                          </div>
                        </div>
                      </Widget>
                    </div>
                  );
                })
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
                  <span>
                    Sorry, we couldn't find any results for the search
                    {searchTerm}
                  </span>
                </div>
              )}
            </div>
          </Widget>
        </div>
      </div>
      <Toast ref={toast} />
    </>
  );
};

export default Connections;
