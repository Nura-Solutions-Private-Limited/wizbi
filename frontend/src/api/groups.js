import * as CONSTANTS from "../utilities/Constants";

export const fetchGroups = async (callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.FETCH_GROUPS, {
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
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
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};
export const addGroup = async (roleInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.ADD_GROUP, {
      method: "POST",
      body: JSON.stringify(roleInfo),
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
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};
export const updateGroupById = async (groupInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.UPDATE_GROUP}/${groupInfo.id}`, {
      method: "PUT",
      body: JSON.stringify(groupInfo),
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
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};
export const deleteGroupById = async (id, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.DELETE_GROUP}/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
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
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};
