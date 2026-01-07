"""
Integration Service
Handles integrations with ERP systems, accounting software, and email services
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from app.core.config import settings
from app.core.logging import logger
import json

class ERPIntegrationService:
    """Service for ERP system integrations (SAP, Oracle, NetSuite, etc.)"""
    
    def __init__(self, erp_type: str = "generic", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.erp_type = erp_type
        self.api_key = api_key or settings.OPENAI_API_KEY  # Placeholder
        self.base_url = base_url or "https://api.erp.example.com"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def sync_customers(self, customers: List[Dict]) -> Dict[str, Any]:
        """Sync customers to ERP system"""
        try:
            response = await self.client.post(
                f"{self.base_url}/customers",
                json={"customers": customers},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            logger.info(f"Synced {len(customers)} customers to ERP")
            return {"success": True, "synced_count": len(customers)}
        except Exception as e:
            logger.error(f"ERP customer sync error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_invoices(self, invoices: List[Dict]) -> Dict[str, Any]:
        """Sync invoices to ERP system"""
        try:
            response = await self.client.post(
                f"{self.base_url}/invoices",
                json={"invoices": invoices},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            logger.info(f"Synced {len(invoices)} invoices to ERP")
            return {"success": True, "synced_count": len(invoices)}
        except Exception as e:
            logger.error(f"ERP invoice sync error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_inventory_levels(self) -> Dict[str, Any]:
        """Get inventory levels from ERP"""
        try:
            response = await self.client.get(
                f"{self.base_url}/inventory",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return {"success": True, "inventory": response.json()}
        except Exception as e:
            logger.error(f"ERP inventory fetch error: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class AccountingIntegrationService:
    """Service for accounting software integrations (QuickBooks, Xero, Sage, etc.)"""
    
    def __init__(self, accounting_type: str = "quickbooks", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.accounting_type = accounting_type
        self.api_key = api_key
        self.base_url = base_url or "https://api.accounting.example.com"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def sync_chart_of_accounts(self) -> Dict[str, Any]:
        """Sync chart of accounts"""
        try:
            response = await self.client.get(
                f"{self.base_url}/accounts",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return {"success": True, "accounts": response.json()}
        except Exception as e:
            logger.error(f"Accounting sync error: {e}")
            return {"success": False, "error": str(e)}
    
    async def post_journal_entry(self, entry: Dict) -> Dict[str, Any]:
        """Post journal entry to accounting system"""
        try:
            response = await self.client.post(
                f"{self.base_url}/journal-entries",
                json=entry,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            logger.info("Posted journal entry to accounting system")
            return {"success": True, "entry_id": response.json().get("id")}
        except Exception as e:
            logger.error(f"Accounting journal entry error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Sync transactions to accounting system"""
        try:
            response = await self.client.post(
                f"{self.base_url}/transactions",
                json={"transactions": transactions},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            logger.info(f"Synced {len(transactions)} transactions")
            return {"success": True, "synced_count": len(transactions)}
        except Exception as e:
            logger.error(f"Accounting transaction sync error: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class EmailIntegrationService:
    """Service for email integrations (SendGrid, Mailgun, SMTP, etc.)"""
    
    def __init__(self, email_type: str = "sendgrid", api_key: Optional[str] = None):
        self.email_type = email_type
        self.api_key = api_key or settings.SENDGRID_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send email via integration service"""
        try:
            if self.email_type == "sendgrid":
                return await self._send_via_sendgrid(to, subject, body, from_email, attachments)
            elif self.email_type == "smtp":
                return await self._send_via_smtp(to, subject, body, from_email, attachments)
            else:
                logger.warning(f"Email type {self.email_type} not implemented")
                return {"success": False, "error": "Email type not supported"}
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_via_sendgrid(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str],
        attachments: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send email via SendGrid"""
        try:
            response = await self.client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json={
                    "personalizations": [{"to": [{"email": to}]}],
                    "from": {"email": from_email or "noreply@example.com"},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": body}]
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            logger.info(f"Email sent to {to} via SendGrid")
            return {"success": True, "message_id": response.headers.get("X-Message-Id")}
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_via_smtp(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str],
        attachments: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = from_email or settings.SMTP_USER
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to} via SMTP")
            return {"success": True}
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_bulk_emails(self, emails: List[Dict]) -> Dict[str, Any]:
        """Send bulk emails"""
        results = []
        for email in emails:
            result = await self.send_email(
                email.get('to'),
                email.get('subject'),
                email.get('body'),
                email.get('from')
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('success'))
        return {
            "success": True,
            "total": len(emails),
            "successful": success_count,
            "failed": len(emails) - success_count,
            "results": results
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class IntegrationService:
    """Main integration service that manages all integrations"""
    
    def __init__(self):
        self.erp_service: Optional[ERPIntegrationService] = None
        self.accounting_service: Optional[AccountingIntegrationService] = None
        self.email_service: Optional[EmailIntegrationService] = None
    
    def initialize_erp(self, erp_type: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize ERP integration"""
        self.erp_service = ERPIntegrationService(erp_type, api_key, base_url)
        logger.info(f"ERP integration initialized: {erp_type}")
    
    def initialize_accounting(self, accounting_type: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize accounting integration"""
        self.accounting_service = AccountingIntegrationService(accounting_type, api_key, base_url)
        logger.info(f"Accounting integration initialized: {accounting_type}")
    
    def initialize_email(self, email_type: str = "sendgrid", api_key: Optional[str] = None):
        """Initialize email integration"""
        self.email_service = EmailIntegrationService(email_type, api_key)
        logger.info(f"Email integration initialized: {email_type}")
    
    async def sync_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync all data to integrated systems"""
        results = {}
        
        if self.erp_service and data.get('customers'):
            results['erp'] = await self.erp_service.sync_customers(data['customers'])
        
        if self.accounting_service and data.get('transactions'):
            results['accounting'] = await self.accounting_service.sync_transactions(data['transactions'])
        
        return results
    
    async def close(self):
        """Close all integration services"""
        if self.erp_service:
            await self.erp_service.close()
        if self.accounting_service:
            await self.accounting_service.close()
        if self.email_service:
            await self.email_service.close()

# Global instance
integration_service = IntegrationService()

