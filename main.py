import requests
from io import BytesIO
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


def google_sheet_df(google_sheet_url):
    request = requests.get(google_sheet_url)
    data = request.content
    df = pd.read_csv(BytesIO(data), index_col=0)
    return df


# Load data frames.
exercises_df = google_sheet_df(
    'https://docs.google.com/spreadsheets/d/17nSqFUoBa4QSGofWNvRCEyMwN86vZ8uD/export?format=csv&gid=905957569')
sessions_df = google_sheet_df(
    'https://docs.google.com/spreadsheets/d/17nSqFUoBa4QSGofWNvRCEyMwN86vZ8uD/export?format=csv&gid=1806664148')
authentication_df = google_sheet_df(
    'https://docs.google.com/spreadsheets/d/17nSqFUoBa4QSGofWNvRCEyMwN86vZ8uD/export?format=csv&gid=353408653')
authentication_df = authentication_df.reset_index()
exercises_df = exercises_df.reset_index()
session_options = sessions_df.index.values  # Generate session list.

standard_font = ('Times New Roman', 13)
standard_main_loop_pady = 10
standard_main_loop_padx = 15


def generate_session():
    selected_session = session_entry_var.get()
    number_of_exercises = number_of_exercises_entry_var.get()

    session_recipe_df = sessions_df[
        sessions_df.index == selected_session]  # Retrieve categories for the selected session.
    # List of tuples with the category in the cardinal position & number of exercises in the secondary.
    category_number_of_exercises_tuples = []
    try:
        for category in sessions_df.columns.values:
            if category != 'Stretches':  # Ensure we are not including stretches because it is absoulte, not relative.
                category_exercises = round(((session_recipe_df[category][0] / 100) * number_of_exercises),
                                           0)  # Get the number of exercises for category.
            else:
                category_exercises = session_recipe_df[category][0]  # Returns absolute stretch number.
            category_number_of_exercises_tuples.append((category, category_exercises))  # Add to the category/exercise list.
    except IndexError:
        return messagebox.showerror('Sessions', 'Please select a session.')
    export_df = pd.DataFrame(columns=exercises_df.columns)

    for category in category_number_of_exercises_tuples:
        if category[1] > 0:
            try:
                if category[0] == 'Stretches':
                    sample = (exercises_df[(exercises_df['Categories'] == selected_session) & (exercises_df['Stretches'] == 1)]).sample(int(category[1]))
                else:
                    sample = (exercises_df[(exercises_df['Categories'] == category[0]) & (exercises_df['Stretches'] == 0)]).sample(int(category[1]))
                export_df = export_df.append(sample, ignore_index=True)
            except ValueError:
                return messagebox.showerror(category[0], 'You do not have enough ' + category[
                    0].lower() + ' to build ' + selected_session + '.')
    if len(export_df) > 0:
        export_file_path = filedialog.asksaveasfilename(title='Default', defaultextension='.csv')
        export_df.to_csv(export_file_path, index=False, header=True)


def login_command():
    if login_username_entry.get() in authentication_df['Permitted Users'].to_list():
        login_frame_position = authentication_df['Permitted Users'].to_list().index(login_username_entry.get())
        if login_password_entry.get() == str(
                authentication_df['Secret Token'].iloc[login_frame_position]):  # Validate user
            root.deiconify()  # Unhide the root window
            top.destroy()  # Removes the top level window
        else:
            messagebox.showerror('Incorrect credentials', 'Incorrect credentials')
    else:
        messagebox.showerror('Incorrect credentials', 'Incorrect credentials')


# Application
root = tk.Tk()
root.title('AdaptationX')
root.geometry('300x300')
# Login Screen
top = tk.Toplevel()
top.title('AdaptationX')
top.geometry('300x300')
login_welcome = tk.Label(top, text='Login', font=('Times New Roman', 25), justify='center')
login_welcome.grid(column=0, row=0, columnspan=2, sticky='NSEW')
login_username_label = tk.Label(top, text='Username: ', font=standard_font, justify='left')
login_username_label.grid(column=0, row=1, sticky='W', pady=standard_main_loop_pady)
login_password_label = tk.Label(top, text='Password: ', font=standard_font, justify='left')
login_password_label.grid(column=0, row=2, sticky='W', pady=standard_main_loop_pady)
login_username_entry = tk.Entry(top, font=standard_font, justify='left')
login_username_entry.grid(column=1, row=1, sticky='NSEW', pady=standard_main_loop_pady)
login_password_entry = tk.Entry(top, font=standard_font, justify='left')
login_password_entry.grid(column=1, row=2, sticky='NSEW', pady=standard_main_loop_pady)
login_button = tk.Button(top, text='Login', font=standard_font, command=login_command)
login_button.grid(column=0, row=4, columnspan=2)

welcome_title = tk.Label(text='AdaptationX', font=('Times New Roman', 25), justify='center')
welcome_title.grid(column=0, row=0, columnspan=2, sticky='NSEW')
slogan_title = tk.Label(text='With creativity & innovation we can make being \n fit & staying fit easier for everyone!',
                        font=('Times New Roman', 12), justify='center')
slogan_title.grid(column=0, row=1, columnspan=2, sticky='NSEW')
session_label = tk.Label(text='Session:', font=standard_font, justify='left')
session_label.grid(column=0, row=2, sticky='W', pady=standard_main_loop_pady)
exercises_label = tk.Label(text='Exercises:', font=standard_font, justify='left')
exercises_label.grid(column=0, row=3, sticky='W', pady=standard_main_loop_pady)

session_entry_var = tk.StringVar()
session_entry = tk.OptionMenu(root, session_entry_var, *session_options)
session_entry.config(font=standard_font)
session_entry.grid(row=2, column=1, padx=standard_main_loop_pady, pady=standard_main_loop_pady, sticky='E')
number_of_exercises_entry_var = tk.IntVar()
number_of_exercises_entry = tk.Entry(root, textvariable=number_of_exercises_entry_var, font=standard_font, bd=2,
                                     justify='right', width=5)
number_of_exercises_entry.grid(row=3, column=1, padx=standard_main_loop_pady, pady=standard_main_loop_pady, sticky='E')

submit_button = tk.Button(root, text='Generate\nWorkout', command=generate_session, pady=20,
                          padx=standard_main_loop_padx, bd=2,
                          font=('Times New Roman', 15))
submit_button.grid(row=4, column=1)

root.withdraw()  # Hides the main window, it's still present it just can't be seen or interacted with
root.mainloop()
