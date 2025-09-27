import axios from "axios";
import * as CONSTANTS from "../utilities/Constants";
import { getHeaders } from "./common";

// export const generateQuestions = async (questionInfo, type) => {
//   try {
//     const response = await axios.post(
//       type === "fact"
//         ? CONSTANTS.GENAI_FACT_QUESTION
//         : CONSTANTS.GENAI_OTHER_QUESTION,
//       questionInfo,
//       {
//         headers: getHeaders(),
//       }
//     );
//     return response?.data || {};
//   } catch (err) {
//     return err;
//   }
// };

export const generateQuestions = async (questionInfo, type, callback) => {
    const url =     type === "fact"
        ? CONSTANTS.GENAI_FACT_QUESTION
        : CONSTANTS.GENAI_OTHER_QUESTION;
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(url, {
      method: "POST",
      body: JSON.stringify(questionInfo),
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

// export const generateCode = async (questionInfo) => {
//   try {
//     const response = await axios.post(
//       CONSTANTS.GENAI_FOLLOWUP_QUESTION,
//       questionInfo,
//       {
//         headers: getHeaders(),
//       }
//     );
//     return response.data;
//   } catch (err) {
//     return err;
//   }
// };


export const generateCode = async (questionInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.GENAI_FOLLOWUP_QUESTION, {
      method: "POST",
      body: JSON.stringify(questionInfo),
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

export const generateConnectionQuestion = async (questionInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.CONNECTION_QUESTION, {
      method: "POST",
      body: JSON.stringify(questionInfo),
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

export const generateGenAIDashboards = async (questionInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.GENAI_DASHBOARD_FACT_QUESTION, {
      method: "POST",
      body: JSON.stringify(questionInfo),
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

// export const generateGenAIDashboards = async (questionInfo) => {
//   try {
//     const response = await axios.post(
//       CONSTANTS.GENAI_DASHBOARD_FACT_QUESTION,
//       questionInfo,
//       {
//         headers: getHeaders(),
//       }
//     );
//     return response?.data || {};
//   } catch (err) {
//     return err;
//   }
// };

export const generateGenAIDashboardsOtherQuestions = async (questionInfo, callback) => {
  const userInfo = JSON.parse(localStorage.userInfo);
  try {
    const response = await fetch(CONSTANTS.GENAI_DASHBOARD_OTHER_QUESTION, {
      method: "POST",
      body: JSON.stringify(questionInfo),
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
}
// };
// export const generateGenAIDashboardsOtherQuestions = async (questionInfo) => {
//   try {
//     const response = await axios.post(
//       CONSTANTS.GENAI_DASHBOARD_OTHER_QUESTION,
//       questionInfo,
//       {
//         headers: getHeaders(),
//       }
//     );
//     return response?.data || {};
//   } catch (err) {
//     return err;
//   }
// };
