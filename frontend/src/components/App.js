import { Route, Routes, Navigate, Outlet } from "react-router-dom";
/* eslint-disable */
import ErrorPage from "../pages/error/ErrorPage";
/* eslint-enable */
import "../styles/theme.scss";
import LayoutComponent from "../components/Layout/Layout";
import Login from "../pages/login/Login";
import Register from "../pages/register/Register";
// import { logoutUser } from '../actions/user';
import React from "react";

const PrivateRoute = () => {
  return JSON.parse(localStorage.getItem("authenticated")) ? (
    <Outlet />
  ) : (
    <Navigate to="/login" />
  );
};

function App() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Navigate to="/app/main" />} />
        <Route path="/app" element={<Navigate to="/app/main" />} />
        <Route element={<PrivateRoute />}>
          <Route path="/app/*" element={<LayoutComponent />} />
        </Route>

        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/error" element={<ErrorPage />} />
        <Route element={<ErrorPage />} />
        <Route path="*" element={<Navigate to="/app/main/home" />} />
      </Routes>
    </div>
  );
}

export default App;
