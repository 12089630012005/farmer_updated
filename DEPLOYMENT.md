# Deploying farmer_updated with Docker and Jenkins on Azure VM

## Fixing "fatal: not in a git directory" in Jenkins

This error happens when Jenkins is set to **Pipeline script from SCM** but runs `git config` in a directory that is **not a git repository** (e.g. empty workspace or wrong path).

### Step 1: Wipe the job workspace (most common fix)

1. In Jenkins, open your **farmer_updated** (or the job name you use) pipeline job.
2. Click **Workspace** in the left menu (or go to the job → **Workspace**).
3. Click **Wipe Out Current Workspace** (or **Delete workspace**).
4. Run the pipeline again (**Build Now**).

This forces a fresh clone so the workspace is a proper git repo.

### Step 2: Check Pipeline configuration

1. Go to the job → **Configure**.
2. Under **Pipeline**:
   - **Definition**: `Pipeline script from SCM`
   - **SCM**: `Git`
   - **Repository URL**: `https://github.com/12089630012005/farmer_updated.git`
   - **Credentials**: Add a GitHub credential if the repo is private (Username/Password or token).
   - **Branch**: `*/main` or `*/master` (match your default branch).
   - **Script Path**: `Jenkinsfile` (must be exactly this if the file is at repo root).
3. Do **not** use **Checkout to a subdirectory** unless you really need it.
4. If you see **Lightweight checkout**, **disable** it so Jenkins does a full clone (required for "Pipeline script from SCM" to work correctly in many setups).
5. Save and run **Build Now** again.

### Step 3: Verify Git and repo access on the VM

SSH into your Azure VM and run:

```bash
ssh azureuser@mrtlife-devops-vm1

# Ensure git is installed
git --version

# Test clone (use a temp dir)
cd /tmp
rm -rf farmer_updated
git clone https://github.com/12089630012005/farmer_updated.git
ls farmer_updated
```

- If the clone fails (e.g. 404 or auth), fix repo URL or credentials in Jenkins.
- If the clone works, the problem is usually workspace/configuration (Steps 1–2).

### Step 4: Run Jenkins with correct workspace (optional)

If the job runs under a user that has a weird home or workspace path:

- In **Configure** → **Advanced** → set **Use custom workspace** to a path like `/var/lib/jenkins/workspace/farmer_updated` (or your job name) so Jenkins always uses a clean, known directory.

---

## Quick checklist

| Check | Action |
|-------|--------|
| Workspace | Wipe workspace and rebuild |
| Repo URL | `https://github.com/12089630012005/farmer_updated.git` |
| Script Path | `Jenkinsfile` |
| Lightweight checkout | Off |
| Private repo | Add GitHub credentials in Jenkins |
| Branch | `*/main` or `*/master` |

---

## After the pipeline runs

- The pipeline uses **docker-compose**: it starts **MySQL** and the **Flask app** together. The app connects to MySQL using env vars (`MYSQL_HOST=mysql`, etc.).
- App URL: `http://<your-vm-public-ip>/` (or `http://mrtlife-devops-vm1` if you use that hostname).
- Ensure Azure NSG allows inbound **80** (and **8080** for Jenkins if needed).

## Database (MySQL)

- **In Docker**: The Jenkinsfile runs `docker compose up -d --build`, which starts MySQL and the app. The database `farmer_updated` and tables are created on first run from `schema.sql` (mounted into MySQL’s init folder).
- **DB config**: The app reads from environment variables (no hardcoded credentials):
  - `MYSQL_HOST` (default `127.0.0.1`; in Docker use `mysql`)
  - `MYSQL_USER` (default `root`)
  - `MYSQL_PASSWORD` (set in compose or `.env`)
  - `MYSQL_DATABASE` (default `farmer_updated`)
- **Custom password**: Copy `.env.example` to `.env` and set `MYSQL_ROOT_PASSWORD`. Use the same value in the app container (docker-compose passes it). For production, use a strong password and do not commit `.env`.

---

## Alternative: Pipeline script not from SCM

If you prefer not to load the Jenkinsfile from Git:

1. **Definition**: `Pipeline script` (not "from SCM").
2. Paste the contents of `Jenkinsfile` into the script box.
3. Then add a first stage that checks out your repo, e.g.:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm: [
                    $class: 'GitSCM',
                    userRemoteConfigs: [[url: 'https://github.com/12089630012005/farmer_updated.git']],
                    branches: [[name: '*/main']]
                ], poll: false
            }
        }
        // ... rest of your stages
    }
}
```

Note: with "Pipeline script" you must use a **generic** job or pass the repo via a parameter; the `scm` object is only available when using "Pipeline script from SCM". So the recommended approach is to fix the SCM/workspace setup (Steps 1–2 above) and keep **Pipeline script from SCM**.
