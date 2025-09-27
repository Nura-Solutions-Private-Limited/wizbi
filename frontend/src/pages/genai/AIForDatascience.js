import React, { useState, useEffect, useRef } from "react";
import { generateCode, generateQuestions, generateConnectionQuestion } from "../../api/genai";
import { fetchPipelines } from "../../api/pipeLine";
import { fetchConnections as fetchAllConnections } from "../../api/connection";
import { Select, Radio, Button, Input, Row, Col, Modal } from "antd";

import { isArray, isEmpty } from "lodash";
import { CodeExtract } from "./CodeExtract";
import WizBIDropDown from "../../core/WizBIDropDown/WizBIDropDown";
import { Dropdown } from "primereact/dropdown";
import { Toast } from "primereact/toast";

const { Option } = Select;

const resetPipelineInfo = {
  name: "",
  description: "description",
  airflow_pipeline_name: "airflow_pipeline_name",
  airflow_pipeline_link: "airflow_pipeline_link",
  status: "",
  source_schema_name: "",
  dest_schema_name: "",
  db_conn_source_id: 0,
  db_conn_dest_id: 0,
};

const AIForDataScience = () => {
  const toast = useRef(null);
  const [questions, setQuestions] = useState({});
  const [loading, setLoading] = useState(true);
  const [qType, setQType] = useState("fact");
  const [pipelineOptions, setPipelineOptions] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState(resetPipelineInfo);
  const [radioEnabled, setRadioEnabled] = useState(false);
  const [customQuestion, setCustomQuestion] = useState("");
  const [customQuestionError, setCustomQuestionError] = useState("");
  const [generateLoading, setGenerateLoading] = useState(false);
  const [generateCodeLoading, setGenerateCodeLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState("");
  const [selectedQuestion, setSelectedQuestion] = useState([]);

  const [algorithmEnabled, setAlgorithmEnabled] = useState(false);
  const [algorithmName, setAlgorithmName] = useState("");
  const [sourceType, setSourceType] = useState("pipeline"); // 'pipeline' | 'connection'
  const [connectionOptions, setConnectionOptions] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [connectionResponse, setConnectionResponse] = useState(null);
  const pipelineQuery = {
    pipeline_status: "active",
    pipeline_type: "ETL",
  };
  const [viewGeneratedCode, setViewVisible] = useState(false);

  const generateTextModal = () => {
    setViewVisible(true);
  };

  const handleModalOk = () => {
    setViewVisible(false);
  };

  const handleModalCancel = () => {
    setViewVisible(false);
  };

  

  const fetchQuestions = async (questionInfo) => {
    setGenerateLoading(true);
    setLoading(true);
    generateQuestions(questionInfo, qType, (resp) => {
      if (!!resp && (!!resp.detail || !!resp.message)) {
        setLoading(false);
        setGenerateLoading(false);
        toast.current.show({
          severity: "error",
          summary: "Error",
          detail: resp.detail || resp.message,
          life: 3000,
        });
      } else {
        if (resp) {
          if (qType === "fact") {
            setQuestions(resp?.questions || []);
          } else {
            setQuestions([
              {
                customQuestion,
              },
            ]);
          }
          setLoading(false);
          setGenerateLoading(false);
        }
      }
    });
  };

  useEffect(() => {
    fetchPipelines(pipelineQuery, (data) => {
      isArray(data) && setPipelineOptions(data);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const hasSelection =
      (sourceType === "pipeline" && !!selectedPipeline && !!selectedPipeline.id) ||
      (sourceType === "connection" && !!selectedConnection && !!selectedConnection.id);
    setRadioEnabled(hasSelection);
  }, [sourceType, selectedPipeline, selectedConnection]);

  useEffect(() => {
    if (sourceType === "connection") {
      fetchAllConnections((data) => {
        if (Array.isArray(data)) {
          setConnectionOptions(data);
        }
      });
    }
  }, [sourceType]);

  const handlePipelineChange = (value) => {
    setSelectedPipeline(value);
    setGeneratedCode("");
    setCustomQuestion("");
    setCustomQuestionError("");
    setAlgorithmEnabled(false);
    setQType(null);
    setAlgorithmName("");
    setQuestions([]);
  };

  const handleConnectionChange = (value) => {
    setSelectedConnection(value);
    setGeneratedCode("");
    setCustomQuestion("");
    setCustomQuestionError("");
    setAlgorithmEnabled(false);
    setQType("other");
    setAlgorithmName("");
    setQuestions([]);
    setConnectionResponse(null);
  };

  const handleSourceTypeChange = (e) => {
    const newType = e.target.value;
    setSourceType(newType);
    setGeneratedCode("");
    setCustomQuestion("");
    setCustomQuestionError("");
    setAlgorithmEnabled(false);
    setQType(newType === "connection" ? "other" : "fact");
    setAlgorithmName("");
    setQuestions([]);
    setConnectionResponse(null);
    if (newType === "pipeline") {
      setSelectedConnection(null);
    } else {
      setSelectedPipeline(resetPipelineInfo);
    }
  };

  const handleRadioChange = (e) => {
    setQType(e.target.value);
    setCustomQuestion("");
    setCustomQuestionError("");
    setAlgorithmEnabled(false);
    setGeneratedCode("");
    setAlgorithmName("");
  };

  const handleGenerateClick = () => {
    setLoading(true);
    if (sourceType === "pipeline") {
      const payload = qType === "fact"
        ? { pipeline_id: selectedPipeline.id }
        : { pipeline_id: selectedPipeline.id, question: customQuestion };
      fetchQuestions(payload);
    } else if (sourceType === "connection") {
      // For connections, call the connection question API with { db_conn_id, question }
      setGenerateLoading(true);
      generateConnectionQuestion(
        { db_conn_id: selectedConnection?.id, question: customQuestion },
        (resp) => {
          if (!!resp && (!!resp.detail || !!resp.message)) {
            setLoading(false);
            setGenerateLoading(false);
            toast.current.show({
              severity: "error",
              summary: "Error",
              detail: resp.detail || resp.message,
              life: 3000,
            });
          } else {
            if (resp) {
              const sql = resp?.sql_query || resp?.response || "";
              setConnectionResponse({
                question: resp?.question || customQuestion,
                sql_query: sql,
              });
              // Treat SQL as generated code for connection flow
              setGeneratedCode(sql);
              setLoading(false);
              setGenerateLoading(false);
            }
          }
        }
      );
    }
  };

  const handleCustomQuestionChange = (e) => {
    const value = e.target.value;
    setCustomQuestion(value);
    setGeneratedCode("");
    if (sourceType === "connection") {
      setConnectionResponse(null);
    }
    if (value.length < 20) {
      setCustomQuestionError("Please enter at least 20 characters");
    } else {
      setCustomQuestionError("");
      qType !== "fact" && setAlgorithmEnabled(true);
    }
  };

  const handleAlgorithmNameChange = (e) => {
    setGeneratedCode("");
    setAlgorithmName(e.target.value);
  };

  const handleQuestionSelection = (e) => {
    setSelectedQuestion(e.target.value);
    setGeneratedCode("");
    if (e.target.value.length > 0) {
      setAlgorithmEnabled(true);
    } else {
      setAlgorithmEnabled(false);
    }
  };

  const handleGenerateCodeClick = async () => {
    setGenerateCodeLoading(true);
    generateCode(
      {
        pipeline_id: selectedPipeline.id,
        question: selectedQuestion,
        algorithm: algorithmName,
      },
      (resp) => {
        if (!!resp && (!!resp.detail || !!resp.message)) {
          setGenerateCodeLoading(false);
          toast.current.show({
            severity: "error",
            summary: "Error",
            detail: resp.detail || resp.message,
            life: 3000,
          });
        } else {
          if (resp) {
            setGenerateCodeLoading(false);
            setGeneratedCode(resp?.response ?? "");
          }
        }
      }
    );
  };

  // Note: For connection flow, generated SQL is directly set as generatedCode

  return (
    <div style={{ padding: 20 }}>
      <h5 className="mb-5">
        Generative AI assisted code for advanced data analysis
      </h5>

      <Row gutter={[16, 16]} justify="start" align="middle" className="mb-3">
        <Col span={6}>
          <h6 htmlFor="engine">Select AI Engine:</h6>
        </Col>
        <Col span={6}>
          <Select
            id="engine"
            placeholder="Select Pipeline"
            style={{ width: "100%" }}
            defaultValue={"1"}
          >
            {[{ id: "1", name: "LLM-ChatGPT-4o" }].map((engine) => (
              <Option key={engine.id} value={engine.id}>
                {engine.name}
              </Option>
            ))}
          </Select>
        </Col>
      </Row>
      <Row gutter={[16, 16]} justify="start" align="middle" className="mb-3">
        <Col span={6}>
          <h6 htmlFor="sourceType">Select Data Source:</h6>
        </Col>
        <Col span={16}>
          <Radio.Group onChange={handleSourceTypeChange} value={sourceType}>
            <Radio value="pipeline">Pipeline</Radio>
            <Radio value="connection">Connection</Radio>
          </Radio.Group>
        </Col>
      </Row>
      {sourceType === "pipeline" && (
        <Row gutter={[16, 16]} justify="start" align="middle" className="mb-3">
          <Col span={6}>
            <h6 htmlFor="pipeline">Select Data Warehouse Pipeline:</h6>
          </Col>
          <Col span={6}>
            <WizBIDropDown labelName="Pipeline" panelClass="mb-2 w-100">
              <Dropdown
                filter
                value={selectedPipeline}
                style={{ height: "35px" }}
                className="w-100 d-flex form-control active  align-items-center"
                onChange={(e) => handlePipelineChange(e.value)}
                options={pipelineOptions}
                optionLabel="name"
                placeholder="Select a Pipeline"
              />
            </WizBIDropDown>
          </Col>
        </Row>
      )}
      {sourceType === "connection" && (
        <Row gutter={[16, 16]} justify="start" align="middle" className="mb-3">
          <Col span={6}>
            <h6 htmlFor="connection">Select Connection:</h6>
          </Col>
          <Col span={6}>
            <WizBIDropDown labelName="Connection" panelClass="mb-2 w-100">
              <Dropdown
                filter
                value={selectedConnection}
                style={{ height: "35px" }}
                className="w-100 d-flex form-control active  align-items-center"
                onChange={(e) => handleConnectionChange(e.value)}
                options={connectionOptions}
                optionLabel="db_conn_name"
                placeholder="Select a Connection"
              />
            </WizBIDropDown>
          </Col>
        </Row>
      )}

      {radioEnabled && sourceType === "pipeline" && (
        <Row
          gutter={[16, 16]}
          justify="start"
          align="middle"
          className="mb-3"
          style={{ marginTop: 20 }}
        >
          <Col span={6}>
            <h6 htmlFor="pipeline">Select Question Type:</h6>
          </Col>
          <Col span={16}>
            <Radio.Group onChange={handleRadioChange} value={qType}>
              <Radio value="fact">
                Generate 25 questions for analysis based on data warehouse
                schema
              </Radio>
              <Radio value="other">
                Ask a question based on the data warehouse schema
              </Radio>
            </Radio.Group>
          </Col>
        </Row>
      )}

      {qType === "other" && (
        <Row
          gutter={[16, 16]}
          justify="start"
          align="start"
          style={{ marginTop: 10 }}
        >
          <Col span={6} />
          <Col span={sourceType === "connection" ? 12 : 4}>
            {sourceType === "connection" ? (
              <Input.TextArea
                rows={4}
                placeholder="Enter your custom question"
                value={customQuestion}
                onChange={handleCustomQuestionChange}
              />
            ) : (
              <Input
                placeholder="Enter your custom question"
                value={customQuestion}
                onChange={handleCustomQuestionChange}
              />
            )}
            {customQuestionError && (
              <span style={{ color: "red" }}>{customQuestionError}</span>
            )}
          </Col>
        </Row>
      )}

      {radioEnabled && qType === "fact" && sourceType === "pipeline" && (
        <Row gutter={[16, 16]} justify="start" align="start" className="mb-3">
          <Col span={6} />
          <Col span={8}>
            <Button
              type="primary"
              style={{ marginLeft: 10 }}
              onClick={handleGenerateClick}
              disabled={!isEmpty(questions) && Object.keys(questions).length}
              loading={generateLoading}
            >
              Generate
            </Button>
          </Col>
        </Row>
      )}

      {radioEnabled && qType === "other" && (
        <Row gutter={[16, 16]} justify="start" align="start" className="mb-3" style={{ marginTop: 16 }}>
          {sourceType === "connection" ? (
            <>
              <Col span={3} offset={6}>
                <Button
                  type="primary"
                  onClick={handleGenerateClick}
                  size="medium"
                  disabled={
                    (!!customQuestionError || !customQuestion || customQuestion.length < 20) ||
                    (!isEmpty(questions) && Object.keys(questions).length)
                  }
                  loading={generateLoading}
                >
                  Generate Code
                </Button>
              </Col>
              <Col span={1}></Col>
              <Col span={3} className="ml-1">
                <Button
                  size="medium"
                  type="primary"
                  onClick={generateTextModal}
                  disabled={!generatedCode}
                >
                  View Generated Code
                </Button>
              </Col>
            </>
          ) : (
            <>
              <Col span={6} />
              <Col span={8}>
                <Button
                  type="primary"
                  style={{ marginLeft: 10 }}
                  onClick={handleGenerateClick}
                  disabled={
                    (!!customQuestionError || !customQuestion || customQuestion.length < 20) ||
                    (!isEmpty(questions) && Object.keys(questions).length)
                  }
                  loading={generateLoading}
                >
                  Generate
                </Button>
              </Col>
            </>
          )}
        </Row>
      )}

      {sourceType === "connection" && connectionResponse?.sql_query && (
        <Row gutter={[16, 16]} justify="start" align="start" className="mb-3">
          <Col span={6}>
            <h6 htmlFor="generatedSql">Generated SQL:</h6>
          </Col>
          <Col span={12}>
            <div
              style={{
                maxHeight: "26vh",
                overflowY: "auto",
                overflowX: "hidden",
                border: "1px solid #eee",
                borderRadius: 4,
                padding: 10,
                background: "#fafafa",
              }}
            >
              <div style={{ marginBottom: 8 }}>
                <strong>Question:</strong> {connectionResponse.question}
              </div>
              <pre style={{ margin: 0 }}>{connectionResponse.sql_query}</pre>
            </div>
          </Col>
        </Row>
      )}

      {false && sourceType === "connection" && (
        <Row
          gutter={[16, 16]}
          justify="start"
          align="middle"
          className="mb-3"
          style={{ marginTop: 20, marginBottom: 20 }}
        >
          <Col span={3} className="ml-1" offset={6}>
            <Button
              size="medium"
              type="primary"
              onClick={generateTextModal}
              disabled={!generatedCode}
            >
              View Generated Code
            </Button>
          </Col>
        </Row>
      )}

      {!loading && qType === "fact" && Object.keys(questions).length > 0 && (
        <Row gutter={[16, 16]} justify="start" align="start" className="mb-3">
          <Col span={6}>
            <h6 htmlFor="genretedQuestions">Generated Questions:</h6>
          </Col>

          <Col span={12}>
            <div
              style={{
                maxHeight: "26vh",
                overflowY: "auto",
                overflowX: "hidden",
              }}
            >
              <Radio.Group onChange={handleQuestionSelection}>
                {Object.entries(questions).map(([id, question]) => (
                  <Radio
                    key={id}
                    value={question}
                    className="mb-1"
                    style={{ width: "100%" }}
                  >
                    {question}
                  </Radio>
                ))}
              </Radio.Group>
            </div>
          </Col>
        </Row>
      )}

      {algorithmEnabled && sourceType === "pipeline" && (
        <Row
          gutter={[16, 16]}
          justify="start"
          align="start"
          className="mb-3 pt-2 pb-2"
        >
          <Col span={6}>
            <h6 htmlFor="chooseAlgo">Choose Algorithm:</h6>
          </Col>
          <Col span={16}>
            <Radio.Group
              onChange={handleAlgorithmNameChange}
              value={algorithmName}
            >
              <Radio value="linearRegression">Linear Regression</Radio>
              <Radio value="naiveBayes">Naive Bayes</Radio>
              <Radio value="randomForest">Random Forest</Radio>
              <Radio value="customAlgorithm">
                <Input
                  placeholder="Enter custom algorithm name"
                  onChange={handleAlgorithmNameChange}
                  style={{ width: 200 }}
                />
              </Radio>
            </Radio.Group>
          </Col>
        </Row>
      )}

      {sourceType === "pipeline" && !(
        (algorithmName !== "custom" && !algorithmName) ||
        (algorithmName === "custom" && !algorithmName)
      ) && (
        <Row
          gutter={[16, 16]}
          justify="start"
          align="middle"
          className="mb-3"
          style={{ marginTop: 20, marginBottom: 20 }}
        >
          <Col span={3} offset={6}>
            <Button
              type="primary"
              onClick={handleGenerateCodeClick}
              size="medium"
              loading={generateCodeLoading}
              disabled={generatedCode}
            >
              Generate Code
            </Button>
          </Col>
          <Col span={1}></Col>
          <Col span={3} className="ml-1">
            <Button
              size="medium"
              type="primary"
              onClick={generateTextModal}
              disabled={!generatedCode}
            >
              View Generated Code
            </Button>
          </Col>
        </Row>
      )}

      <Modal
        title="Generated Code"
        visible={viewGeneratedCode}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={"70%"}
        footer={[
          <Button key="cancel" onClick={handleModalCancel}>
            Cancel
          </Button>,
        ]}
      >
        {CodeExtract(generatedCode)}
      </Modal>

      <Toast ref={toast} />
    </div>
  );
};

export default AIForDataScience;
