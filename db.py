import os
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_QUERY_USUARIO = """
    SELECT
        u.login,
        u.pswd,
        u.name,
        u.email,
        u.active,
        u.priv_admin,
        u.picture,
        u.role,
        u.phone,
        c.setor,
        c.filial,
        c.com_cargo,
        c.com_id_sap
    FROM public.sec_users u
    LEFT JOIN public.ad_user_cfg c ON c.login = u.login
    WHERE u.login = %s
      AND u.active = TRUE
"""


def _get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def buscar_usuario(login: str) -> dict | None:
    """Retorna os dados do usuário ativo ou None se não encontrado."""
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(_QUERY_USUARIO, (login,))
            row = cur.fetchone()
            return dict(row) if row else None


def verificar_senha(senha_digitada: str, hash_armazenado: str) -> bool:
    """
    Detecta automaticamente o esquema de hash pelo formato do valor armazenado:
      - bcrypt   → começa com $2b$, $2a$ ou $2y$
      - SHA-256  → 64 chars hex
      - SHA-1    → 40 chars hex
      - MD5      → 32 chars hex
    """
    if not hash_armazenado:
        return False

    # bcrypt
    if hash_armazenado.startswith(("$2b$", "$2a$", "$2y$")):
        try:
            import bcrypt
            return bcrypt.checkpw(senha_digitada.encode(), hash_armazenado.encode())
        except Exception:
            return False

    h = hash_armazenado.lower()
    s = senha_digitada.encode()

    if len(h) == 64:
        return hashlib.sha256(s).hexdigest() == h

    if len(h) == 40:
        return hashlib.sha1(s).hexdigest() == h

    if len(h) == 32:
        return hashlib.md5(s).hexdigest() == h

    return False


def resolver_tipo_consultor(usuario: dict) -> tuple[str | None, str | None]:
    """
    Retorna (tipo_consultor, id_sap) com base no com_cargo do usuário.
      CONSULTOR → consultor externo, retorna o com_id_sap
      LOJA      → consultor interno
      outro     → None, None
    """
    cargo = (usuario.get("com_cargo") or "").upper().strip()
    if cargo == "CONSULTOR":
        return "externo", usuario.get("com_id_sap")
    if cargo == "LOJA":
        return "interno", None
    return None, None
