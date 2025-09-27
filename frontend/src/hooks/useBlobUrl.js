import { useEffect, useState } from "react";
import { fetchDestERDiagram, fetchSourceERDiagram } from "../api/datawarehouse";

const useBlobUrl = (pipelineId, sourceTarget) => {
  const [blobSrc, setBlobSrc] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setError] = useState({ showError: false, message: "" });
  useEffect(() => {
    // dispatch(showLoader());
    setIsLoading(true);
    if (sourceTarget === "S") {
      fetchSourceERDiagram(pipelineId, (response) => {
        // dispatch(hideLoader());
        if (!!response.detail || !!response.stack) {
          setError({ showError: true, message: "Unable to load ER diagram!" });
        } else {
          setTimeout(() => {
            setBlobSrc(URL.createObjectURL(response));
          }, 0);
        }
        setIsLoading(false);
      });
    } else {
      fetchDestERDiagram(pipelineId, (response) => {
        // dispatch(hideLoader());
        if (!!response.detail || !!response.stack) {
          setError({ showError: true, message: "Unable to load ER diagram!" });
        } else {
          setTimeout(() => {
            setBlobSrc(URL.createObjectURL(response));
          }, 0);
        }
        setIsLoading(false);
      });
    }
  }, [pipelineId, sourceTarget]);

  return { blobSrc, isLoading, isError };
};

export default useBlobUrl;
