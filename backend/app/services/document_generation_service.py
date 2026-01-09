"""
Document Generation Service
Generates various legal documents using AI and templates.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DocumentGenerationService:
    """Service for generating legal documents."""
    
    def __init__(self, llm_client=None):
        """
        Initialize the document generation service.
        
        Args:
            llm_client: LLM client for AI-powered generation
        """
        self.llm_client = llm_client
        
        # Document templates
        self.templates = {
            'sue_letter': self._generate_sue_letter,
            'amendment': self._generate_amendment,
            'nda': self._generate_nda,
            'will': self._generate_will,
            'power_of_attorney': self._generate_power_of_attorney,
            'lease_agreement': self._generate_lease_agreement,
            'employment_contract': self._generate_employment_contract,
            'business_contract': self._generate_business_contract
        }
    
    async def generate_document(
        self,
        document_type: str,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a legal document based on type and form data.
        
        Args:
            document_type: Type of document to generate
            form_data: Form data filled by user
            jurisdiction: Legal jurisdiction
            user_id: User ID for tracking
            
        Returns:
            Dictionary with generated document
        """
        try:
            if document_type not in self.templates:
                return {
                    "success": False,
                    "error": f"Unknown document type: {document_type}"
                }
            
            # Generate document using appropriate template
            generator = self.templates[document_type]
            content = await generator(form_data, jurisdiction)
            
            # Create document metadata
            document_id = f"doc_{document_type}_{datetime.now().timestamp()}"
            
            return {
                "success": True,
                "document_id": document_id,
                "document_type": document_type,
                "content": content,
                "source": "AI-Powered Document Generator",
                "jurisdiction": jurisdiction,
                "generated_at": datetime.now().isoformat(),
                "note": "This document has been generated automatically. Please review carefully and consult with a licensed attorney before use."
            }
            
        except Exception as e:
            logger.error(f"Document generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to generate document: {str(e)}"
            }
    
    async def _generate_sue_letter(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate a sue letter (legal complaint)."""
        
        content = f"""
LEGAL COMPLAINT

IN THE {jurisdiction or 'UNITED STATES'} COURT

{form_data.get('plaintiff_name', '[PLAINTIFF NAME]')}
Plaintiff

v.

{form_data.get('defendant_name', '[DEFENDANT NAME]')}
Defendant

CASE NO: [TO BE ASSIGNED]

═══════════════════════════════════════════════════════════════

COMPLAINT FOR DAMAGES

═══════════════════════════════════════════════════════════════

NOW COMES the Plaintiff, {form_data.get('plaintiff_name', '[PLAINTIFF NAME]')}, by and through undersigned counsel, and for their Complaint against Defendant {form_data.get('defendant_name', '[DEFENDANT NAME]')}, states as follows:

PARTIES

1. Plaintiff {form_data.get('plaintiff_name', '[PLAINTIFF NAME]')} is a resident of:
   {form_data.get('plaintiff_address', '[PLAINTIFF ADDRESS]')}

2. Defendant {form_data.get('defendant_name', '[DEFENDANT NAME]')} is a resident of:
   {form_data.get('defendant_address', '[DEFENDANT ADDRESS]')}

JURISDICTION AND VENUE

3. This Court has jurisdiction over this matter pursuant to applicable law.

4. Venue is proper in this Court.

FACTUAL ALLEGATIONS

5. On or about {form_data.get('incident_date', '[DATE OF INCIDENT]')}, the following events occurred:

{form_data.get('legal_grounds', '[DESCRIPTION OF LEGAL GROUNDS]')}

LEGAL GROUNDS

6. The Defendant's actions constitute:
   {form_data.get('legal_grounds', '[LEGAL GROUNDS FOR LAWSUIT]')}

7. As a direct and proximate result of Defendant's actions, Plaintiff has suffered damages.

DAMAGES

8. Plaintiff has incurred the following damages:
   - Economic damages: ${form_data.get('damages_amount', '[AMOUNT]')}
   - Non-economic damages: [TO BE PROVEN AT TRIAL]
   - Punitive damages: [AS APPLICABLE]

RELIEF SOUGHT

WHEREFORE, Plaintiff respectfully requests that this Court:

{form_data.get('relief_sought', '[RELIEF SOUGHT]')}

{form_data.get('additional_clauses', '')}

And for such other and further relief as the Court deems just and proper.

Respectfully submitted,

_______________________________
{form_data.get('plaintiff_name', '[PLAINTIFF NAME]')}
Plaintiff

Date: {datetime.now().strftime('%B %d, %Y')}

═══════════════════════════════════════════════════════════════

VERIFICATION

I, {form_data.get('plaintiff_name', '[PLAINTIFF NAME]')}, declare under penalty of perjury that the foregoing is true and correct to the best of my knowledge.

_______________________________
{form_data.get('plaintiff_name', '[PLAINTIFF NAME]')}

Date: {datetime.now().strftime('%B %d, %Y')}

═══════════════════════════════════════════════════════════════

IMPORTANT NOTICE:
This is a legal document. It should be reviewed by a licensed attorney before filing with any court.
Filing requirements vary by jurisdiction. Consult local court rules.
"""
        return content.strip()
    
    async def _generate_amendment(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate an amendment to contract."""
        
        content = f"""
AMENDMENT TO CONTRACT

═══════════════════════════════════════════════════════════════

This Amendment ("Amendment") is entered into as of {form_data.get('effective_date', datetime.now().strftime('%B %d, %Y'))}, by and between:

PARTY A: {form_data.get('party_a', '[PARTY A NAME]')}
PARTY B: {form_data.get('party_b', '[PARTY B NAME]')}

(collectively, the "Parties")

RECITALS

WHEREAS, the Parties entered into a contract titled "{form_data.get('original_contract_name', '[ORIGINAL CONTRACT NAME]')}" (the "Original Contract");

WHEREAS, the Parties wish to amend certain provisions of the Original Contract;

WHEREAS, the reason for this amendment is: {form_data.get('reason_for_amendment', '[REASON FOR AMENDMENT]')};

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, the Parties agree as follows:

AMENDMENTS

1. SECTIONS TO BE AMENDED

The following sections of the Original Contract are hereby amended:

{form_data.get('sections_to_amend', '[SECTIONS TO AMEND]')}

2. NEW TERMS AND CONDITIONS

The amended sections shall now read as follows:

{form_data.get('new_terms', '[NEW TERMS AND CONDITIONS]')}

3. EFFECTIVE DATE

This Amendment shall be effective as of {form_data.get('effective_date', datetime.now().strftime('%B %d, %Y'))}.

4. REMAINING TERMS

All other terms and conditions of the Original Contract not specifically amended herein shall remain in full force and effect.

5. GOVERNING LAW

This Amendment shall be governed by the laws of {jurisdiction or 'the applicable jurisdiction'}.

6. ENTIRE AGREEMENT

This Amendment, together with the Original Contract, constitutes the entire agreement between the Parties with respect to the subject matter hereof.

{form_data.get('additional_notes', '')}

IN WITNESS WHEREOF, the Parties have executed this Amendment as of the date first written above.

PARTY A:

_______________________________
{form_data.get('party_a', '[PARTY A NAME]')}
Date: _______________


PARTY B:

_______________________________
{form_data.get('party_b', '[PARTY B NAME]')}
Date: _______________

═══════════════════════════════════════════════════════════════

IMPORTANT NOTICE:
This amendment should be reviewed by legal counsel before execution.
Both parties should retain signed copies for their records.
"""
        return content.strip()
    
    async def _generate_nda(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate a Non-Disclosure Agreement."""
        
        content = f"""
NON-DISCLOSURE AGREEMENT (NDA)

═══════════════════════════════════════════════════════════════

This Non-Disclosure Agreement ("Agreement") is entered into as of {form_data.get('effective_date', datetime.now().strftime('%B %d, %Y'))}, by and between:

DISCLOSING PARTY: {form_data.get('disclosing_party', '[DISCLOSING PARTY NAME]')}
RECEIVING PARTY: {form_data.get('receiving_party', '[RECEIVING PARTY NAME]')}

RECITALS

WHEREAS, the Disclosing Party possesses certain confidential and proprietary information;

WHEREAS, the Receiving Party desires to receive such information for the following purpose:
{form_data.get('purpose', '[PURPOSE OF DISCLOSURE]')};

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

1. DEFINITION OF CONFIDENTIAL INFORMATION

"Confidential Information" means:
{form_data.get('confidential_info', '[DESCRIPTION OF CONFIDENTIAL INFORMATION]')}

2. OBLIGATIONS OF RECEIVING PARTY

The Receiving Party agrees to:
a) Hold the Confidential Information in strict confidence;
b) Not disclose the Confidential Information to any third parties;
c) Use the Confidential Information solely for the stated purpose;
d) Protect the Confidential Information with the same degree of care used for its own confidential information.

3. TERM

This Agreement shall remain in effect for {form_data.get('term_years', '2')} years from the Effective Date.

4. EXCEPTIONS

This Agreement does not apply to information that:
a) Is or becomes publicly available through no breach of this Agreement;
b) Was rightfully in the Receiving Party's possession prior to disclosure;
c) Is independently developed by the Receiving Party;
d) Is required to be disclosed by law or court order.

5. RETURN OF MATERIALS

Upon termination of this Agreement or upon request, the Receiving Party shall return or destroy all Confidential Information.

6. GOVERNING LAW

This Agreement shall be governed by the laws of {form_data.get('governing_law', jurisdiction or 'the applicable jurisdiction')}.

7. REMEDIES

The parties acknowledge that breach of this Agreement may cause irreparable harm for which monetary damages may be inadequate, and agree that injunctive relief may be appropriate.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

DISCLOSING PARTY:

_______________________________
{form_data.get('disclosing_party', '[DISCLOSING PARTY NAME]')}
Date: _______________


RECEIVING PARTY:

_______________________________
{form_data.get('receiving_party', '[RECEIVING PARTY NAME]')}
Date: _______________

═══════════════════════════════════════════════════════════════
"""
        return content.strip()
    
    async def _generate_will(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate a Last Will and Testament."""
        
        content = f"""
LAST WILL AND TESTAMENT

═══════════════════════════════════════════════════════════════

I, {form_data.get('testator_name', '[YOUR NAME]')}, residing at:
{form_data.get('testator_address', '[YOUR ADDRESS]')}

being of sound mind and memory, do hereby make, publish, and declare this to be my Last Will and Testament, hereby revoking all wills and codicils previously made by me.

ARTICLE I - EXECUTOR

I hereby nominate and appoint {form_data.get('executor_name', '[EXECUTOR NAME]')}, residing at {form_data.get('executor_address', '[EXECUTOR ADDRESS]')}, as the Executor of this Will.

ARTICLE II - BENEFICIARIES

I hereby give, devise, and bequeath my estate as follows:

{form_data.get('beneficiaries', '[LIST OF BENEFICIARIES AND THEIR SHARES]')}

ARTICLE III - SPECIFIC BEQUESTS

{form_data.get('specific_bequests', 'No specific bequests.')}

ARTICLE IV - GUARDIAN FOR MINOR CHILDREN

{f"I appoint {form_data.get('guardian_minor', '[GUARDIAN NAME]')} as guardian of any minor children." if form_data.get('guardian_minor') else 'Not applicable.'}

ARTICLE V - POWERS OF EXECUTOR

I grant my Executor full power and authority to:
a) Sell, transfer, or dispose of any property;
b) Pay all debts, taxes, and expenses;
c) Distribute assets to beneficiaries;
d) Take any actions necessary to administer this estate.

ARTICLE VI - GOVERNING LAW

This Will shall be governed by the laws of {jurisdiction or 'the applicable jurisdiction'}.

IN WITNESS WHEREOF, I have hereunto set my hand this {datetime.now().strftime('%d day of %B, %Y')}.

_______________________________
{form_data.get('testator_name', '[YOUR NAME]')}
Testator


WITNESSES:

We, the undersigned witnesses, each do hereby declare that the Testator signed this Will in our presence, and that we signed as witnesses in the Testator's presence and in the presence of each other.

Witness 1:
_______________________________
Name: _______________
Address: _______________
Date: _______________

Witness 2:
_______________________________
Name: _______________
Address: _______________
Date: _______________

═══════════════════════════════════════════════════════════════

IMPORTANT NOTICE:
This Will should be reviewed by an attorney and executed according to state law requirements.
Most jurisdictions require two witnesses and may require notarization.
Store the original in a safe place and inform your executor of its location.
"""
        return content.strip()
    
    async def _generate_power_of_attorney(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate a Power of Attorney."""
        
        durable_clause = """

This Power of Attorney shall not be affected by the subsequent disability or incapacity of the Principal (Durable Power of Attorney).""" if form_data.get('durable') else ""
        
        content = f"""
POWER OF ATTORNEY

═══════════════════════════════════════════════════════════════

KNOW ALL MEN BY THESE PRESENTS:

I, {form_data.get('principal_name', '[YOUR NAME]')} (the "Principal"), residing at:
{form_data.get('principal_address', '[YOUR ADDRESS]')}

do hereby appoint {form_data.get('agent_name', '[AGENT NAME]')} (the "Agent" or "Attorney-in-Fact"), residing at:
{form_data.get('agent_address', '[AGENT ADDRESS]')}

as my true and lawful Attorney-in-Fact to act in my name, place, and stead.

POWERS GRANTED

I hereby grant to my Agent full power and authority to:

{form_data.get('powers_granted', '[POWERS GRANTED TO AGENT]')}

EFFECTIVE DATE

This Power of Attorney shall be effective as of {form_data.get('effective_date', datetime.now().strftime('%B %d, %Y'))}.{durable_clause}

LIMITATIONS

This Power of Attorney does not authorize my Agent to:
- Make healthcare decisions (unless specifically stated)
- Change my will or estate plan
- Act in a manner contrary to my best interests

REVOCATION

I reserve the right to revoke this Power of Attorney at any time by providing written notice to my Agent.

GOVERNING LAW

This Power of Attorney shall be governed by the laws of {jurisdiction or 'the applicable jurisdiction'}.

THIRD PARTY RELIANCE

Any third party who receives a copy of this document may rely upon and act under it. Revocation of this Power of Attorney is not effective as to a third party until the third party has actual knowledge of the revocation.

IN WITNESS WHEREOF, I have executed this Power of Attorney on {datetime.now().strftime('%B %d, %Y')}.

_______________________________
{form_data.get('principal_name', '[YOUR NAME]')}
Principal

STATE OF _______________
COUNTY OF _______________

On this ___ day of _______, 20___, before me personally appeared {form_data.get('principal_name', '[YOUR NAME]')}, known to me to be the person whose name is subscribed to the foregoing instrument, and acknowledged that they executed the same.

_______________________________
Notary Public
My Commission Expires: _______________

═══════════════════════════════════════════════════════════════

IMPORTANT NOTICE:
This Power of Attorney must be notarized to be valid in most jurisdictions.
Provide copies to relevant financial institutions and healthcare providers.
Review and update this document regularly.
"""
        return content.strip()
    
    async def _generate_lease_agreement(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate a Lease Agreement."""
        
        content = f"""
RESIDENTIAL LEASE AGREEMENT

═══════════════════════════════════════════════════════════════

This Lease Agreement ("Lease") is entered into as of {form_data.get('start_date', datetime.now().strftime('%B %d, %Y'))}, by and between:

LANDLORD: {form_data.get('landlord_name', '[LANDLORD NAME]')}
TENANT: {form_data.get('tenant_name', '[TENANT NAME]')}

PROPERTY

The Landlord hereby leases to the Tenant the following property:
{form_data.get('property_address', '[PROPERTY ADDRESS]')}
(the "Premises")

TERM

The term of this Lease shall be {form_data.get('lease_term', '[TERM]')} months, commencing on {form_data.get('start_date', '[START DATE]')}.

RENT

Tenant agrees to pay rent in the amount of ${form_data.get('monthly_rent', '[AMOUNT]')} per month, due on the first day of each month.

SECURITY DEPOSIT

Tenant has deposited ${form_data.get('security_deposit', '[AMOUNT]')} as a security deposit, to be held by Landlord and returned upon termination of this Lease, subject to deductions for damages.

UTILITIES

{form_data.get('utilities_included', 'Tenant is responsible for all utilities unless otherwise specified.')}

PETS

{form_data.get('pet_policy', 'No pets allowed without prior written consent of Landlord.')}

MAINTENANCE AND REPAIRS

Landlord shall maintain the Premises in habitable condition. Tenant shall be responsible for minor repairs and maintenance.

USE OF PREMISES

The Premises shall be used solely as a residential dwelling. No commercial activities are permitted without Landlord's written consent.

TERMINATION

Either party may terminate this Lease upon 30 days' written notice, subject to applicable law.

GOVERNING LAW

This Lease shall be governed by the laws of {jurisdiction or 'the applicable jurisdiction'}.

ENTIRE AGREEMENT

This Lease constitutes the entire agreement between the parties.

IN WITNESS WHEREOF, the parties have executed this Lease as of the date first written above.

LANDLORD:

_______________________________
{form_data.get('landlord_name', '[LANDLORD NAME]')}
Date: _______________


TENANT:

_______________________________
{form_data.get('tenant_name', '[TENANT NAME]')}
Date: _______________

═══════════════════════════════════════════════════════════════
"""
        return content.strip()
    
    async def _generate_employment_contract(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate an Employment Contract."""
        
        content = f"""
EMPLOYMENT CONTRACT

═══════════════════════════════════════════════════════════════

This Employment Contract ("Agreement") is entered into as of {form_data.get('start_date', datetime.now().strftime('%B %d, %Y'))}, by and between:

EMPLOYER: {form_data.get('employer_name', '[EMPLOYER NAME]')}
EMPLOYEE: {form_data.get('employee_name', '[EMPLOYEE NAME]')}

POSITION

Employee is hired for the position of {form_data.get('position', '[JOB POSITION]')}.

START DATE

Employment shall commence on {form_data.get('start_date', '[START DATE]')}.

COMPENSATION

Employee shall receive an annual salary of ${form_data.get('salary', '[AMOUNT]')}, payable in accordance with Employer's standard payroll practices.

BENEFITS

{form_data.get('benefits', 'Employee shall be eligible for benefits as described in the Employee Handbook.')}

WORK HOURS

{form_data.get('work_hours', 'Standard work hours are Monday through Friday, 9:00 AM to 5:00 PM.')}

PROBATION PERIOD

{f"Employee shall be subject to a probationary period of {form_data.get('probation_period', '90')} days." if form_data.get('probation_period') else 'No probationary period applies.'}

TERMINATION

{f"Either party may terminate this Agreement upon {form_data.get('termination_notice', '30')} days' written notice." if form_data.get('termination_notice') else 'Termination terms as per applicable law.'}

CONFIDENTIALITY

Employee agrees to maintain the confidentiality of all proprietary information of the Employer.

NON-COMPETE

Employee agrees not to engage in any competing business during employment and for a reasonable period thereafter, as permitted by law.

GOVERNING LAW

This Agreement shall be governed by the laws of {jurisdiction or 'the applicable jurisdiction'}.

ENTIRE AGREEMENT

This Agreement constitutes the entire agreement between the parties regarding employment.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

EMPLOYER:

_______________________________
{form_data.get('employer_name', '[EMPLOYER NAME]')}
Date: _______________


EMPLOYEE:

_______________________________
{form_data.get('employee_name', '[EMPLOYEE NAME]')}
Date: _______________

═══════════════════════════════════════════════════════════════
"""
        return content.strip()
    
    async def _generate_business_contract(
        self,
        form_data: Dict[str, Any],
        jurisdiction: Optional[str]
    ) -> str:
        """Generate a Business Contract."""
        
        content = f"""
BUSINESS CONTRACT

═══════════════════════════════════════════════════════════════

This Business Contract ("Agreement") is entered into as of {form_data.get('effective_date', datetime.now().strftime('%B %d, %Y'))}, by and between:

PARTY A: {form_data.get('party_a_name', '[PARTY A NAME]')}
PARTY B: {form_data.get('party_b_name', '[PARTY B NAME]')}

(collectively, the "Parties")

PURPOSE

The purpose of this Agreement is:
{form_data.get('contract_purpose', '[PURPOSE OF CONTRACT]')}

OBLIGATIONS OF PARTY A

Party A agrees to:
{form_data.get('obligations_party_a', '[OBLIGATIONS OF PARTY A]')}

OBLIGATIONS OF PARTY B

Party B agrees to:
{form_data.get('obligations_party_b', '[OBLIGATIONS OF PARTY B]')}

PAYMENT TERMS

{form_data.get('payment_terms', '[PAYMENT TERMS]')}

TERM

This Agreement shall remain in effect for {form_data.get('contract_term', '[TERM]')}, commencing on {form_data.get('effective_date', '[EFFECTIVE DATE]')}.

TERMINATION

Either party may terminate this Agreement upon written notice if the other party materially breaches any provision of this Agreement.

CONFIDENTIALITY

Both parties agree to maintain the confidentiality of all proprietary information exchanged under this Agreement.

DISPUTE RESOLUTION

Any disputes arising under this Agreement shall be resolved through mediation, and if necessary, arbitration.

GOVERNING LAW

This Agreement shall be governed by the laws of {jurisdiction or 'the applicable jurisdiction'}.

ENTIRE AGREEMENT

This Agreement constitutes the entire agreement between the parties and supersedes all prior agreements and understandings.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

PARTY A:

_______________________________
{form_data.get('party_a_name', '[PARTY A NAME]')}
Date: _______________


PARTY B:

_______________________________
{form_data.get('party_b_name', '[PARTY B NAME]')}
Date: _______________

═══════════════════════════════════════════════════════════════

IMPORTANT NOTICE:
This is a general business contract template.
Have this agreement reviewed by legal counsel before execution.
Customize terms to fit your specific business needs.
"""
        return content.strip()


# Singleton instance
_document_generation_service = None

def get_document_generation_service(llm_client=None):
    """Get or create the document generation service singleton."""
    global _document_generation_service
    if _document_generation_service is None:
        _document_generation_service = DocumentGenerationService(llm_client)
    return _document_generation_service
