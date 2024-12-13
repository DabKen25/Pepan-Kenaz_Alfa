import os
import re
import zipfile
import json
import streamlit as st
import tempfile
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import random  # Untuk menghasilkan prediksi True/False secara acak


def analyze_kotlin_files(directory):
    file_count = 0
    class_count = 0
    function_count = 0
    property_count = 0
    packages = set()

    files = []
    classes = []
    functions = []
    properties = []
    package_dict = {}

    for root, dirs, files_in_dir in os.walk(directory):
        for file in files_in_dir:
            if file.endswith(".kt"):
                file_count += 1
                file_path = os.path.join(root, file)
                files.append(file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    found_classes = re.findall(r"class\s+\w+", content)
                    found_functions = re.findall(r"fun\s+\w+", content)
                    found_properties = re.findall(r"val\s+\w+|var\s+\w+", content)

                    classes.extend(found_classes)
                    functions.extend(found_functions)
                    properties.extend(found_properties)

                    class_count += len(found_classes)
                    function_count += len(found_functions)
                    property_count += len(found_properties)

                    package_name = re.search(r"package\s+([\w\.]+)", content)
                    if package_name:
                        package = package_name.group(1)
                    else:
                        package = "default"

                    packages.add(package)

                    if package not in package_dict:
                        package_dict[package] = {
                            "files": [],
                            "classes": [],
                            "functions": [],
                            "properties": [],
                        }

                    package_dict[package]["files"].append(file)
                    package_dict[package]["classes"].extend(found_classes)
                    package_dict[package]["functions"].extend(found_functions)
                    package_dict[package]["properties"].extend(found_properties)

    return {
        "number of files": file_count,
        "number of classes": class_count,
        "number of functions": function_count,
        "number of properties": property_count,
        "number of packages": len(packages),
        "Packages": package_dict,
    }


def extract_zip(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def generate_prediction_report(results):
    report = []
    extraction_date = datetime.now().strftime("%Y-%m-%d")

    for package, details in results["Packages"].items():
        for file in details["files"]:
            detection_result = random.choice([True, False])  # Hasil prediksi acak
            report.append(
                {
                    "Extraction Date": extraction_date,
                    "Package": package,
                    "File": file,
                    "Detection Result": detection_result,
                }
            )
    return pd.DataFrame(report)


def show_prediction_page():
    st.title("Prediction Report")

    uploaded_file = st.file_uploader(
        "Upload a ZIP file containing Kotlin files", type="zip"
    )

    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, uploaded_file.name)

            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            extract_zip(zip_path, temp_dir)
            results = analyze_kotlin_files(temp_dir)

            # Generate the prediction report
            prediction_df = generate_prediction_report(results)

            # Display the prediction table
            st.subheader("Prediction Results")
            st.dataframe(prediction_df)

            # Add a download button for the prediction results
            st.download_button(
                label="Download Prediction Report as CSV",
                data=prediction_df.to_csv(index=False),
                file_name="kotlin_prediction_report.csv",
                mime="text/csv",
            )


def style_sidebar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Summary Report",
                "Detailed Report",
                "Complexity Report",
                "Download Report",
                "Prediction",  # Tambahkan menu "Prediction"
            ],
            icons=["graph-up", "list-task", "bar-chart", "download", "check2-all"],
            menu_icon="menu-button-wide",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "5px", "background-color": "#f0f0f0"},
                "icon": {"color": "#FF4B4B", "font-size": "25px"},
                "nav-link": {
                    "font-size": "18px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#FF4B4B"},
            },
        )
    return selected


def main():
    page = style_sidebar()

    if page == "Summary Report":
        show_summary_report_page()
    elif page == "Detailed Report":
        show_detailed_report_page()
    elif page == "Complexity Report":
        show_complexity_report_page()
    elif page == "Download Report":
        show_download_report_page()
    elif page == "Prediction":  # Tambahkan kondisi untuk menu "Prediction"
        show_prediction_page()


if __name__ == "__main__":
    main()
