CREATE EXTENSION IF NOT EXISTS vector;

-- Ingestion tables they catches raw text before embedding
--table 1. Raw articles and transcripts
create table raw_articles(
    id UUID primary key default gen_random_uuid(),
    url_hash text unique not null, --sha256 of url for deduplicate
    ticker text not null,
    source text not null,
    title text not null,
    body_text text, -- Main arti or 8-k test
    body_prepared text,--earning call prepared remark(inno3)
    body_qa text,--earning call QA(inno 3)
    has_consensus boolean default TRUE,--False for sudden CEO resign etc
    published_at timestamptz not null,
    created_at timestamptz default now()
);

--table 2. Market Regime (Novelty 4)
create table market_regimes(
    id UUID primary key default gen_random_uuid(),
    regime_label text not null, --'Risk-on Bull','cautios neutral',etc.
    vix_level numeric,
    yield_slope numeric,
    spx_20d_return numeric,
    created_at timestamptz default now()
);

--Latent space tables 
-- Table 3 consensus baseline (novelty 5 + inno 1)
create table consensus_baseline(
    id UUID primary key default gen_random_uuid(),
    ticker text not null,
    regime text not null,
    v_consensus_bear vector(768),
    v_consensus_base vector(768),
    v_consensus_bull vector(768),
    v_consensus_options vector(768), -- inno 1
    analyst_options_divergence numeric,
    created_at timestamptz default now()
);

-- Table 4 actual embed
create table embeddings(
    id UUID primary key default gen_random_uuid(),
    article_id UUID references raw_articles(id) on delete cascade,
    v_actual vector(768),
    v_prepared vector(768),--transcript prepared reamrks
    v_qa vector(768),--transcrpt QA
    created_at timestamptz default now()
);

--Output and execution tables
-- Table 5 trading signls
create table trading_signals(
    id UUID primary key default gen_random_uuid(),
    ticker text not null,
    direction_label text not null,--'bullish','bearish'
    signal_type text default 'standard',
    confidence text not null,
    uncertainty_score numeric,
    regime_adjusted_tier text,
    predicted_returns JSONB,
    suggested_allocations_pct numeric,--kelly criterion sizing(inno 9)
    created_at timestamptz default now()
);

--Table 6 Signal outcome(feedback loop inno 6)
create table signal_outcome(
    id UUID primary key default gen_random_uuid(),
    signal_id UUID references trading_signals(id) on delete cascade,
    horizon text not null,
    accuracy_score numeric,
    ci_covered boolean,
    created_at timestamptz default now()
);