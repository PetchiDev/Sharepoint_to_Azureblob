# SharePoint to Azure Blob Sync: Prerequisites (Power Automate Implementation)

This document outlines the requirements to build the synchronization system using **Microsoft Power Automate** (instead of Azure Functions). This is a low-code approach.

## 1. Licensing Prerequisites
Unlike the Azure Functions approach, Power Automate requires a specifically licensed user or environment:

### A. Power Automate License
- **Requirement**: A license that includes **Premium Connectors**.
- **Options**: 
    - Power Automate "Per User" plan.
    - Power Automate "Per Flow" plan.
    - Office 365 license with Power Automate Premium add-on.
- *Reason*: The "Azure Blob Storage" connector is a **Premium** connector.

---

## 2. Azure Environment Prerequisites
You still need the destination storage in Azure:

### A. Azure Storage Account
- **Name**: `stattorneysync` (or preferred unique name).
- **Container**: Create a container (e.g., `attorneys`) where files will be stored.

### B. Access Key
- You will need the **Access Key** or **Connection String** from the Azure Storage Account to create the connection in Power Automate.

---

## 3. SharePoint Configuration
- **Access**: The user building the flow (or the Service Account) must have **Site Member** or **Site Owner** access to the SharePoint site and the specific document library.
- **Document Library Name**: e.g., `Attorney_Documents`.

---

## 4. Power Automate Connectors
The flow will use the following two connectors:

| Connector | Type | Purpose |
| :--- | :--- | :--- |
| **SharePoint** | Standard | To detect when a file is created or modified. |
| **Azure Blob Storage** | **Premium** | To upload the file content to your Azure container. |

---

## 5. Implementation Summary (How it works)
If using Power Automate, the setup involves:
1. **Trigger**: "When a file is created or modified (properties only)" (SharePoint).
2. **Action**: "Get file content" using the Identifier from the trigger (SharePoint).
3. **Action**: "Create blob" using the Name and Content from the previous steps (Azure Blob Storage).

---

## Comparison: Azure Functions vs. Power Automate

| Feature | Azure Functions | Power Automate |
| :--- | :--- | :--- |
| **Cost** | 100% Free (Free Tier) | Requires Premium License (~$15/user/mo) |
| **Configuration** | Code-based (Python) | UI-based (Low-code/No-code) |
| **Permissions** | Azure AD App Registration | User-based Connection |
| **Maintenance** | Auto-renewal via code | Managed by Microsoft |

---

## Recommendation
- If the client wants the **Lowest Cost (Free)**: Use the **Azure Functions** approach.
- If the client wants the **Easiest Maintenance (No-code)**: Use **Power Automate** (requires license).
