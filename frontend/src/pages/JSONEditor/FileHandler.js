import React from "react";
const FileHandler = ({ onUpload, data, isEditable }) => {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const jsonData = JSON.parse(event.target.result);
        onUpload(jsonData);
      };
      reader.readAsText(file);
    }
  };

  const handleDownload = () => {
    // Assuming data is the current JSON data
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "data.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {!isEditable && (
        <input
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="mx-3 form-control text-wizBi"
          style={{ width: "100px" }}
        />
      )}
      <button
        className="p-button p-component mx-2 bg-wizBi p-2"
        onClick={handleDownload}
      >
        Download JSON
      </button>
    </>
  );
};

export default FileHandler;
