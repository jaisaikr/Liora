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

from google.auth import default
from google.api_core.exceptions import ResourceExhausted
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag import TransformationConfig, ChunkingConfig
import os
import time
import json
import base64
from dotenv import load_dotenv, set_key
import requests
import tempfile
from google.cloud import storage
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import FailedPrecondition
from typing import List, Tuple

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )
CORPUS_DISPLAY_NAME = "airbnb_founder_corpus"
CORPUS_DESCRIPTION = "Corpus containing Airbnb pitch deck document"
# PDF_URL = "https://abc.xyz/assets/77/51/9841ad5c4fbe85b4440c47a4df8d/goog-10-k-2024.pdf"
# PDF_FILENAME = "goog-10-k-2024.pdf"

# GCS Configuration
GCS_BUCKET_NAME = os.getenv("GCS_CORPUS_BUCKET_NAME")
if not GCS_BUCKET_NAME:
    raise ValueError(
        "GCS_CORPUS_BUCKET_NAME environment variable not set. Please set it in your .env file."
    )
GCS_FOLDER_PATH = os.getenv("GCS_CORPUS_FOLDER_PATH", "")  # Optional subfolder

# Document AI Configuration
DOCAI_PROCESSOR_ID = os.getenv("DOCAI_PROCESSOR_ID")
DOCAI_LOCATION = os.getenv("DOCAI_LOCATION", "us")

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# --- Start of the script ---
def initialize_vertex_ai():
  credentials, _ = default()
  vertexai.init(
      project=PROJECT_ID, location=LOCATION, credentials=credentials
  )


def create_or_get_corpus():
  """Creates a new corpus or retrieves an existing one."""
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-005"
  )
  existing_corpora = rag.list_corpora()
  corpus = None
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
      break
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
  return corpus


def download_pdf_from_url(url, output_path):
  """Downloads a PDF file from the specified URL."""
  print(f"Downloading PDF from {url}...")
  response = requests.get(url, stream=True)
  response.raise_for_status()  # Raise an exception for HTTP errors
  
  with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
      f.write(chunk)
  
  print(f"PDF downloaded successfully to {output_path}")
  return output_path


def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
  """Uploads a PDF file to the specified corpus."""
  print(f"Uploading {display_name} to corpus...")
  try:
    rag_file = rag.upload_file(
        corpus_name=corpus_name,
        path=pdf_path,
        display_name=display_name,
        description=description,
    )
    print(f"Successfully uploaded {display_name} to corpus")
    return rag_file
  except ResourceExhausted as e:
    print(f"Error uploading file {display_name}: {e}")
    print("\nThis error suggests that you have exceeded the API quota for the embedding model.")
    print("This is common for new Google Cloud projects.")
    print("Please see the 'Troubleshooting' section in the README.md for instructions on how to request a quota increase.")
    return None
  except Exception as e:
    print(f"Error uploading file {display_name}: {e}")
    return None

def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def list_corpus_files(corpus_name):
  """Lists files in the specified corpus."""
  files = list(rag.list_files(corpus_name=corpus_name))
  print(f"Total files in corpus: {len(files)}")
  for file in files:
    print(f"File: {file.display_name} - {file.name}")



def setup_processor(project_id: str, location: str, processor_display_name: str = "Layout Parser Processor") -> str:
  """Setup a LAYOUT_PARSER_PROCESSOR - check if exists, create if needed, and ensure it's enabled.

  Args:
    project_id: Google Cloud project ID
    location: Processor location (e.g., 'us' or 'eu')
    processor_display_name: Display name for the processor

  Returns:
    The processor ID if successful, None otherwise
  """
  try:
    # Set up client with proper endpoint
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # List existing processors to check if one already exists
    parent = client.common_location_path(project_id, location)
    processors = client.list_processors(parent=parent)

    layout_parser_processor = None
    for processor in processors:
      if processor.type_ == "LAYOUT_PARSER_PROCESSOR":
        layout_parser_processor = processor
        processor_id = processor.name.split("/")[-1]
        print(f"📋 Found existing Layout Parser Processor: {processor_id}")
        break

    # If processor doesn't exist, create it
    if not layout_parser_processor:
      print(f"🔄 Creating new Layout Parser Processor...")
      processor = client.create_processor(
          parent=parent,
          processor=documentai.Processor(
              display_name=processor_display_name,
              type_="LAYOUT_PARSER_PROCESSOR"
          ),
      )
      layout_parser_processor = processor
      processor_id = processor.name.split("/")[-1]
      print(f"✅ Created Processor ID: {processor_id}")

    # Check if processor is enabled
    if layout_parser_processor.state != documentai.Processor.State.ENABLED:
      print(f"🔄 Enabling processor {processor_id}...")
      processor_name = client.processor_path(project_id, location, processor_id)
      request = documentai.EnableProcessorRequest(name=processor_name)

      try:
        operation = client.enable_processor(request=request)
        operation.result()  # Wait for operation to complete
        print(f"✅ Processor {processor_id} enabled successfully!")
      except FailedPrecondition as e:
        if "already enabled" in str(e):
          print(f"ℹ️  Processor {processor_id} is already enabled")
        else:
          raise e
    else:
      print(f"✅ Processor {processor_id} is already enabled")

    return processor_id

  except Exception as e:
    print(f"❌ Error setting up Layout Parser Processor: {e}")
    return None


def process_pdf_with_layout_parser(pdf_gcs_path: str, chunk_size: int = 1024) -> str:
  """Process PDF through Document AI Layout Parser.

  Args:
    pdf_gcs_path: GCS path to the PDF file (e.g., gs://bucket/file.pdf)
    chunk_size: Chunk size for layout parser

  Returns:
    Extracted text content as string
  """
  print(f"🔄 Processing PDF with Document AI Layout Parser: {pdf_gcs_path}")

  try:
    # Ensure processor is setup and enabled before processing
    processor_id = setup_processor(PROJECT_ID, DOCAI_LOCATION)
    if not processor_id:
      raise ValueError("Failed to setup Document AI Layout Parser processor")

    print(f"✅ Using processor: {processor_id}")

    # Initialize DocAI client
    opts = ClientOptions(api_endpoint=f"{DOCAI_LOCATION}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # Download PDF content from GCS
    storage_client = storage.Client(project=PROJECT_ID)
    bucket_name = pdf_gcs_path.replace("gs://", "").split("/")[0]
    blob_path = "/".join(pdf_gcs_path.replace("gs://", "").split("/")[1:])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    pdf_content = blob.download_as_bytes()

    # Prepare the request
    processor_name = f"projects/{PROJECT_ID}/locations/{DOCAI_LOCATION}/processors/{processor_id}"

    # Configure the request
    raw_document = documentai.RawDocument(
        content=pdf_content,
        mime_type="application/pdf"
    )

    # Configure layout processing options
    layout_config = documentai.ProcessOptions.LayoutConfig(
        chunking_config=documentai.ProcessOptions.LayoutConfig.ChunkingConfig(
            chunk_size=chunk_size,
            include_ancestor_headings=True
        )
    )

    process_options = documentai.ProcessOptions(layout_config=layout_config)

    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document,
        process_options=process_options
    )

    # Process the document
    print("📄 Sending PDF to Document AI Layout Parser...")
    result = client.process_document(request=request)

    # Extract text from the result
    text_content = extract_text_from_docai_response(result.document)

    print(f"✅ Successfully processed PDF. Extracted {len(text_content)} characters of text.")
    return text_content

  except Exception as e:
    print(f"❌ Error processing PDF with Document AI: {e}")
    raise


def extract_text_from_docai_response(document) -> str:
  """Extract formatted text from Document AI response.

  Args:
    document: Document AI document response

  Returns:
    Formatted text content preserving document structure
  """
  text_content = []

  try:
    # If document has chunked content, use that for better structure
    if hasattr(document, 'chunked_document') and document.chunked_document:
      print("📋 Using chunked document structure")
      for chunk in document.chunked_document.chunks:
        if hasattr(chunk, 'content') and chunk.content:
          text_content.append(chunk.content)

    # Fallback to document text if no chunks
    elif hasattr(document, 'text') and document.text:
      print("📋 Using document text")
      text_content.append(document.text)

    # Join all text content
    full_text = "\n\n".join(text_content)

    if not full_text.strip():
      raise ValueError("No text content extracted from document")

    return full_text

  except Exception as e:
    print(f"❌ Error extracting text from DocAI response: {e}")
    raise


def upload_processed_text_to_gcs(text_content: str, original_pdf_path: str) -> str:
  """Upload processed text content to GCS as a .txt file.

  Args:
    text_content: Extracted text content
    original_pdf_path: Original PDF GCS path

  Returns:
    GCS path to the uploaded text file
  """
  try:
    # Generate text file path based on original PDF path
    text_file_path = original_pdf_path.replace(".pdf", "_processed.txt")

    # Parse GCS path
    bucket_name = text_file_path.replace("gs://", "").split("/")[0]
    blob_path = "/".join(text_file_path.replace("gs://", "").split("/")[1:])

    # Upload to GCS
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    # Upload text content
    blob.upload_from_string(text_content, content_type="text/plain")

    print(f"✅ Uploaded processed text to: {text_file_path}")
    return text_file_path

  except Exception as e:
    print(f"❌ Error uploading processed text to GCS: {e}")
    raise


def parse_import_failures(partial_failures_sink: str, bucket_name: str) -> List[str]:
  """Parse partial failures log to identify failed PDF files.

  Args:
    partial_failures_sink: GCS path to failures log
    bucket_name: GCS bucket name

  Returns:
    List of failed PDF file paths
  """
  failed_pdfs = []

  try:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob_name = partial_failures_sink.replace(f"gs://{bucket_name}/", "")
    blob = bucket.blob(blob_name)

    if not blob.exists():
      print("⚠️  No failure log found")
      return failed_pdfs

    # Read and parse failure log
    error_logs = blob.download_as_text()

    for line in error_logs.strip().split('\n'):
      if not line.strip():
        continue

      try:
        log_entry = json.loads(line)

        # Check if this is a PDF text extraction failure
        if (log_entry.get("Status") == "INVALID_ARGUMENT" and
            "PDF was invalid or file contains no text pages" in log_entry.get("Message", "") and
            log_entry.get("Filename", "").endswith(".pdf")):

          failed_pdfs.append(log_entry["Filename"])
          print(f"📄 Found failed PDF: {log_entry['Filename']}")

      except json.JSONDecodeError:
        continue

    return failed_pdfs

  except Exception as e:
    print(f"⚠️  Error parsing import failures: {e}")
    return failed_pdfs


def import_files_from_gcs(corpus_name: str, bucket_name: str, folder_path: str = "", chunk_size: int = 1024, chunk_overlap: int = 200):
  """Imports files from GCS directly into the RAG corpus using rag.import_files.

  Args:
    corpus_name: Name of the RAG corpus
    bucket_name: Name of the GCS bucket
    folder_path: Optional folder path within the bucket
    chunk_size: Number of tokens each chunk should have (default: 1024)
    chunk_overlap: Number of tokens overlap between chunks (default: 200)

  Returns:
    Import operation result if successful, None otherwise
  """
  try:
    # Construct the GCS URI
    if folder_path:
      gcs_uri = f"gs://{bucket_name}/{folder_path.rstrip('/')}"
    else:
      gcs_uri = f"gs://{bucket_name}"

    print(f"Importing files from GCS URI: {gcs_uri}")
    print(f"Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")

    # Create transformation config with proper chunking configuration
    transformation_config = TransformationConfig(
        chunking_config=ChunkingConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ),
    )

    # Create a partial failures sink to capture detailed error information
    timestamp = int(time.time())
    partial_failures_sink = f"gs://{bucket_name}/rag_import_failures_{timestamp}.ndjson"

    # Import files from Cloud Storage using the RAG API
    print("Starting import operation from Cloud Storage...")
    print("This may take several minutes depending on file size and count...")

    result = rag.import_files(
        corpus_name=corpus_name,
        paths=[gcs_uri],
        transformation_config=transformation_config,
        max_embedding_requests_per_min=1000,
        timeout=600,
        partial_failures_sink=partial_failures_sink
    )

    print("✅ Import operation completed!")
    print(f"Import result: {result}")

    if hasattr(result, 'imported_rag_files_count'):
        print(f"✅ Imported files count: {result.imported_rag_files_count}")
    if hasattr(result, 'skipped_rag_files_count'):
        print(f"⏭️  Skipped files count: {result.skipped_rag_files_count}")
    if hasattr(result, 'failed_rag_files_count'):
        print(f"❌ Failed files count: {result.failed_rag_files_count}")
        if result.failed_rag_files_count > 0:
            print(f"💡 Partial failures sink: {partial_failures_sink}")

            # Try to read and display the error logs
            try:
                print("\n📋 Error Details from Partial Failures Log:")
                print("=" * 60)

                client = storage.Client(project=PROJECT_ID)
                bucket = client.bucket(bucket_name)
                blob_name = partial_failures_sink.replace(f"gs://{bucket_name}/", "")
                blob = bucket.blob(blob_name)

                if blob.exists():
                    error_logs = blob.download_as_text()
                    print(error_logs)
                else:
                    print("❌ No error log file found at the specified location.")
                    print("   This might mean the import operation hasn't written logs yet.")

            except Exception as log_error:
                print(f"⚠️  Could not read error logs: {log_error}")

            print("=" * 60)

    # Check for failed PDFs and process them with DocAI if available
    if (hasattr(result, 'failed_rag_files_count') and
        result.failed_rag_files_count > 0):

      print(f"\n🔄 Attempting to process failed PDFs with Document AI Layout Parser...")

      # Try to setup processor - if it fails, skip DocAI processing
      processor_id = setup_processor(PROJECT_ID, DOCAI_LOCATION)
      if not processor_id:
        print("⚠️  Could not setup Document AI processor. Skipping DocAI processing.")
        print("   Some files failed to import and cannot be processed.")
      else:
        print(f"✅ Using processor {processor_id} for failed PDF processing...")
        failed_pdfs = parse_import_failures(partial_failures_sink, bucket_name)

        if failed_pdfs:
          processed_files = []

          for pdf_path in failed_pdfs:
            try:
              # Process PDF with DocAI Layout Parser
              text_content = process_pdf_with_layout_parser(pdf_path, chunk_size)

              # Upload processed text to GCS
              text_file_path = upload_processed_text_to_gcs(text_content, pdf_path)
              processed_files.append(text_file_path)

            except Exception as pdf_error:
              print(f"❌ Failed to process PDF {pdf_path} with DocAI: {pdf_error}")
              continue

          # Retry import with processed text files
          if processed_files:
            print(f"\n🔄 Retrying import with {len(processed_files)} processed text files...")

            try:
              retry_result = rag.import_files(
                  corpus_name=corpus_name,
                  paths=processed_files,
                  transformation_config=transformation_config,
                  max_embedding_requests_per_min=1000,
                  timeout=600
              )

              print("✅ Retry import completed!")
              print(f"Retry result: {retry_result}")

              if hasattr(retry_result, 'imported_rag_files_count'):
                  print(f"✅ Retry imported files count: {retry_result.imported_rag_files_count}")
              if hasattr(retry_result, 'failed_rag_files_count'):
                  print(f"❌ Retry failed files count: {retry_result.failed_rag_files_count}")

              # Update success status if retry was successful
              if (hasattr(retry_result, 'imported_rag_files_count') and
                  retry_result.imported_rag_files_count > 0):
                print("🎉 DocAI processing successful! Files imported after text extraction.")
                return retry_result

            except Exception as retry_error:
              print(f"❌ Error in retry import: {retry_error}")

    elif (hasattr(result, 'failed_rag_files_count') and
          result.failed_rag_files_count > 0):
      print("\n💡 Some files failed to import. Document AI Layout Parser will be automatically")
      print("   configured if needed when processing failed PDFs.")

    # Return success only if files were actually imported
    if hasattr(result, 'imported_rag_files_count') and result.imported_rag_files_count > 0:
        return result
    else:
        print("⚠️  No files were successfully imported.")
        return None

  except Exception as e:
    print(f"❌ Error importing files from GCS: {e}")
    print("\nTroubleshooting tips:")
    print("1. Ensure the service account has Storage Object Viewer permissions on the bucket")
    print("2. Verify the bucket and files exist")
    print("3. Check that files are in supported formats (.pdf, .txt, .docx, .html, .md, etc.)")
    print("4. Ensure you haven't exceeded embedding model quotas")
    print("5. For PDFs, ensure they contain extractable text (not just images)")
    return None


def main():
  initialize_vertex_ai()
  corpus = create_or_get_corpus()

  # Update the .env file with the corpus name
  update_env_file(corpus.name, ENV_FILE_PATH)

  # Import files from GCS bucket into the RAG corpus
  print(f"\n🔄 Starting import from GCS bucket: {GCS_BUCKET_NAME}")
  if GCS_FOLDER_PATH:
    print(f"📁 Folder path: {GCS_FOLDER_PATH}")

  import_result = import_files_from_gcs(
      corpus_name=corpus.name,
      bucket_name=GCS_BUCKET_NAME,
      folder_path=GCS_FOLDER_PATH,
      chunk_size=1024,
      chunk_overlap=200
  )

  if import_result:
    print(f"\n✅ Import completed successfully!")
  else:
    print(f"\n❌ Import failed. Please check the error messages above.")

  # List all files in the corpus to verify the import
  print(f"\n📋 Current files in corpus:")
  list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
  main()
