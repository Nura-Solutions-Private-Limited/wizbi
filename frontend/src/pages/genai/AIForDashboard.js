import React, { useState, useEffect, useRef } from "react";
import {
  generateGenAIDashboards,
  generateGenAIDashboardsOtherQuestions,
} from "../../api/genai";
import { fetchPipelines } from "../../api/pipeLine";
import { Select, Radio, Button, Row, Col, Modal, QRCode } from "antd";
import { isArray } from "lodash";
import TextArea from "antd/es/input/TextArea";
import { CodeExtract } from "./CodeExtract";
import { GenAIDashboardCodeExtract } from "./GenAIDashboardCodeExtract";
import WizBIDropDown from "../../core/WizBIDropDown/WizBIDropDown";
import { Dropdown } from "primereact/dropdown";
import { Toast } from "primereact/toast";

const { Option } = Select;

const AIForDashboard = () => {
  const toast = useRef(null);
  const [pipelineOptions, setPipelineOptions] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState("");
  const [radioEnabled, setRadioEnabled] = useState(false);

  const [customQuestion, setCustomQuestion] = useState("");
  const [customQuestionAnswer, setCustomQuestionAnswer] = useState("");
  const [customQuestionError, setCustomQuestionError] = useState("");
  const [loading, setLoading] = useState(true);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [questions, setQuestions] = useState({});

  const [qType, setQType] = useState("fact");

  const [showCode, setShowCode] = useState(false);

  const [showViewCodeButton, setShowViewCodeButton] = useState(false);

  const showModal = () => {
    setShowCode(true);
  };

  const closeModal = () => {
    setShowCode(false);
  };

  const pipelineQuery = {
    pipeline_status: "active",
    pipeline_type: "ETL",
  };

  const fetchPipelineOptions = async () => {
    fetchPipelines(pipelineQuery, (data) => {
      isArray(data) && setPipelineOptions(data);
    });
  };

  useEffect(() => {
    fetchPipelineOptions();
  }, []);

  useEffect(() => {
    if (selectedPipeline) {
      setRadioEnabled(true);
    } else {
      setRadioEnabled(false);
    }
  }, [selectedPipeline]);

  const handlePipelineChange = (value) => {
    setSelectedPipeline(value);
    setCustomQuestion("");
    setCustomQuestionError("");
    setQType(null);
    setQuestions([]);
    setCustomQuestionAnswer("");
  };

  const handleRadioChange = (e) => {
    setQType(e.target.value);
    setCustomQuestion("");
    setCustomQuestionError("");
  };

  const handleCustomQuestionChange = (e) => {
    const value = e.target.value;
    setCustomQuestion(value);
    // setGeneratedCode("");
    if (value.length < 20) {
      setCustomQuestionError("Please enter at least 20 characters");
    } else {
      setCustomQuestionError("");
    }
  };

  const handleGenerateClick = () => {
    setLoading(true);
    fetchQuestions({ pipeline_id: selectedPipeline.id });
  };

  const fetchQuestions = async (questionInfo) => {
    setGenerateLoading(true);
    if (qType === "fact") {
      generateGenAIDashboards(
        {
          ...questionInfo,
          prompt: "",
        },
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
              setLoading(false);
              setGenerateLoading(false);
              setQuestions(resp || {});
            }
          }
        }
      );
    } else {
      generateGenAIDashboards(
        {
          ...questionInfo,
          prompt: customQuestion,
        },
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
              setCustomQuestionAnswer(resp?.answer || "");
              setLoading(false);
              setGenerateLoading(false);
            }
          }
        }
      );
    }
  };

  useEffect(() => {
    const flag =
      (qType === "fact" && Object.keys(questions).length) ||
      (qType === "other" && customQuestionAnswer.length);
    setShowViewCodeButton(flag);
  }, [qType, questions, customQuestionAnswer]);

  return (
    <div className="mt-5">
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
          {/* <Select
            id="pipeline"
            onChange={handlePipelineChange}
            placeholder="Select Pipeline"
            style={{ width: "100%" }}
          >
            {pipelineOptions?.length &&
              pipelineOptions.map((pipeline) => (
                <Option key={pipeline.id} value={pipeline.id}>
                  {pipeline.name}
                </Option>
              ))}
          </Select> */}
        </Col>
      </Row>
      {radioEnabled && (
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
                Generate 10 SQL queries for the selected pipeline
              </Radio>
              <Radio value="other">
                Write a description for a metric to create SQL query for the
                selected pipeline
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
          style={{ marginTop: 10, marginBottom: 10 }}
        >
          <Col span={6} />
          <Col span={12}>
            <TextArea
              placeholder="Enter your custom question"
              value={customQuestion}
              onChange={handleCustomQuestionChange}
              size="large"
            />
            {customQuestionError && (
              <span style={{ color: "red" }}>{customQuestionError}</span>
            )}
          </Col>
        </Row>
      )}

      {qType !== null && radioEnabled && (
        <Row gutter={[16, 16]} justify="start" align="start" className="mb-3">
          <Col span={6} />
          <Col span={4}>
            <Button
              type="primary"
              style={{ marginLeft: 10 }}
              onClick={handleGenerateClick}
              disabled={qType === "other" && customQuestion.length < 20}
              loading={generateLoading}
            >
              Generate SQL Queries
            </Button>
          </Col>

          {!!showViewCodeButton && (
            <>
              <Col span={1} />
              <Col span={4} className="ml-2">
                <Button size="medium" type="primary" onClick={showModal}>
                  View Generated Code
                </Button>
              </Col>
            </>
          )}
        </Row>
      )}

      <Modal
        title="Generated Code"
        visible={showCode}
        onOk={closeModal}
        onCancel={closeModal}
        width={"70%"}
        footer={[
          <Button key="cancel" onClick={closeModal}>
            Cancel
          </Button>,
        ]}
      >
        {qType === "fact"
          ? GenAIDashboardCodeExtract(JSON.parse(questions.answer ?? "[]"))
          : CodeExtract(customQuestionAnswer)}
      </Modal>
      <Toast ref={toast} />
    </div>
  );
};

export default AIForDashboard;
