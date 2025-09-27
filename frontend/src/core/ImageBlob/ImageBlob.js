import React from "react";
import useBlobUrl from "../../hooks/useBlobUrl";
import { Image } from "primereact/image";

const ImageBlob = ({ pipelineId, sourceTarget, alt, ...rest }) => {
  const { blobSrc, isLoading, isError } = useBlobUrl(pipelineId, sourceTarget);
  const icon = <i className="fa fa-expand"></i>;

  return (
    <div className="d-flex justify-content-center flex-column align-items-center">
      {isLoading && <div className="spinner-border text-wizBi"></div>}
      {!isLoading && !isError.showError ? (
        <Image
          src={blobSrc}
          alt={alt}
          {...rest}
          className="w-100"
          style={{ height: "auto" }}
          template={icon}
          preview
          width="100%"
          height="auto"
        />
      ) : (
        <h6 className="text-center">{isError.message}</h6>
      )}
    </div>
  );
};

export default ImageBlob;
