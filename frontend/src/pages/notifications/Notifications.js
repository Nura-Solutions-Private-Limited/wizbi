import React, { useEffect, useRef, useState } from "react";
import s from "./Notifications.module.scss";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import { fetchNotifications, markAsViewed } from "../../api/notificationsAPI";
import { Divider } from "primereact/divider";
import { Button } from "primereact/button";
import { Toast } from "primereact/toast";
const NotificationsContainer = ({ notifyParent }) => {
  const [notificationsList, setNotificationsList] = useState([]);
  const toast = useRef(null);
  const dispatch = useDispatch();

  const getNotificationsInfo = () => {
    dispatch(showLoader());
    fetchNotifications((resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        setNotificationsList(resp);
      }
    });
  };

  const markNotificationsAsRead = (id) => {
    dispatch(showLoader());
    markAsViewed({ id }, (resp) => {
      dispatch(hideLoader());
      if (!!resp && !!resp.detail) {
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail,
          life: 3000,
        });
      } else {
        toast.current.show({
          severity: "success",
          summary: "Confirmed",
          detail: resp.message,
          life: 3000,
        });

        notifyParent();
        getNotificationsInfo();
      }
    });
  };

  useEffect(() => {
    getNotificationsInfo();
  }, []);

  const timeAgo = (dateString) => {
    const targetDate = new Date(dateString);
    const currentDate = new Date();
    const difference = currentDate - targetDate; // Difference in milliseconds

    const hoursAgo = Math.floor(difference / (1000 * 60 * 60));
    const daysAgo = Math.floor(difference / (1000 * 60 * 60 * 24));

    return hoursAgo < 24 ? `${hoursAgo} hours ago` : `${daysAgo} days ago`;
  };

  const markAsRead = ({ id }) => {
    markNotificationsAsRead(id);
  };

  return (
    <>
      <div className={`row ${s.root}`}>
        <div className={`col-md-12 col-lg-12 ${s.wrapper}`}>
          <div className={`w-100 h-100 p-4 d-flex flex-column`}>
            <div>
              <span className="font-weight-bold">
                You have {notificationsList.length} notifications
              </span>
              <Divider />
            </div>
            {!!notificationsList.length ? (
              <div style={{ overflow: "auto", flex: 1 }}>
                {notificationsList.map((item) => {
                  return (
                    <>
                      <div className="d-flex flex-wrap p-2 align-items-center gap-3">
                        <div className="flex-1 d-flex flex-column gap-2">
                          <span className="font-bold">{item.description}</span>
                          <div className="d-flex justify-content-between w-100 align-items-center">
                            <span>{timeAgo(item.alert_datetime)}</span>
                            {!item.viewed && (
                              <Button
                                severity="info"
                                className="mx-2 bg-wizBi p-2"
                                onClick={() => markAsRead(item)}
                              >
                                <i className="pi pi-eye mx-2"></i> Mark as read
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                      <Divider />
                    </>
                  );
                })}
              </div>
            ) : (
              <div className="d-flex justify-content-center align-items-center">
                <h6>You have no notifications</h6>
              </div>
            )}
          </div>
        </div>
      </div>
      <Toast ref={toast} />
    </>
  );
};

export default NotificationsContainer;
