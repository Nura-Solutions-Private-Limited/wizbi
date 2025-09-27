import { useEffect, useState } from "react";
import { hideLoader, showLoader } from "../actions/loader";
import { useDispatch } from "react-redux";
import { fetchPipelines } from "../api/pipeLine";

function usePipelines(props = {}) {
  const [pipelinesResult, setPipelinesResult] = useState([]);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(showLoader());
    fetchPipelines(props, (resp) => {
      dispatch(hideLoader());
      if (!!resp && (!!resp.detail || !!resp.message)) {
      } else {
        setPipelinesResult(resp);
      }
    });
  }, []);

  return { pipelinesResult };
}

export { usePipelines };
