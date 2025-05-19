### Step 5: n8n Workflow Setup

n8n will serve as your automation platform for capturing inputs, processing them with GPT-4, and storing the results in Supabase. You will use your self-hosted n8n installation at `do.treesurgeonhereford.com`.

**Initial Workflow: Daily Log Processing & Supabase Insertion**

This first workflow will handle manual text input, parse it for daily log and gym information, and then store this data in your Supabase tables (`daily_logs` and conditionally `gym_logs`).

**Workflow Nodes & Configuration:**

1.  **Start Node (Manual Trigger):**

    - **Type:** `Start` (Default manual trigger)
    - **Purpose:** To manually initiate the workflow for testing.
    - **Input (when executing manually):** Provide JSON with two keys:
      - `text_input`: (String) Your daily log text (e.g., "Mood 8/10. Gym: bench press 3x5 80kg. Work: coded for 2 hours on project X.").
      - `user_uuid`: (String) The UUID of your user from the Supabase `auth.users` table.

2.  **OpenAI Node ("Parse Log with OpenAI"):**

    - **Type:** `OpenAI Chat Model`
    - **Purpose:** Sends the `text_input` to an OpenAI model (e.g., GPT-4o) to extract structured data.
    - **Credentials:** Your configured OpenAI credential.
    - **Model:** `gpt-4o` (or `gpt-4-turbo`).
    - **Response Format/JSON Mode:** Enable "JSON Mode" (or equivalent parameter like `responseFormat: "jsonFormat"`).
    - **Messages:**
      - **System Prompt:** (Use the detailed system prompt previously provided that defines the target JSON schema, including fields like `daily_free_text`, `daily_mood_score`, `gym_exercise_name`, etc., and instructs the AI to use `null` for missing values and output only JSON).
      - **User Prompt (Expression):** `{{ $('Start').item.json.text_input }}`

3.  **Set Node ("Prepare Data"):**

    - **Type:** `Set`
    - **Purpose:** Consolidates data for subsequent Supabase nodes.
    - **Mode:** "Keep Only Set".
    - **Values to Add:**
      - `user_uuid` (String, Expression): `{{ $('Start').item.json.user_uuid }}`
      - `current_date` (String, Expression): `{{ new Date().toISOString().split('T')[0] }}` (Formats as YYYY-MM-DD).
      - `parsed_log_data` (JSON, Expression): `{{ $('Parse Log with OpenAI').item.json }}` (Test this: if OpenAI's JSON output is a string within `choices[0].message.content`, use `JSON.parse($('Parse Log with OpenAI').item.json.choices[0].message.content)` instead).

4.  **Supabase Node ("Insert daily_log"):**

    - **Type:** `Supabase`
    - **Purpose:** Inserts general daily log information into the `daily_logs` table.
    - **Credentials:** Your configured Supabase credential.
    - **Resource:** `Table`, **Operation:** `Insert`
    - **Table Name:** `daily_logs`
    - **Columns (Map with expressions based on 'Prepare Data' output):**
      - `user_id`: `{{ $('Prepare Data').item.json.user_uuid }}`
      - `date`: `{{ $('Prepare Data').item.json.current_date }}`
      - `free_text`: `{{ $('Prepare Data').item.json.parsed_log_data.daily_free_text }}`
      - `mood_score`: `{{ $('Prepare Data').item.json.parsed_log_data.daily_mood_score }}`
      - (Map other `daily_logs` fields like `energy_level`, `stress_level`, `sleep_hours`, `sleep_quality` similarly).

5.  **If Node ("Gym Data Exists?")**

    - **Type:** `If`
    - **Purpose:** Checks if gym exercise information was extracted.
    - **Condition:**
      - **Value 1 (Expression):** `{{ $('Prepare Data').item.json.parsed_log_data.gym_exercise_name }}`
      - **Operation:** "Is Not Empty" (or similar).
    - Connect the 'true' output of this node to the "Insert gym_log" node.

6.  **Supabase Node ("Insert gym_log"):**
    - **Type:** `Supabase`
    - **Purpose:** Inserts gym-specific data into the `gym_logs` table (only if the If node condition is met).
    - **Credentials:** Your configured Supabase credential.
    - **Resource:** `Table`, **Operation:** `Insert`
    - **Table Name:** `gym_logs`
    - **Columns (Map with expressions based on 'Prepare Data' output):**
      - `user_id`: `{{ $('Prepare Data').item.json.user_uuid }}`
      - `date`: `{{ $('Prepare Data').item.json.current_date }}`
      - `exercise_name`: `{{ $('Prepare Data').item.json.parsed_log_data.gym_exercise_name }}`
      - `sets`: `{{ $('Prepare Data').item.json.parsed_log_data.gym_sets }}`
      - (Map other `gym_logs` fields like `reps`, `weight`, `duration_minutes`, `notes` similarly).

**Next Steps for n8n:**

- Replace the manual "Start" node with a "Telegram Trigger" node to capture messages from your Telegram bot.
- Add error handling to the workflow.
- Expand the workflow to parse and store data for other log types (jiu-jitsu, nutrition, career, finance) by adding more conditional logic (If nodes) and Supabase Insert nodes, potentially with more specific OpenAI prompts if needed for those structures.
- Implement a step to generate embeddings for the `free_text` and store them (either in Supabase using pgvector or in ChromaDB via an HTTP request to a Python API you'll build).

**Schemas for Additional Tables (for future workflow expansion):**

- **jiujitsu_logs**

  - id (UUID, PK)
  - user_id (UUID)
  - date (DATE)
  - session_type (TEXT)
  - techniques_trained (TEXT[])
  - rolls_count (INTEGER)
  - roll_partners (TEXT[])
  - performance_rating (INTEGER)
  - notes (TEXT)
  - created_at (TIMESTAMP)

- **nutrition_logs**

  - id (UUID, PK)
  - user_id (UUID)
  - date (DATE)
  - meal_type (TEXT)
  - meal_time (TIME)
  - foods (TEXT[])
  - calories (INTEGER)
  - protein_grams (NUMERIC)
  - carbs_grams (NUMERIC)
  - fat_grams (NUMERIC)
  - notes (TEXT)
  - created_at (TIMESTAMP)

- **career_logs**

  - id (UUID, PK)
  - user_id (UUID)
  - date (DATE)
  - work_hours (NUMERIC)
  - productivity_rating (INTEGER)
  - tasks_completed (TEXT[])
  - achievements (TEXT[])
  - challenges (TEXT[])
  - goals (TEXT[])
  - notes (TEXT)
  - created_at (TIMESTAMP)

- **financial_transactions**

  - id (UUID, PK)
  - user_id (UUID)
  - date (DATE)
  - amount (NUMERIC)
  - currency (TEXT)
  - category (TEXT)
  - description (TEXT)
  - source (TEXT)
  - transaction_type (TEXT)
  - created_at (TIMESTAMP)

- **investment_logs**

  - id (UUID, PK)
  - user_id (UUID)
  - date (DATE)
  - asset_name (TEXT)
  - asset_type (TEXT)
  - transaction_type (TEXT)
  - quantity (NUMERIC)
  - price_per_unit (NUMERIC)
  - total_amount (NUMERIC)
  - currency (TEXT)
  - platform (TEXT)
  - notes (TEXT)
  - created_at (TIMESTAMP)

- **embeddings** (if using Supabase for vector search)
  - id (UUID, PK)
  - user_id (UUID)
  - content_type (TEXT)
  - content_id (UUID)
  - embedding (VECTOR(1536))
  - created_at (TIMESTAMP)

These schemas will guide you when expanding your n8n workflow to cover all aspects of your life data.
