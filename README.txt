NEISS INJURY ANALYSIS

======================

Github repo: https://github.com/dva023/neiss-injury-analysis/

DESCRIPTION
-----------

In this project, we utilized the National Electronic Injury Surveillance System (NEISS) database to develop a model predicting injury severity. Our approach combines machine learning with natural language processing (NLP) techniques to extract insights from unstructured medical narratives.

You will run a workbook locally with the connection to our TabPy server.

INSTALLATION
------------

Prerequisites

1. TabPy Server Config/Setup

   - Ensure you have access to the details: [SharePoint](https://gtvault.sharepoint.com/:t:/s/cse6242groupprojectchat/EVJUuC2n5QRLg9DnvhpDjX8BPPnen92JcfalH8GllpUUkw?e=VnCnmU) (GaTech email login required)
   - Alternatively, you can follow TabPy server setup instructions in notebooks/tabpy_v6_no_db.ipynb to boot up a local tabpy server.

2. Software

   - Tableau Desktop installed on your computer.

3. Network Access

   - Confirm that you can access the TabPy server over your network.  
   - Check any VPN, firewall, or proxy settings that might block the connection.

Configure the Tableau Connection to TabPy Server

1. Open Tableau Desktop.
2. Go to Help > Settings and Performance > Manage External Service Connection.
3. In the dialog box:
   - Select TabPy as the service.
   - Enter the Server URL (tabpy.ericy.me) in the Hostname field.
   - Set the Port (9004).
   - Check the Sign in with username and password box and provide the Username and Password.
      - Username: dva023
      - Password: YL8bar-_3.jXGFet
   - Click Test Connection to ensure the connection is successful.

4. Click OK to save the settings.

EXECUTION
---------

Open the Workbook:

1. Double-click the workbook file (./CODE/tableau/team023tableau.twbx).
2. Select Yes for the warning box Do you want to run these scripts?.
3. Verify that the workbook connects to the TabPy server without errors.
4. Enter Presentation Mode by selecting icon in the toolbar, pressing the F7 key, or select Window > Presentation Mode

DEMO VIDEO
----------

For a step-by-step demonstration of the process, please watch our video: <https://youtu.be/WvGWpX0jjmU>

TROUBLESHOOTING
---------------

1. Error: Authentication Failed
   - Double-check the username and password.
   - Confirm with the server admin if your credentials have been updated or restricted.

2. Connection Test Fails in Tableau
   - Ensure that Tableau Desktop is configured with the correct host and port.
   - Restart Tableau and reattempt the connection test.

3. Additional Help
   - Please feel free to reach out to any members of Team 23 if help needed to resolve any issues.
