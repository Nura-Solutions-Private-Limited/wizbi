import { useEffect, useState } from "react";
import { hideLoader, showLoader } from "../actions/loader";
import { useDispatch } from "react-redux";
import { fetchConnections } from "../api/connection";

function useConnections() {
  const [connectionResult, setConnectionResult] = useState([]);
  const [error, setError] = useState(null);
  const dispatch = useDispatch();

  useEffect(() => {
    const fetchData = async () => {
      dispatch(showLoader());

      await fetchConnections((resp) => {
        try {
          if (resp && (resp.detail || resp.message)) {
            setError(resp.message || "An error occurred.");
          } else {
            setConnectionResult(resp);
          }
        } catch (err) {
          console.error(err); // Log any errors
          setError("Failed to fetch connections.");
        } finally {
          dispatch(hideLoader());
        }
      });
    };

    fetchData();
  }, [dispatch]);

  return { connectionResult, error };
}

export { useConnections };
