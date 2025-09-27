import React, { useState } from "react";
import { json } from "@codemirror/lang-json";
import { EditorView } from "@codemirror/view";
import { useCodeMirror } from "@uiw/react-codemirror";
import debounce from "lodash.debounce";

const JsonEditor = ({
  isEditable,
  data,
  theme = "none",
  toast,
  onChange = () => {},
  debounceDelay = 500,
}) => {
  React.useEffect(() => {
    const jsonFormat = JSON.stringify(data, null, 2);
    setJsonCode(jsonFormat);
  }, [data]);

  const [jsonCode, setJsonCode] = useState("");
  const [error, setError] = useState("");

  const debouncedOnChange = React.useMemo(() => {
    return debounce((value) => {
      if (typeof value === "string") {
        const parsedValue = JSON.parse(value); // Ensure valid JSON before passing
        return onChange(parsedValue); // Properly format before sending
      }
      return onChange(value);
    }, debounceDelay);
  }, [onChange, debounceDelay]);

  // Call debouncedOnChange whenever localJsonCode changes
  React.useEffect(() => {
    debouncedOnChange(data);
    // Cleanup the debounce on component unmount
    return () => {
      debouncedOnChange.cancel();
    };
  }, [data, debouncedOnChange]);

  // CodeMirror setup with editable or read-only JSON
  const { setContainer } = useCodeMirror({
    value: jsonCode,
    extensions: [json(), EditorView.editable.of(isEditable)], // JSON mode, editable based on prop
    theme,
    onChange: (value) => {
      setJsonCode(value); // Update JSON as user edits
    },
  });

  // Validate and format JSON
  const validateAndFormatJson = (event) => {
    try {
      event.preventDefault();
      const parsedJson = JSON.parse(jsonCode); // Validate JSON
      const formattedJson = JSON.stringify(parsedJson, null, 2); // Format JSON
      setJsonCode(formattedJson); // Update the editor with formatted JSON
      onChange(formattedJson); // Send formatted JSON to parent
      setError(""); // Clear any error
      toast.current.show({
        severity: "success",
        summary: "Confirmed",
        detail: "JSON is valid and formatted!",
        life: 3000,
      });
    } catch (err) {
      setError(`Invalid JSON: ${err.message}`); // Set error message if invalid
      toast.current.show({
        severity: "error",
        summary: "Error",
        detail: err.message,
        life: 3000,
      });
    }
  };

  // Copy JSON to clipboard
  const copyToClipboard = (event) => {
    event.preventDefault();
    navigator.clipboard.writeText(jsonCode);
    toast.current.show({
      severity: "success",
      summary: "Confirmed",
      detail: "JSON copied to clipboard!",
      life: 3000,
    });
  };

  return (
    <div className="p-2 h-100">
      <div
        ref={setContainer}
        style={{
          border: "1px solid #ddd",
          minHeight: "100px",
          height: "100%",
          backgroundColor: "#1e1e1e",
          color: "white",
          padding: "10px",
          overflow: "auto",
        }}
      />
      <br />
      {isEditable && (
        <>
          <button
            className="p-button p-component p-2 bg-wizBi"
            onClick={validateAndFormatJson}
          >
            Validate & Format JSON
          </button>
        </>
      )}
      <button
        className="p-button p-component p-2 bg-wizBi"
        onClick={copyToClipboard}
        style={{ marginLeft: "10px" }}
      >
        Copy JSON
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default JsonEditor;
