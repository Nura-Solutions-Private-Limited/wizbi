import React, { useEffect, useRef, useState } from "react";
import s from "./Notifications.module.scss";
import { useDispatch } from "react-redux";
import { hideLoader, showLoader } from "../../actions/loader";
import { fetchNotifications } from "../../api/notificationsAPI";
import { OverlayPanel } from "primereact/overlaypanel";
import NotificationsContainer from "../../pages/notifications/Notifications";

const Notifications = () => {
  const [notificationsList, setNotificationsList] = useState([]);
  const [notificationsCount, setNotificationsCount] = useState(0);
  const toast = useRef(null);
  const dispatch = useDispatch();
  const op = useRef(null);

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
        const items = resp.filter((item) => !item.viewed);
        setNotificationsCount(items.length);
      }
    });
  };

  useEffect(() => {
    getNotificationsInfo();
  }, []);

  return (
    <>
      <OverlayPanel
        ref={op}
        showCloseIcon
        closeOnEscape
        dismissable={true}
        style={{ height: "400px", width: "500px" }}
      >
        <NotificationsContainer notifyParent={getNotificationsInfo} />
      </OverlayPanel>
      <a onClick={(e) => op.current.toggle(e)} class="none">
        <div className="d-flex justify-content-center align-items-center">
          <span className={`${s.avatar} rounded-circle thumb-sm`}>
            <i class="fa fa-bell fa-2x" aria-hidden="true"></i>
          </span>
          <div class="position-relative py-3">
            Notifications
            {!!notificationsCount && (
              <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger d-flex align-items-center justify-content-center">
                {notificationsCount}
                <span class="visually-hidden">unread messages</span>
              </span>
            )}
          </div>
        </div>
      </a>
    </>
  );
};

export default Notifications;
