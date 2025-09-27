import React from "react";
import { Link } from "react-router-dom";

import s from "./ErrorPage.module.scss";

class ErrorPage extends React.Component {
  render() {
    return (
      <div className={s.errorPage}>
        <div className="container">
          <div className={`${s.errorContainer} mx-auto`}>
            <h1 className={s.errorCode}>404</h1>
            <p className={s.errorInfo}>
              Opps, it seems that this page does not exist here.
            </p>
            <p className={[s.errorHelp, "mb-3"].join(" ")}>
              If you are sure it should, please search for it:
            </p>

            <div className="form" method="get">
              <div className="form-group">
                <input
                  className="input-no-border form-control"
                  type="text"
                  placeholder="Search Pages"
                />
              </div>
              <Link to="app/extra/search">
                <button
                  className={`btn ${s.errorBtn}`}
                  type="submit"
                  color="inverse"
                >
                  Search <i className="fa fa-search text-secondary ml-xs" />
                </button>
              </Link>
            </div>
          </div>
          <footer className={s.pageFooter}></footer>
        </div>
      </div>
    );
  }
}

export default ErrorPage;
