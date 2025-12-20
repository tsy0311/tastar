"""
Demo/Interactive Endpoints for Testing
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any

router = APIRouter()

@router.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """
    Interactive demo page for testing features
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unified AI Business Assistant - Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 5px;
            }
            .section h2 {
                color: #4CAF50;
            }
            .endpoint {
                background: #e8f5e9;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #4CAF50;
                border-radius: 3px;
            }
            .endpoint code {
                background: #333;
                color: #4CAF50;
                padding: 2px 6px;
                border-radius: 3px;
            }
            .button {
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
            }
            .button:hover {
                background: #45a049;
            }
            .info {
                background: #e3f2fd;
                padding: 15px;
                border-left: 4px solid #2196F3;
                margin: 15px 0;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Unified AI Business Assistant - Interactive Demo</h1>
            
            <div class="info">
                <strong>📌 Quick Start:</strong> Use the Swagger UI below to interact with all API endpoints. 
                You can upload documents, chat with AI, and manage your business data.
            </div>
            
            <div class="section">
                <h2>📚 API Documentation</h2>
                <p>Interactive API documentation where you can test all endpoints:</p>
                <a href="/api/docs" class="button" target="_blank">Open Swagger UI</a>
                <a href="/api/redoc" class="button" target="_blank">Open ReDoc</a>
            </div>
            
            <div class="section">
                <h2>📄 Document Processing</h2>
                <div class="endpoint">
                    <strong>Upload Document:</strong> <code>POST /api/v1/documents/upload</code><br>
                    Upload PDF, JPEG, PNG, or TIFF files for OCR processing and data extraction.
                </div>
                <div class="endpoint">
                    <strong>Bulk Upload:</strong> <code>POST /api/v1/documents/upload/bulk</code><br>
                    Upload multiple documents at once.
                </div>
                <div class="endpoint">
                    <strong>List Documents:</strong> <code>GET /api/v1/documents/list</code><br>
                    View all uploaded documents.
                </div>
            </div>
            
            <div class="section">
                <h2>🤖 AI Assistant</h2>
                <div class="endpoint">
                    <strong>Chat:</strong> <code>POST /api/v1/ai/chat</code><br>
                    Chat with the AI assistant. Try: "Hello", "What can you do?", "Help me with invoices"
                </div>
                <div class="endpoint">
                    <strong>Chat History:</strong> <code>GET /api/v1/ai/chat/history</code><br>
                    View conversation history for a session.
                </div>
                <div class="endpoint">
                    <strong>Sentiment Analysis:</strong> <code>POST /api/v1/ai/analyze/sentiment</code><br>
                    Analyze sentiment of text (positive, negative, neutral).
                </div>
                <div class="endpoint">
                    <strong>Entity Extraction:</strong> <code>POST /api/v1/ai/extract/entities</code><br>
                    Extract emails, phone numbers, amounts, and dates from text.
                </div>
            </div>
            
            <div class="section">
                <h2>💼 Business Data Management</h2>
                <div class="endpoint">
                    <strong>Customers:</strong> <code>GET/POST/PUT/DELETE /api/v1/customers</code><br>
                    Manage customer information.
                </div>
                <div class="endpoint">
                    <strong>Invoices:</strong> <code>GET/POST/PUT /api/v1/invoices</code><br>
                    Create and manage invoices.
                </div>
                <div class="endpoint">
                    <strong>Payments:</strong> <code>GET/POST /api/v1/payments</code><br>
                    Record and track payments.
                </div>
                <div class="endpoint">
                    <strong>Companies:</strong> <code>GET/POST/PUT /api/v1/companies</code><br>
                    Manage company information.
                </div>
            </div>
            
            <div class="section">
                <h2>🔐 Authentication</h2>
                <div class="endpoint">
                    <strong>Login:</strong> <code>POST /api/v1/auth/login</code><br>
                    Get authentication token. Use email: <code>admin@example.com</code>, password: <code>admin123</code> (if seeded)
                </div>
                <div class="endpoint">
                    <strong>Get Current User:</strong> <code>GET /api/v1/auth/me</code><br>
                    Get current authenticated user information.
                </div>
            </div>
            
            <div class="section">
                <h2>💡 Example Workflows</h2>
                <ol>
                    <li><strong>Process Invoice:</strong> Upload invoice PDF → Extract data → Create invoice record</li>
                    <li><strong>AI Assistance:</strong> Chat with AI → Get guidance → Create customer/invoice</li>
                    <li><strong>Bulk Processing:</strong> Upload multiple documents → Review extracted data → Process all</li>
                </ol>
            </div>
            
            <div class="info">
                <strong>📖 Full Documentation:</strong> See <code>USER_GUIDE.md</code> for detailed usage instructions and examples.
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

