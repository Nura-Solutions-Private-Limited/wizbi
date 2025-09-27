import { combineReducers } from "redux";
import auth from "./auth";
import navigation from "./navigation";
import loader from "./loader";
import register from "./register";

export default combineReducers({
  loader,
  auth,
  navigation,
  register,
});
