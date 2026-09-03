# START HERE — No command line required

This first workflow uses only your web browser.

## Part 1: Create your GitHub account

1. Open GitHub and create a free personal account.
2. Choose a professional username because it will appear in your portfolio URL.
3. Verify your email address.
4. Turn on two-factor authentication when prompted.

## Part 2: Create the project repository

1. Sign in to GitHub.
2. Select the plus icon in the upper-right corner.
3. Select **New repository**.
4. Repository name: `options-payoff-visualiser`
5. Description:
   `Interactive Python tool for analysing option profit and loss at expiration.`
6. Select **Public**.
7. Do not add another README because this starter folder already contains one.
8. Select **Create repository**.

## Part 3: Upload the starter files

1. Unzip the starter download on your computer.
2. Open the unzipped folder.
3. In your empty GitHub repository, select the link to upload existing files.
   If files already exist, use **Add file > Upload files**.
4. Drag these files into the upload area:
   - `app.py`
   - `payoff_engine.py`
   - `requirements.txt`
   - `README.md`
   - `START_HERE.md`
   - `.gitignore`
5. Commit message:
   `Add working options payoff visualiser starter`
6. Commit directly to the `main` branch.

Important: upload the files inside the folder, not only the ZIP file.

## Part 4: Deploy with Streamlit Community Cloud

1. Open Streamlit Community Cloud.
2. Sign in with GitHub.
3. Authorise Streamlit to read your public GitHub repositories.
4. Select **Create app**.
5. Select **Yup, I have an app**.
6. Enter:
   - Repository: `<your-username>/options-payoff-visualiser`
   - Branch: `main`
   - Main file path: `app.py`
7. Select **Deploy**.
8. When deployment succeeds, save the public `streamlit.app` address.

## Part 5: Verify the financial outputs

With the default covered-call inputs, confirm:

- break-even = A$151.95;
- maximum gain = A$805;
- maximum loss = A$15,195.

Inspect the table at A$140, A$151.95, A$160, and A$170.

## Part 6: Make your first code edit

1. Return to the GitHub repository.
2. Open `app.py`.
3. Select the pencil icon.
4. Find:

   `st.title("Options Payoff Visualiser")`

5. Change it to:

   `st.title("Nathaniel's Options Payoff Visualiser")`

6. Select **Commit changes**.
7. Use this commit message:

   `Personalise app title`

Streamlit will read the new GitHub commit and update the deployed app.

## Basic GitHub vocabulary

- Repository: the online folder containing your project.
- Commit: a saved checkpoint with a short description.
- Main branch: the primary version of the project.
- README: the front-page explanation of the project.
- Deploy: publish the code as a functioning website.
