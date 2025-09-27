export const validateKeyValueIgnoreCase = (obj, propertyName, value) => {
  const propertyValue = obj[propertyName]?.toLowerCase();
  return propertyValue && propertyValue.includes(value.toLowerCase());
};
