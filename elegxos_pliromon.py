import pandas as pd
from tkinter import filedialog
import time

'''
Logistikos Elegxos
Κωδικός Οργανισμού	
Δίκτυο	1
Υπηρεσία 2	
Ημερομηνία 3 
Τύπος Πληρωμής 4	
Οργανισμός	5 
Όνομα Εμπόρου 6	
ΑΦΜ	7
Αριθμός Τερματικού 8	
Τρόπος Πληρωμής	9
Ποσό 10	
Κατάσταση Πληρωμής 11	
Αριθμός Αναφοράς 18
Μον. Αριθμός Συναλλαγής 20	
Προμήθεια Εμπόρου 21	
Προμήθεια Δικτύου 22
Προμήθεια Συνεργάτη	23
Προμήθεια ETE 24	
Συνολική Προμήθεια 25	
Δηλωθέν Ποσό 36	
Ρέστα 37	
Αξία Χαρτονομισμάτων 38	
Αξία Κερμάτων 39	
Ποσό Επιστροφής	Κωδικός Πληρωμής 41
'''

def find_file():
    promt_flag = True
    while promt_flag:
        print("Please select excel file location: ")
        time.sleep(2)
        excel_script_location = filedialog.askopenfilename().replace("/","\\")
        if ".xlsx" in excel_script_location:
            promt_flag = False
        else:
            promt_flag = True

    return excel_script_location

def return_project_name():
    promt_flag = True
    while promt_flag:
        project_name = input("Please enter the project name: ")
        time.sleep(2)
        if project_name != '':
            promt_flag = False
        else:
            promt_flag = True

    return project_name

# Open source file
source_excel = find_file()
source_df = pd.read_excel(source_excel)

source_df = source_df.drop(
    columns=[
        "Ίδρυμα Πληρωμών",
        "Αιτία Αποτυχίας",	
        "Όνομα Οφειλέτη",	
        "Τηλέφωνο Οφειλέτη",	
        "Λογαριασμός Χρέωσης",	
        "Διεύθυνση",	
        "Τύπος Τερματικού",		
        "12ψήφιο Αναγνωριστικό",
        "Λογαριασμός Πίστωσης",	
        "Όνομα Δικαιούχου",	
        "SRN Συναλλαγής",
        "Τρόπος Εισαγ. Κωδ. Πληρωμής",	
        "Α.Α. Συναλλαγής",	
        "Α.Α. Ταμείου",	
        "Χρόνος Διενέργειας (ms)",	
        "Αιτιολογία Επιστροφής",	
        "Αιτιολογία Τερματισμού",	
        "Αιτιολογία Συναλλαγής"
        ])

project_name = return_project_name()
source_df.to_excel(f'spare/destination_{project_name}.xlsx', index=False)

log_el_df = pd.read_excel(f'spare/destination_{project_name}.xlsx')

log_el_df = log_el_df.dropna()

log_el_df['Ποσό'] = log_el_df["Ποσό"].str.replace(",",".")
log_el_df['Ποσό'] = log_el_df["Ποσό"].astype(float)

final_df = pd.DataFrame()

# Payment type conditions
cash_condition = log_el_df['Τρόπος Πληρωμής'] == 'Μετρητά'
# cash_over_750_condition = float(log_el_df['Ποσό']) > 750
debit_card_condition = log_el_df['Τρόπος Πληρωμής'] == 'Με χρήση λογαριασμού χρεωστικής κάρτας'
credit_card_condition = log_el_df['Τρόπος Πληρωμής'] == 'Με χρήση πιστωτικής κάρτας'
not_on_us_condition = log_el_df['Τρόπος Πληρωμής'] == 'Με χρήση κάρτας'

# Pattern

# Find unique values of organization
print("\n")
print(f"Unique organizations: {log_el_df['Οργανισμός'].nunique()}")

large_dir = {}

def append_rows(final_df, filtered_rows):
    if not filtered_rows.empty:
        final_df = pd.concat([final_df, filtered_rows.iloc[0]])
    return final_df


for item in log_el_df['Οργανισμός'].unique():

    org_condition = log_el_df['Οργανισμός'] == item

    cash_filtered_rows = log_el_df.loc[(cash_condition) & (log_el_df['Ποσό'] < 750) & (org_condition)]
    if not cash_filtered_rows.empty:
        final_df = pd.concat([final_df, cash_filtered_rows.head(1)])

    cash_over_750_filtered_rows = log_el_df.loc[(cash_condition) & (log_el_df['Ποσό'] > 750) & (org_condition)]
    if not cash_over_750_filtered_rows.empty:
        final_df = pd.concat([final_df, cash_over_750_filtered_rows.head(1)])

    debit_filtered_rows = log_el_df.loc[(debit_card_condition) & (org_condition)]
    if not debit_filtered_rows.empty:
        final_df = pd.concat([final_df, debit_filtered_rows.head(1)])

    credit_filtered_rows = log_el_df.loc[(credit_card_condition) & (org_condition)]
    if not credit_filtered_rows.empty:
        final_df = pd.concat([final_df, credit_filtered_rows.head(1)])

    off_us_filtered_rows = log_el_df.loc[(not_on_us_condition) & (org_condition)]
    if not off_us_filtered_rows.empty:
        final_df = pd.concat([final_df, off_us_filtered_rows.head(1)])

# Get unique rows based on specified columns
# final_df = final_df.drop_duplicates(subset=["Οργανισμός", "Τρόπος Πληρωμής", "Κωδικός Πληρωμής"], keep=False)



final_df.to_excel(f'Ελεγχος_πληρωμων_{project_name}.xlsx', index=False)