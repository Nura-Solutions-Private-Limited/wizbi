// import { useNavigate } from 'react-router-dom';
const { fetch: originalFetch, location } = window;
window.fetch = async (...args) => {
  let [resource, config] = args;
  const userInfo = localStorage.userInfo
    ? JSON.parse(localStorage.userInfo)
    : "";
  config["headers"] = config["headers"] ? config["headers"] : {};
  config["headers"]["Authorization"] = `Bearer ${userInfo?.access_token}`;
  let response = await originalFetch(resource, config);
  if (!response.ok && response.status === 401) {
    // 404 error handling
    // const navigate = useNavigate();
    // navigate('/login');

    localStorage.removeItem("userInfo");
    localStorage.removeItem("authenticated");
    if (location.href.indexOf(`${location.origin}/login`) === -1) {
      location.href = `${location.origin}/login`;
    }
    // return Promise.reject(response);
  }
  return response;
};
