const WizBIDropDown = (props) => {
  const getTextWidth = (text, font) => {
    // re-use canvas object for better performance
    const canvas =
      getTextWidth.canvas ||
      (getTextWidth.canvas = document.createElement("canvas"));
    const context = canvas.getContext("2d");
    context.font = font;
    const metrics = context.measureText(text);
    return Math.ceil(metrics.width) + 11;
  };
  return (
    <div className={`${props.panelClass ? props.panelClass : "my-4"}`}>
      <div
        className={`form-outline ${
          props.className ? ` ${props.className}` : ""
        }`}
      >
        {Array.isArray(props.children) ? props.children[0] : props.children}
        <label
          className={`form-label ${props.labelClass ? props.labelClass : ""}`}
          htmlFor={props.labelName}
        >
          {props.labelName}
        </label>
        <div className="form-notch">
          <div className="form-notch-leading" style={{ width: "9px" }}></div>
          <div
            className="form-notch-middle"
            style={{ width: getTextWidth(props.labelName) }}
          ></div>
          <div className="form-notch-trailing"></div>
        </div>
      </div>
      {Array.isArray(props.children) && props.children[1]}
    </div>
  );
};

export default WizBIDropDown;
