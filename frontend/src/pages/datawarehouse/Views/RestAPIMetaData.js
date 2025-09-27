import JsonEditor from "../../connections/JsonEditor";

const RestAPIMetaData = ({
  // setJsonData,
  setMetaData,
  // setCloneMetaData,
  metaData,
  isSaved,
  toast,
}) => {
  return (
    <JsonEditor
      data={metaData}
      isEditable={!isSaved}
      toast={toast}
      onChange={(updatedJson) => {
        const response = updatedJson ? updatedJson : [];
        // setJsonData(response);
        setMetaData(response);
        // setCloneMetaData(response);
      }}
    />
  );
};

export default RestAPIMetaData;
