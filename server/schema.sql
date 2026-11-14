-- Stardrift bulut hesap veritabanı (Cloudflare D1)
CREATE TABLE IF NOT EXISTS users (
  email TEXT PRIMARY KEY,
  pilot TEXT,
  pw_salt TEXT NOT NULL,
  pw_hash TEXT NOT NULL,
  verified INTEGER NOT NULL DEFAULT 0,
  code TEXT,          -- aktivasyon / şifre sıfırlama kodu (özeti)
  code_kind TEXT,     -- 'verify' | 'reset'
  code_t INTEGER,     -- kodun verildiği an (ms)
  code_n INTEGER NOT NULL DEFAULT 0,   -- son bir saatte gönderilen kod sayısı
  code_tries INTEGER NOT NULL DEFAULT 0,
  created INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS tokens (
  token TEXT PRIMARY KEY,
  email TEXT NOT NULL,
  t INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS tokens_email ON tokens(email);
CREATE TABLE IF NOT EXISTS saves (
  email TEXT PRIMARY KEY,
  data TEXT NOT NULL,
  t INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS codes (
  code TEXT PRIMARY KEY,
  data TEXT NOT NULL,
  t INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS hits (
  k TEXT PRIMARY KEY,
  n INTEGER NOT NULL,
  t INTEGER NOT NULL
);
