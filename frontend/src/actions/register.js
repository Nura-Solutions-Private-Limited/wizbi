import { register } from "../api/authAPI";

export const REGISTER_REQUEST = "REGISTER_REQUEST";
export const REGISTER_SUCCESS = "REGISTER_SUCCESS";
export const REGISTER_FAILURE = "REGISTER_FAILURE";

export function receiveRegister(payload) {
  return {
    type: REGISTER_SUCCESS,
    payload,
  };
}

export function registerError(payload) {
  return {
    type: REGISTER_FAILURE,
    payload,
  };
}

export function registerUser(payload) {
  return (dispatch) => {
    register(payload, (resp) => {
      if (payload.callbackRef) {
        payload.callbackRef();
      }
      if (!!resp && (!!resp.detail || !!resp.message)) {
        dispatch(registerError("Something was wrong. Please try again."));
      } else {
        dispatch(receiveRegister("You have successfully registered."));
      }
    });
  };
}
