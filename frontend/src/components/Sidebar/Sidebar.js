import React, { useRef } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import s from "./Sidebar.module.scss";
import LinksGroup from "./LinksGroup/LinksGroup";

import {
  changeActiveSidebarItem,
  closeSidebar,
  openSidebar,
} from "../../actions/navigation";
import { logoutUser } from "../../actions/user";
import HomeIcon from "../Icons/SidebarIcons/HomeIcon";
import { withRouter } from "../../core/withRouter";
import LogsIcon from "../Icons/Global/LogsIcon";
import ScheduleIcon from "../Icons/Global/ScheduleIcon";

import ReportsIcon from "../Icons/Global/ReportsIcon";
import LogoIcon from "../Icons/HeaderIcons/LogoIcon";
import { TieredMenu } from "primereact/tieredmenu";
import avatar from "../../assets/avatar.png";
import AIIcon from "../Icons/Global/AIIcon";
import ConnectionsIcon from "../Icons/Global/ConnectionsIcon";
import PipelineIcon from "../Icons/Global/PipelineIcon";
import pdfFile from "../../assets/user_guide.pdf";
import AdminIconIcon from "../Icons/Global/AdminIcon";
import { OverlayPanel } from "primereact/overlaypanel";
import Notifications from "../Notifications/Notifications";

class Sidebar extends React.Component {
  static propTypes = {
    sidebarStatic: PropTypes.bool,
    sidebarOpened: PropTypes.bool,
    dispatch: PropTypes.func.isRequired,
    activeItem: PropTypes.string,
    location: PropTypes.shape({
      pathname: PropTypes.string,
    }).isRequired,
  };

  static defaultProps = {
    sidebarStatic: false,
    activeItem: "",
  };

  constructor(props) {
    super(props);

    this.doLogout = this.doLogout.bind(this);
    this.itemRenderer = this.itemRenderer.bind(this);

    this.toggleSidebar = this.toggleSidebar.bind(this);
    this.items = [
      {
        label: "User Guide",
        icon: "fa fa-file-pdf-o text-wizBi",
        template: this.itemRenderer,
        name: "guide",
      },
      {
        label: "Logout",
        icon: "fa fa-power-off text-wizBi",
        template: this.itemRenderer,
        name: "logout",
      },
    ];

    this.userDetails = JSON.parse(localStorage.getItem("userInfo") || {});
  }

  itemRenderer(item) {
    if (item.name === "logout") {
      return (
        <a
          className="flex align-items-center p-menuitem-link text-wizBi"
          onClick={this.doLogout}
          href="#"
        >
          <span className={item.icon} />

          <span className="mx-2">{item.label}</span>
          {/* {item.badge && <Badge className="ml-auto" value={item.badge} />} */}
          {item.shortcut && (
            <span className="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">
              {item.shortcut}
            </span>
          )}
        </a>
      );
    }
    return (
      <a
        className="flex align-items-center p-menuitem-link text-wizBi"
        href={pdfFile}
        download="user_guide.pdf"
      >
        <span className={item.icon} />
        <span className="mx-2">{item.label}</span>
        {/* {item.badge && <Badge className="ml-auto" value={item.badge} />} */}
        {item.shortcut && (
          <span className="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">
            {item.shortcut}
          </span>
        )}
      </a>
    );
  }

  doLogout(evt) {
    evt.preventDefault();
    this.props.dispatch(logoutUser());
    this.props.navigate("/login");
  }

  toggleSidebar(evt) {
    evt.preventDefault();
    // evt.stopImmediatePropagation();

    this.props.sidebarOpened
      ? this.props.dispatch(closeSidebar())
      : this.props.dispatch(openSidebar());
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
      genai,
      reports,
    } = userDetails?.permissions;

    return (
      <nav
        className={[
          s.root,
          "d-flex flex-column",
          this.props.sidebarOpened ? s.sidebarOpen : "",
        ].join(" ")}
        ref={(nav) => {
          this.element = nav;
        }}
      >
        <a
          onClick={this.toggleSidebar}
          className={`d-flex bg-wizBi navbar-brand align-items-end py-3 px-2 `}
          href="#"
        >
          <LogoIcon />
          {this.props.sidebarOpened && (
            <h1 className="m-0 p-0 text-white">WizBI</h1>
          )}
        </a>

        <ul className={`${s.nav} d-flex flex-column m-0`}>
          {dashboards && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Home"
              isHeader
              iconName={<HomeIcon className={s.menuIcon} />}
              link="/app/main"
              index="main"
            />
          )}
          {connections && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Connections"
              isHeader
              iconName={<ConnectionsIcon className={s.menuIcon} />}
              link="/app/connections"
              index="connections"
            />
          )}
          {pipelines && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Pipelines"
              isHeader
              iconName={<PipelineIcon className={s.menuIcon} />}
              link="/app/pipelines?filterId=all"
              index="pipelines"
              childrenLinks={[
                {
                  header: "SQL Data Warehouse",
                  link: "/app/pipelines?filterId=all&pipelineType=ETL",
                },
                {
                  header: "Staging Database",
                  link: "/app/pipelines?filterId=all&pipelineType=ELT",
                },
                {
                  header: "Data Migration",
                  link: "/app/pipelines?filterId=all&pipelineType=Migration",
                },
                {
                  header: "Data Lake",
                  link: "/app/pipelines?filterId=all&pipelineType=Spark",
                },
                {
                  header: "Social Media Analytics",
                  link: "/app/pipelines?filterId=all&pipelineType=SOCIAL_MEDIA",
                },
              ]}
            />
          )}
          {/* {etls && (
            <LinksGroup
              onActiveSidebarItemChange={(t) =>
                this.props.dispatch(changeActiveSidebarItem(t))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Data Warehouse"
              isHeader
              iconName={<TablesIcon className={s.menuIcon} />}
              link="/app/datawarehouse"
              index="datawarehouse"
            />
          )} */}
          {audits && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Audits"
              isHeader
              iconName={<LogsIcon className={s.menuIcon} />}
              link="/app/audits"
              index="audits"
            />
          )}
          {jobs && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Jobs"
              isHeader
              iconName={
                <ScheduleIcon className={s.menuIcon} />
                // <i className={`fa fa-clock-o  fa-2x mx-2 ${s.menuIcon}`}></i>
              }
              link="/app/jobs"
              index="jobs"
            />
          )}
          {reports && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Reports"
              isHeader
              iconName={<ReportsIcon className={s.menuIcon} />}
              link="/app/reports"
              index="reports"
            />
          )}

          {admin && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Administration"
              isHeader
              iconName={<AdminIconIcon className={s.menuIcon} />}
              link="/app/admin"
              index="admin"
            />
          )}

          {genai && (
            <LinksGroup
              onActiveSidebarItemChange={(activeItem) =>
                this.props.dispatch(changeActiveSidebarItem(activeItem))
              }
              activeItem={this.props.activeItem}
              sidebarOpened={this.props.sidebarOpened}
              header="Gen AI"
              isHeader
              iconName={<AIIcon className={s.menuIcon} />}
              link="/app/genai"
              index="genai"
            />
          )}

          <li style={{ marginTop: "auto" }}>
            <ul className="d-flex flex-column m-0">
              <li
                className={[s.customLink, "m-0"].join(" ")}
                style={{ alignSelf: "flex-end" }}
              >
                <Notifications />
              </li>

              <li
                className={[s.customLink, "m-0"].join(" ")}
                style={{ alignSelf: "flex-end" }}
              >
                <TieredMenu
                  model={this.items}
                  popup
                  ref={(menu) => {
                    this.menu = menu;
                  }}
                />
                <a onClick={(e) => this.menu.toggle(e)} class="none">
                  <span
                    className={`${s.avatar} rounded-circle thumb-sm float-left`}
                  >
                    <img src={avatar} alt="user" />
                  </span>
                  {userDetails.username}
                  <small className="d-block text-wizBi">
                    {userDetails.group_name}
                  </small>
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </nav>
    );
  }
}

function mapStateToProps(store) {
  return {
    sidebarOpened: store.navigation.sidebarOpened,
    sidebarStatic: store.navigation.sidebarStatic,
    activeItem: store.navigation.activeItem,
  };
}

export default withRouter(connect(mapStateToProps)(Sidebar));
