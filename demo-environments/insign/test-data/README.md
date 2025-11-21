# InSign Demo Test Data

This directory contains sample documents used for InSign product demonstrations.

## Required Files

Place the following PDF documents in this directory for demos:

1. **NDA_Template.pdf** - Non-Disclosure Agreement template
   - Used to demonstrate document upload and signature field placement
   - Should be a standard NDA with signature blocks

2. **Employment_Agreement.pdf** - Employment contract template
   - Used to demonstrate signing workflow
   - Should have pre-placed signature fields

## File Format Requirements

- PDF format preferred
- Maximum file size: 10MB per document
- Documents should have clear signature placeholders
- Multi-page documents work best for demonstrations

## Creating Sample PDFs

If you don't have sample documents, you can:

1. Download free templates from legal template websites
2. Create simple PDFs with placeholder text
3. Use the provided generator script: `python scripts/generate_sample_docs.py`

## Security Note

These are **demo documents only**. Do not include:
- Real signatures
- Personally identifiable information (PII)
- Sensitive company data
- Production documents

All documents in this directory should be publicly shareable test data.
