import axios from "axios";
import * as CONSTANTS from "../utilities/Constants";
import { getHeaders } from "./common";

export const fetchERDiagram = async (
  pipelineId,
  sourceTarget = "S",
  callback,
) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.FETCH_ER_DIAGRAM}/${pipelineId}?source_target=${sourceTarget}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      },
    );
    let jsonData = await response.blob();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const fetchSourceERDiagram = async (pipelineId, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.FETCH_ER_SOURCE_DIAGRAM}/${pipelineId}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      },
    );
    let jsonData = await response.blob();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};


export const fetchDestERDiagram = async (pipelineId, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.FETCH_ER_DEST_DIAGRAM}/${pipelineId}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      },
    );
    let jsonData = await response.blob();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};


//data



export const fetchSourceERDiagramData = async (pipelineId, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.FETCH_ER_SOURCE_DIAGRAM_DATA}/${pipelineId}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      },
    );
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};



export const fetchDestERDiagramData = async (pipelineId, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.FETCH_ER_DEST_DIAGRAM_DATA}/${pipelineId}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      },
    );
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

// 


export const genDWFromSource = async (pipelineId, metInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(
      `${CONSTANTS.GEN_DW_FROM_SOURCE}/${pipelineId}`,
      {
        method: "POST",
        body: JSON.stringify(metInfo),
        headers: {
          Authorization: `Bearer ${userInfo.access_token}`,
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      },
    );
    // if (!response.ok) {
    //     throw new Error(
    //         `This is an HTTP error: The status is ${response.status}`
    //     );
    // }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const runETL = async (summaryInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.RUN_ETL}`, {
      method: "POST",
      body: JSON.stringify(summaryInfo),
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const saveMetaData = async (pipelineId, metaData, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.SAVE_METADATA}/${pipelineId}`, {
      method: "POST",
      body: JSON.stringify(metaData),
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${errorDetails.detail || errorDetails.message
        }`,
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const runPipeline = async (pipelineId, callback, isDatalake) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${isDatalake ? CONSTANTS.SETUP_DATALAKE : CONSTANTS.RUN_PIPELINE}/${pipelineId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    // if (!response.ok) {
    //     throw new Error(
    //         `This is an HTTP error: The status is ${response.status}`
    //     );
    // }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const fetchDataTypes = async (pipelineId, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.FETCH_DATATYPES}/${pipelineId}`, {
      headers: { Authorization: `Bearer ${userInfo.access_token}` },
    });
    if (!response.ok) {
      let errorDetails = await response.json();
      throw new Error(
        `This is an HTTP error: The status is ${response.status} \n ${errorDetails.detail || errorDetails.message
        }`,
      );
    }
    let jsonData = await response.json();
    callback(jsonData);
  } catch (err) {
    callback(err);
  }
};

export const fetchDatabaseDatatypes = async () => {
  try {
    const response = await axios.get(CONSTANTS.FETCH_DATABASE_DATATYPES, {
      headers: getHeaders(),
    });
    return response.data;
  } catch (err) {
    return err;
  }
};

export const fetchDateForamtTypes = async () => {
  try {
    const response = await axios.get(CONSTANTS.FETCH_DATE_FORMAT_TYPES, {
      headers: getHeaders(),
    });
    return response.data;
  } catch (err) {
    return err;
  }
};

export const fetchFilePreview = async (id, isDataLake=false) => {
  try {
    const response = await axios.get(`${isDataLake? CONSTANTS.FETCH_ICEBERG_FILE_PREVIEW : CONSTANTS.FETCH_FILE_PREVIEW}/${id}`, {
      headers: getHeaders(),
    });
    return response.data;
  } catch (err) {
    return err;
  }
};

export const s3dataLoad = async (id, dataloadInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.S3_DATA_LOAD}/${id}`, {
      method: "POST",
      body: JSON.stringify(dataloadInfo),
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    // if (!response.ok) {
    //     throw new Error(
    //         `This is an HTTP error: The status is ${response.status}`
    //     );
    // }
    let jsonData = await response.json();
    if (callback) {
      callback(jsonData);
    }
  } catch (err) {
    callback(err);
  }
};

export const localDataLoad = async (id, dataloadInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(`${CONSTANTS.LOCAL_DATA_LOAD}/${id}`, {
      method: "POST",
      body: JSON.stringify(dataloadInfo),
      headers: {
        Authorization: `Bearer ${userInfo.access_token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    // if (!response.ok) {
    //     throw new Error(
    //         `This is an HTTP error: The status is ${response.status}`
    //     );
    // }
    let jsonData = await response.json();
    if (callback) {
      callback(jsonData);
    }
  } catch (err) {
    callback(err);
  }
};
