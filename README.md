# say-less

Captures the YouTube zeitgeist by collecting links to videos that can be fed into NotebookLM.

## Prerequisites

- Have a [Google Cloud Platform](https://cloud.google.com) account
- Have `YouTube data API v3` enabled on the account
  - API & Services > Library > Search "Youtube data api v3" > enable
- Have `Google Sheets API` enabled on the account
  - API & Services > Library > Search "google sheets api" > enable
- Created a [Service Account](https://cloud.google.com/iam/docs/service-account-overview) in Google Cloud Platform to utilize the APIs
  - IAM & Admin > Service Accounts > Create Service Account
  - Provide a name and description for the account
  - Record the email address for the service account
  - Save the `pc-api-.*.json` file
- Created a new Google Sheet and retrieved the id of the sheet from the URL
  - example: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/`
- Shared the Google Sheet with the service account
  - Share Button > `Add peoples, groups, and calendar events` textbox > enter email address of service account > Assign as editor.
- Have the tags of the YouTube channels to follow
  - Found in the YouTube URL when clicking on a channel's icon
  - example: `https://www.youtube.com/{CHANNEL_TAG}`

## Initial setup

[install uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) for virtual environment and package management.

```
brew install uv
```

Install dependencies

```
uv sync
```

Create a `./local` directory

```
mkdir local
```

Create a `./local/config.json` file

```
{
    "spreadsheet": {
        "id": "SPREADSHEET_ID"
    },
    "channel_handles" : [
        "@ChannelTag",
    ]
}
```

Copy `pc-api-.*.json` file into `./local/secrets/service-account.json`

```
cp ~/Downloads/pc-api-.*.json ./local/secrets/service-account.json
```

## Usage

Execute the python script

```
uv run say-less.py gather --configPath "./local/configs.json" --serviceAccountPath "./local/secrets/service-account.json"
```
