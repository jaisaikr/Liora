# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import FailedPrecondition
from google.cloud import documentai
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("DOCAI_LOCATION", "us")
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

def create_layout_parser_processor(project_id: str, location: str, processor_display_name: str = "RAG Layout Parser") -> str:
    """Create a Document AI Layout Parser processor.

    Args:
        project_id: Google Cloud project ID
        location: Processor location ('us' or 'eu')
        processor_display_name: Display name for the processor

    Returns:
        Processor ID string
    """
    print(f"🔄 Creating Document AI Layout Parser processor...")

    # Set API endpoint based on location
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the location
    parent = client.common_location_path(project_id, location)

    # Create a processor
    processor = client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            display_name=processor_display_name,
            type_="LAYOUT_PARSER_PROCESSOR"
        ),
    )

    # Extract processor ID from the full resource name
    # Format: projects/PROJECT_ID/locations/LOCATION/processors/PROCESSOR_ID
    processor_id = processor.name.split("/")[-1]

    print(f"✅ Processor created successfully!")
    print(f"   Processor Name: {processor.name}")
    print(f"   Processor Display Name: {processor.display_name}")
    print(f"   Processor ID: {processor_id}")
    print(f"   Processor Type: {processor.type_}")

    return processor_id


def enable_processor(project_id: str, location: str, processor_id: str) -> bool:
    """Enable a Document AI processor.

    Args:
        project_id: Google Cloud project ID
        location: Processor location ('us' or 'eu')
        processor_id: Processor ID to enable

    Returns:
        True if successful, False otherwise
    """
    print(f"🔄 Enabling Document AI processor: {processor_id}")

    # Set API endpoint based on location
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor
    processor_name = client.processor_path(project_id, location, processor_id)
    request = documentai.EnableProcessorRequest(name=processor_name)

    try:
        operation = client.enable_processor(request=request)
        print(f"   Operation started: {operation.operation.name}")

        # Wait for operation to complete
        print("   Waiting for operation to complete...")
        operation.result()

        print("✅ Processor enabled successfully!")
        return True

    except FailedPrecondition as e:
        if "already enabled" in str(e).lower():
            print("✅ Processor is already enabled!")
            return True
        else:
            print(f"❌ Failed to enable processor: {e}")
            return False
    except Exception as e:
        print(f"❌ Error enabling processor: {e}")
        return False


def update_env_file(processor_id: str):
    """Update the .env file with the processor ID."""
    try:
        set_key(ENV_FILE_PATH, "DOCAI_PROCESSOR_ID", processor_id)
        print(f"✅ Updated DOCAI_PROCESSOR_ID in {ENV_FILE_PATH}")
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")


def setup_docai_processor():
    """Complete setup of Document AI Layout Parser processor."""
    if not PROJECT_ID:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set.")
        return False

    print(f"🚀 Setting up Document AI Layout Parser for project: {PROJECT_ID}")
    print(f"   Location: {LOCATION}")

    try:
        # Step 1: Create the processor
        processor_id = create_layout_parser_processor(PROJECT_ID, LOCATION)

        # Step 2: Enable the processor
        enabled = enable_processor(PROJECT_ID, LOCATION, processor_id)

        if enabled:
            # Step 3: Update .env file
            update_env_file(processor_id)

            print(f"\n🎉 Document AI Layout Parser setup complete!")
            print(f"   Processor ID: {processor_id}")
            print(f"   Location: {LOCATION}")
            print(f"\nYou can now run the RAG corpus preparation script to import PDFs with automatic")
            print(f"fallback to Document AI Layout Parser for scanned documents.")

            return True
        else:
            print(f"\n❌ Failed to enable processor. Please check your permissions.")
            return False

    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False


if __name__ == "__main__":
    setup_docai_processor()