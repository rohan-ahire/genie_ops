import requests
import json
import os


############################################################
# UTILS FOR EXPORT GENIE
############################################################


class ExportGenie:
    def __init__(
        self,
        host: str,
        token: str,
        root_dir: str,
        genie_name: str,
        src_genie_space_id: str,
        path_to_genie_folder: str,
        env: str,
    ) -> None:
        """
        Args:
            host (str): The base URL for the Genie API.
            token (str): Bearer token for API authentication.
            root_dir (str): Root directory of the git repository.
            genie_name (str): Folder name of the Genie space
                (e.g., 'Pipeline_overview').
            src_genie_space_id (str): Source Genie space ID to export.
            path_to_genie_folder (str): Path to Genie folder
                (e.g., 'src/sales_genie_spaces').
            env (str): Target environment (e.g., 'dev', 'stg', 'tst', 'prd').
        """
        self.HOST = host
        self.HEADERS = {"Authorization": f"Bearer {token}"}
        self.root_dir = root_dir
        self.path_to_genie_folder = path_to_genie_folder
        self.genie_name = genie_name
        self.src_genie_space_id = src_genie_space_id
        self.env = env

    # creates a write path for the exported json
    def write_path(self, env: str) -> str:
        return os.path.join(
            self.root_dir,
            self.path_to_genie_folder,
            self.genie_name,
            f"exported_{self.src_genie_space_id}_{env}.json",
        )

    # read and apply find and replace logic
    def apply_find_and_replace(self, json_data, env: str):
        replace_patterns = ["_dev", "_tst", "_stg", "_prd"]
        for pattern in replace_patterns:
            # Convert to string for replacement
            json_data = json.dumps(json_data)
            json_data = json_data.replace(pattern, f"_{env}")
            # Convert back to JSON
            json_data = json.loads(json_data)
        return json_data

    def __call__(self):
        # check for valid genie space id
        if (
            self.src_genie_space_id is None
            or str(self.src_genie_space_id).lower() == "none"
            or not self.src_genie_space_id
        ):
            raise Exception(
                f"Please provide a valid genie space id for genie name: {self.genie_name}"
            )

        # call the export API
        url = (
            f"{self.HOST}/api/2.0/genie/spaces/"
            f"{self.src_genie_space_id}?include_serialized_space=true"
        )
        response = requests.get(url, headers=self.HEADERS)

        if response.status_code == 200:
            json_data = response.json()
            # Generate one file per environment
            for env in ["dev", "tst", "stg", "prd"]:
                # Apply find and replace logic
                modified_json_data = self.apply_find_and_replace(json_data, env)
                file_path = self.write_path(env)
                with open(file_path, "w") as f:
                    json.dump(modified_json_data, f)
                print(f"Exported space {self.src_genie_space_id} to {file_path}")
            return response.status_code
        else:
            raise Exception(
                f"Failed to export Genie Space {self.src_genie_space_id}: "
                f"{response.status_code} {response.text}"
            )


############################################################
# UTILS FOR IMPORT GENIE (UPDATE, CREATE)
############################################################


class ImportGenie:
    """
    Helpers for importing / updating Genie spaces via API.
    """

    def __init__(
        self,
        host: str,
        token: str,
        src_genie_dir: str,
        tgt_genie_dir: str,
        src_genie_space_id: str,
        tgt_genie_space_id: str,
        warehouse_id: str,
        env: str,
    ) -> None:
        """
        Args:
            host (str): The base URL for the Genie API.
            token (str): Bearer token for API authentication.
            src_genie_dir (str): Directory containing the exported
                Genie JSON file.
            tgt_genie_dir (str): Target directory where the Genie
                will be imported.
            src_genie_space_id (str): Source Genie space ID used to
                read the exported JSON file.
            tgt_genie_space_id (str): Target Genie space ID; if None,
                a new Genie space will be created.
            warehouse_id (str): SQL warehouse ID used for Genie creation.
            env (str): Target environment (e.g., 'dev', 'stg', 'tst', 'prd').
        """
        self.HOST = host
        self.HEADERS = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.src_genie_dir = src_genie_dir
        self.src_genie_space_id = src_genie_space_id
        self.tgt_genie_space_id = tgt_genie_space_id
        self.tgt_genie_dir = tgt_genie_dir
        self.warehouse_id = warehouse_id
        self.env = env

    # update an existing genie space
    def update_genie(self, content_json: str):
        url = f"{self.HOST}/api/2.0/genie/spaces/{self.tgt_genie_space_id}"
        response = requests.patch(url, headers=self.HEADERS, data=content_json)
        if response.status_code == 200:
            print(
                f"Successfully imported a Genie Space {self.tgt_genie_space_id} "
                f"from {self.src_genie_space_id}"
            )
            return response
        else:
            raise Exception(
                f"Failed to import a Genie Space {self.tgt_genie_space_id} "
                f"from {self.src_genie_space_id}: "
                f"{response.status_code} {response.text}"
            )

    # create a new genie space
    def create_genie(self, content_json: str):
        url = f"{self.HOST}/api/2.0/genie/spaces/"
        response = requests.post(url, headers=self.HEADERS, data=content_json)
        if response.status_code == 200:
            r = response.json()
            print(
                f"Successfully created a new Genie Space {r['space_id']} "
                f"from {self.src_genie_space_id}"
            )
            return response
        else:
            raise Exception(
                f"Failed to create a new genie and import a Genie Space "
                f"from {self.src_genie_space_id}: "
                f"{response.status_code} {response.text}"
            )

    def __call__(self):
        # read genie json
        try:
            file_path = os.path.join(
                self.src_genie_dir,
                f"exported_{self.src_genie_space_id}_{self.env}.json",
            )
            with open(file_path, "r") as f:
                json_export = json.load(f)
        except FileNotFoundError:
            raise Exception(
                "Error! Please provide a valid genie export file. "
                f"File: exported_{self.src_genie_space_id}_{self.env}.json "
                "has not been found"
            )

        # specify tgt genie information
        content = {
            "warehouse_id": self.warehouse_id,  # used for creation; optional for update
            "parent_path": self.tgt_genie_dir,  # used for creation; optional for update
            "serialized_space": json_export["serialized_space"],
            "title": json_export["title"] if "title" in json_export else "",
            "description": (
                json_export["description"] if "description" in json_export else ""
            ),
        }
        content_json = json.dumps(content)

        if (
            self.tgt_genie_space_id is None
            or str(self.tgt_genie_space_id).lower() == "none"
            or not self.tgt_genie_space_id
        ):
            # if genie target space id is none, create a new genie and import
            response = self.create_genie(content_json)
        else:
            # if tgt genie space id is specified, update the genie space
            response = self.update_genie(content_json)

        return response.status_code
