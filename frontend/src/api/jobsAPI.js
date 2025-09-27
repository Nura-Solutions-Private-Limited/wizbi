import * as CONSTANTS from "../utilities/Constants";
export const fetchJobs = async (callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.FETCH_JOBS, {
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

export const createSchedule = async ({ ...scheduleInfo }, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.CREATE_SCHEDULE, {
      method: "POST",
      body: JSON.stringify(scheduleInfo),
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




export const getJobs = async ({ queryKey }) => {
  const [_key, { page, size }] = queryKey;
  const userInfo = JSON.parse(localStorage.userInfo);
  const res = await fetch(
    `${CONSTANTS.FETCH_PAGINATED_JOBS}?page=${page}&size=${size}`,
    {
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
    }
  );
  if (!res.ok) {
    throw new Error("Error fetching users");
  }
  return res.json();
};
