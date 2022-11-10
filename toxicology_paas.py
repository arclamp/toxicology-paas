import json
import numpy as np
import pandas as pd
import streamlit as st
import tempfile
import torch

def load_model_from_package(path, arch_name=None, module_name=None):
    imp = torch.package.PackageImporter(path)
    # Assume this standardized header information exists that tells us the
    # name of the resource corresponding to the model
    if arch_name is None or module_name is None:
        package_header = json.loads(imp.load_text(
            'package_header', 'package_header.json'))
        arch_name = package_header['arch_name']
        module_name = package_header['module_name']

    model = imp.load_pickle(module_name, arch_name)

    # store stuff like mean/std of dataset like this
    # try:
        # fit_config_text = imp.load_text('package_header', 'fit_config.yaml')
    # except Exception:
        # pass
    # else:
        # import io
        # import yaml
        # file = io.StringIO(fit_config_text)
        # # Note: types might be wrong here
        # fit_config = yaml.safe_load(file)
        # model.fit_config = fit_config

    return model


st.title('Toxicology - Prediction as a Service')

@st.cache(show_spinner=False)
def df_from_file(file) -> pd.DataFrame:
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

upload_container = st.empty()
data_file = upload_container.file_uploader('Select data', type=['csv', 'xlsx'])

if data_file:
    upload_container.empty()

    model = load_model_from_package('current_best_model.pt')

    df = df_from_file(data_file)

    inputs = [
        'AeroMassPerPuff_In',
        'InitDiameter',
        'AeroTemp',
        'FRC',
        'PuffVol',
        'DiluAirVol',
        'PuffDur',
        'MouthHoldDur',
        'InhaleDur',
        'PauseDur',
        'ExhaleDur',
        'OralHumidity',
        'AeroMassFraction_In_Water',
        'AeroMassFraction_In_Nicotine',
        'AeroMassFraction_In_PropGlycol',
        'AeroMassFraction_In_Glycerin',
        'AeroMassFraction_In_Cadmium',
    ]

    outputs = [
        'DepMass_Oral_Water',
        'DepMass_TB_Water',
        'DepMass_Pul_Water',
        'DepMass_Oral_Nicotine',
        'DepMass_TB_Nicotine',
        'DepMass_Pul_Nicotine',
        'DepMass_Oral_PropGlycol',
        'DepMass_TB_PropGlycol',
        'DepMass_Pul_PropGlycol',
        'DepMass_Oral_Glycerin',
        'DepMass_TB_Glycerin',
        'DepMass_Pul_Glycerin',
        'DepMass_Oral_Cadmium',
        'DepMass_TB_Cadmium',
        'DepMass_Pul_Cadmium',
    ]

    input_df = df.rename(columns={
        'AeroMassPerPuff_In': 'AeroMassPerPuff',
        'AeroMassFraction_In_Water': 'AeroMassFraction_Water',
        'AeroMassFraction_In_Nicotine': 'AeroMassFraction_Nicotine',
        'AeroMassFraction_In_PropGlycol': 'AeroMassFraction_PropGlycol',
        'AeroMassFraction_In_Glycerin': 'AeroMassFraction_Glycerin',
        'AeroMassFraction_In_Cadmium': 'AeroMassFraction_Cadmium',
    })

    # Select a sample of rows to predict.
    rows = [5, 10, 20, 40, 60, 100]
    sample = input_df.iloc[rows]
    sample_out = df[outputs].iloc[rows]

    # Write out input data to disk.
    input_file = tempfile.NamedTemporaryFile(suffix='.xlsx')
    sample.to_excel(input_file.name)

    # Prepare an output file as well.
    output_file = tempfile.NamedTemporaryFile(suffix='.xlsx')

    # Run the model.
    model.inference(input_file.name, output_file.name)

    # Display the results.
    st.markdown('## Input dataframe')
    input_df

    st.markdown('## Sample')
    sample

    st.markdown('## Predicted values for output variables')
    prediction = pd.read_excel(output_file.name)[outputs]
    prediction.index = rows
    prediction

    st.markdown('## Ground truth values for output variables')
    sample_out

    st.markdown('## Error measurement')
    diff = prediction - sample_out
    residuals = pd.DataFrame((np.sqrt(np.sum(row * row)) for index, row in diff.iterrows()), index=diff.index, columns=['L2(residual)'])
    residuals
