# Low-literacy seed conversations

- Endpoint: `https://support-chatbot-dev.azurewebsites.net`
- Manual: `121`
- User: `eval-seed-user-low-literacy`
- Generated: 2026-09-24 11:04 UTC

> [!NOTE]
> **User** turns are blue.

> [!TIP]
> **Chatbot** answers are green.

## Conversation 1

`session: 38b579fe-f0f5-4b8b-9b42-5dcf1ae7fa26`

> [!NOTE]
> **User**
>
> how i put the peple from my excel in the sistem

> [!TIP]
> **Chatbot**
>
> To put people from your Excel into the 121 system, you need to **import a registration list as a CSV file**. [1]
>
> 1) **Download the CSV template** from 121  
> - Open your **Program** → go to **Registrations**  
> - Click **Import new registrations** (right side) → **Download template CSV-file** [1]
>
> 2) **Fill in your data in the template**  
> - Open the template in Excel  
> - Copy your registration data into the template, making sure each value goes into the **correct column/label** [1]
>
> 3) **Upload and import the CSV**  
> - Go back to **Registrations** in your selected Program  
> - Click **Import new registrations**  
> - Choose your **matched CSV file** from your computer  
> - Click **Import file**  
> - Wait for the confirmation pop-up (it may take some time depending on the number of registrations) [1]
>
> If the import fails, check that your file is **correctly formatted and saved as .CSV**. [1]
>
> <details><summary>Sources</summary>
>
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
> - [Add team members](https://manual.121.global/en/team/add-team-members/)
>
> </details>
>
> `trace: 877eb91d6a106a80dec4e1b897b3e834`

> [!NOTE]
> **User**
>
> it dont work it give me a error

> [!TIP]
> **Chatbot**
>
> Sorry it’s not working. The manual says that if the **registration import is unsuccessful or shows an error message**, you should **check that your Excel file is correctly formatted and saved as .CSV**. [1]
>
> A few things to verify based on the import requirements:
> - Make sure you used the **121 template CSV** (downloaded from your Program) and that your data is in the **correct columns/labels**. [1]
> - Confirm the file you upload is saved as **.CSV** (not .xlsx or another format). [1]
>
> If you tell me the **exact error message** you see (or a screenshot), I can help you narrow down what to check next.
>
> <details><summary>Sources</summary>
>
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [What if I see empty page](https://manual.121.global/en/registration/registration-list-empty/)
>
> </details>
>
> `trace: aaa729f9c751f0b981bf8fbcb03de24e`

> [!NOTE]
> **User**
>
> wher can i find a exampel file to copy

> [!TIP]
> **Chatbot**
>
> You can get an example/template directly from 121:
>
> - Go to your **Program** → **Registrations** page  
> - Click **Import new registrations** (right side)  
> - Choose **Download template CSV-file** [1]
>
> That downloaded template is automatically generated based on your program registration form, and you can copy your registration data into it. [1]
>
> <details><summary>Sources</summary>
>
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Registrations page](https://manual.121.global/en/registration/registrations-page/)
>
> </details>
>
> `trace: 030bfc74663f0da662626ac8a0a0e7fa`

## Conversation 2

`session: 309069f6-720f-45a7-8ca0-a4a0289bb32d`

> [!NOTE]
> **User**
>
> the money did not arive to the famlies why

> [!TIP]
> **Chatbot**
>
> I can help with 121 payment troubleshooting. In 121, when money doesn’t arrive to families, it’s usually because the payment ended up **Failed** (or is still **Pending/Processing**).
>
> ### 1) Check the payment status
> - **Failed**: the transaction failed and registrations **have not received any payments**. [1][2]
> - **Pending / Processing**: the payment is waiting for reconciliation/confirmation, so it may not be delivered yet. [1][2]
>
> ### 2) If it’s **Failed**, check the reason
> On the **Payments** page, open the specific payment and filter the registration list by **Transaction status = Failed**. Then check the **Reason** column. Common reasons include: [5]
> - **Incorrect payment details** (e.g., full name, phone number, bank account number, ID number, or location/KYC mismatch)
> - **Wrong format of the reconciliation file** (for manual payments)
> - **Registration changed payment details** (so the FSP can’t match them)
> - **Integration issue (FSP–121)** (if you use an integrated FSP)
>
> ### 3) Fix and retry (if applicable)
> If you identify the issue, you can **retry failed transactions**:
> - Go to the **Payments** page → open the payment round
> - Select the registrations with **failed** status
> - Click **Retry failed transaction(s)** and confirm **Retry transactions** [5]
>
> If you tell me what you see for the payment status (**Failed**, **Pending**, or **Processing**) and (if available) the **Reason** shown in the failed list, I can guide you on the next step.
>
> <details><summary>Sources</summary>
>
> - [Create and Approve payments](https://manual.121.global/en/payment/create-approve-payment/)
> - [Payments page](https://manual.121.global/en/payment/payment/)
> - [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
> - [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
> - [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
>
> </details>
>
> `trace: 5eb0b4bc00fe9ef4461c9b5f338435bf`

> [!NOTE]
> **User**
>
> how i send it agan to only those ones

> [!TIP]
> **Chatbot**
>
> To retry **only the registrations whose payments failed**:
>
> 1. Go to the **Payments** page and open the **specific payment round**. [1]  
> 2. In the transaction list, **select only the registrations** that show **Failed**. [1]  
> 3. Click **Retry failed transaction(s)** (top right). [1]  
> 4. Click **Approve** → **Retry transactions**. [1]  
>
> After that, 121 will automatically retry for the selected registrations identified with **failed payment** status, and their payment status will update. [1]
>
> <details><summary>Sources</summary>
>
> - [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
> - [Payment statuses in 121](https://manual.121.global/en/payment/list-status-payment-page/)
> - [Decline registrations](https://manual.121.global/en/registration/registration-reject-pa/)
> - [End payments](https://manual.121.global/en/payment/end-payments/)
> - [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
>
> </details>
>
> `trace: 534c4ff0571f3d35567da2ab672f8f15`

## Conversation 3

`session: ae98c8da-d358-45ed-8dd2-683686e0b4aa`

> [!NOTE]
> **User**
>
> i want my colega to see the projekt to how i do

> [!TIP]
> **Chatbot**
>
> To let your colleague see the project, you need to check their **role/permissions** on the **Program Team**.
>
> - Go to your program **Settings** page → **Program Team** tab. [3][4]  
> - If you have the permission, you can use the **pencil** to edit roles, then **select/deselect** the roles for the user and **Save changes**. [2]  
> - Users who are not given edit permissions will typically have **View** permissions, which lets them only see the program. [1][3]
>
> If you tell me what you want your colleague to do (only view, or also edit/change settings), I can point you to the right place in the portal.
>
> <details><summary>Sources</summary>
>
> - [Program Info & Settings](https://manual.121.global/en/Settings/project-info/)
> - [Change team members roles](https://manual.121.global/en/team/change-team-roles-program/)
> - [Program Settings page](https://manual.121.global/en/Settings/project-settings-page/)
> - [Manage your program team](https://manual.121.global/en/team/team-page/)
> - [Setting-up 121 Platform](https://manual.121.global/en/faq/setting-up-121-platform/)
>
> </details>
>
> `trace: b594849b817183c45d126e82d5b00de3`

> [!NOTE]
> **User**
>
> can she also chang the amont or only look

> [!TIP]
> **Chatbot**
>
> It depends on her **role/permissions**.
>
> - **Only Program Admin and users with Program Update permissions** can change **budget/payment settings** (like the amount). [5]  
> - If she only has **View** permission, she can **look** but not change the amount. [5]
>
> If you want, tell me what role(s) she currently has on the **Program Team** page, and I can help you confirm whether she should be able to edit the amount. [3][5]
>
> <details><summary>Sources</summary>
>
> - [Data Changes Overview](https://manual.121.global/en/monitoring/data-changes/)
> - [Change team members roles](https://manual.121.global/en/team/change-team-roles-program/)
> - [Program Settings page](https://manual.121.global/en/Settings/project-settings-page/)
> - [Program Info & Settings](https://manual.121.global/en/Settings/project-info/)
> - [Budget & Payment settings](https://manual.121.global/en/Settings/payment-budget-settings/)
>
> </details>
>
> `trace: f32057b55d23cfe53b64f006dc868eed`

## Conversation 4

`session: 6f7d72d7-e8b3-463d-a63b-620868285e0d`

> [!NOTE]
> **User**
>
> how i colect the info from the famlies wen there is no internett in the village

> [!TIP]
> **Chatbot**
>
> If there’s no internet in the village, you can still collect beneficiary information offline using **Kobo Collect** (or another supported offline data collection app). Internet is only required when you need to **sync** the collected data back to the 121 portal—so you collect offline first, then sync once you have connectivity. [1]
>
> When you’re ready to sync:
> - Make sure the device has internet/mobile data available.
> - Then upload/sync so the registrations appear in 121. [1][3]
>
> If you’re doing **offline verification** (not just registration), the process is similar: you prepare an offline Kobo verification form, collect data in the field offline, then connect to the internet afterward to upload all collected forms so the updates reflect in 121. [5]
>
> <details><summary>Sources</summary>
>
> - [Setting-up 121 Platform](https://manual.121.global/en/faq/setting-up-121-platform/)
> - [Timeline](https://manual.121.global/en/faq/timeline-121-integration/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [Step-by-Step Guide - Prepare your CVA Program](https://manual.121.global/en/general/prepare-your-project/)
> - [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)
>
> </details>
>
> `trace: 9d6ad27758851e9de0b16856939d89da`

> [!NOTE]
> **User**
>
> and wen the internet come back what i must do

> [!TIP]
> **Chatbot**
>
> When the internet comes back, you must **upload/sync the data you collected offline** so it updates in the 121 Platform.
>
> - **For offline verification (Kobo forms):** connect your devices to the internet and make sure you **upload ALL collected Kobo forms**, then **check that all changes are correctly reflected** on the 121 platform. [1]
>
> - **For registrations collected with Kobo:** the Kobo integration uploads registrations to 121 **only when an internet connection is established** (real-time once connected). [2]
>
> If you tell me whether you mean **registration** or **verification**, I can point you to the exact “what to do next” steps for that case.
>
> <details><summary>Sources</summary>
>
> - [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [Step-by-Step Guide - Prepare your CVA Program](https://manual.121.global/en/general/prepare-your-project/)
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Timeline](https://manual.121.global/en/faq/timeline-121-integration/)
>
> </details>
>
> `trace: 54c55295d366a780742425f5f45982b5`

## Conversation 5

`session: f315f95b-f620-40b0-a5dd-57bd4a968f8a`

> [!NOTE]
> **User**
>
> i cant go inside the sistem it say my paswrd is wrong

> [!TIP]
> **Chatbot**
>
> Sorry you’re running into that. Here are the 121 steps to regain access:
>
> 1) **Double-check your login details**
> - Make sure you enter the **email address exactly as in the login email** (it’s case sensitive) and use the **password that was shared in your email**. [1]
>
> 2) **If you forgot the password: reset it**
> - Contact your **121 User Manager** to reset your password via the **Users** page.
> - The User Manager will use the **three dots** on your user row → **Reset Password** → **Confirm**.
> - An **email** will be sent to you with instructions to set a new password. [2]
>
> 3) **If you still can’t log in**
> - Contact support at **support@121.global**. [2]
>
> If you tell me whether your organization uses **SSO (Microsoft login)**, I can point you to the right login method. [1]
>
> <details><summary>Sources</summary>
>
> - [Log In](https://manual.121.global/en/general/logging-in/)
> - [Reset password](https://manual.121.global/en/general/reset-password/)
> - [Add User to 121](https://manual.121.global/en/users/add-users/)
> - [Change current password](https://manual.121.global/en/general/change-current-password/)
> - [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
>
> </details>
>
> `trace: 42cf4e013759be73aba16dfa546d1ca0`

> [!NOTE]
> **User**
>
> who can giv me a new paswrd

> [!TIP]
> **Chatbot**
>
> A new password can be provided/reset by your **121 User Manager** (they can reset your password from the **Users** page, and you’ll receive an email to set a new one). [4]
>
> If you’re not able to log in even after that, you can contact **support@121.global**. [4]
>
> <details><summary>Sources</summary>
>
> - [Add User to 121](https://manual.121.global/en/users/add-users/)
> - [Change current password](https://manual.121.global/en/general/change-current-password/)
> - [Log In](https://manual.121.global/en/general/logging-in/)
> - [Reset password](https://manual.121.global/en/general/reset-password/)
> - [Users page](https://manual.121.global/en/users/users-roles-page/)
>
> </details>
>
> `trace: 4d4ed5239a0ff22a37c81375ac9d3f65`

## Conversation 6

`session: 6d1ce1df-2981-4fac-a65e-a865bf74c594`

> [!NOTE]
> **User**
>
> some famlies are two time in my list

> [!TIP]
> **Chatbot**
>
> It sounds like you may have duplicate registrations in your list. In 121, duplicates can be checked and resolved from the **Deduplication** area, and duplicates are identified using **unique criteria** (commonly phone number or ID number) configured in your Kobo form. [2]
>
> To resolve duplicates:
> 1. Go to the **Registrations** page.
> 2. Use **Manage the table** → select **Duplicates** → **Apply** (this shows a Duplicates column). [2]
> 3. In the **Duplicates** column, use the filter icon and filter on **Duplicate** to show only the duplicated entries. [2]
> 4. Open a duplicated registration (click **Reg #** or **Name**) to see the **“Duplicated with”** banner and the matching field. [2]
> 5. Then choose one of the actions:
>    - **Edit** the value in the registration profile (and click **Save** with a reason), or
>    - **Decline** the duplicate (requires a reason), or
>    - **Ignore the duplicate** (if your SOPs allow it). [2]
>
> Note: duplicates can only be checked **within a single project/program** (not across different programs). [2]
>
> If you tell me which field is triggering the duplicate (e.g., phone number vs ID), I can point you to the most appropriate option (ignore vs edit vs decline) based on the platform guidance.
>
> <details><summary>Sources</summary>
>
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Deduplication](https://manual.121.global/en/registration/registration-deduplication/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Registrations page](https://manual.121.global/en/registration/registrations-page/)
> - [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
>
> </details>
>
> `trace: 5a8710be690770cff748bfc03de690fe`

> [!NOTE]
> **User**
>
> how i delet the one that is dubbel

> [!TIP]
> **Chatbot**
>
> In 121 you don’t “delete” a duplicate record directly. Instead, you resolve it in the **Deduplication** workflow by either **declining** it (removes it from being treated as a valid registration) or **ignoring** it, depending on your SOPs. [1]
>
> ### To decline the duplicate registration
> 1. Go to the **Registrations** page and filter to show duplicates (Duplicates column → filter on **Duplicate**). [1]
> 2. Find the duplicate and open its profile (click **Reg #**). [1]
> 3. On the top left, click **Action** → **Decline**. [1]
> 4. **Approve** the action (only if you’re sure). [1]
> 5. Enter a **reason for declining** the beneficiary, then confirm. [1]
>
> ### If you meant “remove it from the list”
> If your SOP allows it, you can also use **Ignore the duplicate** (Action → **Ignore the duplicate** → Approve). [1]
>
> If you tell me whether your duplicates are based on **phone number** or **ID number**, I can help you choose between **Decline** vs **Ignore**.
>
> <details><summary>Sources</summary>
>
> - [Deduplication](https://manual.121.global/en/registration/registration-deduplication/)
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Registrations page](https://manual.121.global/en/registration/registrations-page/)
> - [Validate registrations](https://manual.121.global/en/registration/registration-validate-pa/)
> - [Edit registration details](https://manual.121.global/en/registration/edit-pa-profile/)
>
> </details>
>
> `trace: 805eff3b8b8c43a5c35a3228ca85acd4`

## Conversation 7

`session: 238172ba-6733-48b6-85cf-bd56bd633ad8`

> [!NOTE]
> **User**
>
> i want to send a sms to all the famlies in my list

> [!TIP]
> **Chatbot**
>
> To send an SMS to all families in your registrations list, you can use the **“Send a message to registrations”** option on the **Registrations** page (this sends outbound messages via **SMS or WhatsApp**). [1]
>
> Before you can send SMS, you must:
> 1) **Create a Twilio account** and have it linked to your 121 Platform instance (121 support helps with the technical integration). [1]  
> 2) Ensure you have **sufficient messaging credits/funds** in Twilio—otherwise SMS/WhatsApp will fail. [1]
>
> Then, in the **Registrations page**:
> - Select the registrations you want to message (for “all families”, select all registrations in the list/table).
> - Click the **Message** icon/button at the top of the page.
> - Choose **Custom message** (or a **predefined template**, if you have one set up).
> - (Optional) Use **variables** with **@** to insert fields from each registration automatically (e.g., @name, @amount). [1]
>
> If you tell me whether you want to use a **custom message** or a **predefined template**, I can guide you through the exact clicks for that option.
>
> <details><summary>Sources</summary>
>
> - [Sending messages](https://manual.121.global/en/registration/sending-messages/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Decline registrations](https://manual.121.global/en/registration/registration-reject-pa/)
> - [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
>
> </details>
>
> `trace: 0cb258ba2abc63495f201361ce925177`

> [!NOTE]
> **User**
>
> can i writ there name inside the mesage

> [!TIP]
> **Chatbot**
>
> Yes. You can insert each person’s name in the message using a **variable**.
>
> In the **Custom message** editor:
> - Type **@**
> - Select the field for the name (e.g., **@name**)
> - The message will automatically pull the name from each registration and adjust per person. [1]
>
> <details><summary>Sources</summary>
>
> - [Sending messages](https://manual.121.global/en/registration/sending-messages/)
> - [Decline registrations](https://manual.121.global/en/registration/registration-reject-pa/)
> - [Include registrations](https://manual.121.global/en/registration/inclusion-in-program/)
> - [Edit registration details](https://manual.121.global/en/registration/edit-pa-profile/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
>
> </details>
>
> `trace: 8fa3c577184e7ccd6fca1706b0468054`

## Conversation 8

`session: 123ff6a4-3860-43ad-ab8d-e12c94019637`

> [!NOTE]
> **User**
>
> how much money evry famly get and can i chang that

> [!TIP]
> **Chatbot**
>
> I'm here to help with questions about 121, so I can't help with that one.  
> Is there something about 121 I can help you with?
>
> `trace: 9a7f806a3770a9971f237508e47dd9c5`

> [!NOTE]
> **User**
>
> if the famly have many childrin do they get more

> [!TIP]
> **Chatbot**
>
> I don't have the right information to answer your question. Could you share more details with me?
>
> <details><summary>Sources</summary>
>
> - [Financial Service Providers (FSP)](https://manual.121.global/en/faq/financial-service-provider/)
> - [Payments page](https://manual.121.global/en/payment/payment/)
> - [End payments](https://manual.121.global/en/payment/end-payments/)
> - [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
> - [Budget & Payment settings](https://manual.121.global/en/Settings/payment-budget-settings/)
>
> </details>
>
> `trace: 315a31dd5653369ae4e0d0bbaaddb3e8`

## Conversation 9

`session: 82fd8dfb-bae7-406d-8846-949c247fb9af`

> [!NOTE]
> **User**
>
> i give the cash with my hand to the peple how i writ it in the sistem after

> [!TIP]
> **Chatbot**
>
> It sounds like you’re asking how to record **cash you gave by hand** in the 121 system.
>
> From the 121 manual pages I have here, the “Payments” workflow is specifically about **processing payments through a Financial Service Provider (FSP)**—either:
> - **Manual payment via an FSP portal** (export payment instructions, then reconcile using a CSV reconciliation file), or
> - **Instant/direct payments with an integrated FSP** (status updates automatically). [1][2][3][5]
>
> I don’t have instructions in the provided documents for how to record **cash-in-hand / manual cash distribution without an FSP**.
>
> Can you tell me which one matches your situation?
> 1) Are you using an **FSP portal** (manual export/import + reconciliation CSV)? [1][5]  
> 2) Or do you have an **integrated FSP** (instant payment)? [4]  
> 3) Or is this **cash given directly by staff** with **no FSP** involved?
>
> <details><summary>Sources</summary>
>
> - [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
> - [Create and Approve payments](https://manual.121.global/en/payment/create-approve-payment/)
> - [Payments page](https://manual.121.global/en/payment/payment/)
> - [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
> - [Reconcile manual payments](https://manual.121.global/en/payment/manual-payment-reconciliation/)
>
> </details>
>
> `trace: 660713c4c1dacfab9b8485bbbe3cb75a`

> [!NOTE]
> **User**
>
> what colums i must put in that file

> [!TIP]
> **Chatbot**
>
> For manual payment reconciliation in 121, the file you import must be a **.csv** and it must include the **required columns** from the **template** you download in 121. [1][2]
>
> In the documents I have, the exact column names beyond the payment status labels aren’t listed—so the safest answer is:
>
> 1) Go to **Payments** → select the specific **payment round**  
> 2) Click **Import Reconciliation data** → **Download template**  
> 3) Edit that template and keep all required columns, then save as **.csv** and import it back. [1][2]
>
> Also, you must overwrite the payment status values to match 121 exactly: [1][2]  
> - **Completed** → `success`  
> - **Failed** → `error`  
> - **Pending** → `waiting`  
>
> If you tell me which FSP you used (or share the header row from your template), I can help you confirm the columns you should keep.
>
> <details><summary>Sources</summary>
>
> - [Reconcile manual payments](https://manual.121.global/en/payment/manual-payment-reconciliation/)
> - [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
> - [Payments page](https://manual.121.global/en/payment/payment/)
> - [Payment statuses in 121](https://manual.121.global/en/payment/list-status-payment-page/)
> - [Payment reporting and activty](https://manual.121.global/en/payment/payment-reporting/)
>
> </details>
>
> `trace: 53e825c411d13728c1699c2f708cb08f`

## Conversation 10

`session: c9c65f58-285a-4c13-ba78-bfe63f0c5537`

> [!NOTE]
> **User**
>
> helo good morning

> [!TIP]
> **Chatbot**
>
> Good morning! 👋 How can I help you with questions about 121 today?
>
> `trace: f8d2317cd23e751375b4b3bab22f5b44`

> [!NOTE]
> **User**
>
> how i take the list of peple to my computer

> [!TIP]
> **Chatbot**
>
> To take a list of people to your computer, you can **export registrations** from the **Registrations** page in 121. [2]
>
> 1. Open your **Program** → go to the **Registrations** page.  
> 2. (Optional) Use **Settings** to add the columns you want to see in the table, then click **Apply**. [2]  
> 3. Select the registrations you want to export.  
> 4. Click **Export** (top right of the table) → choose **Export selected registrations**. [2]  
> 5. Choose the file format (**Excel or CSV**). The file will be generated and saved in your **Downloads** folder. [2]
>
> If you tell me whether you want **Excel or CSV**, I can point you to the exact option to choose.
>
> <details><summary>Sources</summary>
>
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)
>
> </details>
>
> `trace: 1d084ec6c9753146f517fc7d58a648c4`

> [!NOTE]
> **User**
>
> ok tank you very much

> [!TIP]
> **Chatbot**
>
> You’re welcome! If you have any more questions about 121, feel free to ask.
>
> <details><summary>Sources</summary>
>
> - [Import Registrations with excel](https://manual.121.global/en/registration/registration-import-list/)
> - [Export registration lists](https://manual.121.global/en/registration/registration-export-list/)
> - [Import Mass Data Changes](https://manual.121.global/en/registration/import-data-changes/)
> - [Registration with KOBO form](https://manual.121.global/en/registration/registration-automatic-import-kobo/)
> - [Offline Verification with 121 and Kobo Toolbox](https://manual.121.global/en/verification/offline-verification/)
>
> </details>
>
> `trace: 7a2c074211102b0eb65949e6e893fa39`

## Conversation 11

`session: ffd9a6b6-7211-4d23-9a7d-5a6b487f4e0c`

> [!NOTE]
> **User**
>
> waht is the wether in nairobi tomorow

> [!TIP]
> **Chatbot**
>
> I'm here to help with questions about 121, so I can't help with that one.
> Is there something about 121 I can help you with?
>
> `trace: 1ef78f7b5e4b9f7f317d45b2bbc26285`

> [!NOTE]
> **User**
>
> ok sory. can u tel me how i add a new persn

> [!TIP]
> **Chatbot**
>
> Sure—on 121 you add a new person by creating a **user account** first, then (optionally) adding them to the **specific program(s)** they should access.
>
> ### 1) Add the user account (Users page)
> - Open the left menu and select **Users**. [2]
> - Click **Add new users** (top right). [2]
> - Enter the **Name(s)** and **email address**.
> - Click **Submit**. [2]
>
> An email will be automatically sent to the address you enter with a link for the user to access the 121 platform. Make sure the email is correct. [2]
>
> ### 2) Add them to a program (Program Team)
> - Go to the program’s **Settings** page.
> - Under **Program Team**, click the **pencil** icon.
> - Select **+ Add user to team**.
> - Search by the user’s **email** and select them.
> - Under **Assign Roles**, tick the role(s) you want.
> - Click **Submit**. [1]
>
> **Note:** Adding a user account does not automatically assign them to programs—each program assignment must be done separately. [2]
>
> If you tell me whether you’re adding them to a program already (and which one), I can guide you through the exact steps for that screen.
>
> <details><summary>Sources</summary>
>
> - [Add team members](https://manual.121.global/en/team/add-team-members/)
> - [Add User to 121](https://manual.121.global/en/users/add-users/)
> - [Edit registration details](https://manual.121.global/en/registration/edit-pa-profile/)
> - [Change team members roles](https://manual.121.global/en/team/change-team-roles-program/)
> - [Manage your program team](https://manual.121.global/en/team/team-page/)
>
> </details>
>
> `trace: 992c802140cb5e330342baef25378384`

## Conversation 12

`session: fde8cd10-b26c-46c3-9fd6-81ef6a2170b8`

> [!NOTE]
> **User**
>
> nothing is wrking the hole day and my boss is angry with me

> [!TIP]
> **Chatbot**
>
> I’m sorry you’re dealing with this. Based on the 121 manual, if the **Registrations** page is empty or not showing data, the most common causes are:
>
> 1) **No new registration imported** → the table will show **“No data”**. [1]  
> 2) **No internet connection** (especially if you’re using KOBO Toolbox/offline registration) → you must connect to the internet, start the upload with KOBO, then **refresh the registration page**. [1]  
> 3) **Filters/search are applied** → clear them (click **Clear filters** on the top right). [1]  
> 4) If the page is **fully blank** and doesn’t even show the registration column, it may be a **technical issue** → contact support. [1]
>
> If you tell me which page is blank/empty (Registrations? Payments? something else) and what you see (e.g., “No data” vs fully blank), I can guide you to the right check.  
>
> For urgent technical issues, you can contact support via **instant channels** or email **support@121.global** (and copy your Account Manager). [2]
>
> <details><summary>Sources</summary>
>
> - [What if I see empty page](https://manual.121.global/en/registration/registration-list-empty/)
> - [Support](https://manual.121.global/en/general/support-contact/)
> - [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
> - [Reset password](https://manual.121.global/en/general/reset-password/)
> - [Timeline](https://manual.121.global/en/faq/timeline-121-integration/)
>
> </details>
>
> `trace: e2b6f385bb011fd23748dd1bf365f47d`

> [!NOTE]
> **User**
>
> the paymnt still not go out i dont know what to do anymor

> [!TIP]
> **Chatbot**
>
> I understand—let’s narrow it down using the payment statuses in 121.
>
> ### 1) Check the payment status
> Go to **Payments** and open the specific payment round. The status determines what you should do next:
>
> - **PENDING APPROVAL**: it can’t go out yet—**approvers must approve** it. [1]  
> - **APPROVED**: it’s ready to be sent—**a Finance Manager must start the payment** (top right **Start payment**). [1]  
> - **PROCESSING** (manual payment): it’s waiting for **reconciliation import**—you must **import the reconciliation file (.csv)** into the same payment page to update the status. [1][3]  
> - **FAILED**: the transaction didn’t go out—check the **Reason** and then **retry failed transaction(s)** after fixing the cause. [2]
>
> ### 2) If it’s **FAILED**
> - Filter the registration list to **Failed** and read the **Reason** column. [2]  
> - Then use **Retry failed transaction(s)** (top right) and confirm **Retry transactions**. [2]
>
> ### 3) If it’s **PROCESSING** (manual export/import)
> - Make sure the reconciliation file you import is **.csv** and uses the required status mapping:  
>   **Completed → success**, **Failed → error**, **Pending → waiting**. [3]  
> - Then click **Import reconciliation data** on the specific payment page and upload the file. [3]
>
> If you reply with the **exact status you see** (Pending approval / Approved / Processing / Failed) and whether you’re using **manual payment via FSP portal** or an **integrated FSP**, I’ll tell you the next exact step.
>
> <details><summary>Sources</summary>
>
> - [Create and Approve payments](https://manual.121.global/en/payment/create-approve-payment/)
> - [Failed and Retry payments](https://manual.121.global/en/payment/failed-retry-payment/)
> - [Manual payment instructions (excel export)](https://manual.121.global/en/payment/issue-payment-fsp-portal/)
> - [Payments page](https://manual.121.global/en/payment/payment/)
> - [Payments with integrated FSP](https://manual.121.global/en/payment/payment-integrated-fsp/)
>
> </details>
>
> `trace: 7bdbfd38dbbb69e6a515ccd854bce09f`
