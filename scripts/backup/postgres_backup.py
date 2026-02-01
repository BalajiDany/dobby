import logging
import os
import subprocess
import zlib
from datetime import datetime

from cryptography.fernet import Fernet
from github import Auth, Github, GithubException

db_host = os.getenv("POSTGRES_DB_HOST")
db_name = os.getenv("POSTGRES_DB_NAME")
db_user = os.getenv("POSTGRES_DB_USER")
db_password = os.getenv("POSTGRES_DB_PASSWORD")

dump_command = [
    "pg_dump",
    "-h", db_host,
    "-U", db_user,
    "-d", db_name,
    "--clean",
    "--if-exists",
    "--no-owner",
    "--no-privileges"
]

backup_encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")
cipher_suite = Fernet(backup_encryption_key.encode())

backup_git_repo = os.getenv('BACKUP_GIT_REPO')
backup_git_branch = os.getenv('BACKUP_GIT_BRANCH')
backup_git_access_token = os.getenv('BACKUP_GIT_ACCESS_TOKEN')
git_auth = Auth.Token(backup_git_access_token)


async def run():
    logging.info("Starting PostgreSQL backup process")

    raw_sql = await dump_postgres()
    raw_sql_size = len(raw_sql)
    logging.info(f"Database dump successful. Raw Size: {format_size(raw_sql_size)}")

    compressed_sql = await compress_text(raw_sql)
    compressed_sql_size = len(compressed_sql)
    reduction_rate = ((raw_sql_size - compressed_sql_size) / raw_sql_size) * 100 if raw_sql_size > 0 else 0
    logging.info(f"Compression completed. Size: {format_size(compressed_sql_size)} ({reduction_rate:.2f}% reduction)")

    encrypted_sql = await encrypt_text(compressed_sql)
    encrypted_sql_size = len(encrypted_sql.encode('utf-8'))
    logging.info(f"Encryption/Base64 completed. Size: {format_size(encrypted_sql_size)}")

    uploaded_path = await upload_to_github(encrypted_sql)
    logging.info(f"Uploaded backup at {uploaded_path}")


async def dump_postgres():
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    process = subprocess.run(dump_command, env=env, capture_output=True, check=True)
    return process.stdout


async def compress_text(text: str):
    return zlib.compress(text, level=9)


async def encrypt_text(text: str):
    encrypted_text = cipher_suite.encrypt(text)
    return encrypted_text.decode()


async def upload_to_github(content: str):
    now = datetime.now()

    git_folder = now.strftime("%Y/%m/%d")
    git_filename = "postgres.sql.gz"

    git_path = f"{git_folder}/{git_filename}"
    git_commit_message = f"Backup for {now.strftime('%Y-%m-%d %H:%M:%S')}"

    with Github(auth=git_auth) as git:
        repo = git.get_repo(backup_git_repo)

        try:
            contents = repo.get_contents(git_path, ref=backup_git_branch)
            repo.update_file(
                path=git_path,
                content=content,
                message=git_commit_message,
                branch=backup_git_branch,
                sha=contents.sha,
            )
        except GithubException as e:
            if e.status == 404:
                repo.create_file(
                    path=git_path,
                    content=content,
                    message=git_commit_message,
                    branch=backup_git_branch,
                )
            else:
                raise e

    return git_path


def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

    return f"{bytes_size:.2f} TB"
