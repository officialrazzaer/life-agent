# Supabase Database Schema

## Table: daily_logs

- id (uuid, PK)
- user_id (uuid)
- date (date)
- free_text (text, nullable)
- mood_score (integer, 1-10, nullable)
- energy_level (integer, 1-10, nullable)
- stress_level (integer, 1-10, nullable)
- sleep_hours (numeric, nullable)
- sleep_quality (integer, 1-10, nullable)
- created_at (timestamp with time zone, nullable)

## Table: gym_logs

- id (uuid, PK)
- user_id (uuid)
- date (date)
- exercise_name (text)
- sets (integer, nullable)
- reps (integer, nullable)
- weight (numeric, nullable)
- duration_minutes (integer, nullable)
- notes (text, nullable)
- created_at (timestamp with time zone, nullable)

## Table: jiujitsu_logs

- id (uuid, PK)
- user_id (uuid)
- date (date)
- session_type (text)
- techniques_trained (text[], nullable)
- rolls_count (integer, nullable)
- roll_partners (text[], nullable)
- performance_rating (integer, 1-10, nullable)
- notes (text, nullable)
- created_at (timestamp with time zone, nullable)

## Table: nutrition_logs

- id (uuid, PK)
- user_id (uuid)
- date (date)
- meal_type (text)
- meal_time (time, nullable)
- foods (text[], nullable)
- calories (integer, nullable)
- protein_grams (numeric, nullable)
- carbs_grams (numeric, nullable)
- fat_grams (numeric, nullable)
- notes (text, nullable)
- created_at (timestamp with time zone, nullable)

## Table: career_logs

- id (uuid, PK)
- user_id (uuid)
- date (date)
- work_hours (numeric, nullable)
- productivity_rating (integer, 1-10, nullable)
- tasks_completed (text[], nullable)
- achievements (text[], nullable)
- challenges (text[], nullable)
- goals (text[], nullable)
- notes (text, nullable)
- created_at (timestamp with time zone, nullable)

## Table: financial_transactions

- id (uuid, PK)
- user_id (uuid)
- date (date)
- amount (numeric)
- currency (text, nullable, default 'GBP')
- category (text, nullable)
- description (text, nullable)
- source (text, nullable)
- transaction_type (text)
- created_at (timestamp with time zone, nullable)
- balance_after (numeric, nullable)
- monzo_transaction_id (text, nullable)

## Table: investment_logs

- id (uuid, PK)
- user_id (uuid)
- date (date)
- asset_name (text)
- asset_type (text)
- transaction_type (text)
- quantity (numeric, nullable)
- price_per_unit (numeric, nullable)
- total_amount (numeric, nullable)
- currency (text, nullable, default 'GBP')
- platform (text, nullable)
- notes (text, nullable)
- created_at (timestamp with time zone, nullable)

## Table: embeddings

- id (uuid, PK)
- user_id (uuid)
- content_type (text)
- content_id (uuid)
- embedding (vector, nullable)
- created_at (timestamp with time zone, nullable)
