import s from "./Administration.module.scss";
import adminList from "../../assets/data/admin.json";
import { useEffect, useState } from "react";
import { Groups } from "./Groups/Groups";
import { Roles } from "./Roles/Roles";
import { Permissions } from "./Permissions/Permissions";
import {
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom";

export const Administration = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setRouteParams = (index) => {
    setActiveIndex(index);
    if (index === 1) {
      navigate({
        pathname: "/app/admin",
        search: `?${createSearchParams({
          activeTab: "roles",
        })}`,
      });
    } else if (index === 2) {
      navigate({
        pathname: "/app/admin",
        search: `?${createSearchParams({
          activeTab: "permissions",
        })}`,
      });
    } else {
      navigate({
        pathname: "/app/admin",
      });
    }
  };
  useEffect(() => {
    if (searchParams.get("activeTab")) {
      const info =
        searchParams.get("activeTab") === "roles"
          ? 1
          : searchParams.get("activeTab") === "permissions"
            ? 2
            : 0;
      setActiveIndex(info);
    }
  }, []);
  return (
    <>
      <div className={`row h-100`}>
        <div className={`row`}>
          <div className={`col-md-12 col-lg-12 m-0 p-0`}>
            <div className={`pb-1 d-flex mx-3 d-flex`}>
              {adminList.map((list, index) => {
                return (
                  <button
                    className={`p-button p-component mx-2 p-2 p-button-text ${activeIndex === index && s.active
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
          {activeIndex === 0 && <Groups />}
          {activeIndex === 1 && <Roles />}
          {activeIndex === 2 && <Permissions />}
        </div>
      </div>
    </>
  );
};
