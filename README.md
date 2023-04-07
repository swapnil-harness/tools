How to use helm-airgap.py

Download or make a copy of: https://github.com/harness/helm-charts/blob/main/src/harness/images.txt

Open images.txt and add these images at the end.

harness/aws-ecr-job-runner
harness/aws-security-hub-job-runner
harness/aqua-trivy-job-runner
harness/bandit-job-runner
harness/blackduckhub-job-runner
harness/brakeman-job-runner
harness/sto-plugin
harness/grype-job-runner
harness/nmap-job-runner
harness/nikto-job-runner
harness/sto-plugin
harness/owasp-job-runner
harness/snyk-job-runner
harness/sonarqube-agent-job-runner
harness/prowler-job-runner
harness/twistlock-job-runner
harness/checkmarx-job-runner
harness/veracode-agent-job-runner
harness/zap-job-runner
harness/whitesource-agent-job-runner

Save it and run:

python3 helm-airgap.py images.txt


