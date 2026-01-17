import React from 'react';
import './HelpPages.css';

// Shared Header Component
const PageHeader = ({ title, onBack }) => (
  <div className="help-page-header">
    <button className="help-back-btn" onClick={onBack}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
      Back
    </button>
    <h1 className="help-page-title">{title}</h1>
  </div>
);

// Help Center Page
export const HelpCenterPage = ({ onBack }) => (
  <div className="help-page">
    <PageHeader title="Help Center" onBack={onBack} />
    <div className="help-content">
      <section className="help-section">
        <h2>Getting Started</h2>
        <div className="help-cards">
          <div className="help-card">
            <div className="help-card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <h3>Quick Start Guide</h3>
            <p>Learn the basics of using LEGID for your legal questions.</p>
          </div>
          <div className="help-card">
            <div className="help-card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
            <h3>Document Upload</h3>
            <p>How to upload and analyze legal documents.</p>
          </div>
          <div className="help-card">
            <div className="help-card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h3>Chat Features</h3>
            <p>Get the most out of your legal conversations.</p>
          </div>
        </div>
      </section>

      <section className="help-section">
        <h2>Frequently Asked Questions</h2>
        <div className="faq-list">
          <details className="faq-item">
            <summary>What types of legal questions can LEGID answer?</summary>
            <p>LEGID can assist with traffic law, criminal law, business litigation, constitutional law, and more across Canadian and US jurisdictions.</p>
          </details>
          <details className="faq-item">
            <summary>Is my information kept confidential?</summary>
            <p>Yes, all conversations are private and encrypted. We do not share your personal or legal information with third parties.</p>
          </details>
          <details className="faq-item">
            <summary>Can LEGID replace a lawyer?</summary>
            <p>No, LEGID provides legal information and guidance but is not a substitute for professional legal advice from a licensed attorney.</p>
          </details>
          <details className="faq-item">
            <summary>How do I delete my chat history?</summary>
            <p>You can delete individual conversations from the sidebar or clear all history in Settings.</p>
          </details>
        </div>
      </section>

      <section className="help-section">
        <h2>Contact Support</h2>
        <p className="contact-info">
          Need more help? Contact us at <a href="mailto:support@legid.ai">support@legid.ai</a>
        </p>
      </section>
    </div>
  </div>
);

// Release Notes Page
export const ReleaseNotesPage = ({ onBack }) => (
  <div className="help-page">
    <PageHeader title="Release Notes" onBack={onBack} />
    <div className="help-content">
      <div className="release-list">
        <div className="release-item">
          <div className="release-header">
            <span className="release-version">v2.5.0</span>
            <span className="release-date">January 12, 2026</span>
          </div>
          <div className="release-body">
            <h4>New Features</h4>
            <ul>
              <li>ChatGPT-style profile menu with account management</li>
              <li>Personalization settings (theme, font size, response style)</li>
              <li>Cookie consent management</li>
              <li>Enhanced multi-account support</li>
            </ul>
            <h4>Improvements</h4>
            <ul>
              <li>Improved sidebar navigation</li>
              <li>Better address management in user profiles</li>
              <li>Enhanced security features</li>
            </ul>
          </div>
        </div>

        <div className="release-item">
          <div className="release-header">
            <span className="release-version">v2.4.0</span>
            <span className="release-date">January 5, 2026</span>
          </div>
          <div className="release-body">
            <h4>New Features</h4>
            <ul>
              <li>LOGIN-ONLY authentication (no auto-signup)</li>
              <li>User allowlist management</li>
              <li>Access request workflow</li>
            </ul>
            <h4>Bug Fixes</h4>
            <ul>
              <li>Fixed OAuth redirect issues</li>
              <li>Improved response formatting</li>
            </ul>
          </div>
        </div>

        <div className="release-item">
          <div className="release-header">
            <span className="release-version">v2.3.0</span>
            <span className="release-date">December 20, 2025</span>
          </div>
          <div className="release-body">
            <h4>New Features</h4>
            <ul>
              <li>Voice chat with Andy TTS</li>
              <li>Document generation</li>
              <li>Amendment generator</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Terms and Policies Page
export const TermsPage = ({ onBack }) => (
  <div className="help-page">
    <PageHeader title="Terms of Service" onBack={onBack} />
    <div className="help-content legal-content">
      <p className="last-updated">Last updated: January 12, 2026</p>

      <section>
        <h2>1. Acceptance of Terms</h2>
        <p>
          By accessing and using LEGID ("the Service"), you agree to be bound by these Terms of Service.
          If you do not agree to these terms, please do not use the Service.
        </p>
      </section>

      <section>
        <h2>2. Description of Service</h2>
        <p>
          LEGID is an AI-powered legal information assistant that provides general legal information
          and guidance. The Service is not a law firm and does not provide legal advice, legal representation,
          or attorney-client relationships.
        </p>
      </section>

      <section>
        <h2>3. User Responsibilities</h2>
        <p>Users agree to:</p>
        <ul>
          <li>Provide accurate information when creating an account</li>
          <li>Keep account credentials secure and confidential</li>
          <li>Use the Service for lawful purposes only</li>
          <li>Not attempt to circumvent security measures</li>
          <li>Not share account access with unauthorized users</li>
        </ul>
      </section>

      <section>
        <h2>4. Disclaimer</h2>
        <p>
          THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND. LEGID DOES NOT GUARANTEE
          THE ACCURACY, COMPLETENESS, OR RELIABILITY OF ANY INFORMATION PROVIDED. THE SERVICE IS NOT
          A SUBSTITUTE FOR PROFESSIONAL LEGAL ADVICE.
        </p>
      </section>

      <section>
        <h2>5. Limitation of Liability</h2>
        <p>
          LEGID shall not be liable for any indirect, incidental, special, consequential, or punitive
          damages arising from your use of the Service.
        </p>
      </section>

      <section>
        <h2>6. Privacy</h2>
        <p>
          Your use of the Service is also governed by our Privacy Policy. Please review our Privacy Policy
          to understand how we collect and use your information.
        </p>
      </section>

      <section>
        <h2>7. Contact</h2>
        <p>
          For questions about these Terms, contact us at: <a href="mailto:legal@legid.ai">legal@legid.ai</a>
        </p>
      </section>
    </div>
  </div>
);

// Privacy Policy Page
export const PrivacyPage = ({ onBack }) => (
  <div className="help-page">
    <PageHeader title="Privacy Policy" onBack={onBack} />
    <div className="help-content legal-content">
      <p className="last-updated">Last updated: January 12, 2026</p>

      <section>
        <h2>1. Information We Collect</h2>
        <p>We collect information you provide directly to us, including:</p>
        <ul>
          <li>Account information (name, email, profile data)</li>
          <li>Address information for jurisdiction detection</li>
          <li>Chat conversations and uploaded documents</li>
          <li>Preferences and settings</li>
        </ul>
      </section>

      <section>
        <h2>2. How We Use Your Information</h2>
        <p>We use your information to:</p>
        <ul>
          <li>Provide and improve the Service</li>
          <li>Personalize your experience</li>
          <li>Communicate with you about updates</li>
          <li>Ensure security and prevent fraud</li>
        </ul>
      </section>

      <section>
        <h2>3. Data Security</h2>
        <p>
          We implement industry-standard security measures to protect your data, including encryption
          in transit and at rest, secure authentication, and regular security audits.
        </p>
      </section>

      <section>
        <h2>4. Data Retention</h2>
        <p>
          We retain your data for as long as your account is active or as needed to provide the Service.
          You can request deletion of your data at any time.
        </p>
      </section>

      <section>
        <h2>5. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
          <li>Access your personal data</li>
          <li>Correct inaccurate data</li>
          <li>Delete your account and data</li>
          <li>Export your data</li>
          <li>Opt out of marketing communications</li>
        </ul>
      </section>

      <section>
        <h2>6. Cookies</h2>
        <p>
          We use cookies to improve your experience. You can manage your cookie preferences in Settings.
        </p>
      </section>

      <section>
        <h2>7. Contact Us</h2>
        <p>
          For privacy inquiries, contact us at: <a href="mailto:privacy@legid.ai">privacy@legid.ai</a>
        </p>
      </section>
    </div>
  </div>
);

// Keyboard Shortcuts Page
export const KeyboardShortcutsPage = ({ onBack }) => (
  <div className="help-page">
    <PageHeader title="Keyboard Shortcuts" onBack={onBack} />
    <div className="help-content">
      <section className="shortcuts-section">
        <h2>Navigation</h2>
        <div className="shortcuts-list">
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>K</kbd>
            </span>
            <span className="shortcut-desc">Open search</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd>
            </span>
            <span className="shortcut-desc">New chat</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>B</kbd>
            </span>
            <span className="shortcut-desc">Toggle sidebar</span>
          </div>
        </div>
      </section>

      <section className="shortcuts-section">
        <h2>Chat</h2>
        <div className="shortcuts-list">
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Enter</kbd>
            </span>
            <span className="shortcut-desc">Send message</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Shift</kbd> + <kbd>Enter</kbd>
            </span>
            <span className="shortcut-desc">New line in message</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>C</kbd>
            </span>
            <span className="shortcut-desc">Copy selected text</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Escape</kbd>
            </span>
            <span className="shortcut-desc">Cancel/Close modal</span>
          </div>
        </div>
      </section>

      <section className="shortcuts-section">
        <h2>Accessibility</h2>
        <div className="shortcuts-list">
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Tab</kbd>
            </span>
            <span className="shortcut-desc">Navigate to next element</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Shift</kbd> + <kbd>Tab</kbd>
            </span>
            <span className="shortcut-desc">Navigate to previous element</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>+</kbd>
            </span>
            <span className="shortcut-desc">Increase font size</span>
          </div>
          <div className="shortcut-item">
            <span className="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>-</kbd>
            </span>
            <span className="shortcut-desc">Decrease font size</span>
          </div>
        </div>
      </section>
    </div>
  </div>
);

// Cookie Policy Page
export const CookiePolicyPage = ({ onBack }) => (
  <div className="help-page">
    <PageHeader title="Cookie Policy" onBack={onBack} />
    <div className="help-content">
      <section className="help-section">
        <h2>Overview</h2>
        <p>
          We use cookies to keep LEGID secure, improve performance, and remember your preferences.
          You can manage your choices in Settings at any time.
        </p>
      </section>
      <section className="help-section">
        <h2>Categories</h2>
        <ul className="help-list">
          <li>Necessary: required for authentication and core app functionality.</li>
          <li>Functional: stores user preferences like theme and language.</li>
          <li>Analytics: helps us understand usage patterns to improve the product.</li>
          <li>Marketing: optional and disabled by default.</li>
        </ul>
      </section>
      <section className="help-section">
        <h2>Manage Preferences</h2>
        <p>
          You can update cookie preferences from your profile menu or Settings page under Cookie Preferences.
        </p>
      </section>
    </div>
  </div>
);

export default {
  HelpCenterPage,
  ReleaseNotesPage,
  TermsPage,
  PrivacyPage,
  KeyboardShortcutsPage
};
