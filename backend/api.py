from pathlib import Path
import json

import pymupdf
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from database.database import initialize_database, save_run, get_runs, get_run

from backend.extraction.extractor import extract_rules

from synthetic_data.synthetic_data_generator import (
    generate_dataset,
    save_dataset,
)

from backend.policy_engine.rego_generator import (
    load_rules,
    generate_rego,
    save_rego,
)

from backend.policy_engine.eval import (
    load_dataset,
    validate_dataset_columns,
    evaluate_dataset,
    calculate_summary,
    save_results,
)


app = FastAPI()




# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://YOUR-VERCEL-DOMAIN.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

POLICIES_DIR = BASE_DIR / "policies"
EXTRACTED_TEXT_DIR = BASE_DIR / "extracted_text"

POLICIES_DIR.mkdir(exist_ok=True)
EXTRACTED_TEXT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# Fixed filenames
# --------------------------------------------------

CURRENT_POLICY_PATH = POLICIES_DIR / "current_policy.pdf"
CURRENT_TEXT_PATH = EXTRACTED_TEXT_DIR / "current_policy.json"
CURRENT_RULES_PATH = EXTRACTED_TEXT_DIR / "rules.json"

RESULTS_DIR = BASE_DIR / "evaluation_results"
RESULTS_PATH = RESULTS_DIR / "results.json"


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def root():

    print("Backend health check received")

    return {
        "message": "Policy-As-Code API is running"
    }


# --------------------------------------------------
# Evaluation Results
# --------------------------------------------------

@app.get("/evaluation-results")
def get_evaluation_results():

    print("Evaluation results request received")

    if not RESULTS_PATH.exists():

        return {
            "success": False,
            "message": "Evaluation results not found."
        }

    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        results = json.load(file)

    return {
        "success": True,
        "results": results
    }


# --------------------------------------------------
# Synthetic Data Generation
# --------------------------------------------------

@app.post("/generate-data")
def generate_synthetic_data():

    print()
    print("=" * 60)
    print("SYNTHETIC DATA GENERATION REQUEST RECEIVED")
    print("=" * 60)

    try:

        dataframe = generate_dataset()

        save_dataset(dataframe)

        return {
            "success": True,
            "message": "Synthetic dataset generated successfully.",
            "filename": "synthetic_dataset.xlsx",
            "records": len(dataframe),
            "columns": len(dataframe.columns),
        }

    except Exception as error:

        print()
        print("=" * 60)
        print("SYNTHETIC DATA GENERATION FAILED")
        print("=" * 60)

        print(f"Error: {error}")

        return {
            "success": False,
            "message": f"Synthetic data generation failed: {str(error)}",
        }


# --------------------------------------------------
# Delete Previous Policy
# --------------------------------------------------

def delete_previous_policy():

    print()
    print("Removing previous policy data...")

    files_to_delete = [
        CURRENT_POLICY_PATH,
        CURRENT_TEXT_PATH,
        CURRENT_RULES_PATH,
    ]

    for file_path in files_to_delete:

        if file_path.exists():

            file_path.unlink()

            print(f"Deleted: {file_path}")

        else:

            print(f"Not found: {file_path}")


# --------------------------------------------------
# PDF Upload + Complete Policy Processing
# --------------------------------------------------
@app.post("/upload-policy")
async def upload_policy(file: UploadFile = File(...)):

    print()
    print("=" * 60)
    print("POLICY UPLOAD REQUEST RECEIVED")
    print("=" * 60)

    print(f"Filename     : {file.filename}")
    print(f"Content type : {file.content_type}")

    # --------------------------------------------------
    # Validate PDF
    # --------------------------------------------------

    if file.content_type != "application/pdf":

        print("ERROR: Uploaded file is not a PDF.")

        return {
            "success": False,
            "message": "Only PDF files are supported."
        }

    print("File type validated: PDF")

    # --------------------------------------------------
    # Remove previous policy
    # --------------------------------------------------

    delete_previous_policy()

    # --------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------

    file_contents = await file.read()

    print(f"File size    : {len(file_contents)} bytes")

    # --------------------------------------------------
    # Save uploaded PDF
    # --------------------------------------------------

    with open(
        CURRENT_POLICY_PATH,
        "wb"
    ) as output_file:

        output_file.write(file_contents)

    print(f"PDF saved to : {CURRENT_POLICY_PATH}")

    # --------------------------------------------------
    # Open PDF
    # --------------------------------------------------

    print()
    print("Opening PDF with PyMuPDF...")

    document = pymupdf.open(CURRENT_POLICY_PATH)

    print(f"Page count   : {len(document)}")

    # --------------------------------------------------
    # Extract text page-by-page
    # --------------------------------------------------

    pages = []

    for page_number, page in enumerate(document, start=1):

        print()
        print(f"Extracting text from page {page_number}...")

        text = page.get_text("text").strip()

        pages.append({
            "page_number": page_number,
            "text": text
        })

        print(f"Characters extracted: {len(text)}")

    document.close()

    # --------------------------------------------------
    # Build extracted text result
    # --------------------------------------------------

    extracted_text_result = {
        "success": True,
        "filename": file.filename,
        "page_count": len(pages),
        "pages": pages
    }

    # --------------------------------------------------
    # Save extracted text
    # --------------------------------------------------

    with open(
        CURRENT_TEXT_PATH,
        "w",
        encoding="utf-8"
    ) as json_file:

        json.dump(
            extracted_text_result,
            json_file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(f"Extracted text saved to: {CURRENT_TEXT_PATH}")

    # --------------------------------------------------
    # Combine page text
    # --------------------------------------------------

    policy_text = "\n\n".join(
        page["text"]
        for page in pages
    )

    print()
    print(
        f"Combined policy text length: "
        f"{len(policy_text)} characters"
    )

    # --------------------------------------------------
    # Extract Policy Rules
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("STARTING POLICY RULE EXTRACTION")
    print("=" * 60)

    try:

        rules_result = extract_rules(policy_text)

    except Exception as error:

        print()
        print("=" * 60)
        print("RULE EXTRACTION FAILED")
        print("=" * 60)

        print(f"Error: {error}")

        if CURRENT_POLICY_PATH.exists():
            CURRENT_POLICY_PATH.unlink()

        if CURRENT_TEXT_PATH.exists():
            CURRENT_TEXT_PATH.unlink()

        return {
            "success": False,
            "message": f"Policy rule extraction failed: {str(error)}"
        }

    # --------------------------------------------------
    # Save Extracted Rules
    # --------------------------------------------------

    with open(
        CURRENT_RULES_PATH,
        "w",
        encoding="utf-8"
    ) as rules_file:

        json.dump(
            rules_result,
            rules_file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(f"Rules saved to: {CURRENT_RULES_PATH}")

    rule_count = len(
        rules_result.get("rules", [])
    )

    # --------------------------------------------------
    # Generate Rego Policy
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("GENERATING REGO POLICY")
    print("=" * 60)

    try:

        extracted_rules = load_rules()

        rego_policy = generate_rego(
            extracted_rules
        )

        save_rego(
            rego_policy
        )

        print("Rego policy generated successfully.")

    except Exception as error:

        print()
        print("=" * 60)
        print("REGO GENERATION FAILED")
        print("=" * 60)

        print(f"Error: {error}")

        return {
            "success": False,
            "message": f"Rego generation failed: {str(error)}",
            "rules": rules_result["rules"],
        }

    # --------------------------------------------------
    # Evaluate Synthetic Dataset
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("STARTING OPA DATASET EVALUATION")
    print("=" * 60)

    try:

        dataframe = load_dataset()

        validate_dataset_columns(
            dataframe
        )

        evaluation_results = evaluate_dataset(
            dataframe
        )

        summary = calculate_summary(
            evaluation_results
        )

        save_results(
            evaluation_results,
            summary
        )
        
        run_id = save_run(
            records=evaluation_results,
            dataset_name="synthetic_dataset.xlsx",
            policy_name=file.filename,
        )
                
        print()
        print("OPA evaluation completed successfully.")

    except Exception as error:

        print()
        print("=" * 60)
        print("OPA EVALUATION FAILED")
        print("=" * 60)

        print(f"Error: {error}")

        return {
            "success": False,
            "message": f"OPA evaluation failed: {str(error)}",
            "rules": rules_result["rules"],
        }

    # --------------------------------------------------
    # Final Logging
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("POLICY PROCESSING COMPLETE")
    print("=" * 60)

    print(f"Uploaded file : {file.filename}")
    print(f"Pages         : {len(pages)}")
    print(f"Rules         : {rule_count}")
    print(f"PASS          : {summary['pass']}")
    print(f"FLAG          : {summary['flag']}")
    print(f"BLOCK         : {summary['block']}")
    print(f"Pass rate     : {summary['pass_rate']}%")
    print(f"Policy PDF    : {CURRENT_POLICY_PATH}")
    print(f"Extracted text: {CURRENT_TEXT_PATH}")
    print(f"Rules JSON    : {CURRENT_RULES_PATH}")
    print(f"Results JSON  : {RESULTS_PATH}")

    print("=" * 60)
    print()

    # --------------------------------------------------
    # Return Response
    # --------------------------------------------------

    return {
        "success": True,
        "message": "Policy processed successfully.",
        "filename": file.filename,
        "page_count": len(pages),
        "rule_count": rule_count,
        "policy_file": str(CURRENT_POLICY_PATH),
        "extracted_text_file": str(CURRENT_TEXT_PATH),
        "rules_file": str(CURRENT_RULES_PATH),
        "evaluation": {
            "total_records": summary["total_records"],
            "pass": summary["pass"],
            "flag": summary["flag"],
            "block": summary["block"],
            "pass_rate": summary["pass_rate"],
        },
        "run_id": run_id,
        "rules": rules_result["rules"]
    }
    
    
# --------------------------------------------------
# Evaluation History
# --------------------------------------------------

@app.get("/api/runs")
def api_get_runs():
    return get_runs()

# --------------------------------------------------
# Get Evaluation Run
# --------------------------------------------------

@app.get("/api/runs/{run_id}")
def api_get_run(run_id: int):
    run = get_run(run_id)

    if run is None:
        return {
            "success": False,
            "message": "Evaluation run not found."
        }

    return run