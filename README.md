# DNSUpdater

Updates Cloudflare DNS records to the IP of the machine this script is running on.

# Usage
Create three files in the working directory:
- `targets`: The hostnames to update, separated by a new line. (i.e. `homeserver.example.com`)
- `token`: Your [Cloudflare API token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/).
- `zone`: The [zone ID](https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/) of your domain.

Install the required libraries using `pip install -r "requirements.txt"`.

Finally, run `python3 main.py`.

A systemd `.service` file is provided if you want to run this as a systemd service.