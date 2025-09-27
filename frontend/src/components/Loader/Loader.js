import React from "react";
import cx from "classnames";
import s from "./Loader.module.scss";

const Loader = (props) => {
  return (
    <div className={cx(s.root, props.className)}>
      <div className={cx(s.loader, props.className)}>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
  );
};

export default Loader;
