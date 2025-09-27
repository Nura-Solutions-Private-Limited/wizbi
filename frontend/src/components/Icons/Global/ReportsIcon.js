import React from "react";

class ReportsIcon extends React.Component {
  render() {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className={this.props.className}
        height="30px"
        width="30px"
        version="1.2"
        baseProfile="tiny"
        viewBox="-63 65 128 128"
      >
        <path d="M-31.7,97.6h57.9v31.3h-57.9V97.6z M-31.7,136.8h57.3v5.2h-57.3V136.8z M-31.7,162.2h57.3v5.2h-57.3V162.2z M-31.7,149.2  h57.3v5.2h-57.3V149.2z M-33.1,70.8v10h-11.6v104.6h84.9v-10h11.6V70.8H-33.1z M34.9,170.2v5.2v4.8h-74.4V86h6.4h5.2H35L34.9,170.2  L34.9,170.2z M46.5,170.2h-6.4V80.8h-68V76h74.4V170.2z" />
      </svg>
    );
  }
}

export default ReportsIcon;
