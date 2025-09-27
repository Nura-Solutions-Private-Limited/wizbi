import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import Home from "../../pages/home/Home";
import Sidebar from "../Sidebar/Sidebar";
import s from "./Layout.module.scss";
import { withRouter } from "../../core/withRouter";
import { Navigate, Route, Routes } from "react-router-dom";
import Loader from "../Loader/Loader";
import Pipeline from "../../pages/pipeline/Pipeline";
import Connections from "../../pages/connections/Connections";
import { ConfirmDialog } from "primereact/confirmdialog";
import DataWarehouse from "../../pages/datawarehouse/DataWarehouse";
import Databases from "../../pages/databases/Databases";
import Reports from "../../pages/Reports/Reports";
import Logs from "../../pages/logs/Logs";
import Jobs from "../../pages/Jobs/Jobs";
import Audits from "../../pages/audits/Audits";
import { Administration } from "../../pages/admin/Administration";
import GenAi from "../../pages/genai/GenAi";
import { NewConnection } from "../../pages/connections/NewConnection";
import { ConnectionDetails } from "../../pages/connections/ConnectionDetails";

class Layout extends React.Component {
  static propTypes = {
    sidebarStatic: PropTypes.bool,
    sidebarOpened: PropTypes.bool,
    dispatch: PropTypes.func.isRequired,
  };

  static defaultProps = {
    sidebarStatic: true,
    sidebarOpened: true,
  };
  constructor(props) {
    super(props);
  }

  render() {
    const userDetails = JSON.parse(
      localStorage.getItem("userInfo") || { permissions: {} }
    );
    const {
      admin,
      audits,
      connections,
      dashboards,
      etls,
      jobs,
      pipelines,
      reports,
    } = userDetails?.permissions;
    return (
      <div
        className={[
          s.root,
          "sidebar-" + this.props.sidebarPosition,
          "sidebar-" + this.props.sidebarVisibility,
        ].join(" ")}
      >
        {/* <Header /> */}
        <div
          className={[
            s.wrap,
            this.props.sidebarOpened ? "" : s.sidebarClosed,
          ].join(" ")}
        >
          <Sidebar />
          <div className="d-flex flex-column flex-grow-1">
            <main className={`${s.content} pt-2 px-3 flex-grow-1`}>
              {this.props.loaderVisibility && <Loader />}
              {/* <BreadcrumbHistory url={this.props.location.pathname} /> */}
              <Routes>
                <Route path="/main" element={<Navigate to="/main/home" />} />
                {dashboards && <Route path="/main/home" element={<Home />} />}
                {connections && (
                  <>
                    <Route path="/connections" element={<Connections />} />
                    <Route path="/new_connection" element={<NewConnection />} />
                    <Route
                      path="/connections/:id"
                      element={<ConnectionDetails />}
                    />
                  </>
                )}
                {pipelines && (
                  <Route path="/pipelines" element={<Pipeline />} />
                )}
                {etls && (
                  <Route path="/datawarehouse" element={<DataWarehouse />} />
                )}
                {audits && <Route path="/audits" element={<Audits />} />}
                {jobs && <Route path="/jobs" element={<Jobs />} />}
                {reports && <Route path="/reports" element={<Reports />} />}
                <Route path="/databases" element={<Databases />} />
                <Route path="/logs" element={<Logs />} />
                {admin && <Route path="/admin" element={<Administration />} />}
                {<Route path="/genai" element={<GenAi />} />}
              </Routes>
            </main>
            {/* <footer
              className={`d-flex justify-content-center align-items-end ${s.contentFooter} position-absolute w-100 bg-wizBi text-wizBi`}
            >
              {new Date().getFullYear()} &copy; WizBI 3.0 - Nura Solutions
              Private Limited. All Rights Reserved |
              <a href="#" target="_blank" className="mx-2 text-wizBi">
                License Information
              </a>
            </footer> */}
          </div>
          <ConfirmDialog />
        </div>
      </div>
    );
  }
}

function mapStateToProps(store) {
  return {
    sidebarOpened: store.navigation.sidebarOpened,
    sidebarPosition: store.navigation.sidebarPosition,
    sidebarVisibility: store.navigation.sidebarVisibility,
    loaderVisibility: store.loader.loaderVisibility,
  };
}

export default withRouter(connect(mapStateToProps)(Layout));
