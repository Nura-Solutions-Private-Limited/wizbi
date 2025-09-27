import React, { useState, useEffect } from "react";
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  Handle,
  Controls,
  Background,
} from "react-flow-renderer";
import { useFetchERdiagramData } from "./useFetchERdiagramData";

const NodeLabel = ({ label, json }) => {
  const customNodeStyle = {
    padding: "10px",
    borderRadius: "5px",
    width: "120px", // Set the width of the node here
    textAlign: "center",
    background: "#fff",
    wordWrap: "break-word",
    overflowWrap: "break-word",
  };

  const labelStyle = {
    whiteSpace: "normal",
    wordWrap: "break-word",
    overflowWrap: "break-word",
    overflow: "visible",
    textOverflow: "clip",
    fontWeight: "bold",
    textDecoration: "underline",
  };

  const itemStyle = {
    whiteSpace: "normal",
    overflow: "visible",
    textOverflow: "clip",
  };

  return (
    <div style={customNodeStyle}>
      <div style={labelStyle}>{label}</div>
      <ul>
        {Object.keys(json).map((key) => (
          <li key={key} style={itemStyle}>
            {key}
          </li>
        ))}
      </ul>
    </div>
  );
};

const StarSchema = ({ pipelineId, sourceTarget, alt, ...rest }) => {
  const { response, isLoading, isError } = useFetchERdiagramData(
    pipelineId,
    sourceTarget
  );

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [zoomLevel, setZoomLevel] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  const onNodesChange = (changes) =>
    setNodes((nds) => applyNodeChanges(changes, nds));
  const onEdgesChange = (changes) =>
    setEdges((eds) => applyEdgeChanges(changes, eds));
  const onConnect = (params) => setEdges((eds) => addEdge(params, eds));

  const getNodesData = (elements, tableName) => {
    const obj = {};
    const collection = [...edges];
    elements.Columns.map((column) => {
      if (column.ForeignKey && column.ForeignKey.length) {
        collection.push({
          id: column.ForeignKey[0],
          source: tableName,
          target: column.ForeignKey[0].split(".")[1],
        });
      }
      return (obj[column.ColumnName] =
        `${column.ColumnType}:${column.ColumnType}`);
    });
    return { obj, collection };
  };

  useEffect(() => {
    if (response && response.length) {
      const jsonInfo = [];
      const edgesInfo = [];
      const angleStep = (2 * Math.PI) / (response[0]?.Tables.length - 1);
      const center = { x: 300, y: 300 };
      const radius = 300;
      response[0]?.Tables?.forEach((element, index) => {
        let isFactTable = false;
        if (
          element.TableName.toLowerCase().includes("fact") &&
          sourceTarget === "D"
        ) {
          isFactTable = true;
        }
        const angle = index * angleStep;
        const x = center.x + radius * Math.cos(angle);
        const y = center.y + radius * Math.sin(angle);

        const position = isFactTable ? center : { x, y };
        if (isFactTable) {
          const { obj, collection } = getNodesData(element, element.TableName);
          edgesInfo.push(...collection);

          jsonInfo.push({
            id: element.TableName,
            data: {
              label: element.TableName,
              json: obj,
              type: "input",
            },
            position,
          });
        } else {
          const { obj, collection } = getNodesData(element, element.TableName);
          edgesInfo.push(...collection);
          jsonInfo.push({
            id: element.TableName,
            data: {
              label: element.TableName,
              json: obj,
            },
            position,
          });
        }
      });
      setNodes(jsonInfo);
      setEdges(edgesInfo);
    }
  }, [response]);

  return (
    <div className="d-flex justify-content-center flex-column align-items-center">
      <div style={{ height: "100vh", width: "100%" }}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes.map((node) => ({
              ...node,
              data: {
                ...node.data,
                label: (
                  <NodeLabel label={node.data.label} json={node.data.json} />
                ),
              },
            }))}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            deleteKeyCode={46}
            snapToGrid={true}
            snapGrid={[15, 15]}
            zoom={zoomLevel}
            pan={pan}
            fitView
            minZoom={-100}
          >
            <Controls />
            <Background color="#000" gap={16} />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
    </div>
  );
};

export default StarSchema;
