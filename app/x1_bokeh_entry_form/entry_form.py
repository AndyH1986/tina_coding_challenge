import pandas as pd
from bokeh.io import curdoc
from bokeh.models import TextInput, Select, ColumnDataSource, Button
from bokeh.layouts import layout, row
from bokeh.models.widgets import (
    DataTable,
    TableColumn,
    StringEditor,
    SelectEditor,
)
from bokeh.io import curdoc


############## LOAD DF for Indexes and Currencies ##############
df_currancy = pd.read_excel("../data/index_currency_list.xlsx", skiprows=1)

# create list of the relevent indexes
lst_choose_index = df_currancy.columns[1:].to_list()

# create list of the currencies to the indexes
lst_index_currency = df_currancy.iloc[0].to_list()[1:]

# create dict, assignment from index to currency
dct_index_currency = dict(zip(lst_choose_index, lst_index_currency))

############## LOAD DF for exchange rates ##############
df_exchange = pd.read_excel(
    "../data/index_currency_list.xlsx", sheet_name="currency List", skiprows=1
)
lst_base_currancy = df_exchange.columns[1:].to_list()
lst_reference_date = df_exchange["Index Æ\nMonth "].astype(str).to_list()


############## ENTRY FORM ##############
def validate_input(attr, old_value, new_value) -> None:
    """
    Check if spend amount is a number above 0
    """
    try:
        input_value = int(new_value)
        if isinstance(input_value, int) and input_value > 0:
            spend_amount.value = str(input_value)
    except ValueError:
        spend_amount.value = "Please enter a number"


# DropDown Base Currency
select_base_curr = Select(title="Please choose a Currency:", options=lst_base_currancy)


# DropDown Reference Date
select_ref_date = Select(
    title="Please choose a Reference Date:", options=lst_reference_date
)


# Input Spend Amount
spend_amount = TextInput(title="Base Currency:")
spend_amount.on_change("value", validate_input)


# Add elements to the document
curdoc().add_root(row(select_base_curr, select_ref_date))
curdoc().add_root(spend_amount)


############## TABLE ##############

# create ColumnDataSource with init values
data = {"Index": [""], "Currency": [""], "Percentage": ["0"]}
source = ColumnDataSource(data=data)

# create columns for the table
columns = [
    TableColumn(
        field="Index",
        title="Index",
        editor=SelectEditor(options=lst_choose_index),
    ),
    TableColumn(
        field="Currency",
        title="Currency",
        editor=StringEditor(),
    ),
    TableColumn(field="Percentage", title="Percentage", editor=StringEditor()),
]


def add_row() -> None:
    """
    create a new row in the table
    """
    new_data = {
        col: source.data[col] + [None if col != "Percentage" else 0]
        for col in source.data
    }
    source.data = new_data
    update_data()
    check_sum()


def delete_rows() -> None:
    """
    delete a selected row
    """
    selected_indices = source.selected.indices
    if selected_indices:
        for col in source.data:
            source.data[col] = [
                val
                for i, val in enumerate(source.data[col])
                if i not in selected_indices
            ]
        source.selected.indices = (
            []
        )  # Zurücksetzen der ausgewählten Zeilen auf leere Liste
        update_data()
        check_sum()


def check_sum() -> None:
    """
    Check if the sum of the column 'Percentage' is 100
    """
    percentage_data = source.data["Percentage"]
    try:
        sum_percentage = sum(float(val) for val in percentage_data if val is not None)
        if sum_percentage != 100:
            print(
                "Error: Sum should always be 100:",
                sum_percentage,
            )
        else:
            print("Sum is 100.")
    except ValueError:
        print("Error: No valid value.")


# Funktion zum Abrufen der aktualisierten Daten aus der ColumnDataSource
def update_data() -> None:
    """Just print the new values"""
    updated_data_dict = source.data
    index_data = updated_data_dict["Index"]
    currency_data = updated_data_dict["Currency"]
    percentage_data = updated_data_dict["Percentage"]

    print("update Index:", index_data)
    print("update Currency:", currency_data)
    print("update Percentage:", percentage_data)

    # # Die on_change-Funktion auf die Datenquelle anwenden
    # source.on_change("data", on_percentage_change)


def on_index_change(attr, old_value, new_value) -> None:
    """
    Select the assigned currency for the selected index
    """
    selected_indices = source.selected.indices

    for i in selected_indices:
        if i < len(source.data["Index"]):
            selected_index = source.data["Index"][i]
            if selected_index in dct_index_currency:
                source.data["Currency"][i] = dct_index_currency[selected_index]


def on_percentage_change(attr, old_value, new_value) -> None:
    """
    check if value in column percentage is a number
    """
    new_values = source.data["Percentage"]
    for i in range(len(new_values)):
        try:
            new_values[i] = int(new_values[i])
        except ValueError:
            error_message = (
                f"No valid value {i+1} in column Percentage: {new_values[i]}"
            )
            print(error_message)

            source.data["Percentage"][i] = error_message


# create table
data_table = DataTable(source=source, columns=columns, editable=True, height=200)


# create add row button
# attach add-row function to the add_row_button
add_row_button = Button(label="Add new row")
add_row_button.on_click(add_row)


# create delete button
# attach delete_rows function to the delete button
delete_row_button = Button(label="Delete selected row")
delete_row_button.on_click(delete_rows)

# assign currency to index
source.on_change("data", on_index_change)

# Erstellen Sie ein Layout
table_layout = layout([[data_table]])
button_layout = row(add_row_button, delete_row_button)
layout = layout([button_layout, table_layout])

# Fügen Sie das Layout zum Dokument hinzu
curdoc().add_root(layout)
