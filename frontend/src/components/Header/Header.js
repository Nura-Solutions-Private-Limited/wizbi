import React from "react";
import PowerIcon from "../Icons/HeaderIcons/PowerIcon";
import { logoutUser } from "../../actions/user";
import s from "./Header.module.scss";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import avatar from "../../assets/avatar.png";
import LogoIcon from "../Icons/HeaderIcons/LogoIcon";
import pdfFile from "../../assets/user_guide.pdf";
const Header = (props) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const doLogout = () => {
    dispatch(logoutUser());
    navigate("/login");
  };

  const userDetails = JSON.parse(localStorage.getItem("userInfo") || {});
  return (
    <nav className={`navbar d-print-none ${s.root}`}>
      <Link
        className={`navbar-brand text-center brand text-white m-0 p-0 mx-3`}
        to="/main"
      >
        <div className="d-flex align-items-end justify-content-center flex-start">
          <LogoIcon className={s.headerIcon} />
          <h2 className="m-0 p-0">WizBI</h2>
        </div>
        <small>Redefine Your Business</small>
      </Link>
      <div className={`d-print-none d-flex`}>
        <ul className="ml-md-0 nav d-flex align-items-center justify-content-center">
          <li className="list-item mx-3">
            <a href={pdfFile} download="user_guide.pdf">
              <i
                className="fa fa-file-pdf-o text-white"
                style={{ fontSize: "20px" }}
                role="button"
              ></i>
            </a>
          </li>

          <li className="list-item d-flex align-items-center mx-3">
            <span className={`${s.avatar} rounded-circle thumb-sm float-left`}>
              <img src={avatar} alt="..." />
            </span>
            <span
              className={`small d-sm-down-none text-white text-capitalize ${s.accountCheck}`}
            >
              {userDetails.username}
              <small className="d-block text-muted">
                {userDetails.group_name}
              </small>
            </span>
          </li>
          <li className="list-item mx-3">
            <a
              onClick={doLogout}
              className={`${s.navItem} text-white nav-link`}
              href="#"
            >
              <PowerIcon className={s.headerIcon} />
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Header;
