import logging
import os
import subprocess
import zlib

from cryptography.fernet import Fernet
from github import Auth, Github, GithubException

# --- Configuration (Matches Backup Script) ---
db_host = os.getenv("POSTGRES_DB_HOST")
db_name = os.getenv("POSTGRES_DB_NAME")
db_user = os.getenv("POSTGRES_DB_USER")
db_password = os.getenv("POSTGRES_DB_PASSWORD")
restore_command = [
    "psql",
    "-h", db_host,
    "-U", db_user,
    "-d", db_name,
]

backup_encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")
cipher_suite = Fernet(backup_encryption_key.encode())

backup_git_repo = os.getenv('BACKUP_GIT_REPO')
backup_git_branch = os.getenv('BACKUP_GIT_BRANCH')
backup_git_access_token = os.getenv('BACKUP_GIT_ACCESS_TOKEN')
git_auth = Auth.Token(backup_git_access_token)


async def run(date_str: str):
    logging.info(f"Starting restoration for path: {date_str}")

    date_path = date_str.replace("-", "/")
    git_path = f"{date_path}/postgres.sql.gz"

    encrypted_sql = await download_from_github(git_path)
    if encrypted_sql is None:
        logging.warn(f"Invalid Date {date_str}, Failed to restore.")
        return

    logging.info(f"Successfully downloaded {git_path} from GitHub.")

    compressed_sql = await decrypt_data(encrypted_sql)
    logging.info("Decryption successful.")

    raw_sql = await decompress_data(compressed_sql)
    logging.info("Decompression successful.")

    await restore_postgres(raw_sql)
    logging.info("Database restore completed successfully.")


async def download_from_github(git_path):
    try:
        with Github(auth=git_auth) as git:
            repo = git.get_repo(backup_git_repo)
            contents = repo.get_contents(git_path, ref=backup_git_branch)
            # GitHub returns content as base64 encoded bytes; decoded_content handles this
            return contents.decoded_content.decode()
    except GithubException as e:
        if e.status == 404:
            return None
        else:
            raise e


async def decrypt_data(encrypted_str: str):
    return cipher_suite.decrypt(encrypted_str.encode())


async def decompress_data(compressed_data: bytes):
    return zlib.decompress(compressed_data)


async def restore_postgres(sql_bytes: bytes):
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    process = subprocess.run(
        restore_command,
        input=sql_bytes,
        env=env,
        capture_output=True,
        check=True
    )
    return process.stdout
