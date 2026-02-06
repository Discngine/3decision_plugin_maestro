"""
3decision API Client v1.0

Handles all communication with the 3decision API endpoints.

Version: 1.0
"""

import json
import requests
from typing import Optional, Dict, List, Any
import os
import configparser
import urllib3

# Disable SSL warnings when ignoring certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Simple logging state - stored as module-level variable
_logging_enabled = False

# SSL verification setting - enabled by default for security
_ssl_verify_enabled = True

# Private structure naming attribute - stored as module-level variable
# Options: 'label', 'title', 'external_code', 'internal_id'
_private_structure_naming_attribute = 'label'

def set_logging_enabled(enabled):
    """Enable or disable logging output"""
    global _logging_enabled
    _logging_enabled = enabled

def is_logging_enabled():
    """Check if logging is enabled"""
    global _logging_enabled
    return _logging_enabled

def set_ssl_verify_enabled(enabled):
    """Enable or disable SSL certificate verification.

    SSL verification is enabled by default for security.
    Only disable for development/internal servers with self-signed certificates.
    """
    global _ssl_verify_enabled
    _ssl_verify_enabled = enabled

def is_ssl_verify_enabled():
    """Check if SSL verification is enabled"""
    global _ssl_verify_enabled
    return _ssl_verify_enabled

def set_private_structure_naming_attribute(attribute):
    """Set the attribute to use for naming private structures.

    Args:
        attribute: One of 'label', 'title', 'external_code', or 'internal_id'
    """
    global _private_structure_naming_attribute
    if attribute in ('label', 'title', 'external_code', 'internal_id'):
        _private_structure_naming_attribute = attribute
    else:
        _private_structure_naming_attribute = 'label'  # Default

def get_private_structure_naming_attribute():
    """Get the attribute used for naming private structures.

    Returns:
        One of 'label', 'title', 'external_code', or 'internal_id'
    """
    global _private_structure_naming_attribute
    return _private_structure_naming_attribute

def log_debug(message):
    """Log a debug message if logging is enabled"""
    if _logging_enabled:
        print(f"DEBUG: {message}")

def log_error(message):
    """Log an error message if logging is enabled"""
    if _logging_enabled:
        print(f"ERROR: {message}")


class ThreeDecisionAPIClient:
    """
    Client for interacting with 3decision API

    Note: SSL certificate verification is disabled for all requests
    to support local development servers and internal APIs.
    """

    def __init__(self):
        self.base_url = None
        self.api_key = None
        self.token = None
        self.session = requests.Session()
        self.config_file = os.path.expanduser("~/.3decision_maestro_config")
        self.load_config()
        # Apply SSL verification setting (loaded from config)
        self.session.verify = is_ssl_verify_enabled()

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                config = configparser.ConfigParser()
                config.read(self.config_file)

                if 'API' in config:
                    self.base_url = config['API'].get('base_url')
                    self.api_key = config['API'].get('api_key')
                    self.token = config['API'].get('token')

                    # Load logging setting
                    log_enabled_str = config['API'].get('logging_enabled', 'false')
                    log_enabled = log_enabled_str.lower() == 'true'
                    set_logging_enabled(log_enabled)

                    # Load SSL verification setting (defaults to true for security)
                    ssl_verify_str = config['API'].get('ssl_verify', 'true')
                    ssl_verify = ssl_verify_str.lower() == 'true'
                    set_ssl_verify_enabled(ssl_verify)

                    # Load private structure naming attribute setting
                    naming_attr = config['API'].get('private_structure_naming_attribute', 'label')
                    set_private_structure_naming_attribute(naming_attr)

                    if self.token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.token}',
                            'X-API-Version': '1'
                        })

            except Exception as e:
                log_error(f"Error loading config: {e}")

    def save_config(self):
        """Save configuration to file"""
        try:
            config = configparser.ConfigParser()
            config['API'] = {
                'base_url': self.base_url or '',
                'api_key': self.api_key or '',
                'token': self.token or '',
                'logging_enabled': str(is_logging_enabled()).lower(),
                'ssl_verify': str(is_ssl_verify_enabled()).lower(),
                'private_structure_naming_attribute': get_private_structure_naming_attribute()
            }

            with open(self.config_file, 'w') as f:
                config.write(f)

            # Set restrictive permissions (owner read/write only) for security
            import stat
            os.chmod(self.config_file, stat.S_IRUSR | stat.S_IWUSR)

        except Exception as e:
            log_error(f"Error saving config: {e}")

    def _request_with_retry(self, method: str, url: str, headers: Dict = None,
                            json_data: Dict = None, params: Dict = None,
                            description: str = "request") -> Optional[requests.Response]:
        """
        Make an HTTP request with automatic retry on authentication failure.

        If the request returns 401/403, attempts to re-login and retry once.
        """
        # Ensure headers exist and have Authorization
        if headers is None:
            headers = {}
        if 'Authorization' not in headers and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        # Make initial request
        log_debug(f"{description} URL: {url}")
        log_debug(f"Request method: {method}")

        if method.upper() == 'GET':
            response = self.session.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = self.session.post(url, headers=headers, json=json_data, params=params)
        else:
            log_error(f"Unsupported HTTP method: {method}")
            return None

        log_debug(f"Response status: {response.status_code}")

        # If authentication failed, try to re-login and retry
        if response.status_code in [401, 403]:
            log_debug(f"Authentication failed for {description}, attempting re-login...")

            # Clear the old token
            self.token = None
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']

            if self.login():
                log_debug(f"Re-login successful, retrying {description}")
                # Update headers with new token
                headers['Authorization'] = f'Bearer {self.token}'

                if method.upper() == 'GET':
                    response = self.session.get(url, headers=headers, params=params)
                else:
                    response = self.session.post(url, headers=headers, json=json_data, params=params)

                log_debug(f"Retry response status: {response.status_code}")
            else:
                log_error(f"Re-login failed for {description}")
                return None

        return response

    def save_logging_setting(self, enabled: bool):
        """Save logging setting to config file"""
        set_logging_enabled(enabled)
        self.save_config()

    def save_naming_attribute_setting(self, attribute: str):
        """Save private structure naming attribute setting to config file"""
        set_private_structure_naming_attribute(attribute)
        self.save_config()

    def save_ssl_setting(self, enabled: bool):
        """Save SSL verification setting to config file"""
        set_ssl_verify_enabled(enabled)
        self.session.verify = enabled
        self.save_config()

    def configure(self, base_url: str, api_key: str):
        """Configure API settings"""
        # Ensure the URL includes the scheme
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'http://' + base_url

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.token = None

        # Update session headers
        self.session.headers.update({
            'Dng-Api-Key': self.api_key,
            'X-API-Version': '1',
            'User-Agent': 'Maestro-3decision-Plugin/1.0'
        })

        # Remove Authorization header if present
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']

    def is_configured(self) -> bool:
        """Check if API is configured"""
        return bool(self.base_url and self.api_key)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated (configured and connection works)"""
        return self.is_configured() and self.test_connection()

    def login(self) -> bool:
        """Login and get authentication token"""
        if not self.is_configured():
            return False

        try:
            url = f"{self.base_url}/auth/api/login"
            log_debug(f"Attempting login to: {url}")

            # Ensure we have the API key header for login
            headers = {
                'Dng-Api-Key': self.api_key,
                'X-API-Version': '1',
                'User-Agent': 'Maestro-3decision-Plugin/1.0'
            }

            response = self.session.get(url, headers=headers)
            log_debug(f"Response status: {response.status_code}")

            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.token = data.get('access_token')

                if self.token:
                    # Update session with token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}',
                        'X-API-Version': '1',
                        'User-Agent': 'Maestro-3decision-Plugin/1.0'
                    })
                    # Remove API key header as we now have token
                    if 'Dng-Api-Key' in self.session.headers:
                        del self.session.headers['Dng-Api-Key']

                    self.save_config()
                    log_debug("Login successful")
                    return True

            log_error(f"Login failed: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            log_error(f"Login error: {e}")
            return False

    def test_connection(self) -> bool:
        """Test API connection.

        If we have a token, we trust it's valid. The _request_with_retry method
        will handle re-authentication if the token expires during actual API calls.
        If no token exists, we attempt to login.
        """
        if not self.is_configured():
            return False

        # If we have a token, trust it - _request_with_retry handles re-auth if needed
        if self.token and 'Authorization' in self.session.headers:
            log_debug("Using existing token for connection")
            return True

        # No token - try to login
        log_debug("No token found, attempting login")
        return self.login()

    def submit_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Submit a search query and return job info"""
        if not self.test_connection():
            return None

        try:
            # Step 1: Submit search to get job ID
            url = f"{self.base_url}/search/{query}"

            response = self._request_with_retry(
                method='GET',
                url=url,
                description="Search submission"
            )

            if response is None:
                return None

            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    log_debug(f"Search response data: {data}")

                    # Extract job ID from response
                    job_id = data.get('id')
                    if job_id:
                        log_debug(f"Extracted job ID: {job_id}")

                        # Step 2: Poll the queue endpoint to get results
                        queue_url = f"{self.base_url}/queues/basicSearch/jobs/{job_id}"

                        queue_response = self._request_with_retry(
                            method='GET',
                            url=queue_url,
                            description="Queue polling"
                        )

                        if queue_response is None:
                            return None

                        if queue_response.status_code in [200, 201]:
                            queue_data = queue_response.json()
                            progress = queue_data.get("progress")
                            if progress is None:
                                progress = 0
                            log_debug(f"queue data: {queue_data}")
                            if progress == 100:
                                log_debug("Job completed (progress = 100%), extracting results")

                                # Extract structure IDs from returnvalue.STRUCTURE_ID
                                structure_ids = []
                                if 'returnvalue' in queue_data and 'STRUCTURE_ID' in queue_data['returnvalue']:
                                    structure_ids = queue_data['returnvalue']['STRUCTURE_ID']
                                    log_debug(f"Extracted structure IDs: {structure_ids}")

                                # If we have structure IDs, fetch detailed info via GraphQL
                                if structure_ids:
                                    structures_info = self.get_structures_info(structure_ids)
                                    log_debug(f"Retrieved {len(structures_info)} structure details")

                                    # Return the complete job data with structure details
                                    queue_data['structures_info'] = structures_info
                                    return queue_data
                                else:
                                    log_debug("No structure IDs found in queue response - job completed with no results")
                                    queue_data['structures_info'] = []
                                    return queue_data
                            else:
                                log_debug(f"Job still in progress ({progress}%), need to poll again")
                                return {
                                    'id': job_id,
                                    'queue': 'basicSearch',
                                    'status': 'running',
                                    'progress': progress,
                                    'polling_needed': True
                                }
                        else:
                            log_error(f"Queue polling failed: {queue_response.status_code} - {queue_response.text}")
                            return None
                    else:
                        log_debug("No job ID found in search response")
                        return {
                            'id': 'direct',
                            'queue': 'direct',
                            'status': 'completed',
                            'result': data
                        }

                except json.JSONDecodeError:
                    log_error(f"Non-JSON response from search: {response.text}")
                    return None

            else:
                log_error(f"Search submission failed: {response.status_code}")
                log_error(f"Response text: {response.text}")
                return None

        except Exception as e:
            log_error(f"Search submission error: {e}")
            import traceback
            log_error(f"Full traceback: {traceback.format_exc()}")
            return None

    def get_job_status(self, queue_name: str, job_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a job"""
        if not self.test_connection():
            return None

        try:
            url = f"{self.base_url}/queues/{queue_name}/jobs/{job_id}"

            response = self._request_with_retry(
                method='GET',
                url=url,
                description="Job status check"
            )

            if response is None:
                return None

            if response.status_code in [200, 201]:
                data = response.json()
                log_debug(f"Job status response data: {data}")
                return data
            else:
                log_error(f"Job status check failed: {response.status_code}")
                return None

        except Exception as e:
            log_error(f"Job status error: {e}")
            return None

    def get_structures_info(self, structure_ids: List[int]) -> List[Dict[str, Any]]:
        """Get detailed information for structures using GraphQL"""
        if not self.test_connection():
            return []

        try:
            # If we have more than 500 structures, split into batches
            batch_size = 500
            all_structures = []

            if len(structure_ids) > batch_size:
                log_debug(f"Large dataset detected ({len(structure_ids)} structures). Splitting into batches of {batch_size}...")

                for i in range(0, len(structure_ids), batch_size):
                    batch_ids = structure_ids[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(structure_ids) + batch_size - 1) // batch_size

                    log_debug(f"Processing batch {batch_num}/{total_batches} ({len(batch_ids)} structures)...")

                    batch_structures = self._fetch_structures_batch(batch_ids)
                    if batch_structures:
                        all_structures.extend(batch_structures)
                        log_debug(f"Batch {batch_num} completed: {len(batch_structures)} structures retrieved")

                log_debug(f"All batches completed. Total structures retrieved: {len(all_structures)}")
                return all_structures
            else:
                log_debug(f"Small dataset ({len(structure_ids)} structures). Using single request...")
                return self._fetch_structures_batch(structure_ids)

        except Exception as e:
            log_error(f"Structures info error: {e}")
            return []

    def _fetch_structures_batch(self, structure_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch a batch of structures using GraphQL"""
        try:
            query = """
            query GetStructuresInfo($ids: [Int!]!) {
                getStructuresInfo(ids: $ids) {
                    structure_id
                    general {
                        structure_id
                        external_code
                        title
                        method
                        resolution
                        created_date
                        imported_date
                        created_by
                        imported_by
                        source
                    }
                }
            }
            """

            variables = {"ids": structure_ids}

            url = f"{self.base_url}/graphql"
            payload = {
                "query": query,
                "variables": variables
            }

            log_debug(f"GraphQL batch request (batch size: {len(structure_ids)})")

            response = self._request_with_retry(
                method='POST',
                url=url,
                json_data=payload,
                description="GraphQL structures batch"
            )

            if response is None:
                return []

            if response.status_code in [200, 201]:
                data = response.json()

                if 'data' in data and 'getStructuresInfo' in data['data']:
                    batch_results = data['data']['getStructuresInfo']

                    # Remove duplicates based on structure_id (NMR structures with multiple states)
                    seen_ids = set()
                    unique_structures = []
                    for structure in batch_results:
                        structure_id = structure.get('structure_id')
                        if structure_id and structure_id not in seen_ids:
                            seen_ids.add(structure_id)
                            unique_structures.append(structure)

                    return unique_structures
                else:
                    log_error(f"Unexpected GraphQL response structure")
                    return []
            else:
                log_error(f"GraphQL batch query failed: {response.status_code}")
                return []

        except Exception as e:
            log_error(f"Batch fetch error: {e}")
            return []

    def get_structure_internal_id(self, structure_id: int) -> Optional[str]:
        """
        Fetch the internal_id annotation for a structure.
        """
        if not self.test_connection():
            return None

        try:
            url = f"{self.base_url}/structures/info/annotation"
            params = {
                "structure_id": [int(structure_id)]
            }
            headers = {
                'X-API-VERSION': '1'
            }

            log_debug(f"Fetching internal_id for structure_id: {structure_id}")

            response = self._request_with_retry(
                method='GET',
                url=url,
                headers=headers,
                params=params,
                description=f"Structure annotations for structure_id {structure_id}"
            )

            if response is None:
                return None

            if response.status_code in [200, 201]:
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    structure_data = data[0]
                    annotation_info = structure_data.get('ANNOTATION_INFO', {})
                    structure_annots = annotation_info.get('StructureAnnot', [])

                    for annot in structure_annots:
                        if annot.get('ANNOT_TYPE_LABEL', '').lower() == 'internal id':
                            internal_id = annot.get('ANNOT_VALUE')
                            if internal_id:
                                log_debug(f"Found internal_id for structure_id {structure_id}: {internal_id}")
                                return internal_id

                log_debug(f"No internal_id annotation found for structure_id {structure_id}")
                return None
            else:
                log_error(f"Structure annotations request failed: {response.status_code}")
                return None

        except Exception as e:
            log_error(f"Get internal_id error: {e}")
            return None

    def export_structure_pdb(self, structure_id: str) -> Optional[str]:
        """Export structure in PDB format"""
        if not self.test_connection():
            return None

        try:
            url = f"{self.base_url}/exports/structure"
            params = {"output_format": "structures-pdb-txt"}

            payload = {
                "structures_id": [int(structure_id)]
            }

            log_debug(f"Export request params: {params}")

            response = self._request_with_retry(
                method='POST',
                url=url,
                json_data=payload,
                params=params,
                description="Structure export"
            )

            if response is None:
                return None

            if response.status_code in [200, 201]:
                domain_event_id = response.text.strip()
                log_debug(f"Received domain event ID: {domain_event_id}")

                if domain_event_id:
                    domain_events_url = f"{self.base_url}/domain-events/{domain_event_id}"
                    log_debug(f"Polling domain events endpoint: {domain_events_url}")

                    max_attempts = 30
                    attempt = 0

                    while attempt < max_attempts:
                        log_debug(f"Domain events poll attempt {attempt + 1}/{max_attempts}")

                        domain_response = self._request_with_retry(
                            method='GET',
                            url=domain_events_url,
                            description="Export domain events polling"
                        )

                        if domain_response is None:
                            return None

                        if domain_response.status_code in [200, 201]:
                            try:
                                domain_data = domain_response.json()
                                state = domain_data.get('state')
                                log_debug(f"Export state: {state}")

                                if state == 'success':
                                    content = domain_data.get('content', {})
                                    errors = content.get('errors', {})
                                    not_exported = errors.get('not_exported', [])

                                    if not_exported:
                                        log_error(f"Export completed with errors: {not_exported}")
                                        return None
                                    else:
                                        log_debug("Export completed successfully")

                                        file_names = content.get('file_names', [])
                                        if file_names and len(file_names) > 0:
                                            first_file = file_names[0]
                                            if isinstance(first_file, dict):
                                                filename = first_file.get("file_name")
                                            else:
                                                log_error(f"Unexpected file_names structure")
                                                return None

                                            if not filename:
                                                log_error("No filename found in file_names entry")
                                                return None

                                            filename_without_ext = filename
                                            if '.' in filename:
                                                filename_without_ext = filename.rsplit('.', 1)[0]

                                            download_url = f"{self.base_url}/exports/structure/{domain_event_id}?filename={filename_without_ext}&download=true"

                                            download_response = self._request_with_retry(
                                                method='GET',
                                                url=download_url,
                                                description="PDB file download"
                                            )

                                            if download_response is None:
                                                return None

                                            if download_response.status_code in [200, 201]:
                                                pdb_content = download_response.text
                                                log_debug(f"Download successful, PDB content length: {len(pdb_content)} characters")
                                                return pdb_content
                                            else:
                                                log_error(f"Download failed: {download_response.status_code}")
                                                return None
                                        else:
                                            log_error("No filename found in export response")
                                            return None

                                elif state == 'failed':
                                    log_error("Export failed")
                                    return None
                                else:
                                    log_debug(f"Export still processing (state: {state}), waiting...")
                                    import time
                                    time.sleep(2)
                                    attempt += 1
                                    continue

                            except json.JSONDecodeError as e:
                                log_error(f"Failed to parse domain events response: {e}")
                                return None
                        else:
                            log_error(f"Domain events request failed: {domain_response.status_code}")
                            return None

                    log_error("Export polling timed out")
                    return None
                else:
                    log_error("No domain event ID received")
                    return None
            else:
                log_error(f"Export request failed: {response.status_code}")
                return None

        except Exception as e:
            log_error(f"Structure export error: {e}")
            import traceback
            log_error(f"Full traceback: {traceback.format_exc()}")
            return None

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of available projects"""
        if not self.is_configured():
            raise Exception("API not configured")

        if not self.test_connection():
            raise Exception("Not authenticated")

        try:
            url = f"{self.base_url}/projects"
            headers = {
                "Accept": "application/json"
            }

            response = self._request_with_retry(
                method='GET',
                url=url,
                headers=headers,
                description="Projects request"
            )

            if response is None:
                raise Exception("Authentication failed - please check your API key in Settings")

            if response.status_code == 200:
                projects_data = response.json()
                log_debug(f"Projects response: {projects_data}")

                if isinstance(projects_data, list):
                    return projects_data
                elif isinstance(projects_data, dict):
                    if 'projects' in projects_data:
                        return projects_data['projects']
                    elif 'results' in projects_data:
                        return projects_data['results']
                    else:
                        log_error(f"Unexpected projects response format: {projects_data}")
                        return []
                else:
                    log_error(f"Unexpected projects response format: {projects_data}")
                    return []

            else:
                log_error(f"Projects request failed: {response.status_code}")
                raise Exception(f"Projects request failed: {response.status_code}")

        except Exception as e:
            log_error(f"Projects request error: {e}")
            raise

    def get_project_structures(self, project_id: str) -> List[Dict[str, Any]]:
        """Get structures from a specific project with transformation matrices"""
        if not self.is_configured():
            raise Exception("API not configured")

        if not self.test_connection():
            raise Exception("Not authenticated")

        try:
            url = f"{self.base_url}/projects/{project_id}/structures/matrix"
            headers = {
                "Accept": "application/json"
            }

            response = self._request_with_retry(
                method='GET',
                url=url,
                headers=headers,
                description="Project structures request"
            )

            if response is None:
                raise Exception("Authentication failed - please check your API key in Settings")

            if response.status_code == 200:
                structures_data = response.json()
                log_debug(f"Project structures response: {structures_data}")

                if isinstance(structures_data, list):
                    return structures_data
                elif isinstance(structures_data, dict) and 'results' in structures_data:
                    return structures_data['results']
                else:
                    log_error(f"Unexpected project structures response format: {structures_data}")
                    return []

            else:
                log_error(f"Project structures request failed: {response.status_code}")
                raise Exception(f"Project structures request failed: {response.status_code}")

        except Exception as e:
            log_error(f"Project structures request error: {e}")
            raise

    def export_structures_with_transforms(self, structures_with_transforms: List[Dict]) -> Optional[Dict[str, str]]:
        """Export multiple structures with transformation matrices using batch export"""
        if not self.test_connection():
            return None

        try:
            if len(structures_with_transforms) > 1:
                log_debug(f"Exporting {len(structures_with_transforms)} structures with transformations as ZIP")

                matrix_payload = [
                    {
                        "external_code": item["external_code"],
                        "structure_id": item["structure_id"],
                        "transform": item["transform"]
                    }
                    for item in structures_with_transforms
                ]

                structure_ids = [item["structure_id"] for item in structures_with_transforms]

                zip_content = self.download_structures_zip(structure_ids, matrix_payload)

                if not zip_content:
                    log_error("Failed to download structures as ZIP")
                    return None

                import zipfile
                import io

                pdb_files_dict = {}

                try:
                    with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                        file_list = zip_ref.namelist()
                        log_debug(f"ZIP contains {len(file_list)} files: {file_list}")

                        pdb_files = [f for f in file_list if f.endswith('.pdb')]
                        log_debug(f"Found {len(pdb_files)} PDB files in ZIP")

                        for pdb_filename in pdb_files:
                            log_debug(f"Extracting {pdb_filename} from ZIP")
                            pdb_content = zip_ref.read(pdb_filename).decode('utf-8')
                            base_filename = pdb_filename.split('/')[-1]
                            pdb_files_dict[base_filename] = pdb_content

                        if pdb_files_dict:
                            log_debug(f"Successfully extracted {len(pdb_files_dict)} structures from ZIP")
                            return pdb_files_dict
                        else:
                            log_error("No PDB files were extracted from ZIP")
                            return None

                except zipfile.BadZipFile as e:
                    log_error(f"Invalid ZIP file: {e}")
                    return None
                except Exception as e:
                    log_error(f"Error extracting PDB files from ZIP: {e}")
                    return None

            else:
                # Single structure
                url = f"{self.base_url}/exports/structure"

                matrix_payload = {
                    "external_codes": [item["external_code"] for item in structures_with_transforms],
                    "matrix": [
                        {
                            "external_code": item["external_code"],
                            "structure_id": item["structure_id"],
                            "transform": item["transform"]
                        }
                        for item in structures_with_transforms
                    ]
                }

                params = {
                    "output_format": "structures-pdb-txt"
                }

                log_debug(f"Batch export payload: {json.dumps(matrix_payload, indent=2)}")

                response = self._request_with_retry(
                    method='POST',
                    url=url,
                    json_data=matrix_payload,
                    params=params,
                    description="Batch export (single structure)"
                )

                if response is None:
                    return None

            if response.status_code in [200, 201]:
                domain_event_id = response.text.strip()
                log_debug(f"Received domain event ID: {domain_event_id}")

                if domain_event_id:
                    domain_events_url = f"{self.base_url}/domain-events/{domain_event_id}"

                    max_attempts = 30
                    attempt = 0

                    while attempt < max_attempts:
                        domain_response = self._request_with_retry(
                            method='GET',
                            url=domain_events_url,
                            description="Batch export domain events polling"
                        )

                        if domain_response is None:
                            return None

                        if domain_response.status_code in [200, 201]:
                            try:
                                domain_data = domain_response.json()
                                state = domain_data.get('state')

                                if state == 'success':
                                    content = domain_data.get('content', {})
                                    errors = content.get('errors', {})
                                    not_exported = errors.get('not_exported', [])

                                    if not_exported:
                                        log_error(f"Batch export completed with errors: {not_exported}")
                                        return None

                                    log_debug("Batch export completed successfully")

                                    file_names = content.get('file_names', [])
                                    if file_names and len(file_names) > 0:
                                        first_file = file_names[0]
                                        if isinstance(first_file, dict):
                                            filename = first_file.get("file_name")
                                        else:
                                            log_error(f"Unexpected file_names structure: {first_file}")
                                            return None

                                        if not filename:
                                            log_error("No filename found in file_names entry")
                                            return None

                                        filename_without_ext = filename
                                        if '.' in filename:
                                            filename_without_ext = filename.rsplit('.', 1)[0]

                                        download_url = f"{self.base_url}/exports/structure/{domain_event_id}?filename={filename_without_ext}&download=true"

                                        download_response = self._request_with_retry(
                                            method='GET',
                                            url=download_url,
                                            description="Batch export PDB download"
                                        )

                                        if download_response is None:
                                            return None

                                        if download_response.status_code == 200:
                                            pdb_content = download_response.text
                                            log_debug(f"Successfully downloaded PDB content: {len(pdb_content)} bytes")
                                            external_code = structures_with_transforms[0]["external_code"]
                                            return {f"{external_code}.pdb": pdb_content}
                                        else:
                                            log_error(f"Failed to download PDB: {download_response.status_code}")
                                            return None
                                    else:
                                        log_error("No file_names found in export response")
                                        return None

                                elif state == 'failed':
                                    log_error("Batch export failed")
                                    return None

                            except Exception as e:
                                log_error(f"Error parsing domain event response: {e}")

                        attempt += 1
                        if attempt < max_attempts:
                            import time
                            time.sleep(2)

                    log_error("Batch export polling timed out")
                    return None
                else:
                    log_error("No domain event ID received")
                    return None
            else:
                log_error(f"Batch export request failed: {response.status_code}")
                return None

        except Exception as e:
            log_error(f"Batch export error: {e}")
            import traceback
            log_error(f"Full traceback: {traceback.format_exc()}")
            return None

    def download_structures_zip(self, structure_ids: List[int], matrices: List[Dict] = None) -> Optional[bytes]:
        """Download structures as a ZIP file"""
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            url = f"{self.base_url}/exports/structure"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

            payload = {
                "structures_id": structure_ids
            }

            if matrices:
                payload["matrix"] = matrices

            params = {
                "output_format": "structures-pdb-zip"
            }

            log_debug(f"Structure IDs: {structure_ids}")

            response = self._request_with_retry(
                method='POST',
                url=url,
                headers=headers,
                json_data=payload,
                params=params,
                description="ZIP export request"
            )

            if response is None:
                return None

            if response.status_code in [200, 201]:
                domain_event_id = response.text.strip()
                log_debug(f"Received domain event ID: {domain_event_id}")

                if domain_event_id:
                    domain_events_url = f"{self.base_url}/domain-events/{domain_event_id}"

                    max_attempts = 30
                    attempt = 0

                    while attempt < max_attempts:
                        domain_response = self._request_with_retry(
                            method='GET',
                            url=domain_events_url,
                            description="ZIP export domain events polling"
                        )

                        if domain_response is None:
                            return None

                        if domain_response.status_code in [200, 201]:
                            try:
                                domain_data = domain_response.json()
                                state = domain_data.get('state')

                                if state == 'success':
                                    content = domain_data.get('content', {})
                                    errors = content.get('errors', {})
                                    not_exported = errors.get('not_exported', [])

                                    if not_exported:
                                        log_error(f"Export completed with errors: {not_exported}")
                                        return None
                                    else:
                                        log_debug("Export completed successfully")

                                        file_names = content.get('file_names', [])

                                        if file_names and len(file_names) > 0:
                                            first_file = file_names[0]

                                            if isinstance(first_file, dict):
                                                filename = first_file.get("file_name")
                                            else:
                                                log_error(f"Unexpected file_names structure")
                                                return None

                                            if not filename:
                                                log_error("No filename found in file_names entry")
                                                return None

                                            filename_without_ext = filename
                                            if '.' in filename:
                                                filename_without_ext = filename.rsplit('.', 1)[0]

                                            download_url = f"{self.base_url}/exports/structure/{domain_event_id}?filename={filename_without_ext}&download=true"

                                            download_response = self._request_with_retry(
                                                method='GET',
                                                url=download_url,
                                                description="ZIP file download"
                                            )

                                            if download_response is None:
                                                return None

                                            if download_response.status_code in [200, 201]:
                                                zip_content = download_response.content
                                                log_debug(f"Download successful, ZIP content length: {len(zip_content)} bytes")

                                                if len(zip_content) > 4 and zip_content[:2] == b'PK':
                                                    log_debug("Confirmed ZIP file format (starts with PK signature)")
                                                    return zip_content
                                                else:
                                                    log_debug(f"Warning: Downloaded content may not be a ZIP file")
                                                    return zip_content
                                            else:
                                                log_error(f"Download failed: {download_response.status_code}")
                                                return None
                                        else:
                                            log_error("No filename found in export response")
                                            return None

                                elif state == 'failed':
                                    log_error("Export failed")
                                    return None
                                else:
                                    log_debug(f"Export still processing (state: {state}), waiting...")
                                    import time
                                    time.sleep(2)
                                    attempt += 1
                                    continue

                            except json.JSONDecodeError as e:
                                log_error(f"Failed to parse domain events response: {e}")
                                return None
                        else:
                            log_error(f"Domain events request failed: {domain_response.status_code}")
                            return None

                    log_error("Export polling timed out")
                    return None
                else:
                    log_error("No domain event ID received")
                    return None
            else:
                log_error(f"Export request failed: {response.status_code}")
                return None

        except Exception as e:
            log_error(f"ZIP download error: {e}")
            return None

    def get_associated_files(self, external_code: str) -> List[Dict[str, Any]]:
        """Get associated files for a structure by external code"""
        try:
            if not self.test_connection():
                log_error("Not authenticated for associated files request")
                return []

            url = f"{self.base_url}/structures/{external_code}/associated-files"
            headers = {
                "Accept": "application/json"
            }

            response = self._request_with_retry(
                method='GET',
                url=url,
                headers=headers,
                description="Associated files request"
            )

            if response is None:
                return []

            if response.status_code == 200:
                files_data = response.json()
                log_debug(f"Associated files response: {json.dumps(files_data, indent=2)}")

                if isinstance(files_data, list):
                    return files_data
                elif isinstance(files_data, dict):
                    if 'files' in files_data:
                        return files_data['files']
                    elif 'results' in files_data:
                        return files_data['results']
                    else:
                        log_error(f"Unexpected associated files response format: {files_data}")
                        return []
                else:
                    log_error(f"Unexpected associated files response format: {files_data}")
                    return []

            elif response.status_code == 404:
                log_debug("No associated files found (404)")
                return []
            else:
                log_error(f"Associated files request failed: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            log_error(f"Associated files request error: {e}")
            return []

    def download_file_by_id(self, file_id: str) -> Optional[bytes]:
        """Download file content by ID"""
        try:
            if not self.test_connection():
                log_error("Not authenticated for file download")
                return None

            url = f"{self.base_url}/structures/file/{file_id}/download"

            response = self._request_with_retry(
                method='GET',
                url=url,
                description="File download"
            )

            if response is None:
                return None

            if response.status_code == 200:
                log_debug(f"File downloaded successfully: {len(response.content)} bytes")
                return response.content
            else:
                log_error(f"File download failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            log_error(f"File download error: {e}")
            return None

    def download_file(self, file_info: Dict[str, Any]) -> Optional[bytes]:
        """Download file using file info dictionary"""
        file_id = file_info.get('id') or file_info.get('file_id') or file_info.get('FILE_ID')

        if not file_id:
            download_url = file_info.get('download_url') or file_info.get('url')
            if download_url:
                return self._download_from_url(download_url)
            else:
                log_error("No file ID or download URL found in file info")
                return None

        return self.download_file_by_id(str(file_id))

    def _download_from_url(self, url: str) -> Optional[bytes]:
        """Download file from direct URL"""
        try:
            if not self.test_connection():
                log_error("Not authenticated for URL download")
                return None

            response = self._request_with_retry(
                method='GET',
                url=url,
                description="Direct URL download"
            )

            if response is None:
                return None

            if response.status_code == 200:
                content = response.content
                log_debug(f"Direct URL download successful: {len(content)} bytes")
                return content
            else:
                log_error(f"Direct URL download failed: {response.status_code}")
                return None

        except Exception as e:
            log_error(f"Direct URL download error: {e}")
            return None
