import { SHOW_LOADER, HIDE_LOADER } from "../actions/loader";

export default function auth(
  state = {
    loaderVisibility: false,
  },
  action,
) {
  switch (action.type) {
    case SHOW_LOADER:
      return Object.assign({}, state, {
        loaderVisibility: true,
      });
    case HIDE_LOADER:
      return Object.assign({}, state, {
        loaderVisibility: false,
      });
    default:
      return state;
  }
}
