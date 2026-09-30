import { useEffect, useMemo, useState } from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import "./App.css";

ChartJS.register(ArcElement, Tooltip, Legend);

const API_BASE = "http://127.0.0.1:8001";


const REMEDIATION_BY_COLUMN = {
  customer_name: "Remove or mask the customer's full name.",
  email: "Remove or mask the personal email address.",
  phone: "Remove or mask the phone number.",
  address: "Remove or generalize the postal/home address.",
  dob: "Remove or generalize the date of birth.",
  gender: "Remove or generalize gender information where required.",
  passport_number: "Remove the passport number completely.",
  ni_number: "Remove the National Insurance number completely.",
  credit_card_number: "Remove or mask the payment card number.",
  bank_account: "Remove or mask the bank account number.",
  medical_condition: "Remove the medical information.",
  ethnicity: "Remove the ethnicity information.",
  religion: "Remove the religion or belief information.",
  political_view: "Remove the political opinion information.",
  employee_id: "Remove or mask the employee identifier.",
  department: "Remove or generalize the department when it contributes to identification.",
  job_role: "Remove or generalize the job role when it contributes to identification.",
  customer_id: "Remove or mask the customer identifier.",
  ip_address: "Remove or mask the IP address.",
};

const RULE_COLUMNS = {
  "PII-01": ["customer_name"],
  "PII-02": ["email"],
  "PII-03": ["phone"],
  "PII-04": ["address"],
  "PII-05": ["ni_number"],
  "PII-06": ["passport_number"],
  "PII-07": [],
  "PII-08": ["bank_account", "credit_card_number"],
  "PII-09": ["ip_address"],
  "SPII-01": ["medical_condition"],
  "SPII-02": ["ethnicity"],
  "SPII-03": ["religion"],
  "SPII-04": ["political_view"],
  "SPII-05": [],
  "SPII-06": [],
  "CPII-01": ["customer_name", "dob"],
  "CPII-02": ["customer_name", "address"],
  "CPII-03": ["customer_name", "phone"],
  "CPII-04": ["customer_name", "email"],
  "CPII-05": ["dob", "gender"],
  "CPII-06": ["employee_id", "department", "job_role"],
  "CPII-07": ["customer_id"],
  "CPII-08": [],
};

const normalizeRuleId = (ruleId, category = "") => {
  const value = String(ruleId || "").trim().toUpperCase();
  const categoryValue = String(category || "").trim().toUpperCase();

  if (!value) return "";

  if (
    categoryValue &&
    value.startsWith(`${categoryValue}-${categoryValue}-`)
  ) {
    return value.slice(categoryValue.length + 1);
  }

  return value;
};

function App() {
  // ==========================================
  // PAGE
  // ==========================================

  const [page, setPage] = useState("upload");

  // ==========================================
  // UPLOAD PAGE
  // ==========================================

  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // ==========================================
  // DASHBOARD
  // ==========================================

  const [dashboardData, setDashboardData] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState("");

  const [currentRun, setCurrentRun] = useState(null);
  const [runs, setRuns] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [selectedId, setSelectedId] = useState(null);

  const [showDefinitions, setShowDefinitions] = useState(false);

  // ==========================================
  // FILE SELECTION
  // ==========================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      alert("Please select a PDF file.");
      return;
    }

    setFile(selectedFile);
  };

  // ==========================================
  // UPLOAD POLICY
  // ==========================================

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setIsUploading(true);

      const response = await fetch(
        `${API_BASE}/upload-policy`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed.");
      }

      const result = await response.json();

      console.log("Policy upload response:", result);

      alert(
        `Policy uploaded successfully: ${result.filename}`
      );

      setPage("dashboard");
      await loadDashboard();
    } catch (error) {
      console.error("Upload error:", error);

      alert(
        error.message || "Failed to upload the PDF."
      );
    } finally {
      setIsUploading(false);
    }
  };

  // ==========================================
  // GENERATE SYNTHETIC DATA
  // ==========================================

  const handleGenerateData = async () => {
    try {
      setIsGenerating(true);

      const response = await fetch(
        `${API_BASE}/generate-data`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(
          "Synthetic data generation failed."
        );
      }

      const result = await response.json();

      console.log(
        "Synthetic data response:",
        result
      );

      if (!result.success) {
        throw new Error(
          result.message ||
            "Synthetic data generation failed."
        );
      }

      alert(
        `Synthetic dataset generated successfully: ${result.records} records`
      );
    } catch (error) {
      console.error(
        "Synthetic data generation error:",
        error
      );

      alert(
        error.message ||
          "Failed to generate synthetic data."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // ==========================================
  // LOAD DASHBOARD
  // ==========================================

  const loadRun = async (runId) => {
    try {
      setDashboardLoading(true);
      setDashboardError("");

      const response = await fetch(
        `${API_BASE}/api/runs/${runId}`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load the selected evaluation run."
        );
      }

      const run = await response.json();

      if (run.success === false) {
        throw new Error(
          run.message ||
            "Failed to load the selected evaluation run."
        );
      }

      const runSummary = {
        total_records: run.total_records || 0,
        pass: run.pass_count || 0,
        flag: run.flag_count || 0,
        block: run.block_count || 0,
        pass_rate: run.total_records
          ? ((run.pass_count / run.total_records) * 100)
          : 0,
      };

      setCurrentRun(run);
      setDashboardData({
        summary: runSummary,
        records: run.records || [],
      });

      const loadedRecords = run.records || [];

      setSelectedId(
        loadedRecords.length > 0
          ? loadedRecords[0].record_id
          : null
      );

      setSearch("");
      setFilter("All");
      setShowHistory(false);
    } catch (error) {
      console.error(
        "Run loading error:",
        error
      );

      setDashboardError(error.message);
    } finally {
      setDashboardLoading(false);
    }
  };

  const loadDashboard = async () => {
    try {
      setDashboardLoading(true);
      setDashboardError("");

      const response = await fetch(
        `${API_BASE}/api/runs`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load evaluation history."
        );
      }

      const runList = await response.json();

      setRuns(runList);

      if (runList.length === 0) {
        throw new Error(
          "No evaluation runs found in the database."
        );
      }

      await loadRun(runList[0].id);
    } catch (error) {
      console.error(
        "Dashboard error:",
        error
      );

      setDashboardError(error.message);
      setDashboardLoading(false);
    }
  };

  const openHistory = async () => {
    setShowHistory(true);
    setHistoryLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/api/runs`
      );

      if (!response.ok) {
        throw new Error(
          "Could not load evaluation history."
        );
      }

      const runList = await response.json();
      setRuns(runList);
    } catch (error) {
      console.error(
        "History loading error:",
        error
      );

      setDashboardError(error.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  // ==========================================
  // OPEN DASHBOARD
  // ==========================================

  const handleOpenDashboard = async () => {
    setPage("dashboard");
    await loadDashboard();
  };

  // ==========================================
  // BACK TO UPLOAD
  // ==========================================

  const handleBackToUpload = () => {
    setPage("upload");
  };

  // ==========================================
  // DASHBOARD DATA
  // ==========================================

  const records = dashboardData?.records || [];

  const summary = dashboardData?.summary || {
    total_records: 0,
    pass: 0,
    flag: 0,
    block: 0,
    pass_rate: 0,
  };

  const total = summary.total_records || 0;
  const passed = summary.pass || 0;
  const flagged = summary.flag || 0;
  const blocked = summary.block || 0;

  const passRate = Number(
    summary.pass_rate || 0
  ).toFixed(1);

  // ==========================================
  // SEARCH + FILTER
  // ==========================================

  const filteredData = useMemo(() => {
    let filtered = [...records];

    if (filter !== "All") {
      filtered = filtered.filter(
        (record) =>
          record.outcome === filter
      );
    }

    if (search.trim()) {
      const query =
        search.toLowerCase().trim();

      filtered = filtered.filter(
        (record) => {
          const recordId = String(
            record.record_id || ""
          ).toLowerCase();

          const outcome = String(
            record.outcome || ""
          ).toLowerCase();

          const ruleIds =
            Array.isArray(
              record.triggered_rule_ids
            )
              ? record.triggered_rule_ids
                  .join(" ")
                  .toLowerCase()
              : "";

          const descriptions =
            Array.isArray(
              record.triggered_rules
            )
              ? record.triggered_rules
                  .map(
                    (rule) =>
                      rule.description || ""
                  )
                  .join(" ")
                  .toLowerCase()
              : "";

          return (
            recordId.includes(query) ||
            outcome.includes(query) ||
            ruleIds.includes(query) ||
            descriptions.includes(query)
          );
        }
      );
    }

    return filtered;
  }, [records, filter, search]);

  // ==========================================
  // SELECTED RECORD
  // ==========================================

  const selectedRecord = useMemo(() => {
    return records.find(
      (record) =>
        String(record.record_id) ===
        String(selectedId)
    );
  }, [records, selectedId]);

  // ==========================================
  // CHART
  // ==========================================

  const pieData = {
    labels: [
      "PASS",
      "FLAG",
      "BLOCK",
    ],
    datasets: [
      {
        data: [
          passed,
          flagged,
          blocked,
        ],
        backgroundColor: [
          "#22c55e",
          "#f59e0b",
          "#ef4444",
        ],
        borderWidth: 0,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: "bottom",

        labels: {
          padding: 20,
        },
      },

      tooltip: {
        callbacks: {
          label: function (context) {
            const chartTotal =
              context.dataset.data.reduce(
                (sum, value) =>
                  sum + value,
                0
              );

            const percentage =
              chartTotal
                ? (
                    (context.raw /
                      chartTotal) *
                    100
                  ).toFixed(1)
                : 0;

            return `${context.label}: ${percentage}%`;
          },
        },
      },
    },
  };

  // ==========================================
  // HELPERS
  // ==========================================

  const getOutcomeClass = (
    outcome
  ) => {
    if (outcome === "PASS") {
      return "pass";
    }

    if (outcome === "FLAG") {
      return "flag";
    }

    return "block";
  };

  const getIcon = (outcome) => {
    if (outcome === "PASS") {
      return "✓";
    }

    if (outcome === "FLAG") {
      return "⚠";
    }

    return "✕";
  };

  const formatFieldName = (
    field
  ) => {
    return field
      .replaceAll("_", " ")
      .replace(
        /\b\w/g,
        (letter) =>
          letter.toUpperCase()
      );
  };

  const getRecordNumber = (
    recordId
  ) => {
    return String(recordId).padStart(
      4,
      "0"
    );
  };

  // ==========================================
  // PAGE 1 — UPLOAD
  // ==========================================

  if (page === "upload") {
    return (
      <div className="upload-page">

        <div className="upload-card">

          <h1>
            Policy as Code
          </h1>

          <p className="upload-subtitle">
            Upload your policy document
            to begin
          </p>


          {/* PDF DROP AREA */}

          <label className="drop-zone">

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={
                handleFileChange
              }
            />

            <div className="upload-icon">
              ↑
            </div>

            <h2>
              {file
                ? file.name
                : "Upload Policy PDF"}
            </h2>

            <p>
              {file
                ? "PDF selected"
                : "Click here to select your policy document"}
            </p>

          </label>


          {/* SELECTED FILE */}

          {file && (
            <div className="file-info">

              <span>
                Selected file
              </span>

              <strong>
                {file.name}
              </strong>

            </div>
          )}


          {/* UPLOAD */}

          <button
            className="upload-button"
            onClick={
              handleUpload
            }
            disabled={isUploading}
          >

            {isUploading
              ? "Uploading..."
              : "Upload Policy"}

          </button>


          {/* GENERATE DATA */}

          <button
            className="generate-button"
            onClick={
              handleGenerateData
            }
            disabled={isGenerating}
          >

            {isGenerating
              ? "Generating..."
              : "Generate Synthetic Data"}

          </button>


          {/* DASHBOARD */}

          <button
            className="dashboard-button"
            onClick={
              handleOpenDashboard
            }
          >
            View Evaluation Dashboard
          </button>


          <p className="supported">
            Supported format: PDF
          </p>

        </div>

      </div>
    );
  }

  // ==========================================
  // DASHBOARD LOADING
  // ==========================================

  if (dashboardLoading) {
    return (
      <div className="loading-page">

        <div className="loading-card">

          <div className="loading-spinner"></div>

          <h2>
            Loading Evaluation Dashboard
          </h2>

          <p>
            Fetching the latest policy
            evaluation results...
          </p>

        </div>

      </div>
    );
  }

  // ==========================================
  // DASHBOARD ERROR
  // ==========================================

  if (dashboardError) {
    return (
      <div className="error-page">

        <div className="error-card">

          <h2>
            Unable to load dashboard
          </h2>

          <p>
            {dashboardError}
          </p>

          <p>
            Make sure the FastAPI
            backend is running on
            <b>
              {" "}
              http://127.0.0.1:8001
            </b>.
          </p>

          <div className="error-buttons">

            <button
              className="retry-button"
              onClick={
                loadDashboard
              }
            >
              Retry
            </button>

            <button
              className="back-upload-button"
              onClick={
                handleBackToUpload
              }
            >
              Back to Upload
            </button>

          </div>

        </div>

      </div>
    );
  }

  // ==========================================
  // DASHBOARD
  // ==========================================

  return (
    <div className="app">

      {/* ======================================
          HEADER
      ====================================== */}

      <header className="header">

        <div>

          <div className="breadcrumb">
            Evaluations / Run #{currentRun.run_number}
          </div>

          <h1>
            Policy Evaluation Results
          </h1>

          <p>
            {total} records evaluated
          </p>

        </div>


        <div className="header-actions">

          <button
            type="button"
            className="header-button"
            onClick={() =>
              setShowDefinitions(true)
            }
          >
            DEFINITIONS
          </button>

          <button
            type="button"
            className="header-button"
            onClick={openHistory}
          >
            EVALUATION HISTORY
          </button>

          <button
            type="button"
            className="header-button"
            onClick={
              loadDashboard
            }
          >
            REFRESH
          </button>


          <button
            type="button"
            className="header-button"
            onClick={
              handleBackToUpload
            }
          >
            UPLOAD PAGE
          </button>

          <div className="run-info">

            <span>
              POLICY
            </span>

            <strong>
              {currentRun?.policy_name || "-"}
            </strong>

          </div>

          <div className="run-info">

            <span>
              RUN DATE & TIME
            </span>

            <strong>
              {currentRun
                ? `${new Date(
                    currentRun.run_date
                  ).toLocaleDateString()} ${new Date(
                    currentRun.run_date
                  ).toLocaleTimeString()}`
                : "-"}
            </strong>

          </div>

        </div>

      </header>


      {/* ======================================
          EVALUATION HISTORY
      ====================================== */}

      {showHistory && (
        <div
          className="modal-overlay"
          onClick={() => setShowHistory(false)}
        >
          <div
            className="definitions-modal"
            style={{
              width: "min(760px, 92vw)",
              maxHeight: "90vh",
              overflowY: "auto",
            }}
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <div className="modal-label">
                  DATABASE
                </div>

                <h2>
                  Evaluation History
                </h2>
              </div>

              <button
                type="button"
                className="close-button"
                onClick={() =>
                  setShowHistory(false)
                }
                aria-label="Close evaluation history"
              >
                ×
              </button>
            </div>

            {historyLoading ? (
              <p>
                Loading evaluation history...
              </p>
            ) : runs.length === 0 ? (
              <p>
                No evaluation runs found.
              </p>
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                }}
              >
                {runs.map((run) => (
                  <button
                    key={run.id}
                    type="button"
                    onClick={() =>
                      loadRun(run.id)
                    }
                    style={{
                      width: "100%",
                      textAlign: "left",
                      border: "1px solid #e1e7ef",
                      background:
                        currentRun &&
                        currentRun.id === run.id
                          ? "#f5f8fc"
                          : "#ffffff",
                      borderRadius: "10px",
                      padding: "16px",
                      cursor: "pointer",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent:
                          "space-between",
                        alignItems: "center",
                        gap: "16px",
                      }}
                    >
                      <div>
                        <strong
                          style={{
                            fontSize: "16px",
                          }}
                        >
                          Run #{run.run_number}
                        </strong>

                        <div
                          style={{
                            marginTop: "5px",
                            fontSize: "13px",
                            color: "#718096",
                          }}
                        >
                          {new Date(
                            run.run_date
                          ).toLocaleDateString()}{" "}
                          {new Date(
                            run.run_date
                          ).toLocaleTimeString()}
                        </div>

                        <div
                          style={{
                            marginTop: "4px",
                            fontSize: "13px",
                            color: "#718096",
                          }}
                        >
                          {run.policy_name ||
                            "Unknown policy"}{" "}
                          ·{" "}
                          {run.dataset_name} ·{" "}
                          {run.total_records} records
                        </div>
                      </div>

                      <div
                        style={{
                          display: "flex",
                          gap: "12px",
                          fontSize: "13px",
                          whiteSpace: "nowrap",
                        }}
                      >
                        <span>
                          ✓ {run.pass_count}
                        </span>

                        <span>
                          ⚠ {run.flag_count}
                        </span>

                        <span>
                          ✕ {run.block_count}
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================
          DEFINITIONS MODAL
      ====================================== */}

      {showDefinitions && (
        <div
          className="modal-overlay"
          onClick={() =>
            setShowDefinitions(false)
          }
        >

          <div
            className="definitions-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <div className="modal-header">

              <div>

                <div className="modal-label">
                  POLICY REFERENCE
                </div>

                <h2>
                  Data Classification Definitions
                </h2>

              </div>


              <button
                type="button"
                className="close-button"
                onClick={() =>
                  setShowDefinitions(false)
                }
              >
                ×
              </button>

            </div>


            <div className="definitions-list">

              <div className="definition-item">

                <strong>
                  PII — Personally
                  Identifiable Information
                </strong>

                <p>
                  Information that
                  directly identifies a
                  person, such as their
                  name, email, phone
                  number, or address.
                </p>

              </div>


              <div className="definition-item">

                <strong>
                  SPII — Sensitive
                  Personally Identifiable
                  Information
                </strong>

                <p>
                  Sensitive personal
                  information such as
                  health, ethnicity,
                  religion, political
                  opinion, or other
                  sensitive attributes.
                </p>

              </div>


              <div className="definition-item">

                <strong>
                  CPII — Combination
                  Personally Identifiable
                  Information
                </strong>

                <p>
                  Information that can
                  identify a person when
                  multiple attributes are
                  combined, such as name
                  and date of birth or
                  name and address.
                </p>

              </div>

            </div>

          </div>

        </div>
      )}


      {/* ======================================
          OVERVIEW
      ====================================== */}

      <section className="overview">

        <div className="summary-section">

          <div className="summary-grid">

            <div className="summary-card pass-card">

              <span className="card-label">
                ✓ PASS
              </span>

              <strong>
                {passed}
              </strong>

              <small>
                {total
                  ? (
                      (passed /
                        total) *
                      100
                    ).toFixed(1)
                  : 0}
                %
              </small>

            </div>


            <div className="summary-card flag-card">

              <span className="card-label">
                ⚠ FLAG
              </span>

              <strong>
                {flagged}
              </strong>

              <small>
                {total
                  ? (
                      (flagged /
                        total) *
                      100
                    ).toFixed(1)
                  : 0}
                %
              </small>

            </div>


            <div className="summary-card block-card">

              <span className="card-label">
                ✕ BLOCK
              </span>

              <strong>
                {blocked}
              </strong>

              <small>
                {total
                  ? (
                      (blocked /
                        total) *
                      100
                    ).toFixed(1)
                  : 0}
                %
              </small>

            </div>


            <div className="summary-card rate-card">

              <span className="card-label">
                ◔ PASS RATE
              </span>

              <strong>
                {passRate}%
              </strong>

              <small>
                {passed}/{total} passed
              </small>

            </div>

          </div>

        </div>


        <div className="chart-section">

          <h3>
            Outcome Distribution
          </h3>

          <div className="pie-container">

            <Pie
              data={pieData}
              options={pieOptions}
            />

          </div>

        </div>

      </section>


      {/* ======================================
          RECORDS + ANALYSIS
      ====================================== */}

      <section className="main-content">

        {/* RECORDS */}

        <div className="records-panel">

          <div className="panel-header">

            <div>

              <h2>
                Records
              </h2>

              <span>
                {filteredData.length} records shown
              </span>

            </div>

          </div>


          <input
            className="search"
            placeholder="Search records..."
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
          />


          <div className="filters">

            {[
              "All",
              "PASS",
              "FLAG",
              "BLOCK",
            ].map((name) => (

              <button
                key={name}
                type="button"
                className={`filter-button ${
                  filter === name
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setFilter(name)
                }
              >

                {name === "PASS" &&
                  "✓ "}

                {name === "FLAG" &&
                  "⚠ "}

                {name === "BLOCK" &&
                  "✕ "}

                {name}

              </button>

            ))}

          </div>


          <div className="record-list">

            {filteredData.length === 0 ? (

              <div className="no-records">
                No records match your
                search.
              </div>

            ) : (

              filteredData.map(
                (record) => {

                  const outcome =
                    record.outcome;

                  const rules =
                    Array.isArray(
                      record.triggered_rule_ids
                    )
                      ? record.triggered_rule_ids.join(
                          ", "
                        )
                      : "No violations";

                  return (

                    <button
                      key={
                        record.record_id
                      }
                      type="button"
                      className={`record-item ${
                        String(
                          selectedId
                        ) ===
                        String(
                          record.record_id
                        )
                          ? "selected"
                          : ""
                      }`}
                      onClick={() =>
                        setSelectedId(
                          record.record_id
                        )
                      }
                    >

                      <span
                        className={`status-dot ${getOutcomeClass(
                          outcome
                        )}`}
                      >
                        {getIcon(
                          outcome
                        )}
                      </span>


                      <div className="record-info">

                        <strong>
                          REC-
                          {getRecordNumber(
                            record.record_id
                          )}
                        </strong>

                        <span>
                          {rules}
                        </span>

                      </div>


                      <span
                        className={`outcome-text ${getOutcomeClass(
                          outcome
                        )}`}
                      >
                        {outcome}
                      </span>

                    </button>

                  );
                }
              )

            )}

          </div>

        </div>


        {/* ANALYSIS */}

        <div className="analysis-panel">

          {selectedRecord ? (

            <>

              <div className="analysis-header">

                <div>

                  <span className="analysis-label">
                    RECORD POLICY ANALYSIS
                  </span>

                  <h2>
                    REC-
                    {getRecordNumber(
                      selectedRecord.record_id
                    )}
                  </h2>

                </div>


                <span
                  className={`outcome-badge ${getOutcomeClass(
                    selectedRecord.outcome
                  )}`}
                >

                  {getIcon(
                    selectedRecord.outcome
                  )}{" "}

                  {selectedRecord.outcome}

                </span>

              </div>


              <div className="analysis-content">

                {/* POLICY RULES */}

                <section className="analysis-section">

                  <h3>
                    Policy Rules
                  </h3>


                  {selectedRecord.triggered_rules &&
                  selectedRecord
                    .triggered_rules
                    .length > 0 ? (

                    <div className="rule-list">

                      {selectedRecord.triggered_rules.map(
                        (rule, index) => (

                          <div
                            className="rule-item"
                            key={`${rule.rule_id}-${index}`}
                          >

                            <div className="rule-top">

                              <strong>
                                {normalizeRuleId(rule.rule_id, rule.category)}
                              </strong>

                              <span
                                className={`rule-outcome ${getOutcomeClass(
                                  rule.outcome
                                )}`}
                              >
                                {rule.outcome}
                              </span>

                            </div>

                            <span>
                              {rule.description}
                            </span>

                            <div className="rule-category">
                              {rule.category}
                            </div>

                          </div>

                        )
                      )}

                    </div>

                  ) : (

                    <div className="no-violations">
                      ✓ No policy violations
                      detected
                    </div>

                  )}

                </section>


                {/* EXPLANATION */}

                <section className="analysis-section">

                  <h3>
                    Explanation
                  </h3>


                  {selectedRecord.triggered_rules &&
                  selectedRecord
                    .triggered_rules
                    .length > 0 ? (

                    <div className="line-list">

                      {selectedRecord.triggered_rules.map(
                        (rule, index) => (

                          <div
                            className="line-item"
                            key={index}
                          >

                            <span>
                              •
                            </span>

                            <div>

                              <strong>
                                  {normalizeRuleId(rule.rule_id, rule.category)}:
                              </strong>

                              {rule.explanation ||
                                "Policy condition detected."}

                            </div>

                          </div>

                        )
                      )}

                    </div>

                  ) : (

                    <div className="line-item">

                      <span>
                        •
                      </span>

                      No PII or sensitive
                      information detected.

                    </div>

                  )}

                </section>


                {/* INPUT DATA */}

                <section className="analysis-section">

                  <h3>
                    Input Data
                  </h3>


                  <div className="input-grid">

                    {selectedRecord.input &&
                      Object.entries(
                        selectedRecord.input
                      ).map(
                        ([field, value]) => {

                          if (
                            value ===
                              undefined ||
                            value ===
                              null ||
                            String(
                              value
                            ).trim() ===
                              ""
                          ) {
                            return null;
                          }

                          return (

                            <div
                              className="input-item"
                              key={field}
                            >

                              <span>
                                {formatFieldName(
                                  field
                                )}
                              </span>

                              <strong>
                                {String(
                                  value
                                )}
                              </strong>

                            </div>

                          );
                        }
                      )}

                  </div>

                </section>


                {/* REMEDIATION */}

                <section className="analysis-section">

                  <h3>
                    Suggested Remediation
                  </h3>

                  {selectedRecord.triggered_rules &&
                  selectedRecord.triggered_rules.length > 0 ? (

                    (() => {
                      const remediationItems = [];
                      const seenColumns = new Set();

                      selectedRecord.triggered_rules.forEach((rule) => {
                        const ruleId = normalizeRuleId(
                          rule.rule_id,
                          rule.category
                        );
                        const columns = RULE_COLUMNS[ruleId] || [];

                        columns.forEach((column) => {
                          const value = selectedRecord.input?.[column];

                          if (
                            value === undefined ||
                            value === null ||
                            String(value).trim() === "" ||
                            !REMEDIATION_BY_COLUMN[column] ||
                            seenColumns.has(column)
                          ) {
                            return;
                          }

                          seenColumns.add(column);
                          remediationItems.push({
                            column,
                            text: REMEDIATION_BY_COLUMN[column],
                          });
                        });
                      });

                      if (remediationItems.length === 0) {
                        return (
                          <div className="remediation-item">
                            <span>→</span>
                            <span>No column-specific remediation is required.</span>
                          </div>
                        );
                      }

                      return (
                        <div className="remediation-list">
                          {remediationItems.map((item) => (
                            <div
                              className="remediation-item"
                              key={item.column}
                            >
                              <span>→</span>
                              <span>
                                <strong>
                                  {formatFieldName(item.column)}:
                                </strong>{" "}
                                {item.text}
                              </span>
                            </div>
                          ))}
                        </div>
                      );
                    })()

                  ) : (

                    <div className="remediation-item">
                      <span>→</span>
                      <span>No remediation required.</span>
                    </div>

                  )}

                   </section>

              </div>

            </>

          ) : (

            <div className="empty-analysis">
              Select a record to view
              analysis
            </div>

          )}

        </div>

      </section>

    </div>
  );
}

export default App;