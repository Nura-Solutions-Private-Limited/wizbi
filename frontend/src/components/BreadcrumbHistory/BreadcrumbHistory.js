import React, { Component } from "react";
import { v4 as uuidv4 } from "uuid";

class BreadcrumbHistory extends Component {
  renderBreadCrumbs = () => {
    let route = this.props.url
      .split("/")
      .slice(1)
      .map((route) =>
        route
          .split("-")
          .map((word) => word[0].toUpperCase() + word.slice(1))
          .join(" "),
      );
    const length = route.length;
    return route.map((item, index) =>
      length === index + 1 ? (
        <li className="breadcrumb-item active" key={uuidv4()}>
          <strong>{item}</strong>
        </li>
      ) : (
        <li className="breadcrumb-item" key={uuidv4()}>
          {item}
        </li>
      ),
    );
  };

  render() {
    return (
      <>
        {this.props.url !== "/app/chat" ? (
          <div>
            <nav aria-label="breadcrumb">
              <ol className="breadcrumb">
                {/* <li className="breadcrumb-item">YOU ARE HERE</li> */}
                {this.renderBreadCrumbs()}
              </ol>
            </nav>
          </div>
        ) : null}
      </>
    );
  }
}

export default BreadcrumbHistory;
