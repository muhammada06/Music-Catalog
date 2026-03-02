import tkinter as tk
import csv

root = tk.Tk(screenName="Create Account")

image = tk.PhotoImage(file="watermelionIncLogo.png")
image = image.subsample(4, 4)

image_label = tk.Label(root, image=image).grid(row=0, column=3, padx=10, pady=10)
create_label = tk.Label(root, text="Hey, Lets start creating you account!").grid(row=1, column=3, padx=10, pady=10)

username_label = tk.Label(root, text="Username: ").grid(row=2, column=2)
password_label = tk.Label(root, text="Password: ").grid(row=3, column=2)

username = tk.Entry(root)
username.grid(row=2, column=3)
password = tk.Entry(root)
password.grid(row=3, column=3)

def writing():

    account = [{'username':username.get(), 'password':password.get()}]

    with open('accounts.csv', 'a', newline='') as csvfile:
        fieldnames = ['username', 'password']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(account)
        username.delete(0, tk.END)
        password.delete(0, tk.END)

button = tk.Button(root, text="Enter", width=25, command=writing).grid(row=4, column=3, padx=10, pady=10)

root.mainloop()