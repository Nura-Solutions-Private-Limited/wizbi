import * as CONSTANTS from "../utilities/Constants";

export const fetchDatabaseTypes = async (callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.DATABASE_TYPES, {
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    });
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${
          errorDetails.detail || errorDetails.message
        }`
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const getDatabaseTypes = async () => {
  const userInfo = JSON.parse(localStorage.userInfo);
  const response = await fetch(CONSTANTS.DATABASE_TYPES, {
    headers: {
      Authorization: `Bearer ${userInfo.access_token}`,
    },
  });
  return await response.json();
};
