

## Setup

1. Install Wireguard, along with any additional dependencies
   * https://www.wireguard.com/install/
2. Install Puthon 3.x
    * https://www.python.org/downloads/
3. Run the following command to install all python package script dependencies
   ```bash 
   pip install -r requirements.txt
   ``` 
4. Generate wireguard config files from your VPN provider
    * Mullvad example:  https://mullvad.net/en/account/#/wireguard-config/?platform=windows

## How to run the benchmark script
1. Open `benchmark_wireguard_vpn_servers.py` and edit the `VPN_CONFIG_DIR` variable defined at the top to point to the directory containing all wireguard config files.
2. Run the script:
    * Windows note: admin privelages are required in order to make calls to the wireguard client from within the script 
        ```bash
        python benchmark_wireguard_vpn_servers.py
        ```
    The script will pipe all stdout output to a file named `benchmark_stdout.txt`
    
    When the script has finished benchmarking all wireguard configs, it will write the results to a file named `benchmark_results.json`. This file will be sorted by download speed in descending order and will include information about each config tested (config name, server information, and speedtest information).

## Example `benchmark_results.json` output file

```json
[
    {
        "name": "<config-file-name-1>",
        "ip": "<vpn-server-ip>",
        "city": "<vpn-server-city-name>",
        "region": "<vpn-server-region/state-name>",
        "country": "<vpn-server-country-name>",
        "coordinate": [
            -123.45,
            67.890
        ],
        "speedtest_results": [
            {
                "server_name": "Speedtest Server 1 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12345",
                "upload_speed": 0.0,
                "download_speed": 500.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 2 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12346",
                "upload_speed": 0.0,
                "download_speed": 400.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 3 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12347",
                "upload_speed": 0.0,
                "download_speed": 300.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 4 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12348",
                "upload_speed": 0.0,
                "download_speed": 200.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 5 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12349",
                "upload_speed": 0.0,
                "download_speed": 100.00,
                "ping": 10.000
            }
        ]
    },
    {
        "name": "<config-file-name-2>",
        "ip": "<vpn-server-ip>",
        "city": "<vpn-server-city-name>",
        "region": "<vpn-server-region/state-name>",
        "country": "<vpn-server-country-name>",
        "coordinate": [
            -123.45,
            67.890
        ],
        "speedtest_results": [
            {
                "server_name": "Speedtest Server 1 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12345",
                "upload_speed": 0.0,
                "download_speed": 125.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 2 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12346",
                "upload_speed": 0.0,
                "download_speed": 120.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 3 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12347",
                "upload_speed": 0.0,
                "download_speed": 115.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 4 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12348",
                "upload_speed": 0.0,
                "download_speed": 110.00,
                "ping": 10.000
            },
            {
                "server_name": "Speedtest Server 5 Name (Speedtest Server City, State/Region, Country) [Distance from VPN server]",
                "server_id": "12349",
                "upload_speed": 0.0,
                "download_speed": 105.00,
                "ping": 10.000
            }
        ]
    }
]
```
