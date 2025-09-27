export const TextWizBi = ({ label, value }) => {
  return (
    <div className="form-outline mb-2">
      <label className="form-label text-wizBi" htmlFor={label}>
        {label}:
      </label>
      <span className="mx-2">{value}</span>
    </div>
  );
};
