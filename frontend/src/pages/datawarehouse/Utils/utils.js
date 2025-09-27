export const isDraftStatus = ({ status = "" }) => {
  return ["saved", "design"].includes(status.toLowerCase()) !== true;
};
