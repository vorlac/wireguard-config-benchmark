import json
import os
import requests
import sys
import time

# directory containing all wireguard configs
VPN_CONFIG_DIR = "./mullvad_configs"
# JSON benchmark restults output file
BENCHMARK_RESULTS_FILE = "./benchmark_results.json"
# text log file that stdout is piped to
BENCHMARK_STDOUT_FILE = "./benchmark_stdout.txt"


class StdOutLogger:
    def __init__(self, outfile_path=BENCHMARK_STDOUT_FILE):
        self.console = sys.stdout
        self.file = open(outfile_path, "w", encoding="utf-8", buffering=1)

    def write(self, message):
        self.console.write(message)
        self.file.write(message)

    def flush(self):
        self.console.flush()
        self.file.flush()


class SpeedTestResult:
    def __init__(self, server_name: str, result_json: dict):
        self.ping = result_json.get("ping", 9999)
        self.upload = round(result_json.get("upload", 0) * 1e-6, ndigits=2)
        self.download = round(result_json.get("download", 0) * 1e-6, ndigits=2)
        self.server_id = result_json.get("server", {}).get("id", "unknown_id")
        self.server_host = result_json.get("server", {}).get("host", "unknown_host")
        self.server_name = server_name

    def __repr__(self) -> str:
        return json.dumps(dict(self), indent=4)

    def __str__(self) -> str:
        return f"{{name={self.server_name}, download={self.download}, upload={self.upload}, ping={self.ping}}}"

    def __iter__(self):
        for key in ["server_name", "server_id", "upload_speed", "download_speed", "ping"]:
            yield (key, getattr(self, key))

    def as_dict(self):
        return {
            "server_name": self.server_name,
            "server_id": self.server_id,
            "upload_speed": self.upload,
            "download_speed": self.download,
            "ping": self.ping,
        }

    @staticmethod
    def compare_key(elem) -> float:
        return elem.download


class ConnectionInfo:
    def __init__(self, config_idx: int, name: str, ip_info=None):
        self.name = name
        self.id = config_idx

        if ip_info is None:
            ip_info: dict = self._lookup_ip()

        self.ip = ip_info.get("ip", None)
        self.version = ip_info.get("version", None)
        self.city = ip_info.get("city", None)
        self.region = ip_info.get("region", None)
        self.country = ip_info.get("country_name", None)

        self.coordinate = ("?", "?")
        lat: str = ip_info.get("latitude", "?")
        lon: str = ip_info.get("longitude", "?")
        if "Sign up to access" not in [lon, lat]:
            self.coordinate = (lon, lat)

        self.speedtest_results = []

    def __repr__(self) -> str:
        return json.dumps(dict(self), indent=4)

    def __str__(self) -> str:
        return f"{self.name} : {self.ip} - {self.city}, {self.region}, {self.country} {self.coordinate}"

    def __iter__(self):
        for key in ["name", "ip", "city", "region", "country", "coordinate", "speedtest_results"]:
            yield (key, getattr(self, key))

    def as_dict(self):
        return {
            "name": self.name,
            "ip": self.ip,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "coordinate": self.coordinate,
            "speedtest_results": [r.as_dict() for r in self.speedtest_results],
        }

    @staticmethod
    def _lookup_ip() -> dict:
        try:
            response = requests.get("https://ipapi.co/json")
            return response.json()
        except Exception as e:
            print(f"Failed to lookup IP address information: {e}")
            return {}

    @staticmethod
    def compare_key(elem) -> float:
        if elem.speedtest_results:
            fastest_result: SpeedTestResult = elem.speedtest_results[0]
            return SpeedTestResult.compare_key(fastest_result)

        return float("-inf")

    def speedtest(self) -> None:
        def get_local_speedtest_servers() -> list:
            server_list = []
            server_listing_output = os.popen("speedtest-cli.exe --list").read()
            for server_listing_line in server_listing_output.splitlines():
                server_info = server_listing_line.split(")", 1)
                if len(server_info) == 2:
                    server_id, server_name = server_info
                    server_list.append((server_id.strip(), server_name.strip()))

            return server_list

        print(f"\n{self.id:03}) Benchmarking {self}")

        speedtest_servers = get_local_speedtest_servers()
        print(f"     > Looking up local speedtest servers")
        print(f"       - Found {len(speedtest_servers)} servers: {[int(id) for id, _ in speedtest_servers]}")

        self.speedtest_results = []
        for server_id, server_name in speedtest_servers:
            print(f"     > Speed testing server {server_id}: {server_name}")
            speedtest_output = os.popen(f"speedtest-cli.exe --no-upload --json --server {server_id}").read()
            speedtest_json = json.loads(speedtest_output) if speedtest_output.strip() else {}
            result = SpeedTestResult(server_name, speedtest_json)
            print(f"       - Download: {result.download} Mbps, Upload: {result.upload} Mbps, Ping: {result.ping} ms")
            self.speedtest_results.append(result)

        # order the results by download speed descending
        self.speedtest_results.sort(key=SpeedTestResult.compare_key, reverse=True)


def benchmark_config(config_idx, config_path, base_name):
    def wait_until_tunnel_established():
        # TODO: see if there's a better way to
        # wait for the tunnel to be activated
        time.sleep(5)

    try:
        os.system(f"wireguard.exe /installtunnelservice {config_path}")
        wait_until_tunnel_established()
        connection_info = ConnectionInfo(config_idx, base_name)
        connection_info.speedtest()
        return connection_info
    except:
        raise
    finally:
        os.system(f"wireguard.exe /uninstalltunnelservice {base_name}")


def benchmark_vpn_servers():
    results = []

    if os.path.exists(BENCHMARK_RESULTS_FILE):
        os.remove(BENCHMARK_RESULTS_FILE)

    config_files = [
        os.path.abspath(os.path.join(VPN_CONFIG_DIR, config_file))
        for config_file in os.listdir(VPN_CONFIG_DIR)
        if os.path.isfile(os.path.join(VPN_CONFIG_DIR, config_file))
    ]

    for idx, config_path in enumerate(config_files):
        file_name = os.path.basename(config_path)
        base_name, _ = os.path.splitext(file_name)

        try:
            connection_info = benchmark_config(idx + 1, config_path, base_name)
            results.append(connection_info)
        except KeyboardInterrupt as k:
            print(f"Cancelled {base_name} benchmark: {k.__class__.__name__}")
            break
        except Exception as e:
            print(f"Failed {base_name} benchmark: {e}")
            break

    # order the connection information for each VPN server/config from fastest to slowest
    results.sort(key=ConnectionInfo.compare_key, reverse=True)

    with open(BENCHMARK_RESULTS_FILE, "w", encoding="utf-8", buffering=1) as log_file:
        log_file.write(json.dumps([r.as_dict() for r in results], indent=4))


if __name__ == "__main__":
    sys.stdout = StdOutLogger(BENCHMARK_STDOUT_FILE)
    benchmark_vpn_servers()
