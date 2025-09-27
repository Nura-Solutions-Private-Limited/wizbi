import React from "react";

const FormGroup = ({ children, className }) => (
  <div className={`col col-md-6 ${className}`}>{children}</div>
);

export default FormGroup;
