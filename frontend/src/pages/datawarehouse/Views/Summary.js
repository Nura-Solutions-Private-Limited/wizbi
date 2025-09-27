import { Divider } from "primereact/divider";
import ArrowRightIcon from "../../../components/Icons/Global/ArrowRightIcon";
import StarSchema from "../../../components/StarSchema/StarSchema";

const Summary = ({ pipelineInfo }) => {
    return <div className="p-4">
        <div className="row">
            <div className="col-lg-5 col-md-5">
                <h5 className="my-2 p-0 text-center text-capitalize text-wizBi py-2">
                    {pipelineInfo.source_schema_name}
                </h5>
                <StarSchema pipelineId={pipelineInfo.id}
                    alt="Source ER Diagram"
                    sourceTarget="S" />
            </div>
            <div className="col-lg-2 col-md-2 d-flex d-flex flex-column justify-content-center align-items-center text-truncate">
                <Divider layout="vertical" />
                <div className="d-flex justify-content-center align-items-center flex-column">
                    <small className="text-wizBi">{`${pipelineInfo.name}(${pipelineInfo.id})`}</small>
                    <ArrowRightIcon />
                </div>
                <Divider layout="vertical" />
            </div>
            <div className="col-lg-5 col-md-5">
                <h5 className="my-2 p-0 text-capitalize text-wizBi py-2">
                    {pipelineInfo.dest_schema_name}
                </h5>

                <StarSchema pipelineId={pipelineInfo.id}
                    alt="Target ER Diagram"
                    sourceTarget="D" />
            </div>
        </div>
    </div>
};

export default Summary;