# app.py
from flask import Flask, render_template, request, send_file
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from io import BytesIO
import os
from datetime import datetime

app = Flask(__name__)

# Sample data, replace this with your actual data
doc_path = r'\\10.172.138.106\tbm_MSLDataAnalytic\THO MSL TEM\00_TEMOsiris_Operation_folder\Logbook'
PMC_Osiris = os.path.join(doc_path, 'MMC_TEM_OSIRIS_PM_Checking.xlsx')
PMC_Metrios = os.path.join(doc_path, 'MMC_TEM_METRIOS_PM_Checking.xlsx')

current_file = PMC_Metrios
df_osiris = pd.read_excel(PMC_Osiris)
df_metrios = pd.read_excel(PMC_Metrios)

# Combine both dataframes into a single dataframe with an additional 'Source' column
df_osiris['Source'] = 'PMC_Osiris'
df_metrios['Source'] = 'PMC_Metrios'

# Concatenate dataframes
df = pd.concat([df_osiris, df_metrios])

df['DATE'] = pd.to_datetime(df['DATE'])

# Get unique column names for Y Column selection
y_columns = df.columns.tolist()

# Function to generate plot and return image
def generate_plot(start_date, end_date, y_column, include_osiris=True, include_metrios=True):
    filtered_df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)

    if include_osiris:
        # Plot data from PMC_Osiris
        osiris_data = filtered_df[filtered_df['Source'] == 'PMC_Osiris']
        ax.plot(osiris_data['DATE'], osiris_data[y_column], label='PMC_Osiris - ' + y_column, color='orange')

    if include_metrios:
        # Plot data from PMC_Metrios
        metrios_data = filtered_df[filtered_df['Source'] == 'PMC_Metrios']
        ax.plot(metrios_data['DATE'], metrios_data[y_column], label='PMC_Metrios - ' + y_column, color='blue')

    ax.set_xlabel('Date')
    ax.set_ylabel(y_column)
    ax.legend(loc='upper left')

    # Set the number of ticks to 13
    ax.xaxis.set_major_locator(plt.MaxNLocator(13))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    plt.close(fig)  # Close the figure to free up resources

    return img_buf

@app.route('/')
def index():
    data_source = {'current_file': current_file}
    return render_template('index.html', y_columns=y_columns, data_source=data_source)

@app.route('/plot', methods=['POST'])
def plot():
    start_date = pd.to_datetime(request.form['start_date'])
    end_date = pd.to_datetime(request.form['end_date'])
    y_column = request.form['y_column']
    include_osiris = request.form.get('include_osiris') == 'true'
    include_metrios = request.form.get('include_metrios') == 'true'

    # Generate the plot
    img_buf = generate_plot(start_date, end_date, y_column, include_osiris, include_metrios)

    # Return the plot image as a file
    return send_file(img_buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='192.168.1.114', port=5000, debug=True)
