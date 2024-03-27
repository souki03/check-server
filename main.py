import requests
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style, init

init(autoreset=True)

application_api_key = ""
client_api_key = ""
panel_url = ""
page_number = 1
server_count = 0

with open("server_ids.txt", "w") as file:
    while True:
        response_servers = requests.get(
            f"{panel_url}/api/application/servers?page={page_number}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {application_api_key}",
            },
        )
        if (server_count % 50) == 0:
            page_number = page_number + 1
        if response_servers.status_code == 200:
            try:
                servers_data = response_servers.json()

                if "data" in servers_data:
                    server_list = servers_data["data"]

                    if not server_list:
                        print("Aucun serveur trouvé.")
                        break

                    for server in server_list:
                        server_id = server["attributes"]["identifier"]
                        one_month_ago = datetime.now(timezone.utc) - timedelta(days=600)

                        response_logs = requests.get(
                            f"{panel_url}/api/client/servers/{server_id}/activity",
                            headers={
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {client_api_key}",
                            },
                        )

                        if response_logs.status_code == 200:
                            try:
                                logs_data = response_logs.json()

                                if "meta" in logs_data:
                                    pagination_info = logs_data["meta"]["pagination"]

                                    if "total_pages" in pagination_info:
                                        total_pages = pagination_info["total_pages"]
                                        page_max = total_pages

                                    else:
                                        print(
                                            f"La clé 'total_pages' n'existe pas dans la réponse JSON pour le serveur {server_id}."
                                        )

                                else:
                                    print(
                                        f"La clé 'meta' n'existe pas dans la réponse JSON pour le serveur {server_id}."
                                    )

                            except requests.exceptions.JSONDecodeError as e:
                                print(f"Erreur de décodage JSON : {e}")

                        else:
                            print(
                                f"Erreur de requête HTTP pour le serveur {server_id} : {response_logs.status_code}"
                            )

                        if 1 == 1:
                            response_logs_last_page = requests.get(
                                f"{panel_url}/api/client/servers/{server_id}/activity?page={total_pages}",
                                headers={
                                    "Accept": "application/json",
                                    "Content-Type": "application/json",
                                    "Authorization": f"Bearer {client_api_key}",
                                },
                            )
                            server_count = server_count + 1
                            if response_logs_last_page.status_code == 200:
                                try:
                                    logs_data_last_page = response_logs_last_page.json()

                                    if "data" in logs_data_last_page:
                                        server_logs_last_page = logs_data_last_page[
                                            "data"
                                        ]
                                        one_month = datetime.now(
                                            timezone.utc
                                        ) - timedelta(days=31)
                                        if server_logs_last_page:
                                            last_activity_datetime = datetime.strptime(
                                                server_logs_last_page[-1]["attributes"][
                                                    "timestamp"
                                                ],
                                                "%Y-%m-%dT%H:%M:%S%z",
                                            )
                                            if last_activity_datetime < one_month:
                                                print(
                                                    f"{Fore.RED}Server {server_id} | {last_activity_datetime} | {page_max} | {server_count} {Style.RESET_ALL}"
                                                )
                                                file.write(f"{server_id}\n")

                                            else:
                                                print(
                                                    f"{Fore.GREEN}Server {server_id} | {last_activity_datetime} | {page_max} | {server_count} {Style.RESET_ALL}"
                                                )
                                        else:
                                            print(
                                                f"{Fore.YELLOW}Server {server_id} | NO LOG | {server_count} {Style.RESET_ALL}"
                                            )
                                            file.write(f"{server_id}\n")

                                    else:
                                        print(
                                            f"La clé 'data' n'existe pas dans la réponse JSON pour les logs pour le serveur {server_id}."
                                        )
                                except requests.exceptions.JSONDecodeError as e:
                                    print(
                                        f"Erreur de décodage JSON pour les logs du serveur {server_id} : {e}"
                                    )

                            else:
                                print(
                                    f"Erreur de requête HTTP pour les logs du serveur {server_id} : {response_logs_last_page.status_code}"
                                )

                        else:
                            print(f"Le serveur {server_id} a été mis à jour récemment.")

                else:
                    print(
                        "La clé 'data' n'existe pas dans la réponse JSON pour les serveurs."
                    )

            except requests.exceptions.JSONDecodeError as e:
                print(f"Erreur de décodage JSON pour les serveurs : {e}")

        else:
            print(
                f"Erreur de requête HTTP pour les serveurs : {response_servers.status_code}"
            )
