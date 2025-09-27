import * as CONSTANTS from "../utilities/Constants";
export const login = async ({ username, password }, callback) => {
  let formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  const requestOptions = {
    method: "POST",
    body: formData,
  };
  try {
    const response = await fetch(CONSTANTS.LOGIN, requestOptions);
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${
          errorDetails.detail || errorDetails.message
        }`,
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  } finally {
    // setLoading(false);
  }
};

export const register = async (userInfo, callback) => {
  const requestOptions = {
    method: "POST",
    body: JSON.stringify({ ...userInfo.creds, type: "user" }),
    headers: {
      Authorization: `Bearer ${userInfo.access_token}`,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  };
  try {
    const response = await fetch(CONSTANTS.REGISTER, requestOptions);
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${
          errorDetails.detail || errorDetails.message
        }`,
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};
