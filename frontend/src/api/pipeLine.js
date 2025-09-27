import * as CONSTANTS from "../utilities/Constants";
import axios from "axios";
import { getHeaders } from "./common";

export const fetchPipelines = async (query = {} , callback) => {
  try {
    const response = await axios.get(CONSTANTS.FETCH_PIPELINES, {
      headers: getHeaders(),
      params: query,
    });
    callback(response.data);
  } catch (error) {
    if (error.response) {
      callback(error.response.data);
    } else if (error.request) {
      callback({ error: "No response received from the server" });
    } else {
      callback(error.message);
    }
  }
};

export const fetchConnections = async (callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.FETCH_CONNECTIONS, {
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
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
  } finally {
    // setLoading(false);
  }
};

export const deletePipeLineById = async (id, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.DELETE_PIPELINE}/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
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
  } finally {
    // setLoading(false);
  }
};

export const createPipeline = async (pipelineInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.CREATE_PIPELINE, {
      method: "POST",
      body: JSON.stringify(pipelineInfo),
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
        }`
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const getMetaData = async (pipelineID, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.GET_META_DATA}/${pipelineID}`, {
      method: "GET",
      // body: JSON.stringify(pipelineInfo),
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
        }`
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const getScheduleById = async (pipelineId, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.GET_SCHEDULES_BY_ID}/${pipelineId}`,
      {
        headers: { Authorization: `Bearer ${userInfo.access_token}` },
      }
    );
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
  } finally {
    // setLoading(false);
  }
};

export const updateScheduleById = async (
  pipelineId,
  { ...scheduleInfo },
  callback
) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.UPDATE_SCHEDULE_BY_ID}/${pipelineId}`,
      {
        method: "PATCH",
        body: JSON.stringify(scheduleInfo),
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      }
    );
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

export const getPipelineType = async (callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.PIPELINE_TYPE}`, {
      method: "GET",
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
        }`
      );
    }
    let jsonData = await response.json();
    // To Be Removed
    if (jsonData?.length) {
      jsonData = jsonData.map((item) => {
        if (item.pipeline_type === "DATALAKE") {
          item.description = `${item.description} (Beta)`;
        }
        return item;
      });
    }
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};
