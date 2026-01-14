export const environment = {
  production: true,
  // Update this with your actual Cloud Run backend URL after deployment
  apiUrl: process.env['BACKEND_URL'] || 'https://legal-bot-backend-XXXXX.us-central1.run.app',
  showEvaluation: false,
  
  // OAuth Configuration (client IDs only - secrets stay on backend)
  googleClientId: process.env['GOOGLE_CLIENT_ID'] || '',
  microsoftClientId: process.env['MICROSOFT_CLIENT_ID'] || '',
  
  // Feature flags
  enableMultiAccount: false,
  enableLawyerVerification: true
};
