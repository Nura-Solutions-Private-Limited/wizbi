import React from "react";

const Large = ({ database_type }) => {
  const iconType = database_type?.toLowerCase();
  return (
    <div
      className="db-entity db-entity-lg d-inline-flex align-items-center justify-content-center text-white rounded m-1 me-2"
      style={{
        minHeight: "52px",
        minWidth: "52px",
      }}
    >
      <div className={`db-icon-lg ${iconType}-db`}></div>
    </div>
  );
};

const Small = ({ database_type }) => {
  const iconType = database_type?.toLowerCase();
  return (
    <div className="db-entity db-entity-sm d-inline-flex align-items-center justify-content-center text-white rounded m-1 me-2">
      <div className={`db-icon-sm ${iconType}-db`}></div>
    </div>
  );
};

const DatabaseIcon = {
  Large,
  Small,
};

export default DatabaseIcon;
