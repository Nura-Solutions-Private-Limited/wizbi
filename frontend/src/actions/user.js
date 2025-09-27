import { login } from "../api/authAPI";

export const LOGIN_SUCCESS = "LOGIN_SUCCESS";
export const LOGIN_FAILURE = "LOGIN_FAILURE";
export const LOGOUT_REQUEST = "LOGOUT_REQUEST";
export const LOGOUT_SUCCESS = "LOGOUT_SUCCESS";

export function receiveLogin() {
  return {
    type: LOGIN_SUCCESS,
  };
}

function loginError(payload) {
  return {
    type: LOGIN_FAILURE,
    payload,
  };
}

function requestLogout() {
  return {
    type: LOGOUT_REQUEST,
  };
}

export function receiveLogout() {
  return {
    type: LOGOUT_SUCCESS,
  };
}

// Logs the user out
export function logoutUser() {
  return (dispatch) => {
    dispatch(requestLogout());
    localStorage.removeItem("authenticated");
    localStorage.removeItem("userInfo");
    dispatch(receiveLogout());
  };
}

export function loginUser(creds) {
  return (dispatch) => {
    login(creds, (resp) => {
      if (!!resp && (!!resp.detail || !!resp.message)) {
        dispatch(
          loginError(
            resp.detail || resp.message.indexOf("401") !== -1
              ? "Invalid username/password; logon denied"
              : resp.message,
          ),
        );
      } else {
        dispatch(receiveLogin());
        localStorage.setItem("userInfo", JSON.stringify(resp));
        localStorage.setItem("authenticated", true);
      }
    });
  };
}
