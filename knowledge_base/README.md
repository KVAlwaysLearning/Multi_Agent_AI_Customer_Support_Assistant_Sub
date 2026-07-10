# Knowledge Base

Put your fictional company's PDFs here (per the project doc, e.g. TechMart
Electronics):

- FAQ.pdf
- RefundPolicy.pdf
- ShippingPolicy.pdf
- Warranty.pdf
- Pricing.pdf
- Products.pdf
- InstallationGuide.pdf
- UserManual.pdf

This folder is currently empty - that's expected. The RAG pipeline
(`backend/rag/`) is fully wired and will run with zero PDFs here (retrieval
just returns no results), so you can verify the rest of the system before
writing any of these documents.

Once you add PDFs here, run:

    cd backend
    python rag/ingest.py

to build the FAISS index. Re-run any time you add/change documents.
