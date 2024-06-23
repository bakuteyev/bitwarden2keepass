#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -e EMAIL -k KEEPASS_FILE -b S3_BUCKET [-p S3_PREFIX] [-s S3_ENDPOINT] [-a AWS_PROFILE]"
    echo "  -e EMAIL        Bitwarden email"
    echo "  -k KEEPASS_FILE Path to KeePass file"
    echo "  -b S3_BUCKET    S3 bucket name"
    echo "  -p S3_PREFIX    S3 prefix (default: yadisk-keepass-backups)"
    echo "  -s S3_ENDPOINT  S3 endpoint URL (default: https://storage.yandexcloud.net/)"
    echo "  -a AWS_PROFILE  AWS profile name (default: yc_pass)"
    exit 1
}

# Function to log messages
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log_message "Error: $1"
    exit 1
}

# Function to sync Bitwarden and export to KeePass
sync_and_export() {
    log_message "Starting Bitwarden sync and export to KeePass..."
    
    MASTER_PASSWORD=$(security find-internet-password -s bitwarden.com -a "$BITWARDEN_EMAIL" -w)
    if [ -z "$MASTER_PASSWORD" ]; then
        handle_error "Failed to retrieve Bitwarden master password"
    fi

    bw sync && bitwarden2keepass --master_password "$MASTER_PASSWORD" --keepass_path="$KEEPASS_FILE" || handle_error "Bitwarden sync or export to KeePass failed"
    
    log_message "Bitwarden sync and export completed successfully"
}

# Function to upload file to S3
upload_to_s3() {
    log_message "Starting S3 upload..."
    
    TIMESTAMP=$(date +"%Y-%m-%d/%H:%M")
    FILENAME=$(basename "$KEEPASS_FILE")
    S3_OBJECT_KEY="${S3_PREFIX}/${TIMESTAMP}/${FILENAME}"

    aws s3 --endpoint-url="$S3_ENDPOINT" --profile="$AWS_PROFILE" \
        cp "$KEEPASS_FILE" "s3://${S3_BUCKET}/${S3_OBJECT_KEY}" || handle_error "S3 upload failed"

    log_message "File successfully uploaded to s3://${S3_BUCKET}/${S3_OBJECT_KEY}"
}

# Parse command line arguments
while getopts ":e:k:b:p:s:a:" opt; do
  case $opt in
    e) BITWARDEN_EMAIL="$OPTARG" ;;
    k) KEEPASS_FILE="$OPTARG" ;;
    b) S3_BUCKET="$OPTARG" ;;
    p) S3_PREFIX="$OPTARG" ;;
    s) S3_ENDPOINT="$OPTARG" ;;
    a) AWS_PROFILE="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; usage ;;
  esac
done

# Check for required arguments
if [ -z "$BITWARDEN_EMAIL" ] || [ -z "$KEEPASS_FILE" ] || [ -z "$S3_BUCKET" ]; then
    log_message "Missing required arguments"
    usage
fi

# Set default values for optional arguments
S3_PREFIX=${S3_PREFIX:-"yadisk-keepass-backups"}
S3_ENDPOINT=${S3_ENDPOINT:-"https://storage.yandexcloud.net/"}
AWS_PROFILE=${AWS_PROFILE:-"yc_pass"}

# Main execution
main() {
    sync_and_export
    upload_to_s3
    log_message "All operations completed successfully"
}

# Run the main function
main