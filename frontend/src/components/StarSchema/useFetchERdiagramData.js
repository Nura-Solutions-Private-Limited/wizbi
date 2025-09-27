import { useEffect, useState } from "react";
import { fetchDestERDiagramData, fetchSourceERDiagramData } from "../../api/datawarehouse";

export const useFetchERdiagramData = (pipelineId, sourceTarget) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setError] = useState({ showError: false, message: "" });
  const [response, setResponse] = useState([]);
  useEffect(() => {
    // dispatch(showLoader());
    setIsLoading(true);
    if (sourceTarget === "S") {
      fetchSourceERDiagramData(pipelineId, (response) => {
        // dispatch(hideLoader());
        if (!!response.detail || !!response.stack) {
          setError({ showError: true, message: "Unable to load ER diagram data!" });
        } else {
          setTimeout(() => {
            // setBlobSrc(URL.createObjectURL(response));
            setResponse(response);
          }, 0);
        }
        setIsLoading(false);
      });
    } else {
      fetchDestERDiagramData(pipelineId, (response) => {
        // dispatch(hideLoader());
        if (!!response.detail || !!response.stack) {
          setError({ showError: true, message: "Unable to load ER diagram data!" });
        } else {
          setTimeout(() => {
            // setBlobSrc(URL.createObjectURL(response));
            setResponse(response);
          }, 0);
        }
        setIsLoading(false);
      });
    }
  }, [pipelineId, sourceTarget]);

  return { response, isLoading, isError };
};

export default useFetchERdiagramData;
