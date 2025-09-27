import React, { useState, useEffect } from "react";
import {
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import genAI from "../../assets/data/genAI.json";
import s from "./GenAi.module.scss";
import AIForDashboard from "./AIForDashboard";
import AIForDataScience from "./AIForDatascience";

const PATH_URL = "/app/genai";

const GenAi = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setRouteParams = (index) => {
    setActiveIndex(index);
    if (index === 0) {
      navigate({
        pathname: PATH_URL,
        search: `?${createSearchParams({
          activeTab: "datascience",
        })}`,
      });
    } else if (index === 1) {
      navigate({
        pathname: PATH_URL,
        search: `?${createSearchParams({
          activeTab: "dashboard",
        })}`,
      });
    } else {
      navigate({
        pathname: PATH_URL,
      });
    }
  };

  useEffect(() => {
    if (searchParams.get("activeTab")) {
      const info = searchParams.get("activeTab") === "datascience" ? 0 : 1;
      setActiveIndex(info);
    }
  }, []);

  return (
    <div className={`row h-100`}>
      <div className={`row`}>
        <div className={`col-md-12 col-lg-12 m-0 p-0`}>
          <div className={`pb-1 d-flex mx-3 d-flex`}>
            {genAI.map((list, index) => {
              return (
                <button
                  className={`p-button p-component mx-2 p-2 p-button-text ${
                    activeIndex === index && s.active
                      ? "bg-wizBi text-white"
                      : " text-wizBi"
                  }`}
                  onClick={() => {
                    setRouteParams(index);
                  }}
                >
                  {list.name}
                </button>
              );
            })}
          </div>
        </div>
      </div>
      <div className={`col-md-12 col-lg-12`}>
        {activeIndex === 0 && <AIForDataScience />}
        {activeIndex === 1 && <AIForDashboard />}
      </div>
    </div>
  );
};
export default GenAi;
