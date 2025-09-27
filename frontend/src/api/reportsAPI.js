import * as CONSTANTS from "../utilities/Constants";
export const fetchReports = async (report_type, pipeline_id, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const URL = pipeline_id
      ? `${CONSTANTS.FETCH_REPORTS}/${pipeline_id}?report_type=${report_type}`
      : `${CONSTANTS.FETCH_REPORTS}?report_type=${report_type}`;
    const response = await fetch(URL, {
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
    });
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

export const getReports = async (URL, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(URL, {
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
    });
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

export const showReports = async (url, id, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`/rebiz/v1/${url}/${id}`, {
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
    });
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${
          errorDetails.detail || errorDetails.message
        }`,
      );
    }
    let jsonData = await response.blob();
    callback && callback(jsonData);
  } catch (err) {
    callback && callback(err);
  }
};

export const createReports = async (reportsInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.CREATE_REPORTS}`, {
      method: "POST",
      body: JSON.stringify(reportsInfo),
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${
          errorDetails.detail || errorDetails.message
        }`,
      );
    }
    let jsonData = await response.blob();
    callback && callback(jsonData);
  } catch (err) {
    callback && callback(err);
  }
};
