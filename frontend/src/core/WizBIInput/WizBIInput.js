const WizBIInput = (props) => {
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
        {props.controls.type === "textarea" ? (
          <textarea
            rows={5}
            className={`form-control resize-none text-black ${
              props.inputClass ? props.inputClass : ""
            }  ${
              props.controls.value && props.controls.value.length
                ? "active"
                : ""
            }`}
            {...props.controls}
          ></textarea>
        ) : (
          <input
            autocomplete="off"
            type={props.type || "text"}
            className={`form-control text-black ${
              props.inputClass ? props.inputClass : ""
            }  ${
              (
                typeof props.controls.value === "number"
                  ? typeof props.controls.value !== "undefined"
                  : props.controls.value && props.controls.value.length
              )
                ? "active"
                : ""
            }`}
            {...props.controls}
            style={{ height: "35px" }}
          />
        )}
        <label
          className={`form-label text-center ${
            props.labelClass ? props.labelClass : ""
          }`}
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
      {props.children && props.children}
    </div>
  );
};

export default WizBIInput;
