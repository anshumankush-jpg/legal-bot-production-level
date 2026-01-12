import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { UserContextService } from '../../services/user-context.service';
import { UserPreferencesService } from '../../services/user-preferences.service';

interface Language {
  code: string;
  name: string;
  flag: string;
}

interface Province {
  code: string;
  name: string;
}

@Component({
  selector: 'app-setup-wizard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './setup-wizard.component.html',
  styleUrls: ['./setup-wizard.component.scss']
})
export class SetupWizardComponent implements OnInit {
  currentStep = 1;
  totalSteps = 5;
  
  languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇨🇦' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ', flag: '🇨🇦' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
    { code: 'zh', name: '中文', flag: '🇨🇳' }
  ];

  countries = [
    { code: 'CA', name: 'Canada', flag: '🇨🇦' },
    { code: 'US', name: 'United States', flag: '🇺🇸' }
  ];

  canadianProvinces: Province[] = [
    { code: 'ON', name: 'Ontario' },
    { code: 'BC', name: 'British Columbia' },
    { code: 'QC', name: 'Quebec' },
    { code: 'AB', name: 'Alberta' },
    { code: 'MB', name: 'Manitoba' },
    { code: 'SK', name: 'Saskatchewan' },
    { code: 'NS', name: 'Nova Scotia' },
    { code: 'NB', name: 'New Brunswick' },
    { code: 'NL', name: 'Newfoundland and Labrador' },
    { code: 'PE', name: 'Prince Edward Island' },
    { code: 'NT', name: 'Northwest Territories' },
    { code: 'YT', name: 'Yukon' },
    { code: 'NU', name: 'Nunavut' }
  ];

  usStates: Province[] = [
    { code: 'CA', name: 'California' },
    { code: 'NY', name: 'New York' },
    { code: 'TX', name: 'Texas' },
    { code: 'FL', name: 'Florida' },
    { code: 'IL', name: 'Illinois' },
    { code: 'PA', name: 'Pennsylvania' },
    { code: 'OH', name: 'Ohio' },
    { code: 'GA', name: 'Georgia' },
    { code: 'NC', name: 'North Carolina' },
    { code: 'MI', name: 'Michigan' },
    { code: 'NJ', name: 'New Jersey' },
    { code: 'VA', name: 'Virginia' },
    { code: 'WA', name: 'Washington' },
    { code: 'AZ', name: 'Arizona' },
    { code: 'MA', name: 'Massachusetts' },
    { code: 'TN', name: 'Tennessee' },
    { code: 'IN', name: 'Indiana' },
    { code: 'MO', name: 'Missouri' },
    { code: 'MD', name: 'Maryland' },
    { code: 'WI', name: 'Wisconsin' },
    { code: 'CO', name: 'Colorado' },
    { code: 'MN', name: 'Minnesota' },
    { code: 'SC', name: 'South Carolina' },
    { code: 'AL', name: 'Alabama' },
    { code: 'LA', name: 'Louisiana' },
    { code: 'KY', name: 'Kentucky' },
    { code: 'OR', name: 'Oregon' },
    { code: 'OK', name: 'Oklahoma' },
    { code: 'CT', name: 'Connecticut' },
    { code: 'UT', name: 'Utah' },
    { code: 'IA', name: 'Iowa' },
    { code: 'NV', name: 'Nevada' },
    { code: 'AR', name: 'Arkansas' },
    { code: 'MS', name: 'Mississippi' },
    { code: 'KS', name: 'Kansas' },
    { code: 'NM', name: 'New Mexico' },
    { code: 'NE', name: 'Nebraska' },
    { code: 'WV', name: 'West Virginia' },
    { code: 'ID', name: 'Idaho' },
    { code: 'HI', name: 'Hawaii' },
    { code: 'NH', name: 'New Hampshire' },
    { code: 'ME', name: 'Maine' },
    { code: 'MT', name: 'Montana' },
    { code: 'RI', name: 'Rhode Island' },
    { code: 'DE', name: 'Delaware' },
    { code: 'SD', name: 'South Dakota' },
    { code: 'ND', name: 'North Dakota' },
    { code: 'AK', name: 'Alaska' },
    { code: 'VT', name: 'Vermont' },
    { code: 'WY', name: 'Wyoming' },
    { code: 'DC', name: 'District of Columbia' }
  ];

  setupForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private userContext: UserContextService,
    private preferencesService: UserPreferencesService
  ) {
    this.setupForm = this.fb.group({
      offenceNumber: ['', Validators.required],
      location: ['', Validators.required],
      additionalInfo: ['']
    });
  }

  ngOnInit(): void {
    const existing = this.userContext.getPreferences();
    if (existing) {
      this.setupForm.patchValue({
        offenceNumber: existing.offenceNumber || '',
        location: existing.location || '',
        additionalInfo: existing.additionalInfo || ''
      });
    }
  }

  finishSetup(): void {
    if (this.setupForm.valid) {
      this.isLoading = true;
      const formData = this.setupForm.value;
      
      // Extract province/state from location if possible
      const locationParts = formData.location.split(',').map((s: string) => s.trim());
      const provinceOrState = locationParts.length > 1 ? locationParts[1] : '';
      
      const preferences = {
        language: 'en', // Default to English
        country: provinceOrState ? (provinceOrState.length === 2 ? 'US' : 'CA') : 'CA',
        provinceOrState: provinceOrState || 'ON',
        offenceNumber: formData.offenceNumber,
        location: formData.location,
        additionalInfo: formData.additionalInfo
      };
      
      this.preferencesService.savePreferences(preferences).subscribe({
        next: () => {
          this.userContext.setPreferences(preferences);
          this.router.navigate(['/chat']);
        },
        error: (error) => {
          console.error('Error saving preferences:', error);
          // Still navigate - preferences saved locally
          this.userContext.setPreferences(preferences);
          this.router.navigate(['/chat']);
        }
      });
    }
  }
}