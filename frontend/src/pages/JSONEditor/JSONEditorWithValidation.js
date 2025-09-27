import React, { useMemo, useState } from "react";
import EditableJsonEditor from "./JSONEditorReact";

const JSONEditorWithValidation = ({ data, onChange, isEditable }) => {
  const memoizedData = useMemo(() => data, [data]);

  const [mode, setMode] = useState(isEditable ? "code" : "preview");
  const schema = {
    title: "Example Schema",
    type: "object",
    properties: {
      array: {
        type: "array",
        items: {
          type: "number",
        },
      },
      boolean: {
        type: "boolean",
      },
      number: {
        type: "number",
      },
    },
    required: ["array", "string", "boolean"],
  };
  const modes = ["tree", "form", "view", "code", "text"];

  const onModeChange = (mode) => {
    setMode(mode);
  };
  return (
    <div className="w-100 h-100">
      <div className="w-100 px-4" style={{ height: "calc(100% - 20px)" }}>
        <EditableJsonEditor
          schema={schema}
          data={memoizedData}
          mode={mode}
          modes={modes}
          indentation={4}
          jsonChange={onChange}
          onModeChange={onModeChange}
        />
      </div>
    </div>
  );
};

export default JSONEditorWithValidation;
