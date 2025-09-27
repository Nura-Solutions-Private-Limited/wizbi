import React from "react";
import WizBIInput from "../../core/WizBIInput/WizBIInput";

const ConnectionField = ({
  className,
  labelName,
  value,
  panelClass,
  onChange,
  id,
  submitted,
  isInvalid,
  tabIndex,
  children,
}) => (
  <div className={`form-group mb-2 ${className || ""}`}>
    <WizBIInput
      labelName={labelName}
      className={isInvalid ? "is-invalid" : ""}
      controls={{
        value: value,
        onChange: onChange,
        id: id,
        tabindex: tabIndex,
      }}
      panelClass={panelClass}
    >
      {children}
    </WizBIInput>
  </div>
);

export default ConnectionField;
