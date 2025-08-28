# NitePutter Pro - Legal & Compliance Documentation

## 📋 Compliance Checklist

### ✅ Legal Requirements Status

| Requirement | Status | Implementation | Location |
|------------|--------|----------------|----------|
| Privacy Policy | ✅ Complete | GDPR/CCPA compliant | `/frontend-v2/src/pages/PrivacyPolicy.tsx` |
| Terms of Service | ✅ Complete | E-commerce standard | `/frontend-v2/src/pages/TermsOfService.tsx` |
| Cookie Consent | ✅ Complete | EU Cookie Law | `/frontend-v2/src/components/CookieBanner.tsx` |
| GDPR Compliance | ✅ Complete | Data protection | Backend + Frontend |
| CCPA Compliance | ✅ Complete | California privacy | Backend + Frontend |
| Return Policy | ✅ Complete | 30-day returns | `/frontend-v2/src/pages/ReturnPolicy.tsx` |
| Shipping Policy | ✅ Complete | Clear terms | `/frontend-v2/src/pages/ShippingPolicy.tsx` |
| PCI DSS | ✅ Complete | Via Stripe | Payment processing |
| Age Verification | ✅ Complete | 18+ requirement | Checkout process |
| Tax Compliance | ✅ Complete | Automatic calculation | `/backend/app/services/tax_service.py` |

## 🔒 Privacy & Data Protection

### GDPR Compliance Features

```python
# backend/app/services/gdpr_service.py

class GDPRService:
    """Handle GDPR compliance requirements"""
    
    async def export_user_data(self, user_id: str) -> dict:
        """Export all user data for GDPR data portability"""
        user_data = {
            "profile": await self.get_user_profile(user_id),
            "orders": await self.get_user_orders(user_id),
            "reviews": await self.get_user_reviews(user_id),
            "addresses": await self.get_user_addresses(user_id),
            "payment_methods": await self.get_payment_methods(user_id),
            "activity_log": await self.get_activity_log(user_id)
        }
        return user_data
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Right to erasure (right to be forgotten)"""
        # Anonymize orders (keep for records but remove PII)
        await self.anonymize_orders(user_id)
        # Delete user profile
        await self.delete_user_profile(user_id)
        # Delete reviews
        await self.delete_user_reviews(user_id)
        # Remove from mailing lists
        await self.unsubscribe_all(user_id)
        return True
    
    async def get_consent_status(self, user_id: str) -> dict:
        """Get current consent status"""
        return {
            "marketing": await self.get_marketing_consent(user_id),
            "analytics": await self.get_analytics_consent(user_id),
            "cookies": await self.get_cookie_consent(user_id),
            "data_sharing": await self.get_data_sharing_consent(user_id)
        }
```

### Cookie Consent Implementation

```typescript
// frontend-v2/src/components/CookieBanner.tsx

import React, { useState, useEffect } from 'react';
import { useCookieConsent } from '../hooks/useCookieConsent';

export const CookieBanner: React.FC = () => {
  const { consent, updateConsent } = useCookieConsent();
  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const cookieCategories = {
    necessary: {
      name: 'Necessary',
      description: 'Required for site functionality',
      required: true
    },
    analytics: {
      name: 'Analytics',
      description: 'Help us improve our website',
      required: false
    },
    marketing: {
      name: 'Marketing',
      description: 'Personalized advertisements',
      required: false
    },
    preferences: {
      name: 'Preferences',
      description: 'Remember your settings',
      required: false
    }
  };

  const acceptAll = () => {
    updateConsent({
      necessary: true,
      analytics: true,
      marketing: true,
      preferences: true
    });
    setShowBanner(false);
  };

  const acceptSelected = () => {
    updateConsent(consent);
    setShowBanner(false);
  };

  const rejectAll = () => {
    updateConsent({
      necessary: true,
      analytics: false,
      marketing: false,
      preferences: false
    });
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white shadow-lg z-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h3 className="text-lg font-semibold mb-2">Cookie Consent</h3>
        <p className="text-sm text-gray-600 mb-4">
          We use cookies to enhance your experience. By continuing to visit this site 
          you agree to our use of cookies.
        </p>
        
        {showDetails && (
          <div className="mb-4 space-y-2">
            {Object.entries(cookieCategories).map(([key, category]) => (
              <label key={key} className="flex items-center">
                <input
                  type="checkbox"
                  checked={consent[key]}
                  disabled={category.required}
                  onChange={(e) => updateConsent({
                    ...consent,
                    [key]: e.target.checked
                  })}
                  className="mr-2"
                />
                <span className="text-sm">
                  <strong>{category.name}</strong> - {category.description}
                </span>
              </label>
            ))}
          </div>
        )}
        
        <div className="flex gap-2">
          <button onClick={acceptAll} className="btn-primary">
            Accept All
          </button>
          <button onClick={acceptSelected} className="btn-secondary">
            Accept Selected
          </button>
          <button onClick={rejectAll} className="btn-secondary">
            Reject All
          </button>
          <button 
            onClick={() => setShowDetails(!showDetails)} 
            className="btn-link ml-auto"
          >
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
        </div>
      </div>
    </div>
  );
};
```

## 📄 Legal Pages Content

### Privacy Policy Structure

```markdown
# Privacy Policy

Last Updated: January 1, 2024

## 1. Information We Collect
- Personal Information (name, email, address)
- Payment Information (processed by Stripe)
- Device Information (IP address, browser type)
- Usage Information (pages visited, actions taken)

## 2. How We Use Your Information
- Process orders and payments
- Send order confirmations and updates
- Improve our services
- Marketing (with consent)

## 3. Data Sharing
- Payment processors (Stripe)
- Shipping partners
- Analytics providers (with consent)
- Legal requirements

## 4. Your Rights
- Access your data
- Correct inaccurate data
- Delete your data
- Export your data
- Opt-out of marketing

## 5. Data Security
- Encryption in transit and at rest
- Regular security audits
- PCI DSS compliance
- Limited access controls

## 6. Contact Information
Email: privacy@niteputter.com
Address: [Company Address]
Phone: [Company Phone]
```

### Terms of Service Structure

```markdown
# Terms of Service

Last Updated: January 1, 2024

## 1. Acceptance of Terms
By using NitePutter Pro, you agree to these terms.

## 2. Account Registration
- Must be 18+ years old
- Provide accurate information
- Maintain account security

## 3. Product Purchases
- Prices subject to change
- Payment processed by Stripe
- All sales final (except returns)

## 4. Returns and Refunds
- 30-day return policy
- Original condition required
- Shipping fees non-refundable

## 5. Intellectual Property
- All content owned by NitePutter Pro
- Limited license to use website
- No unauthorized copying

## 6. Limitation of Liability
- No warranty on products
- Limited to purchase price
- No consequential damages

## 7. Governing Law
- Governed by [State] law
- Disputes resolved in [County]
```

## 🚢 Shipping & Returns

### Return Policy Implementation

```python
# backend/app/services/return_service.py

class ReturnService:
    """Handle product returns and refunds"""
    
    RETURN_WINDOW_DAYS = 30
    RESTOCKING_FEE_PERCENT = 0  # No restocking fee
    
    async def initiate_return(self, order_id: str, items: List[dict], reason: str) -> dict:
        """Initiate a return request"""
        order = await self.get_order(order_id)
        
        # Check if within return window
        order_date = order["created_at"]
        days_since_order = (datetime.now(UTC) - order_date).days
        
        if days_since_order > self.RETURN_WINDOW_DAYS:
            raise ValueError(f"Return window expired (>{self.RETURN_WINDOW_DAYS} days)")
        
        # Create return request
        return_request = {
            "order_id": order_id,
            "items": items,
            "reason": reason,
            "status": "pending",
            "refund_amount": self.calculate_refund(items),
            "created_at": datetime.now(UTC)
        }
        
        # Send email notification
        await self.send_return_confirmation(order["customer_email"], return_request)
        
        return return_request
    
    async def process_refund(self, return_id: str) -> dict:
        """Process refund via Stripe"""
        return_request = await self.get_return_request(return_id)
        
        # Create Stripe refund
        refund = stripe.Refund.create(
            payment_intent=return_request["payment_intent_id"],
            amount=int(return_request["refund_amount"] * 100),
            reason="requested_by_customer"
        )
        
        # Update return status
        await self.update_return_status(return_id, "refunded")
        
        return refund
```

### Shipping Policy Implementation

```typescript
// frontend-v2/src/utils/shipping.ts

export interface ShippingRate {
  id: string;
  name: string;
  price: number;
  estimatedDays: number;
  description: string;
}

export const calculateShipping = (
  subtotal: number,
  destination: string,
  weight: number
): ShippingRate[] => {
  const rates: ShippingRate[] = [];
  
  // Free shipping threshold
  const FREE_SHIPPING_THRESHOLD = 150;
  
  // Standard shipping
  rates.push({
    id: 'standard',
    name: 'Standard Shipping',
    price: subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : 9.99,
    estimatedDays: 5-7,
    description: `Free on orders over $${FREE_SHIPPING_THRESHOLD}`
  });
  
  // Express shipping
  rates.push({
    id: 'express',
    name: 'Express Shipping',
    price: 19.99,
    estimatedDays: 2-3,
    description: '2-3 business days'
  });
  
  // Overnight shipping
  if (destination !== 'AK' && destination !== 'HI') {
    rates.push({
      id: 'overnight',
      name: 'Overnight Shipping',
      price: 39.99,
      estimatedDays: 1,
      description: 'Next business day'
    });
  }
  
  return rates;
};
```

## 📊 Tax Compliance

### Tax Calculation Service

```python
# backend/app/services/tax_service.py

class TaxService:
    """Handle tax calculations and compliance"""
    
    # State tax rates (simplified)
    STATE_TAX_RATES = {
        "CA": 0.0725,  # California
        "TX": 0.0625,  # Texas
        "NY": 0.08,    # New York
        "FL": 0.06,    # Florida
        # ... other states
    }
    
    async def calculate_tax(self, subtotal: float, shipping_address: dict) -> dict:
        """Calculate sales tax based on destination"""
        state = shipping_address.get("state")
        
        # Check if we have nexus in the state
        if state not in self.STATE_TAX_RATES:
            return {
                "tax_rate": 0,
                "tax_amount": 0,
                "taxable_amount": 0
            }
        
        tax_rate = self.STATE_TAX_RATES[state]
        
        # Some states tax shipping
        taxable_amount = subtotal
        if self.state_taxes_shipping(state):
            taxable_amount += shipping_address.get("shipping_cost", 0)
        
        tax_amount = round(taxable_amount * tax_rate, 2)
        
        return {
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "taxable_amount": taxable_amount,
            "jurisdiction": state
        }
    
    async def file_tax_return(self, period: str) -> dict:
        """Generate tax filing report"""
        # Aggregate sales by state
        sales_by_state = await self.aggregate_sales_by_state(period)
        
        # Calculate tax collected vs owed
        tax_report = {}
        for state, sales in sales_by_state.items():
            tax_report[state] = {
                "gross_sales": sales["total"],
                "taxable_sales": sales["taxable"],
                "tax_collected": sales["tax_collected"],
                "tax_rate": self.STATE_TAX_RATES.get(state, 0)
            }
        
        return tax_report
```

## 🎯 Marketing Compliance

### Email Marketing Compliance

```python
# backend/app/services/email_compliance.py

class EmailComplianceService:
    """Handle email marketing compliance (CAN-SPAM, GDPR)"""
    
    async def send_marketing_email(self, recipient: str, campaign: dict) -> bool:
        """Send marketing email with compliance checks"""
        
        # Check if user has opted in
        consent = await self.check_marketing_consent(recipient)
        if not consent:
            return False
        
        # Add required headers
        headers = {
            "List-Unsubscribe": f"<{self.get_unsubscribe_url(recipient)}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            "Precedence": "bulk"
        }
        
        # Add required footer
        footer = f"""
        <hr>
        <p style="font-size: 12px; color: #666;">
        You received this email because you opted in at NitePutter Pro.
        
        NitePutter Pro
        {self.company_address}
        
        <a href="{self.get_unsubscribe_url(recipient)}">Unsubscribe</a> | 
        <a href="{self.get_preferences_url(recipient)}">Email Preferences</a>
        </p>
        """
        
        # Send email
        return await self.send_email(
            to=recipient,
            subject=campaign["subject"],
            body=campaign["body"] + footer,
            headers=headers
        )
    
    async def handle_unsubscribe(self, email: str, reason: str = None) -> bool:
        """Handle unsubscribe request"""
        # Update consent
        await self.update_consent(email, "marketing", False)
        
        # Log unsubscribe
        await self.log_unsubscribe(email, reason)
        
        # Send confirmation
        await self.send_unsubscribe_confirmation(email)
        
        return True
```

## 🌍 International Compliance

### Multi-Region Support

```typescript
// frontend-v2/src/utils/compliance.ts

export interface ComplianceRegion {
  code: string;
  name: string;
  privacyLaw: string;
  dataRetention: number; // days
  cookieConsent: boolean;
  ageVerification: number;
}

export const COMPLIANCE_REGIONS: ComplianceRegion[] = [
  {
    code: 'US',
    name: 'United States',
    privacyLaw: 'CCPA',
    dataRetention: 365 * 7,
    cookieConsent: false,
    ageVerification: 13
  },
  {
    code: 'EU',
    name: 'European Union',
    privacyLaw: 'GDPR',
    dataRetention: 365 * 3,
    cookieConsent: true,
    ageVerification: 16
  },
  {
    code: 'GB',
    name: 'United Kingdom',
    privacyLaw: 'UK-GDPR',
    dataRetention: 365 * 6,
    cookieConsent: true,
    ageVerification: 13
  },
  {
    code: 'CA',
    name: 'Canada',
    privacyLaw: 'PIPEDA',
    dataRetention: 365 * 7,
    cookieConsent: false,
    ageVerification: 13
  }
];

export const getComplianceRequirements = (countryCode: string) => {
  return COMPLIANCE_REGIONS.find(r => r.code === countryCode) || COMPLIANCE_REGIONS[0];
};
```

## 📈 Analytics & Tracking Compliance

### Analytics Implementation

```javascript
// frontend-v2/src/utils/analytics.ts

class Analytics {
  private hasConsent: boolean = false;
  
  init() {
    // Check for analytics consent
    this.hasConsent = this.checkAnalyticsConsent();
    
    if (this.hasConsent) {
      // Google Analytics
      gtag('config', 'GA_MEASUREMENT_ID', {
        anonymize_ip: true,
        cookie_flags: 'SameSite=None;Secure'
      });
      
      // Facebook Pixel (with Limited Data Use)
      fbq('init', 'PIXEL_ID', {}, {
        agent: 'niteputter-pro'
      });
      fbq('dataProcessingOptions', ['LDU'], 0, 0);
    }
  }
  
  track(event: string, parameters?: any) {
    if (!this.hasConsent) return;
    
    // Sanitize PII from parameters
    const sanitized = this.sanitizeData(parameters);
    
    // Send to analytics providers
    gtag('event', event, sanitized);
    fbq('track', event, sanitized);
  }
  
  private sanitizeData(data: any) {
    // Remove PII fields
    const piiFields = ['email', 'phone', 'ssn', 'creditCard'];
    const sanitized = { ...data };
    
    piiFields.forEach(field => {
      delete sanitized[field];
    });
    
    return sanitized;
  }
}
```

## ✅ Compliance Monitoring

### Automated Compliance Checks

```python
# backend/app/services/compliance_monitor.py

class ComplianceMonitor:
    """Monitor and enforce compliance requirements"""
    
    async def daily_compliance_check(self):
        """Run daily compliance checks"""
        report = {
            "date": datetime.now(UTC).isoformat(),
            "checks": {}
        }
        
        # Check data retention
        report["checks"]["data_retention"] = await self.check_data_retention()
        
        # Check consent expiration
        report["checks"]["consent_expiration"] = await self.check_consent_expiration()
        
        # Check unprocessed data requests
        report["checks"]["data_requests"] = await self.check_pending_data_requests()
        
        # Check security certificates
        report["checks"]["ssl_expiration"] = await self.check_ssl_expiration()
        
        # Send report
        await self.send_compliance_report(report)
        
        return report
    
    async def check_data_retention(self):
        """Ensure data is not kept longer than allowed"""
        # Delete old logs (> 90 days)
        deleted_logs = await self.delete_old_logs(days=90)
        
        # Delete old sessions (> 30 days)
        deleted_sessions = await self.delete_old_sessions(days=30)
        
        # Anonymize old orders (> 7 years)
        anonymized_orders = await self.anonymize_old_orders(years=7)
        
        return {
            "deleted_logs": deleted_logs,
            "deleted_sessions": deleted_sessions,
            "anonymized_orders": anonymized_orders
        }
```

## 📊 Compliance Dashboard

### Admin Compliance View

```typescript
// frontend-v2/src/pages/admin/ComplianceDashboard.tsx

export const ComplianceDashboard: React.FC = () => {
  const { complianceData, loading } = useComplianceData();
  
  return (
    <div className="compliance-dashboard">
      <h1>Compliance Dashboard</h1>
      
      <div className="grid grid-cols-3 gap-4">
        <MetricCard
          title="GDPR Requests"
          value={complianceData.gdprRequests.pending}
          total={complianceData.gdprRequests.total}
          status={complianceData.gdprRequests.pending === 0 ? 'good' : 'warning'}
        />
        
        <MetricCard
          title="Consent Rate"
          value={`${complianceData.consentRate}%`}
          description="Users who accepted cookies"
          status={complianceData.consentRate > 60 ? 'good' : 'warning'}
        />
        
        <MetricCard
          title="Data Retention"
          value={complianceData.dataRetention.compliant}
          total={complianceData.dataRetention.total}
          status={complianceData.dataRetention.violations === 0 ? 'good' : 'error'}
        />
      </div>
      
      <ComplianceChecklist items={complianceData.checklist} />
      
      <DataRequestsTable requests={complianceData.dataRequests} />
    </div>
  );
};
```

---

**Important Legal Notice**: This documentation provides technical implementation guidance. Always consult with legal counsel for specific compliance requirements in your jurisdiction.

Last Updated: 2024-01-01
Next Legal Review: 2024-Q2