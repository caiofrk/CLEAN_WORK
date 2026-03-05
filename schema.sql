-- Basic Supabase SQL Schema for Hybrid Marketplace

-- Enable UUID extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles (Platform Users)
-- Extends the built-in auth.users table in Supabase
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  username TEXT UNIQUE,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Scraped Supply (Service Providers)
CREATE TABLE providers (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL, -- Null if not yet claimed
  business_name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  phone TEXT,
  email TEXT,
  website TEXT,
  location TEXT,
  is_claimed BOOLEAN DEFAULT FALSE,
  source_url TEXT, -- Where the data was scraped from
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Scraped Demand (Service Requests)
CREATE TABLE requests (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL, -- Null if scraped, populated if posted directly
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  budget_range TEXT,
  location TEXT,
  status TEXT DEFAULT 'open', -- open, in_progress, closed
  source_url TEXT, -- Where the demand was scraped from, if applicable
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Matches (Connections between Supply and Demand)
CREATE TABLE matches (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  request_id UUID REFERENCES requests(id) ON DELETE CASCADE,
  provider_id UUID REFERENCES providers(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'pending', -- pending, accepted, rejected
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  UNIQUE(request_id, provider_id)
);

-- Setup Row Level Security (RLS) policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;

-- Note: Basic open read access for public marketplace data. Proper RLS should be scoped later.
CREATE POLICY "Public profiles are viewable by everyone." ON profiles FOR SELECT USING (true);
CREATE POLICY "Public providers are viewable by everyone." ON providers FOR SELECT USING (true);
CREATE POLICY "Public requests are viewable by everyone." ON requests FOR SELECT USING (true);

-- 5. Market Leads (Validated Demand from Tenders / Public Sources)
CREATE TABLE market_leads (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  client_name TEXT NOT NULL,
  opportunity_desc TEXT,
  budget_estimate NUMERIC,
  deadline DATE,
  status TEXT DEFAULT 'open', -- 'open', 'contacted', 'closed'
  location_lat_long POINT,
  source_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Tabela de Oportunidades Audiovisual Brasil
CREATE TABLE br_production_leads (
  id uuid primary key default gen_random_uuid(),
  projeto_nome text not null,
  uf char(2) not null, -- Ex: 'RJ', 'SP'
  cidade text,
  vagas text[], -- Array: ['Rigger', 'Dublê']
  descricao_original text,
  contato_producao text,
  url_origem text,
  data_postagem timestamptz default now()
);

-- Índice para busca por estado
CREATE INDEX idx_uf_leads on br_production_leads(uf);

ALTER TABLE br_production_leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public production leads are viewable by everyone." ON br_production_leads FOR SELECT USING (true);
