# Low-literacy seed conversations

- Endpoint: `https://support-chatbot-dev.azurewebsites.net`
- Manual: `121`
- User: `eval-seed-user-low-literacy`
- Generated: 2026-09-24 10:55 UTC

## Conversation 1

`session: f54a4a5d-bfa5-4fb7-8354-5b7124c95238`

**User:** how i put the peple from my excel in the sistem

**Chatbot:**

To put people from your Excel into the 121 system, you need to **import a registration list as a CSV file**. [1]

1) **Download the CSV template** from 121 (it’s generated based on your program registration form).  
- Open your **Program** → **Registrations**  
- Click **Import new registrations** (right side) → **Download template CSV-file** [1]

2) **Copy your Excel data into the template**  
- Open the template in Excel  
- Copy your registration data into the matching columns/labels in the template  
- Save it as a **.CSV** file [1]

3) **Import the CSV into 121**  
- Go back to **Program → Registrations**  
- Click **Import new registrations**  
- Choose the **CSV file** you prepared  
- Click **Import file**  
- Wait for the confirmation pop-up (it may take some time depending on the number of registrations) [1]

If the import fails or shows an error, check that your file is **correctly formatted and saved as .CSV**. [1]

<details><summary>Sources</summary>

- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
- [Add team members](https://manual.121.global/en/team/add-team-members/)

</details>

`trace: fa6ba0e1742cd86ca6e8a51c5e7fe970`

**User:** it dont work it give me a error

**Chatbot:**

Sorry it’s not working. The manual says that if the import is unsuccessful or shows an error, you should **check that your Excel file is correctly formatted and saved as .CSV**. [1]

A few things to verify based on the import requirements:
- Make sure you’re uploading a file that is **saved as .CSV** (not .xlsx). [1]
- Make sure you used the **121 template** and that your data is in the **correct columns/labels**. [1]

If you tell me the **exact error message** you see (or a screenshot), I can help you narrow down what to fix.

<details><summary>Sources</summary>

- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [What if I see empty page](https://manual.121.global/en/registration/registration-list-empty/)

</details>

`trace: ba4fd5fb91f77251e0e463fe1d19e8b4`

**User:** wher can i find a exampel file to copy

**Chatbot:**

You can get an example/template directly from 121:

- Go to your **Program** → **Registrations**  
- Click **Import new registrations** (right side)  
- Select **Download template CSV-file**  
- Open that downloaded CSV in Excel and copy your data into it [1]

<details><summary>Sources</summary>

- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [What if I see empty page](https://manual.121.global/en/registration/registration-list-empty/)
- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)

</details>

`trace: 1c2de82fc1122928379db22ae83ad5fe`

## Conversation 2

`session: 7b09cc43-e470-40f5-a658-19a4973a64c8`

**User:** the money did not arive to the famlies why

**Chatbot:**

If the money didn’t arrive to the families, it’s usually because the payment ended up **Failed** (or is still **Pending/Processing**) in the 121 Platform.

### 1) Check the payment status
- Go to the **Payments** page and open the specific payment round.
- Look at the **transaction/payment status** for the registrations.

**What the statuses mean:**
- **FAILED**: the transaction failed and registrations **did not receive any payments**. [1][2]
- **PENDING / PROCESSING**: the transfer is not confirmed as completed yet (for manual payments, this is typically until reconciliation is imported). [1][3]
- **SUCCESSFUL**: the transfer was sent and families can use it. [1][2]

### 2) If it’s FAILED, check the reason
On the specific payment:
- Filter the registration list by **Transaction status = Failed**
- Open the **Reason** column to see why it failed. [5]

Common reasons include:
- **Incorrect payment details** (e.g., full name, phone number, bank account number, ID number, location) [5]
- **Wrong format of the reconciliation file** (manual payment) [5]
- **Registration changed payment details** (e.g., phone number/payment info changed) [5]
- **Integration issues** (if you use an integrated FSP) [5]

### 3) Fix and retry (if applicable)
If you identified the issue, you can **retry failed transactions**:
- Go to the **Payments** page → open the payment round
- Select the registrations with **failed** status
- Click **Retry failed transaction(s)** and confirm **Retry transactions** [5]

If you tell me whether your payment method is **manual (FSP portal export/import)** or **integrated FSP**, and what status you see (**Failed / Pending / Processing**), I can point you to the most relevant next step.

<details><summary>Sources</summary>

- [Create and Approve payments](https://manual.121.global/en/payment/create-approve-payment/)
- [Payments page](https://manual.121.global/en/payment/payment/)
- [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
- [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
- [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)

</details>

`trace: 0be8f7c80bc483c6cec89eb013b20084`

**User:** how i send it agan to only those ones

**Chatbot:**

To retry **only the registrations whose payment failed**:

1. Go to the **Payments** page and open the **specific payment round**. [1]  
2. In the transaction/registration list, **select only the registrations with status = Failed**. [1]  
3. Click **Retry failed transaction(s)** (top right). [1]  
4. Click **Retry transactions** to approve. [1]  

After that, the platform will **automatically retry** for the selected registrations identified with **failed payment** status, and their payment status will update. [1]

<details><summary>Sources</summary>

- [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
- [Payment statuses in 121](https://manual.121.global/en/payment/list-status-payment-page/)
- [Decline registrations](https://manual.121.global/en/registration/registration-reject-pa/)
- [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
- [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)

</details>

`trace: eff01fd5f5a03611ff77670d76b72161`

## Conversation 3

`session: f8df1501-c19a-4c52-846f-a4d0379053b1`

**User:** i want my colega to see the projekt to how i do

**Chatbot:**

To let your colleague view (or manage) your project in the 121 Platform, you need to check their access/role in the **Program Team**.

- Go to your program and open **Settings** → **Program Team** (under the **Settings** page). [3][4]  
- In the **Program Team** tab, you can see the users and their assigned roles. If you have permission, you can **change/add/remove roles** for a user. [2][4]  
- Users who don’t have edit permissions will only have **View** access on that page. [1][2][4]

If you tell me what you want your colleague to do (only view, or also edit/change settings), I can point you to the right role/permission level based on the platform documentation.

<details><summary>Sources</summary>

- [Program Info & Settings](https://manual.121.global/en/Settings/project-info/)
- [Change team members roles](https://manual.121.global/en/team/change-team-roles-program/)
- [Program Settings page](https://manual.121.global/en/Settings/project-settings-page/)
- [Manage your program team](https://manual.121.global/en/team/team-page/)
- [Setting-up 121 Platform](https://manual.121.global/en/faq/setting-up-121-platform/)

</details>

`trace: 11125e2d400bf9fb34580a06a3284db7`

**User:** can she also chang the amont or only look

**Chatbot:**

It depends on her role/permissions.

- On the **Program Settings** page, **changing budget/payment-related amounts** (like budget, base transfer value, number of maximum payments, currency) can be done by **Program Admin** and users with **Program Update** permissions. [5]  
- If she only has **View** permission, she can **only look**, not change amounts. [1][3][5]

If you want, tell me whether she has **Program Admin**, **Program Update**, or only **View**—and I’ll confirm what she can do.

<details><summary>Sources</summary>

- [Data Changes Overview](https://manual.121.global/en/monitoring/data-changes/)
- [Program Info & Settings](https://manual.121.global/en/Settings/project-info/)
- [Program Settings page](https://manual.121.global/en/Settings/project-settings-page/)
- [Change team members roles](https://manual.121.global/en/team/change-team-roles-program/)
- [Budget & Payment settings](https://manual.121.global/en/Settings/payment-budget-settings/)

</details>

`trace: b7301d8f28218492851591e317f3bd38`

## Conversation 4

`session: 6356d31e-0191-4fc7-a4a8-e4ec9894d018`

**User:** how i colect the info from the famlies wen there is no internett in the village

**Chatbot:**

If there’s no internet in the village, you can still collect beneficiary information offline using a mobile data-collection app (e.g., **Kobo Collect**). Offline collection is possible, but **you will need internet later to sync/upload the collected data into the 121 platform**. [1]

When you’re back online, make sure the devices are connected so the collected forms can be synced and the registration list can be updated in 121. [1][3]

<details><summary>Sources</summary>

- [Setting-up 121 Platform](https://manual.121.global/en/faq/setting-up-121-platform/)
- [Timeline](https://manual.121.global/en/faq/timeline-121-integration/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [Step-by-Step Guide - Prepare your CVA Program](https://manual.121.global/en/general/prepare-your-project/)
- [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)

</details>

`trace: 1ba109bf9601467c8252138b756f7111`

**User:** and wen the internet come back what i must do

**Chatbot:**

When internet comes back, you must **upload/sync all the Kobo forms** so the collected data is sent to the 121 platform.

- **Offline verification (if you used Kobo for verification):** connect your devices to the internet, **upload ALL collected Kobo forms**, then **check that the changes are correctly reflected on the 121 platform**. [1]
- **Registration via Kobo (if you used Kobo for registrations):** the registrations are imported into 121 **only when an internet connection is established** (so connect the device and ensure the Kobo form can sync). [3]

If you tell me whether you collected data for **registration** or for **field verification**, I can point you to the exact “after” step for that case.

<details><summary>Sources</summary>

- [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)
- [Setting-up 121 Platform](https://manual.121.global/en/faq/setting-up-121-platform/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [Step-by-Step Guide - Prepare your CVA Program](https://manual.121.global/en/general/prepare-your-project/)
- [Timeline](https://manual.121.global/en/faq/timeline-121-integration/)

</details>

`trace: 7bfdc4e376fb2d19ca8661f2674c9cd5`

## Conversation 5

`session: bb77b675-3738-46b6-9b3e-d18650f8314a`

**User:** i cant go inside the sistem it say my paswrd is wrong

**Chatbot:**

Sorry you’re running into that. Here are the 121 steps to regain access:

1) **Double-check your login details**
- Make sure you enter the **email address exactly as in the email** (it’s case sensitive) and use the **password that was shared in your login email**. [1]

2) **If you forgot your password, reset it**
- Contact your **121 User Manager** to reset your password from the **Users page**:
  - In the user row, click the **three dots**
  - Select **Reset Password**
  - Confirm
- An **email** will be sent to you with instructions to set a new password. [2]

3) **If you still can’t log in**
- Contact support at **support@121.global**. [2]

If you tell me whether you’re using **SSO (Microsoft account)** or the **email+password login link**, I can point you to the right path.

<details><summary>Sources</summary>

- [Log In](https://manual.121.global/en/general/logging-in/)
- [Reset password](https://manual.121.global/en/general/reset-password/)
- [Add User to 121](https://manual.121.global/en/users/add-users/)
- [Change current password](https://manual.121.global/en/general/change-current-password/)
- [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)

</details>

`trace: 1ab7cd9dd8df31a6712e788aae774414`

**User:** who can giv me a new paswrd

**Chatbot:**

A new password can be given/reset by your **121 User Manager** (they can reset your password from the **Users** page). [2]

If you’re still not able to log in after that, you can contact **support@121.global**. [2]

<details><summary>Sources</summary>

- [Add User to 121](https://manual.121.global/en/users/add-users/)
- [Reset password](https://manual.121.global/en/general/reset-password/)
- [Change current password](https://manual.121.global/en/general/change-current-password/)
- [Log In](https://manual.121.global/en/general/logging-in/)
- [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)

</details>

`trace: 83dca2470b9b812d5eaabddd79fcfd37`

## Conversation 6

`session: c0e84d19-dc6b-4686-a250-095e72a38914`

**User:** some famlies are two time in my list

**Chatbot:**

It sounds like you have duplicate registrations in your list. In 121, duplicates can be checked and handled from the **Registrations** page, and duplicates are identified using unique criteria (commonly things like **phone number** or **ID number**) configured in your Kobo form. [2][4]

To resolve duplicates:
1. Go to the **Registrations** page.
2. Use **Manage the table** → select **Duplicates** → **Apply** (this shows a **Duplicates** column). [2]
3. In the **Duplicates** column, use the filter icon and filter on **Duplicate** to show only the duplicated entries. [2]
4. Open a duplicated registration (click **Reg #** or **Name**) to see the banner **“Duplicated with”** and the matching field. [2]
5. Then choose one of the actions:
   - **Edit** the value in the registration profile (and click **Save** with a reason), or
   - **Decline** the registration (requires a reason), or
   - **Ignore the duplicate** (if your SOPs allow it). [2]

If you tell me which action you want to take (**edit / decline / ignore**) and what field is causing the duplicate (e.g., phone or ID), I can point you to the right option.

<details><summary>Sources</summary>

- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Deduplication](https://manual.121.global/en/registration/registration-deduplication/)
- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Registrations page](https://manual.121.global/en/registration/registrations-page/)
- [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)

</details>

`trace: 354923b95bb7d7adaab1e0015f5a4b05`

**User:** how i delet the one that is dubbel

**Chatbot:**

In 121 you don’t “delete” a duplicate entry. Instead, you resolve it by either **Declining** it (remove it from being included) or **Ignoring** it (keep it as unique per your SOPs). [1]

### To decline the duplicate registration
1. Go to the **Registrations** page and filter to show duplicates (Duplicates column → filter **Duplicate**). [1]
2. Find the duplicate registration and open its profile (click **Reg #**). [1]
3. On the top left, click **Action** → **Decline**. [1]
4. **Approve** the action (only if you’re sure). [1]
5. Enter a **reason** for declining the beneficiary, then confirm. [1]

If you accidentally declined it, you can change it back to **Included** (it’s reversible). [1]

Do you want to **decline** the duplicate, or **ignore** it because your SOPs allow shared values (like the same phone number)?

<details><summary>Sources</summary>

- [Deduplication](https://manual.121.global/en/registration/registration-deduplication/)
- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Registrations page](https://manual.121.global/en/registration/registrations-page/)
- [Edit registration details](https://manual.121.global/en/registration/edit-pa-profile/)

</details>

`trace: 907e166e2e7372ebecd5953a0830eb54`

## Conversation 7

`session: 2c549d23-f92f-4f1f-8782-38003e0384f8`

**User:** i want to send a sms to all the famlies in my list

**Chatbot:**

To send an SMS to all families in your registrations list, you can use the **“Send a message to registrations”** option in the **Registrations** page (for actions like Including/Declining/Payments). [1]

Before you can send SMS, you must:
1) **Enable messaging** by creating a **Twilio account** and ensuring you have **sufficient messaging credits** (contact 121 support to set up the integration). [1]  
2) Make sure your **phone numbers are in international format** (121 won’t automatically reformat them). [1]  
3) **Top up your Twilio account** so messages don’t fail due to insufficient funds. [1]

Then, in the **Registrations page**:
- Select the registrations you want to message (for “all families”, select all from the list),
- Click the **Message** icon,
- Choose **Custom message** (or a **predefined template**, if you’ve set those up),
- (Optional) Use **variables** with `@` to personalize fields per registration. [1]

If you tell me whether you want to use a **custom message** or a **predefined template**, I can point you to the exact option to choose in the Message menu.

<details><summary>Sources</summary>

- [Sending messages](https://manual.121.global/en/registration/sending-messages/)
- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Decline registrations](https://manual.121.global/en/registration/registration-reject-pa/)
- [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)

</details>

`trace: 3d8e899b671bbbd90681059be5639588`

**User:** can i writ there name inside the mesage

**Chatbot:**

Yes. You can insert each family/individual’s name in the SMS using a **variable**.

In the **Custom message** editor:
- Type `@`
- Select the field for the person’s name (e.g., `@name`)
- The message will automatically use the correct value for each registration. [1]

<details><summary>Sources</summary>

- [Sending messages](https://manual.121.global/en/registration/sending-messages/)
- [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
- [Decline registrations](https://manual.121.global/en/registration/registration-reject-pa/)
- [Add team members](https://manual.121.global/en/team/add-team-members/)
- [Edit registration details](https://manual.121.global/en/registration/edit-pa-profile/)

</details>

`trace: bdb40f71911f0881d38209650b43aa87`

## Conversation 8

`session: 18936f1e-c5fe-4772-93bf-1ea8e7ffe85a`

**User:** how much money evry famly get and can i chang that

**Chatbot:**

On 121, the **amount each family/registration receives** is controlled by your program’s **Budget & Payment settings**—specifically the **base transfer value / fixed transfer value** and related budget/payment fields. These settings can be **changed at any time**, and **all changes take effect immediately and apply to the entire registration list**. [5]

**Can you change it?**  
You can update these settings if you have **Program Admin** or **Program Update** permissions. [5]

If you tell me what role you have on the program (e.g., Program Admin, Program Update, View only), I can point you to the exact place to check/edit.

<details><summary>Sources</summary>

- [Payments page](https://manual.121.global/en/payment/payment/)
- [Program Info & Settings](https://manual.121.global/en/Settings/project-info/)
- [Program Settings page](https://manual.121.global/en/Settings/project-settings-page/)
- [End payments](https://manual.121.global/en/payment/end-payments/)
- [Budget & Payment settings](https://manual.121.global/en/Settings/payment-budget-settings/)

</details>

`trace: 7155be29a2bc6542a23e9f5b4fb4b85d`

**User:** if the famly have many childrin do they get more

**Chatbot:**

I don’t have enough information in the 121 manual documents provided to confirm whether families with more children receive more money automatically.

What I *can* say from the documents is that the amount a registration receives is determined by the program’s **Budget & Payment settings** (e.g., base/fixed transfer value and related budget/payment fields), and those settings can be updated by users with the right permissions. [5]

If you share whether your program uses a **fixed transfer value** or any **per-person/per-household** logic in your setup, I can help you interpret what the platform will do based on that.

<details><summary>Sources</summary>

- [Program Info & Settings](https://manual.121.global/en/Settings/project-info/)
- [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
- [Payments page](https://manual.121.global/en/payment/payment/)
- [Budget & Payment settings](https://manual.121.global/en/Settings/payment-budget-settings/)
- [Program Settings page](https://manual.121.global/en/Settings/project-settings-page/)

</details>

`trace: 6c33c0af961afad537c4f63bcba095bc`

## Conversation 9

`session: 202810eb-3d3a-4ca5-895e-4d2f17cf2f4a`

**User:** i give the cash with my hand to the peple how i writ it in the sistem after

**Chatbot:**

It sounds like you’re asking how to record **cash you gave by hand** in the 121 system.

From the 121 manual content I have here, the “Payments” workflow described is for **digital cash distribution** (e.g., mobile money, prepaid cards, bank transfers) and for **manual payments via an FSP portal** (export/import + reconciliation). It doesn’t explain the specific steps for recording **hand-delivered physical cash** directly in the system. [3]

If you tell me which payment method your program uses in 121 (e.g., **FSP portal/manual export**, **integrated FSP/instant payment**, or something else), I can point you to the closest matching 121 steps from the manual.

<details><summary>Sources</summary>

- [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
- [Create and Approve payments](https://manual.121.global/en/payment/create-approve-payment/)
- [Payments page](https://manual.121.global/en/payment/payment/)
- [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
- [Reconcile manual payments](https://manual.121.global/en/payment/manual-payment-reconciliation/)

</details>

`trace: cf7de66280c8f587cabf86b7747826a1`

**User:** what colums i must put in that file

**Chatbot:**

For manual payments via an **FSP portal**, the reconciliation/import file must be in **.csv** format, and you must ensure the **payment status labels** match 121’s expected values: **Completed → success**, **Failed → error**, **Pending → waiting**. [2]

However, the manual content I have here does **not** list the exact column names you must include in the reconciliation file (it only says to use the provided template and ensure required columns are included). [2][3]

What I can confirm from the manual:
- Use the **template** by going to **Payments → Import reconciliation data → Download template**. [3]
- Save your updated file as **.csv** before importing. [3]
- When importing, upload the **.csv** file via **Import reconciliation data** on the specific payment round. [2][3]

If you share whether you mean the **payment instructions file** (export to the FSP) or the **reconciliation file** (import back from the FSP), I can guide you to the right template steps.

<details><summary>Sources</summary>

- [Payments page](https://manual.121.global/en/payment/payment/)
- [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
- [Reconcile manual payments](https://manual.121.global/en/payment/manual-payment-reconciliation/)
- [Payment statuses in 121](https://manual.121.global/en/payment/list-status-payment-page/)
- [Payment reporting and activty](https://manual.121.global/en/payment/payment-reporting/)

</details>

`trace: 512ad9789541c2d98868cf6eb24a9294`

## Conversation 10

`session: d50f83a1-4483-4bf4-817a-05738eb1267a`

**User:** helo good morning

**Chatbot:**

Good morning! 👋 How can I help you with questions about 121 today?

`trace: d204064a8e273d8331628e5abfb3ee7d`

**User:** how i take the list of peple to my computer

**Chatbot:**

To take the registrations list to your computer, you can **export it from the 121 Platform**:

1. Go to the **Registrations** page (for your program).
2. Make sure your table view shows the columns you want (use **Settings** → select columns → **Apply**).  
   *Only visible columns are included in the export.* [1]
3. Select the registrations you want to export.
4. Click **Export** (top right of the table).
5. Choose **Export selected registrations**.
6. Select the file format (**Excel** or **CSV**).
7. The file will be generated and saved in your **Downloads** folder. [1]

If you tell me whether you want **Excel or CSV**, I can guide you on the best option for your next step.

<details><summary>Sources</summary>

- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
- [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)

</details>

`trace: e0b801a078993c52c4cb125e92d97900`

**User:** ok tank you very much

**Chatbot:**

You’re welcome! 😊 If you have any more questions about 121, just tell me.

<details><summary>Sources</summary>

- [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
- [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
- [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
- [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
- [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)

</details>

`trace: f10a70f3f4716f37417dd39e922408da`

## Conversation 11

`session: 6d20fcae-61c5-402e-9f36-6b9d34c0e486`

**User:** waht is the wether in nairobi tomorow

**Chatbot:**

I'm here to help with questions about 121, so I can't help with that one.  
Is there something about 121 I can help you with?

`trace: 91d29caddafcf60bf5ae81f5f44e6780`

**User:** ok sory. can u tel me how i add a new persn

**Chatbot:**

Sure. To add a new person to 121, you first need to create their **121 user account** (so they receive login credentials), and then (optionally) add them to the specific **program(s)** they should access. [1][2]

## 1) Add the new user account (Users page)
- On the left menu, open **Users**.
- On the top right of the **Users** page, click **Add new users**.
- Enter the **Name(s)** and **email address**.
- Click **Submit**. [1]

**Note:** An email is automatically sent to the address you enter—make sure the email is correct so the user receives the access link/credentials. [1]

## 2) Add them to a program (Program Team)
If you want them to access a specific program:
- Go to the program **Settings** page → **Program Team** tab.
- Click the **pencil** (edit).
- Click **+ Add user to team**.
- Search by the user’s **email address**.
- Under **Assign Roles**, tick the role(s) they should have.
- Click **Submit**. [2]

**Important:** Users must be added to each individual program they’re assigned to; it doesn’t happen automatically when you create their user account. [2]

If you tell me whether you’re trying to add them to a **program** as well (and which one), I can guide you through the right steps.

<details><summary>Sources</summary>

- [Add User to 121](https://manual.121.global/en/users/add-users/)
- [Add team members](https://manual.121.global/en/team/add-team-members/)
- [Remove team members](https://manual.121.global/en/team/remove-team-members-program/)
- [Support](https://manual.121.global/en/general/support-contact/)
- [Edit registration details](https://manual.121.global/en/registration/edit-pa-profile/)

</details>

`trace: a1ea36e3f65c6b6f71a54e4931f86d41`

## Conversation 12

`session: da5b0ad2-f4e4-4d25-ad1f-dea0bfaeab24`

**User:** nothing is wrking the hole day and my boss is angry with me

**Chatbot:**

I’m sorry you’re dealing with this. Based on 121’s guidance, an empty/blank page in the **Registrations** table can happen for a few reasons:

1) **No new registration imported**  
- The table will show **“No data”** if there’s nothing new to display. [1]

2) **No Internet connection (KOBO/registration form import)**  
- If you’re using KOBO Toolbox (or an alternative registration form) and you don’t have internet, the list may not import into 121.  
- To fix: connect to the internet → start the upload with KOBO → once done, **refresh the registration page**. [1]

3) **Filters are applied**  
- Clear any search/filter settings: make sure the filter/search bar is empty, and if you see a filter under the search bar, click **“Clear filters”** (top right). [1]

4) **Fully blank page (technical issue)**  
- If the page is completely blank and doesn’t show the registration column, it may be a technical issue—then you should contact support. [1]

If you tell me which page you’re seeing (Registrations or Payments) and whether it’s **“No data”**, **blank**, or showing **registrations but not the ones you expect**, I can point you to the most likely fix.

<details><summary>Sources</summary>

- [What if I see empty page](https://manual.121.global/en/registration/registration-list-empty/)
- [Support](https://manual.121.global/en/general/support-contact/)
- [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
- [Reset password](https://manual.121.global/en/general/reset-password/)
- [Timeline](https://manual.121.global/en/faq/timeline-121-integration/)

</details>

`trace: 79c8009f73eabc24fe0baba3bcb3b8c5`

**User:** the paymnt still not go out i dont know what to do anymor

**Chatbot:**

I understand—if the payment “still not go out,” the key is to check the **payment status** and then do the required next step.

### 1) Check the payment status
On the **Payments** page, payments move through statuses like **Pending approval**, **Approved**, and then **Processing** / **Successful** / **Failed**. [1]

### 2) If it’s **Pending approval**
- It can’t be sent yet.
- An **approver** must approve it. [1]

### 3) If it’s **Approved**
- The **Finance Manager** must **start the payment**.
- Open the approved payment card → click **Start payment** (top right).
- After starting, statuses change from **Approved** to **Processing**. [1]

### 4) If it’s **Processing** (manual payment via FSP portal)
- The transfer isn’t considered complete until the **reconciliation file** is imported into 121.
- Go to the specific payment page → **Import reconciliation data** → upload the **.csv** file → proceed.
- This updates statuses to **Successful / Pending / Failed**. [3]

### 5) If it’s **Failed**
- You can retry only after identifying the reason (wrong details, reconciliation format, registration changed details, or integration issue).
- Then use **Retry failed transaction(s)** (top right) and confirm **Retry transactions**. [2]

---

If you paste the **exact status** you see (e.g., *Pending approval*, *Approved*, *Processing*, *Failed*) and whether you’re using **manual export-import** or an **integrated FSP**, I’ll tell you the exact next click(s) to take.

<details><summary>Sources</summary>

- [Create and Approve payments](https://manual.121.global/en/payment/create-approve-payment/)
- [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
- [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
- [Payments page](https://manual.121.global/en/payment/payment/)
- [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)

</details>

`trace: dfab76de150c033d8054540d702e9c44`
