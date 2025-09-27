import React, { useEffect, useRef, useState } from "react";
import s from "./Home.module.scss";
import Widget from "../../components/Widget/Widget";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import {
  activeDashboardAPI,
  addDashboard,
  deleteDashboardById,
  fetchDashboards,
  updateDashboard,
} from "../../api/homeAPI";
import { hideLoader, showLoader } from "../../actions/loader";
import { useDispatch, useSelector } from "react-redux";
import { v4 as uuidv4 } from "uuid";
import WizBIInput from "../../core/WizBIInput/WizBIInput";
import { confirmDialog } from "primereact/confirmdialog";
import { Toast } from "primereact/toast";
import { Divider } from "primereact/divider";

const Home = () => {
  const dispatch = useDispatch();
  const isLoading = useSelector((state) => state.loader.loaderVisibility);

  useEffect(() => {
    getDashboards();
  }, []);
  const resetDashboardInfo = {
    name: "",
    link: "",
    isactive: false,
  };
  const [dashboardList, setDashboardList] = useState([]);
  const [isDashboardVisible, setIsDashboardVisible] = useState(false);
  const [selectedDashboard, setSelectedDashboard] = useState({});
  const [dashboardInfo, setDashboardInfo] = useState(resetDashboardInfo);
  const [activeDashboard, setActiveDashboard] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [isAdd, setIsAdd] = useState(false);
  const toast = useRef(null);
  const footerContent = (type) => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text text-wizBi mx-2"
          onClick={() => {
            setIsDashboardVisible(false);
            setSubmitted(false);
            setIsAdd(true);
          }}
        />
      </div>
    );
  };

  const getDashboards = () => {
    dispatch(showLoader());
    fetchDashboards((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setDashboardList(resp || []);
        const activeBoard = resp.find((dash) => dash.isactive);
        setActiveDashboard(activeBoard || resp[0]);
      }
    });
  };
  const accept = () => {
    dispatch(showLoader());
    deleteDashboardById(selectedDashboard.id, (resp) => {
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
          detail: "The dashboard record has been successfully deleted",
          life: 3000,
        });
        getDashboards();
      }
    });
  };

  const deleteDashboard = (id) => {
    confirmDialog({
      message: "Do you want to delete this record?",
      header: "Delete Confirmation",
      icon: "pi pi-info-circle",
      acceptClassName: "p-button-danger",
      accept,
    });
  };

  const dashboardActive = (conn) => {
    dispatch(showLoader());
    activeDashboardAPI(conn.id, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setIsDashboardVisible(false);
        setActiveDashboard(conn);
        toast.current.show({
          severity: "success",
          summary: "Confirmed",
          detail: "The dashboard record has been successfully updated ",
          life: 3000,
        });
      }
    });
  };

  const addNewDashboard = () => {
    if (!dashboardInfo.name || !dashboardInfo.link) {
      return setSubmitted(true);
    }
    setSubmitted(false);
    dispatch(showLoader());
    if (isAdd) {
      addDashboard(dashboardInfo, (resp) => {
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
            detail: "The dashboard record has been successfully added ",
            life: 3000,
          });
          setDashboardInfo(resetDashboardInfo);
          getDashboards();
        }
      });
    } else {
      updateDashboard(dashboardInfo.id, dashboardInfo, (resp) => {
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
            detail: "The dashboard record has been successfully updated ",
            life: 3000,
          });
          setDashboardInfo(resetDashboardInfo);
          setIsAdd(true);
          getDashboards();
        }
      });
    }
  };

  const isURL = (str) => {
    return str.startsWith("http://") || str.startsWith("https://");
  };

  const renderIframeContent = (value) => {
    if (isURL(value)) {
      return (
        <iframe
          src={value}
          frameborder="0"
          width="100%"
          height="100%"
          allowtransparency
        ></iframe>
      );
    } else {
      return (
        <div
          dangerouslySetInnerHTML={{ __html: value }}
          style={{ width: "100%", height: "100%" }}
        />
      );
    }
  };

  return (
    <>
      <div className={s.root}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper} position-relative`}>
          <Widget
            title={
              <>
                <div className="w-100">
                  <i
                    className="fa fa-cogs float-end"
                    role="button"
                    onClick={() => {
                      setSubmitted(false);
                      setIsAdd(true);
                      setIsDashboardVisible(true);
                    }}
                  ></i>
                </div>
              </>
            }
            className={`mb-0 ${s.mainWidgetClass}`}
            bodyClass={`m-0 p-0 ${s.widgetBodyClass}`}
          >
            
            <div className={`w-100 h-100 p-2`}>
              {dashboardList &&
                !!dashboardList.length &&
                renderIframeContent(activeDashboard.link)}

              {!dashboardList.length && !isLoading && (
                <h5 className="my-5 d-flex justify-content-center">
                  No dashboards are available. To create your custom dashboard,
                  click on Settings.
                  <i
                    className="fa fa-cogs float-end mx-3"
                    role="button"
                    onClick={() => {
                      setIsDashboardVisible(true);
                    }}
                  ></i>
                </h5>
              )}
            </div>
          </Widget>
        </div>
      </div>

      <Dialog
        visible={isDashboardVisible}
        style={{ width: "70vw", height: "85vh" }}
        onHide={() => setIsDashboardVisible(false)}
        footer={footerContent()}
      >
        <div className="row h-100">
          <div className="col-md-5 h-100">
            <div className="d-flex align-items-center">
              <h6 className="mx-1 px-1 d-block">List of Dashboards</h6>
            </div>
            <div
              className={`w-100 px-3`}
              style={{ height: "90%", overflowY: "auto", flexGrow: 1 }}
            >
              {dashboardList.map((conn) => {
                return (
                  <div>
                    <Widget
                      className={`my-2 p-0 ${
                        conn === activeDashboard ? "active-item" : ""
                      } ${s.dashboardItem}`}
                      key={uuidv4()}
                      title={
                        <div className={`w-100 h-100 m-2 p-2 mt-0 pt-0`}>
                          <div className="d-flex flex-row justify-content-between align-items-center">
                            <div className="text-truncate">
                              <h6 className="mx-2 text-wizBi text-capitalize p-0 my-0 text-align-left">
                                {conn.name}
                              </h6>
                            </div>
                            <div className="px-2 d-flex flex-row justify-content-end">
                              <span className="float-end mx-2" role="button">
                                <i
                                  className="fa fa-trash"
                                  onClick={() => {
                                    setSelectedDashboard(conn);
                                    deleteDashboard();
                                  }}
                                ></i>
                              </span>
                              <span className="float-end mx-2" role="button">
                                <i
                                  className="fa fa-edit"
                                  onClick={() => {
                                    setIsAdd(false);
                                    setDashboardInfo(conn);
                                  }}
                                ></i>
                              </span>

                              {dashboardList && dashboardList.length > 1 && (
                                <span className="float-end" role="button">
                                  <i
                                    className="fa fa-check"
                                    onClick={(evt) => {
                                      evt.preventDefault();
                                      dashboardActive(conn);
                                    }}
                                  ></i>
                                </span>
                              )}
                              <span className="mx-2" role="button">
                                <i className="fa fa-link text-muted"></i>
                              </span>
                            </div>
                          </div>
                        </div>
                      }
                    />
                  </div>
                );
              })}
            </div>
          </div>
          <div className="col-md-1">
            <Divider layout="vertical" />
          </div>
          <div className="col-md-6">
            <div className="d-flex align-items-center">
              <h6 className="mx-1 px-1 d-block">Create Dashboard</h6>
            </div>
            <div
              className={`w-100 px-1 row align-items-center justify-content-center`}
            >
              <div className="form-group mb-2">
                <WizBIInput
                  labelName="Name"
                  panelClass="my-2"
                  className={`${
                    submitted && !dashboardInfo.name ? "is-invalid" : ""
                  }`}
                  controls={{
                    value: dashboardInfo.name,
                    onChange: (e) => {
                      setDashboardInfo({
                        ...dashboardInfo,
                        name: e.target.value,
                      });
                    },
                    id: "name",
                    tabindex: 1,
                  }}
                >
                  
                  <div className="invalid-feedback">
                    A valid name is required!
                  </div>
                </WizBIInput>
              </div>
              <div className="form-group mb-2">
                <WizBIInput
                  labelName="Link"
                  panelClass="my-2"
                  className={`${
                    submitted && !dashboardInfo.link ? "is-invalid" : ""
                  }`}
                  controls={{
                    type: "textarea",
                    value: dashboardInfo.link,
                    onChange: (e) => {
                      setDashboardInfo({
                        ...dashboardInfo,
                        link: e.target.value,
                      });
                    },
                    id: "link",
                    tabindex: 2,
                  }}
                >
                  
                  <div className="invalid-feedback">
                    A valid link is required!
                  </div>
                </WizBIInput>
              </div>
              <div className="d-flex justify-content-end">
                {
                  (!!dashboardInfo.name || !!dashboardInfo.link) && (
                    <button
                      className="btn bg-wizBi text-white mx-2"
                      style={{ width: "100px", height: "40px" }}
                      onClick={() => {
                        setIsAdd(true);
                        setDashboardInfo(resetDashboardInfo);
                      }}
                    >
                      Clear
                    </button>
                  )

                  // <i className="fa fa-close mx-3" role="button" onClick={() => { setIsAdd(true); setDashboardInfo(resetDashboardInfo) }}></i>
                }
                <button
                  className="btn bg-wizBi text-white"
                  style={{ width: "100px", height: "40px" }}
                  onClick={() => {
                    addNewDashboard();
                  }}
                >
                  {isAdd ? "Add" : "Update"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Dialog>
      <Toast ref={toast} />
    </>
  );
};

export default Home;
