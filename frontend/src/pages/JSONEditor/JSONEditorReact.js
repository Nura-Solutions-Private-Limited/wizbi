import React, { useState, useEffect, useRef } from "react";
import JSONEditor from "jsoneditor";
import "jsoneditor/dist/jsoneditor.css";

import debouce from "lodash.debounce";
const EditableJsonEditor = ({ data, jsonChange, mode }) => {
  const jsonEditorRef = useRef(null);

  useEffect(() => {
    if (!jsonEditorRef.current) {
      const container = document.getElementById("json_editor");
      const options = {
        mode: mode, // Set the default mode to 'tree'
        navigationBar: false,
        statusBar: false,
        outer: "jsoneditor-outer", // Set the outer container class
        mainMenuBar: false,
        onChange: debouce(() => {
          try {
            jsonChange(editor.get());
          } catch (e) {
            console.log(editor.get());
            console.log(e);
          }
        }, 1000),
      };
      const editor = new JSONEditor(container, options);
      jsonEditorRef.current = editor;
    }
    jsonEditorRef.current.set(data);
  }, [data, Object.keys(data)]);

  useEffect(() => {
    if (jsonEditorRef.current) {
      const dataSizeInBytes = new TextEncoder().encode(
        JSON.stringify(data),
      ).length;
      // Switch to 'text' mode if data size is greater than 10 MB
      if (dataSizeInBytes > 10 * 1024 * 1024) {
        jsonEditorRef.current.setMode("text");
      } else {
        jsonEditorRef.current.setMode(mode);
      }
    }
  }, [data, Object.keys(data)]);

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <div
        id="json_editor"
        className="jsoneditor-outer"
        style={{ height: "100%", width: "100%" }}
      ></div>
    </div>
  );
};

export default EditableJsonEditor;
