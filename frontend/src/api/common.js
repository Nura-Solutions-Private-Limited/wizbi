export const getHeaders = () => {
  const userInfo = JSON.parse(localStorage.userInfo);
  return {
    Authorization: `Bearer ${userInfo.access_token}`,
    Accept: "application/json",
    "Content-Type": "application/json",
  };
};
