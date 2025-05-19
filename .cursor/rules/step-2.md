### Step 2: Supabase Setup and Schema Design

Supabase will serve as your primary structured database. Begin by creating a new Supabase project through their dashboard.

Once your project is created, design and implement the database schema. Here's a comprehensive schema design that covers all your tracking requirements:

```sql
-- Users table (for authentication)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily logs table
CREATE TABLE daily_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  free_text TEXT,
  mood_score INTEGER CHECK (mood_score BETWEEN 1 AND 10),
  energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
  stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
  sleep_hours NUMERIC(3,1),
  sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, date)
);

-- Gym logs table
CREATE TABLE gym_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  exercise_name TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight NUMERIC(6,2),
  duration_minutes INTEGER,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jiu-jitsu logs table
CREATE TABLE jiujitsu_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  session_type TEXT NOT NULL, -- e.g., 'class', 'open mat', 'private'
  techniques_trained TEXT[],
  rolls_count INTEGER,
  roll_partners TEXT[],
  performance_rating INTEGER CHECK (performance_rating BETWEEN 1 AND 10),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Nutrition logs table
CREATE TABLE nutrition_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  meal_type TEXT NOT NULL, -- e.g., 'breakfast', 'lunch', 'dinner', 'snack'
  meal_time TIME,
  foods TEXT[],
  calories INTEGER,
  protein_grams NUMERIC(5,1),
  carbs_grams NUMERIC(5,1),
  fat_grams NUMERIC(5,1),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Career logs table
CREATE TABLE career_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  work_hours NUMERIC(4,1),
  productivity_rating INTEGER CHECK (productivity_rating BETWEEN 1 AND 10),
  tasks_completed TEXT[],
  achievements TEXT[],
  challenges TEXT[],
  goals TEXT[],
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial transactions table
CREATE TABLE financial_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  amount NUMERIC(10,2) NOT NULL,
  currency TEXT DEFAULT 'GBP',
  category TEXT,
  description TEXT,
  source TEXT, -- e.g., 'Monzo', 'Nationwide', 'Manual'
  transaction_type TEXT NOT NULL, -- e.g., 'income', 'expense', 'transfer'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investment logs table
CREATE TABLE investment_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  date DATE NOT NULL,
  asset_name TEXT NOT NULL,
  asset_type TEXT NOT NULL, -- e.g., 'stock', 'crypto', 'real estate'
  transaction_type TEXT NOT NULL, -- e.g., 'buy', 'sell'
  quantity NUMERIC(16,8),
  price_per_unit NUMERIC(16,8),
  total_amount NUMERIC(16,2),
  currency TEXT DEFAULT 'GBP',
  platform TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector embeddings table
CREATE TABLE embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) NOT NULL,
  content_type TEXT NOT NULL, -- e.g., 'daily_log', 'gym_log', etc.
  content_id UUID NOT NULL, -- Reference to the original content
  embedding VECTOR(1536), -- For OpenAI embeddings
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

After creating these tables, set up Row Level Security (RLS) policies to ensure data privacy:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE gym_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE jiujitsu_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutrition_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE investment_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can only access their own data" ON users
  FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can only access their own daily logs" ON daily_logs
  FOR ALL USING (auth.uid() = user_id);

-- Repeat similar policies for all other tables
```
