from pathlib import Path
import re
import paramiko

HOST = "login.expanse.sdsc.edu"
USER = "jcuzick"
REMOTE_DIR = "/home/jcuzick"
KEY_PATH = str(Path.home() / ".ssh" / "id_ed25519")


def connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=HOST,
        username=USER,
        key_filename=KEY_PATH,
    )
    return ssh


def run_remote(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err


def upload_file(ssh, local_file):
    local_file = Path(local_file)
    remote_path = f"{REMOTE_DIR}/{local_file.name}"

    sftp = ssh.open_sftp()
    sftp.put(str(local_file), remote_path)
    sftp.close()

    return remote_path


def submit_gaussian(local_com_file, cpus=1, hours=1):
    ssh = connect()

    upload_file(ssh, local_com_file)
    filename = Path(local_com_file).name

    command = f"cd {REMOTE_DIR} && python exp.py {filename} {cpus} {hours}"
    out, err = run_remote(ssh, command)

    ssh.close()

    match = re.search(r"Submitted batch job (\d+)", out)
    job_id = match.group(1) if match else None

    return {
        "job_id": job_id,
        "stdout": out,
        "stderr": err,
    }


def job_status(job_id):
    ssh = connect()

    command = f"squeue -j {job_id} -o '%i %j %T %M %D %C'"
    out, err = run_remote(ssh, command)

    ssh.close()

    return out, err
