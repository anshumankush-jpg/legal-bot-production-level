import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import EnhancedLegalResponse from './EnhancedLegalResponse';
import RecentUpdates from './RecentUpdates';
import GovernmentResources from './GovernmentResources';
import VoiceChat from './VoiceChat';
import CaseLookup from './CaseLookup';
import AmendmentGenerator from './AmendmentGenerator';
import DocumentGenerator from './DocumentGenerator';
import ChatHistorySearch from './ChatHistorySearch';
import AISummaryModal from './AISummaryModal';
import ChatSidebar from './ChatSidebar';

const API_URL = 'http://localhost:8000';

const ChatInterface = ({ preferences, lawTypeSelection, onResetPreferences, onChangeLawType, onLogout, user, onNavigate }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [offenceNumber, setOffenceNumber] = useState('');
  const [userId] = useState('test_user_' + Date.now()); // For demo purposes
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [contextMenu, setContextMenu] = useState(null);
  const [savedChats, setSavedChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoRead, setAutoRead] = useState(false);
  const [showRecentUpdates, setShowRecentUpdates] = useState(false);
  const [recentUpdates, setRecentUpdates] = useState([]);
  const [showVoiceChat, setShowVoiceChat] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const [showCaseLookup, setShowCaseLookup] = useState(false);
  const [showAmendmentGenerator, setShowAmendmentGenerator] = useState(false);
  const [showDocumentGenerator, setShowDocumentGenerator] = useState(false);
  const [showChatHistory, setShowChatHistory] = useState(false);
  const [showAISummary, setShowAISummary] = useState(false);
  const [sessionId] = useState('session_' + Date.now());
  const [activeResource, setActiveResource] = useState(() => {
    const saved = localStorage.getItem('legubot_activeResource');
    return saved || null;
  });
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const pdfInputRef = useRef(null);
  const docInputRef = useRef(null);
  const textInputRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  };

  const loadConversations = async () => {
    try {
      const response = await fetch(`${API_URL}/api/profile/conversations`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) return;
      const data = await response.json();
      const conversations = (data.conversations || []).map(c => ({
        id: c.id,
        title: c.title || 'Untitled Chat',
        updated_at: c.updated_at || c.created_at,
        last_message_at: c.last_message_at
      }));
      setSavedChats(conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversationMessages = async (conversationId) => {
    try {
      const response = await fetch(
        `${API_URL}/api/profile/conversations/${conversationId}/messages`,
        { headers: getAuthHeaders() }
      );
      if (!response.ok) return;
      const data = await response.json();
      const loadedMessages = (data.messages || []).map(m => ({
        id: m.id,
        role: m.role,
        content: m.content,
        timestamp: m.created_at ? new Date(m.created_at) : new Date()
      }));
      setMessages(loadedMessages);
      setCurrentChatId(conversationId);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
    }
  };

  const createConversation = async () => {
    const payload = {
      title: 'New Chat',
      law_type: lawTypeSelection?.lawType,
      jurisdiction_country: preferences?.country,
      jurisdiction_region: preferences?.province
    };
    const response = await fetch(`${API_URL}/api/profile/conversations`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }
    const data = await response.json();
    const newChat = {
      id: data.id,
      title: data.title || 'New Chat',
      updated_at: data.created_at
    };
    setSavedChats(prev => [newChat, ...prev]);
    setCurrentChatId(data.id);
    return data.id;
  };

  const persistMessage = async (conversationId, message) => {
    try {
      await fetch(`${API_URL}/api/profile/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          role: message.role,
          content: message.content
        })
      });
    } catch (error) {
      console.error('Failed to persist message:', error);
    }
  };

  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

  // Show welcome message when law type is selected
  useEffect(() => {
    if (lawTypeSelection && messages.length === 0) {
      showWelcomeMessage();
    }
  }, [lawTypeSelection]);

  // Save activeResource to localStorage
  useEffect(() => {
    if (activeResource) {
      localStorage.setItem('legubot_activeResource', activeResource);
    }
  }, [activeResource]);

  // Handle resource clicks from sidebar
  const handleResourceClick = (resourceId) => {
    const isLawyerApproved = user?.role === 'lawyer' && user?.lawyer_status === 'approved';
    const lawyerOnly = ['amendments', 'documents'];
    if (lawyerOnly.includes(resourceId) && !isLawyerApproved) {
      addSystemMessage('Access restricted: lawyer verification required for this tool.', true);
      return;
    }
    setActiveResource(resourceId);
    switch(resourceId) {
      case 'recent-updates':
        setShowRecentUpdates(true);
        break;
      case 'case-lookup':
        setShowCaseLookup(true);
        break;
      case 'amendments':
        setShowAmendmentGenerator(true);
        break;
      case 'documents':
        setShowDocumentGenerator(true);
        break;
      case 'history':
        setShowChatHistory(true);
        break;
      case 'change-law-type':
        onChangeLawType && onChangeLawType();
        break;
      case 'settings':
        onResetPreferences && onResetPreferences();
        break;
      case 'ai-summary':
        setShowAISummary(true);
        break;
      case 'quick-summary':
        if (messages.length > 0) {
          setShowAISummary(true);
        }
        break;
      default:
        break;
    }
  };

  const getLawTypeGuidedQuestions = (lawType) => {
    const guidedQuestions = {
      'Constitutional Law': [
        'What constitutional right do you believe was violated? (Freedom of speech, religion, equality, due process)',
        'When and where did this occur? (Date, location, circumstances)',
        'What government action or law are you challenging?',
        'Have you filed any complaints or legal actions yet?'
      ],
      'Criminal Law': [
        'What criminal charge were you given? (Theft, Assault, Fraud, Drug Offense, etc.)',
        'When and where did this occur? (Date, time, location, road conditions)',
        'What were the specific circumstances of the incident?',
        'Have you been arrested? Do you have a court date?',
        'Do you have prior criminal convictions or a criminal record?'
      ],
      'Traffic Law': [
        'What traffic offense were you charged with? (Speeding, Careless Driving, Distracted Driving, Impaired Driving, etc.)',
        'When and where did this occur? (Date, time, location, road conditions)',
        'If speeding: What was the speed limit and your actual speed?',
        'If distracted driving: What were you doing? (Phone use, eating, other)',
        'If impaired driving: What was your Blood Alcohol Content (BAC) or THC level? (Legal limit: 0.08% BAC, 2-5ng THC)',
        'Were you given a roadside test? What were the results?',
        'Do you have prior traffic convictions or demerit points?',
        'Have you received a court date or summons?'
      ],
      'Business Litigation': [
        'What type of business do you have? (Corporation, Partnership, Sole Proprietorship, LLC)',
        'What is your industry or business sector?',
        'What specific business dispute or litigation issue do you have? (Breach of contract, partnership conflict, shareholder dispute, franchise dispute)',
        'Who are the other parties involved in the dispute?',
        'What is the approximate value of the claim or damages?',
        'Have you attempted mediation, arbitration, or settlement discussions?'
      ],
      'Business Law': [
        'What type of business do you have or want to start? (Corporation, Partnership, Sole Proprietorship, LLC, Franchise)',
        'What is your industry or business sector? (Retail, Tech, Healthcare, Manufacturing, Professional Services, etc.)',
        'What specific business legal matter do you need help with? (Formation/Incorporation, Contracts, Financing, Mergers & Acquisitions, Compliance, Intellectual Property, Franchising)',
        'What is the current stage of your business? (Startup/Planning, Operating, Expanding, Selling)',
        'Are there any regulatory or compliance requirements specific to your industry?',
        'What is your main legal question or concern?'
      ],
      'Family Law': [
        'What family law matter do you need help with? (Divorce, child custody, support, separation)',
        'Are you married or in a common-law relationship? For how long?',
        'Do you have children? What are their ages?',
        'Are there any existing court orders or agreements?',
        'What assets or property are involved?'
      ],
      'Employment Law': [
        'What employment issue do you have? (Wrongful dismissal, harassment, discrimination)',
        'How long have you been employed with this employer?',
        'What were the circumstances of the issue?',
        'Do you have an employment contract?',
        'Have you filed a complaint with the labor board or HR?'
      ],
      'Immigration Law': [
        'What immigration matter do you need help with? (Work permit, permanent residence, citizenship, refugee claim)',
        'What is your current immigration status in Canada/USA?',
        'What is your country of origin?',
        'Have you applied for any immigration programs before?',
        'Do you have any inadmissibility issues? (Criminal record, medical, etc.)'
      ],
      'Real Estate Law': [
        'What real estate matter do you need help with? (Buying, selling, landlord-tenant, property dispute)',
        'What type of property is involved? (Residential, commercial)',
        'Are there any existing contracts or agreements?',
        'What is the nature of the dispute or transaction?'
      ],
      'Tax Law': [
        'What tax matter do you need help with? (Tax audit, tax debt, tax planning, tax dispute)',
        'Is this related to personal or corporate taxes?',
        'What tax years are involved?',
        'Have you received any notices from CRA or IRS?',
        'What is the nature of the tax issue?'
      ],
      'Civil Law': [
        'What type of civil dispute do you have? (Contract dispute, personal injury, property dispute)',
        'Who are the parties involved?',
        'What damages or compensation are you seeking?',
        'Have you attempted to resolve this dispute informally?'
      ],
      'Administrative Law': [
        'What government agency decision are you challenging? (Immigration board, tax authority, licensing board)',
        'When did you receive the decision?',
        'What are the grounds for your challenge?',
        'Have you filed an appeal or judicial review?'
      ],
      'Wills, Estates, and Trusts': [
        'What estate matter do you need help with? (Will, estate planning, probate, estate dispute)',
        'Are you the executor, beneficiary, or estate owner?',
        'What assets are involved in the estate?',
        'Are there any disputes among beneficiaries?'
      ],
      'Health Law': [
        'What healthcare legal matter do you have? (Medical malpractice, patient rights, consent issues)',
        'When did the incident occur?',
        'What healthcare provider or facility is involved?',
        'What damages or harm occurred?'
      ]
    };

    return guidedQuestions[lawType] || [
      'Please describe your legal situation in detail',
      'When did this occur?',
      'What outcome are you seeking?'
    ];
  };

  // Fetch government resources dynamically from backend
  const getGovernmentResourcesForLawType = async (lawType, province = null) => {
    try {
      const provinceParam = province || preferences?.province || '';
      const url = `${API_URL}/api/artillery/government-resources?law_type=${encodeURIComponent(lawType)}${provinceParam ? `&province=${provinceParam}` : ''}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        console.error('Failed to fetch government resources');
        return [];
      }
      
      const data = await response.json();
      return data.resources || [];
    } catch (error) {
      console.error('Error fetching government resources:', error);
      return [];
    }
  };

  const getTranslatedWelcomeText = (lang) => {
    const translations = {
      'en': {
        welcome: 'Welcome to LEGID - Your Legal Intelligence Assistant!',
        greeting: 'Thank you for reaching out. I\'m here to assist you with your',
        matter: 'matter.',
        howCanHelp: 'How may I assist you today? Please provide a detailed description of your legal situation, including:',
        keyPoints: [
          'The nature of your legal issue or question',
          'Relevant dates, locations, and parties involved',
          'Any documents or evidence you have',
          'What outcome or information you\'re seeking'
        ],
        disclaimer: 'I\'ll provide you with relevant legal information based on official sources and statutes. Please note that this is general legal information, not legal advice.',
        selectedArea: 'Selected Legal Area',
        jurisdiction: 'Jurisdiction',
        whatCovers: 'What This Covers',
        canOnlyHelp: 'I can only help with',
        questions: 'questions.',
        thisIncludes: 'This includes:',
        questionsOutside: 'Questions outside',
        willBeRedirected: 'will be redirected to the appropriate legal area.',
        toHelpBest: 'To help you best, please describe your situation by answering:',
        pleaseDescribe: 'Please describe your',
        situation: 'situation in detail, and I\'ll provide relevant legal information based on official sources.'
      },
      'hi': {
        welcome: 'LEGID कानूनी सहायक में आपका स्वागत है!',
        greeting: 'संपर्क करने के लिए धन्यवाद। मैं आपके',
        matter: 'मामले में आपकी सहायता के लिए यहां हूं।',
        howCanHelp: 'आज मैं आपकी कैसे सहायता कर सकता हूं? कृपया अपनी कानूनी स्थिति का विस्तृत विवरण प्रदान करें, जिसमें शामिल हो:',
        keyPoints: [
          'आपके कानूनी मुद्दे या प्रश्न की प्रकृति',
          'प्रासंगिक तिथियां, स्थान और संबंधित पक्ष',
          'आपके पास कोई दस्तावेज या साक्ष्य',
          'आप क्या परिणाम या जानकारी चाहते हैं'
        ],
        disclaimer: 'मैं आपको आधिकारिक स्रोतों और क़ानूनों के आधार पर प्रासंगिक कानूनी जानकारी प्रदान करूंगा। कृपया ध्यान दें कि यह सामान्य कानूनी जानकारी है, कानूनी सलाह नहीं।',
        selectedArea: 'चयनित कानूनी क्षेत्र',
        jurisdiction: 'न्यायालय क्षेत्र',
        whatCovers: 'यह क्या कवर करता है',
        canOnlyHelp: 'मैं केवल',
        questions: 'प्रश्नों में मदद कर सकता हूं।',
        thisIncludes: 'इसमें शामिल है:',
        questionsOutside: 'बाहर के प्रश्न',
        willBeRedirected: 'उचित कानूनी क्षेत्र में पुनर्निर्देशित किए जाएंगे।',
        toHelpBest: 'आपकी सर्वोत्तम मदद के लिए, कृपया अपनी स्थिति का वर्णन करें:',
        pleaseDescribe: 'कृपया अपनी',
        situation: 'स्थिति का विस्तार से वर्णन करें, और मैं आधिकारिक स्रोतों के आधार पर प्रासंगिक कानूनी जानकारी प्रदान करूंगा।'
      },
      'fr': {
        welcome: 'Bienvenue dans l\'assistant juridique LEGID!',
        greeting: 'Merci de nous avoir contactés. Je suis là pour vous aider avec votre',
        matter: 'affaire.',
        howCanHelp: 'Comment puis-je vous aider aujourd\'hui? Veuillez fournir une description détaillée de votre situation juridique, incluant:',
        keyPoints: [
          'La nature de votre problème ou question juridique',
          'Les dates, lieux et parties concernées pertinents',
          'Tous documents ou preuves que vous avez',
          'Le résultat ou l\'information que vous recherchez'
        ],
        disclaimer: 'Je vous fournirai des informations juridiques pertinentes basées sur des sources et des lois officielles. Veuillez noter qu\'il s\'agit d\'informations juridiques générales, et non de conseils juridiques.',
        selectedArea: 'Domaine juridique sélectionné',
        jurisdiction: 'Juridiction',
        whatCovers: 'Ce que cela couvre',
        canOnlyHelp: 'Je ne peux aider qu\'avec',
        questions: 'questions.',
        thisIncludes: 'Cela inclut:',
        questionsOutside: 'Les questions en dehors de',
        willBeRedirected: 'seront redirigées vers le domaine juridique approprié.',
        toHelpBest: 'Pour mieux vous aider, veuillez décrire votre situation en répondant:',
        pleaseDescribe: 'Veuillez décrire votre',
        situation: 'situation en détail, et je fournirai des informations juridiques pertinentes basées sur des sources officielles.'
      },
      'es': {
        welcome: '¡Bienvenido al asistente legal LEGID!',
        greeting: 'Gracias por contactarnos. Estoy aquí para ayudarle con su',
        matter: 'asunto.',
        howCanHelp: '¿Cómo puedo ayudarle hoy? Por favor proporcione una descripción detallada de su situación legal, incluyendo:',
        keyPoints: [
          'La naturaleza de su problema o pregunta legal',
          'Fechas, lugares y partes involucradas relevantes',
          'Cualquier documento o evidencia que tenga',
          'Qué resultado o información está buscando'
        ],
        disclaimer: 'Le proporcionaré información legal relevante basada en fuentes y estatutos oficiales. Tenga en cuenta que esta es información legal general, no asesoramiento legal.',
        selectedArea: 'Área legal seleccionada',
        jurisdiction: 'Jurisdicción',
        whatCovers: 'Qué cubre esto',
        canOnlyHelp: 'Solo puedo ayudar con',
        questions: 'preguntas.',
        thisIncludes: 'Esto incluye:',
        questionsOutside: 'Las preguntas fuera de',
        willBeRedirected: 'serán redirigidas al área legal apropiada.',
        toHelpBest: 'Para ayudarle mejor, por favor describa su situación respondiendo:',
        pleaseDescribe: 'Por favor describa su',
        situation: 'situación en detalle, y proporcionaré información legal relevante basada en fuentes oficiales.'
      },
      'pa': {
        welcome: 'LEGID ਕਾਨੂੰਨੀ ਸਹਾਇਕ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ!',
        greeting: 'ਸੰਪਰਕ ਕਰਨ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ। ਮੈਂ ਤੁਹਾਡੇ',
        matter: 'ਮਾਮਲੇ ਵਿੱਚ ਤੁਹਾਡੀ ਸਹਾਇਤਾ ਕਰਨ ਲਈ ਇੱਥੇ ਹਾਂ।',
        howCanHelp: 'ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਸਹਾਇਤਾ ਕਰ ਸਕਦਾ ਹਾਂ? ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਕਾਨੂੰਨੀ ਸਥਿਤੀ ਦਾ ਵਿਸਤ੍ਰਿਤ ਵਰਣਨ ਪ੍ਰਦਾਨ ਕਰੋ, ਜਿਸ ਵਿੱਚ ਸ਼ਾਮਲ ਹੈ:',
        keyPoints: [
          'ਤੁਹਾਡੇ ਕਾਨੂੰਨੀ ਮੁੱਦੇ ਜਾਂ ਸਵਾਲ ਦੀ ਪ੍ਰਕਿਰਤੀ',
          'ਸੰਬੰਧਿਤ ਤਾਰੀਖਾਂ, ਸਥਾਨ ਅਤੇ ਸ਼ਾਮਲ ਧਿਰਾਂ',
          'ਤੁਹਾਡੇ ਕੋਲ ਕੋਈ ਦਸਤਾਵੇਜ਼ ਜਾਂ ਸਬੂਤ',
          'ਤੁਸੀਂ ਕਿਹੜਾ ਨਤੀਜਾ ਜਾਂ ਜਾਣਕਾਰੀ ਚਾਹੁੰਦੇ ਹੋ'
        ],
        disclaimer: 'ਮੈਂ ਤੁਹਾਨੂੰ ਅਧਿਕਾਰਤ ਸਰੋਤਾਂ ਅਤੇ ਕਾਨੂੰਨਾਂ ਦੇ ਆਧਾਰ ਤੇ ਸੰਬੰਧਿਤ ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ ਪ੍ਰਦਾਨ ਕਰਾਂਗਾ। ਕਿਰਪਾ ਕਰਕੇ ਨੋਟ ਕਰੋ ਕਿ ਇਹ ਆਮ ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ ਹੈ, ਕਾਨੂੰਨੀ ਸਲਾਹ ਨਹੀਂ।',
        selectedArea: 'ਚੁਣਿਆ ਕਾਨੂੰਨੀ ਖੇਤਰ',
        jurisdiction: 'ਅਧਿਕਾਰ ਖੇਤਰ',
        whatCovers: 'ਇਹ ਕੀ ਕਵਰ ਕਰਦਾ ਹੈ',
        canOnlyHelp: 'ਮੈਂ ਸਿਰਫ਼',
        questions: 'ਸਵਾਲਾਂ ਵਿੱਚ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ।',
        thisIncludes: 'ਇਸ ਵਿੱਚ ਸ਼ਾਮਲ ਹੈ:',
        questionsOutside: 'ਬਾਹਰ ਦੇ ਸਵਾਲ',
        willBeRedirected: 'ਢੁਕਵੇਂ ਕਾਨੂੰਨੀ ਖੇਤਰ ਵਿੱਚ ਮੁੜ ਨਿਰਦੇਸ਼ਤ ਕੀਤੇ ਜਾਣਗੇ।',
        toHelpBest: 'ਤੁਹਾਡੀ ਸਭ ਤੋਂ ਵਧੀਆ ਮਦਦ ਕਰਨ ਲਈ, ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਸਥਿਤੀ ਦਾ ਵਰਣਨ ਕਰੋ:',
        pleaseDescribe: 'ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ',
        situation: 'ਸਥਿਤੀ ਦਾ ਵਿਸਤਾਰ ਨਾਲ ਵਰਣਨ ਕਰੋ, ਅਤੇ ਮੈਂ ਅਧਿਕਾਰਤ ਸਰੋਤਾਂ ਦੇ ਆਧਾਰ ਤੇ ਸੰਬੰਧਿਤ ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ ਪ੍ਰਦਾਨ ਕਰਾਂਗਾ।'
      },
      'zh': {
        welcome: '欢迎使用 LEGID 法律助手！',
        greeting: '感谢您的联系。我在这里帮助您处理您的',
        matter: '事务。',
        howCanHelp: '今天我能如何帮助您？请提供您法律情况的详细描述，包括：',
        keyPoints: [
          '您的法律问题或疑问的性质',
          '相关日期、地点和涉及的各方',
          '您拥有的任何文件或证据',
          '您寻求的结果或信息'
        ],
        disclaimer: '我将根据官方来源和法规为您提供相关的法律信息。请注意，这是一般法律信息，而非法律建议。',
        selectedArea: '选定的法律领域',
        jurisdiction: '管辖权',
        whatCovers: '涵盖范围',
        canOnlyHelp: '我只能帮助',
        questions: '问题。',
        thisIncludes: '这包括：',
        questionsOutside: '之外的问题',
        willBeRedirected: '将被重定向到适当的法律领域。',
        toHelpBest: '为了更好地帮助您，请描述您的情况：',
        pleaseDescribe: '请详细描述您的',
        situation: '情况，我将根据官方来源提供相关的法律信息。'
      }
    };
    return translations[lang] || translations['en'];
  };

  const showWelcomeMessage = async () => {
    const lawType = lawTypeSelection.lawType;
    const jurisdiction = lawTypeSelection.jurisdiction;
    const province = preferences?.province || null;
    
    // Fetch government resources dynamically based on province
    const governmentResources = await getGovernmentResourcesForLawType(lawType, province);
    
    const selectedLang = preferences?.language?.code || 'en';
    const t = getTranslatedWelcomeText(selectedLang);
    
    // Professional welcome message with greeting
    let message = `${t.welcome}\n\n`;
    message += `${t.greeting} ${lawType} ${t.matter}\n\n`;
    message += `${t.howCanHelp}\n\n`;
    
    // Add key points
    t.keyPoints.forEach((point, idx) => {
      message += `   ${idx + 1}. ${point}\n`;
    });
    
    message += `\n${t.disclaimer}`;
    
    // Add language note if not English
    if (selectedLang !== 'en') {
      const langName = getLanguageName(selectedLang);
      if (selectedLang === 'hi') {
        message += `\n\n🌐 मैं आपके सभी प्रश्नों का उत्तर हिन्दी में दूंगा।`;
      } else if (selectedLang === 'fr') {
        message += `\n\n🌐 Je répondrai à toutes vos questions en français.`;
      } else if (selectedLang === 'es') {
        message += `\n\n🌐 Responderé a todas tus preguntas en español.`;
      } else if (selectedLang === 'pa') {
        message += `\n\n🌐 ਮੈਂ ਤੁਹਾਡੇ ਸਾਰੇ ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦੇਵਾਂਗਾ।`;
      } else if (selectedLang === 'zh') {
        message += `\n\n🌐 我将用中文回答您的所有问题。`;
      } else {
        message += `\n\n🌐 I will respond to all your questions in ${langName}.`;
      }
    }
    
    const welcomeMessage = {
      id: Date.now(),
      role: 'assistant',
      content: message,
      timestamp: new Date(),
      isWelcome: true,
      governmentResources: governmentResources // Attach resources to message
    };
    
    setMessages([welcomeMessage]);
  };

  // Load saved chats from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('legubot_chats');
    if (saved) {
      try {
        setSavedChats(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load saved chats', e);
      }
    }
  }, []);

  // Save current chat when messages change
  useEffect(() => {
    if (messages.length > 0) {
      const chatData = {
        id: currentChatId || Date.now(),
        messages,
        timestamp: new Date().toISOString(),
        title: messages[0]?.content?.substring(0, 50) || 'New Chat'
      };
      
      if (!currentChatId) {
        setCurrentChatId(chatData.id);
      }

      // Update saved chats
      const updated = savedChats.filter(c => c.id !== chatData.id);
      updated.unshift(chatData);
      setSavedChats(updated.slice(0, 20)); // Keep last 20 chats
      localStorage.setItem('legubot_chats', JSON.stringify(updated.slice(0, 20)));
    }
  }, [messages]);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showUploadMenu && !event.target.closest('.upload-menu-container')) {
        setShowUploadMenu(false);
      }
      if (contextMenu && !event.target.closest('.context-menu')) {
        setContextMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUploadMenu, contextMenu]);

  // 🎯 Drag and Drop + Ctrl+V Paste Support
  useEffect(() => {
    const handleDragEnter = (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('🎯 Drag Enter - Counter:', dragCounter + 1);
      setDragCounter(prev => prev + 1);
      setIsDragging(true);
    };

    const handleDragLeave = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragCounter(prev => {
        const newCounter = prev - 1;
        console.log('🎯 Drag Leave - Counter:', newCounter);
        if (newCounter === 0) {
          setIsDragging(false);
        }
        return newCounter;
      });
    };

    const handleDragOver = (e) => {
      e.preventDefault();
      e.stopPropagation();
      // Keep showing overlay
      if (!isDragging) {
        setIsDragging(true);
      }
    };

    const handleDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('🎯 File Dropped!');
      setIsDragging(false);
      setDragCounter(0);

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        const file = files[0];
        console.log('📁 Processing file:', file.name);
        handleFileUpload(file);
      }
    };

    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        
        // Handle image paste
        if (item.type.indexOf('image') !== -1) {
          e.preventDefault();
          const blob = item.getAsFile();
          if (blob) {
            // Create a file from blob with proper name
            const file = new File([blob], `pasted-image-${Date.now()}.png`, { type: blob.type });
            handleFileUpload(file);
          }
          break;
        }
      }
    };

    // Add event listeners
    document.addEventListener('dragenter', handleDragEnter);
    document.addEventListener('dragleave', handleDragLeave);
    document.addEventListener('dragover', handleDragOver);
    document.addEventListener('drop', handleDrop);
    document.addEventListener('paste', handlePaste);

    return () => {
      document.removeEventListener('dragenter', handleDragEnter);
      document.removeEventListener('dragleave', handleDragLeave);
      document.removeEventListener('dragover', handleDragOver);
      document.removeEventListener('drop', handleDrop);
      document.removeEventListener('paste', handlePaste);
    };
  }, []);

  // Add system message helper
  const addSystemMessage = (content, isTemporary = false) => {
    const message = {
      id: Date.now(),
      role: 'system',
      content,
      timestamp: new Date(),
      isTemporary
    };
    setMessages(prev => [...prev, message]);

    // Auto-remove temporary messages after 5 seconds
    if (isTemporary) {
      setTimeout(() => {
        setMessages(prev => prev.filter(msg => msg.id !== message.id));
      }, 5000);
    }
  };

  // Message action handlers
  const handleCopyMessage = (content) => {
    navigator.clipboard.writeText(content);
    addSystemMessage('✅ Copied to clipboard', true);
  };

  const handleLikeMessage = (messageId) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, liked: !msg.liked, disliked: false } : msg
    ));
  };

  const handleDislikeMessage = (messageId) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, disliked: !msg.disliked, liked: false } : msg
    ));
  };

  const handleRegenerateResponse = async (messageId) => {
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex > 0) {
      const userMessage = messages[messageIndex - 1];
      if (userMessage.role === 'user') {
        // Remove the old response
        setMessages(prev => prev.filter(msg => msg.id !== messageId));
        // Resend the question
        setInput(userMessage.content);
        setTimeout(() => {
          document.querySelector('.chat-input')?.focus();
        }, 100);
      }
    }
  };

  const handleShareMessage = (content) => {
    if (navigator.share) {
      navigator.share({ text: content })
        .catch(err => console.log('Share failed', err));
    } else {
      handleCopyMessage(content);
    }
  };

  // Get language code for TTS
  const getLanguageCode = () => {
    if (!preferences || !preferences.language) return 'en';
    
    const langMap = {
      'en': 'en',
      'fr': 'fr',
      'es': 'es',
      'hi': 'hi',
      'pa': 'pa',
      'zh': 'zh'
    };
    
    return langMap[preferences.language.code] || 'en';
  };

  // Andy TTS - Multilingual text-to-speech
  const handleReadAloud = (content) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(content);
      
      // Get available voices
      let voices = window.speechSynthesis.getVoices();
      
      // If voices aren't loaded yet, wait for them
      if (voices.length === 0) {
        window.speechSynthesis.onvoiceschanged = () => {
          voices = window.speechSynthesis.getVoices();
          setupAndyVoice(utterance, voices, content);
        };
      } else {
        setupAndyVoice(utterance, voices, content);
      }
    } else {
      addSystemMessage('❌ Text-to-speech not supported in this browser', true);
    }
  };

  const setupAndyVoice = (utterance, voices, content) => {
    const selectedLang = getLanguageCode();
    
    // Language-specific voice preferences
    const voicePreferences = {
      'en': {
        codes: ['en-US', 'en-GB', 'en-CA', 'en-AU', 'en'],
        names: ['Microsoft Mark', 'Microsoft David', 'Google US English Male', 'Alex', 'Daniel', 'Fred'],
        langName: 'English'
      },
      'hi': {
        codes: ['hi-IN', 'hi'],
        names: ['Google हिन्दी', 'Microsoft Hemant', 'Lekha', 'Google Hindi'],
        langName: 'Hindi'
      },
      'fr': {
        codes: ['fr-FR', 'fr-CA', 'fr'],
        names: ['Google français', 'Microsoft Paul', 'Thomas', 'Google French'],
        langName: 'French'
      },
      'es': {
        codes: ['es-ES', 'es-MX', 'es-US', 'es'],
        names: ['Google español', 'Microsoft Pablo', 'Diego', 'Google Spanish'],
        langName: 'Spanish'
      },
      'pa': {
        codes: ['pa-IN', 'pa'],
        names: ['Google ਪੰਜਾਬੀ', 'Google Punjabi'],
        langName: 'Punjabi'
      },
      'zh': {
        codes: ['zh-CN', 'zh-TW', 'zh-HK', 'zh'],
        names: ['Google 普通话', 'Microsoft Kangkang', 'Ting-Ting', 'Google Chinese'],
        langName: 'Chinese'
      }
    };

    const langConfig = voicePreferences[selectedLang] || voicePreferences['en'];
    let selectedVoice = null;

    console.log('🎙️ Andy looking for', langConfig.langName, 'voice from', voices.length, 'available voices');

    // Strategy 1: Try exact name matches first
    for (const preferred of langConfig.names) {
      selectedVoice = voices.find(voice => voice.name.includes(preferred));
      if (selectedVoice) {
        console.log('✅ Found by name:', selectedVoice.name);
        break;
      }
    }

    // Strategy 2: Try language code matches
    if (!selectedVoice) {
      for (const code of langConfig.codes) {
        selectedVoice = voices.find(voice => voice.lang.startsWith(code));
        if (selectedVoice) {
          console.log('✅ Found by language code:', selectedVoice.name, selectedVoice.lang);
          break;
        }
      }
    }

    // Strategy 3: Try male voices in the language
    if (!selectedVoice) {
      for (const code of langConfig.codes) {
        selectedVoice = voices.find(voice => 
          voice.lang.startsWith(code) && 
          (voice.name.toLowerCase().includes('male') || 
           voice.name.toLowerCase().includes('man'))
        );
        if (selectedVoice) {
          console.log('✅ Found male voice:', selectedVoice.name);
          break;
        }
      }
    }

    // Strategy 4: Fallback to any voice in the language
    if (!selectedVoice && selectedLang !== 'en') {
      for (const code of langConfig.codes) {
        selectedVoice = voices.find(voice => voice.lang.startsWith(code.split('-')[0]));
        if (selectedVoice) {
          console.log('⚠️ Fallback voice found:', selectedVoice.name);
          break;
        }
      }
    }

    // Final fallback to English
    if (!selectedVoice) {
      selectedVoice = voices.find(voice => voice.lang.startsWith('en'));
      console.log('⚠️ Using English fallback:', selectedVoice?.name);
    }

    if (selectedVoice) {
      utterance.voice = selectedVoice;
      utterance.lang = selectedVoice.lang;
      console.log('🎙️ Andy speaking in:', selectedVoice.name, '(' + selectedVoice.lang + ')');
      
      // Show notification about which voice is being used
      if (selectedLang !== 'en') {
        addSystemMessage(`🎙️ Andy speaking in ${langConfig.langName} (${selectedVoice.name})`, true);
      }
    } else {
      console.warn('⚠️ No suitable voice found, using default');
      
      // Notify user if voice not available
      if (selectedLang !== 'en') {
        addSystemMessage(`⚠️ ${langConfig.langName} voice not found. Install language pack from Windows Settings → Time & Language → Language. Using English voice as fallback.`, true);
      }
    }

    // Andy's voice characteristics - optimized for legal assistant
    utterance.rate = 0.95;     // Slightly slower for clarity
    utterance.pitch = 1.0;     // Natural pitch
    utterance.volume = 1.0;    // Full volume

    // Event handlers
    utterance.onstart = () => {
      setIsSpeaking(true);
      addSystemMessage(`🔊 Andy is speaking in ${langConfig.langName}...`, true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      console.error('TTS error:', event);
      setIsSpeaking(false);
      
      // Provide helpful error message based on error type
      let errorMsg = '❌ Speech error: ';
      if (event.error === 'not-allowed') {
        errorMsg += 'Microphone permission denied. Please allow microphone access in browser settings.';
      } else if (event.error === 'network') {
        errorMsg += 'Network error. Please check your internet connection.';
      } else if (event.error === 'synthesis-failed') {
        errorMsg += 'Voice synthesis failed. Try clicking the speaker icon again.';
      } else if (event.error === 'audio-busy') {
        errorMsg += 'Audio is busy. Please wait and try again.';
      } else {
        errorMsg += 'Unable to speak. Try refreshing the page or use a different browser.';
      }
      
      addSystemMessage(errorMsg, true);
      
      // Try to recover by canceling any pending speech
      try {
        window.speechSynthesis.cancel();
      } catch (e) {
        console.error('Failed to cancel speech:', e);
      }
    };

    window.speechSynthesis.speak(utterance);
  };

  // Stop speech
  const handleStopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      const lang = preferences && preferences.language ? getLanguageName(preferences.language.code) : 'English';
      addSystemMessage(`🔇 Andy stopped speaking ${lang}`, true);
    }
  };

  // Toggle auto-read
  const handleToggleAutoRead = () => {
    const lang = preferences && preferences.language ? getLanguageName(preferences.language.code) : 'English';
    setAutoRead(!autoRead);
    addSystemMessage(
      !autoRead 
        ? `🔊 Auto-read enabled - Andy will read all responses in ${lang}` 
        : '🔇 Auto-read disabled',
      true
    );
  };

  const handleBranchChat = (messageId) => {
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    const branchedMessages = messages.slice(0, messageIndex + 1);
    setMessages(branchedMessages);
    setCurrentChatId(null); // Create new chat
    addSystemMessage('🌿 Branched into new chat', true);
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentChatId(null);
    setOffenceNumber('');
    if (user) {
      createConversation().catch((error) => console.error(error));
    }
  };

  const generateCaseSummary = () => {
    if (messages.length < 2) return;

    const summary = {
      title: "LEGAL CASE SUMMARY",
      generated: new Date().toLocaleString(),
      client_info: {
        jurisdiction: preferences?.province || preferences?.country || "Not specified",
        law_type: lawTypeSelection?.lawType || "Not specified",
        law_category: lawTypeSelection?.category || "Not specified"
      },
      situation: situationDescription?.description || "Not provided",
      conversation_summary: [],
      violations: [],
      advice_given: [],
      next_steps: [],
      documents_needed: []
    };

    // Extract information from messages
    let currentViolation = null;
    messages.forEach((msg, idx) => {
      if (msg.role === 'user') {
        summary.conversation_summary.push({
          type: "Client Statement",
          content: msg.content,
          timestamp: msg.timestamp
        });

        // Extract potential violations (for traffic cases)
        if (msg.content.toLowerCase().includes('charged') || 
            msg.content.toLowerCase().includes('ticket') ||
            msg.content.toLowerCase().includes('offence')) {
          const violationMatch = msg.content;
          if (violationMatch) {
            currentViolation = violationMatch;
          }
        }

        // Extract BAC/THC readings
        if (msg.content.match(/\d+\.?\d*%/)) {
          const reading = msg.content.match(/\d+\.?\d*%/)[0];
          summary.violations.push(`Blood Alcohol Content (BAC): ${reading}`);
        }
        if (msg.content.toLowerCase().includes('thc')) {
          summary.violations.push(`THC levels mentioned in statement`);
        }
      } else if (msg.role === 'assistant') {
        summary.conversation_summary.push({
          type: "Legal Advice",
          content: msg.content || msg.answer,
          timestamp: msg.timestamp
        });

        // Extract advice
        const content = msg.content || msg.answer || '';
        if (content.includes('should') || content.includes('recommend') || content.includes('advise')) {
          const sentences = content.split(/[.!?]/);
          sentences.forEach(sentence => {
            if ((sentence.includes('should') || sentence.includes('recommend') || sentence.includes('advise')) && sentence.trim()) {
              summary.advice_given.push(sentence.trim());
            }
          });
        }
      }
    });

    // Add law-specific information
    if (lawTypeSelection?.lawType === 'Traffic Law' || lawTypeSelection?.category === 'Traffic Law') {
      summary.violations.push(`Traffic Offence under Highway Traffic Act`);
      summary.documents_needed = [
        "Copy of traffic ticket/summons",
        "Driver's license",
        "Vehicle registration",
        "Insurance documents",
        "Any photos or dashcam footage",
        "Witness statements (if any)",
        "Previous driving record"
      ];
      summary.next_steps = [
        "Review the specific section of Highway Traffic Act cited",
        "Determine plea options (guilty, not guilty, guilty with explanation)",
        "Calculate potential fines and demerit points",
        "Consider requesting trial date if disputing",
        "Consult with traffic lawyer for serious charges",
        "Prepare evidence and documentation",
        "Attend court date if scheduled"
      ];
    }

    // Add impaired driving specific info
    if (situationDescription?.description?.toLowerCase().includes('impaired') ||
        situationDescription?.description?.toLowerCase().includes('dui') ||
        situationDescription?.description?.toLowerCase().includes('alcohol') ||
        situationDescription?.description?.toLowerCase().includes('thc')) {
      summary.violations.push(`Impaired Driving Investigation`);
      summary.legal_limits = {
        "Blood Alcohol Content (BAC)": "0.08% - Criminal offence over this limit",
        "Warn Range BAC": "0.05% - 0.08% - Administrative penalties",
        "THC (Cannabis)": "2ng/ml - Warn range, 5ng/ml - Criminal offence",
        "Combined Alcohol & THC": "0.05% BAC + 2.5ng/ml THC - Criminal offence"
      };
      summary.documents_needed.push(
        "Breathalyzer test results",
        "Drug recognition expert (DRE) report",
        "Blood test results (if applicable)",
        "Roadside sobriety test notes"
      );
      summary.next_steps.push(
        "Review Charter rights - were they violated?",
        "Challenge breathalyzer calibration and maintenance",
        "Review arrest procedures",
        "Consider immediate license suspension appeal",
        "Prepare for criminal court proceedings"
      );
    }

    // Generic next steps if none added
    if (summary.next_steps.length === 0) {
      summary.next_steps = [
        "Gather all relevant documents",
        "Consult with a licensed lawyer",
        "Prepare timeline of events",
        "Document all evidence",
        "Respond to any deadlines"
      ];
    }

    if (summary.documents_needed.length === 0) {
      summary.documents_needed = [
        "All relevant correspondence",
        "Supporting documentation",
        "Evidence materials",
        "Timeline of events"
      ];
    }

    return summary;
  };

  const handleGenerateSummary = () => {
    const summary = generateCaseSummary();
    if (!summary) {
      addSystemMessage('Not enough conversation to generate summary. Please have a conversation first.', true);
      return;
    }

    // Format summary as markdown
    let summaryText = `# ${summary.title}\n\n`;
    summaryText += `**Generated:** ${summary.generated}\n\n`;
    summaryText += `---\n\n`;
    
    summaryText += `## CLIENT INFORMATION\n\n`;
    summaryText += `**Jurisdiction:** ${summary.client_info.jurisdiction}\n`;
    summaryText += `**Law Type:** ${summary.client_info.law_type}\n`;
    summaryText += `**Category:** ${summary.client_info.law_category}\n\n`;
    
    summaryText += `## SITUATION DESCRIBED\n\n`;
    summaryText += `${summary.situation}\n\n`;
    
    if (summary.violations.length > 0) {
      summaryText += `## ALLEGED VIOLATIONS / CHARGES\n\n`;
      summary.violations.forEach((v, i) => {
        summaryText += `${i + 1}. ${v}\n`;
      });
      summaryText += `\n`;
    }

    if (summary.legal_limits) {
      summaryText += `## LEGAL LIMITS (For Reference)\n\n`;
      Object.entries(summary.legal_limits).forEach(([key, value]) => {
        summaryText += `**${key}:** ${value}\n`;
      });
      summaryText += `\n`;
    }
    
    if (summary.advice_given.length > 0) {
      summaryText += `## ADVICE PROVIDED\n\n`;
      summary.advice_given.slice(0, 5).forEach((advice, i) => {
        summaryText += `${i + 1}. ${advice}\n`;
      });
      summaryText += `\n`;
    }
    
    summaryText += `## RECOMMENDED NEXT STEPS\n\n`;
    summary.next_steps.forEach((step, i) => {
      summaryText += `${i + 1}. ${step}\n`;
    });
    summaryText += `\n`;
    
    summaryText += `## DOCUMENTS NEEDED\n\n`;
    summary.documents_needed.forEach((doc, i) => {
      summaryText += `${i + 1}. ${doc}\n`;
    });
    summaryText += `\n`;
    
    summaryText += `---\n\n`;
    summaryText += `## IMPORTANT DISCLAIMER\n\n`;
    summaryText += `This summary is based on general legal information provided during the conversation. `;
    summaryText += `It is NOT legal advice and should not be relied upon as such. `;
    summaryText += `For advice specific to your situation, consult with a licensed lawyer in your jurisdiction.\n\n`;
    summaryText += `**This is an AI-generated summary for informational purposes only.**\n`;

    // Add summary as a message
    const summaryMessage = {
      id: Date.now(),
      role: 'assistant',
      content: summaryText,
      timestamp: new Date(),
      isSummary: true
    };
    setMessages(prev => [...prev, summaryMessage]);

    // Also copy to clipboard
    navigator.clipboard.writeText(summaryText);
    addSystemMessage('Case summary generated and copied to clipboard!', true);
  };

  const handleLoadChat = (chatId) => {
    const chat = savedChats.find(c => c.id === chatId);
    if (chat) {
      setMessages(chat.messages);
      setCurrentChatId(chat.id);
    }
  };

  // Handle file upload
  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploadProgress(0);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    if (offenceNumber) {
      formData.append('offence_number', offenceNumber);
    }

    // Add temporary upload message
    const tempMessage = addSystemMessage(`Uploading ${file.name}...`, true);

    try {
      const response = await fetch(`${API_URL}/api/artillery/upload`, {
        method: 'POST',
        body: formData,
        // Simulate progress (in real implementation, you'd use XMLHttpRequest for progress)
      });

      if (!response.ok) {
        // Try to get detailed error message from backend
        try {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Upload failed: ${response.status} ${response.statusText}`);
        } catch (jsonError) {
          throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
      }

      const result = await response.json();

      // Remove temporary message
      setMessages(prev => prev.filter(msg => !msg.isTemporary));

      // Check if it's an image file
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      const isImage = imageExtensions.includes(fileExt);

      // 🖼️ Create image preview for images
      if (isImage) {
        // Create a URL for the image preview
        const imageUrl = URL.createObjectURL(file);
        
        // Add message with image preview
        const imageMessage = {
          id: Date.now(),
          role: 'user',
          content: `Uploaded image: ${file.name}`,
          timestamp: new Date(),
          imageUrl: imageUrl,
          fileName: file.name,
          fileSize: (file.size / 1024).toFixed(2) + ' KB',
          isUpload: true
        };
        setMessages(prev => [...prev, imageMessage]);
        
        // Add success message with OCR status
        if (result.chunks_indexed && result.chunks_indexed > 0) {
          addSystemMessage(`✅ Image uploaded! OCR extracted ${result.chunks_indexed} text chunks. You can now ask questions about this document.`);
        } else {
          addSystemMessage(`✅ Image uploaded and saved!\n\n⚠️ OCR not available - Install Tesseract to extract text:\n1. Download: https://github.com/UB-Mannheim/tesseract/wiki\n2. Install to: C:\\Program Files\\Tesseract-OCR\n3. Restart servers\n\nYou can still view the image in chat!`);
        }
      } else {
        // For non-image files, just show success message
        const docMessage = {
          id: Date.now(),
          role: 'user',
          content: `📄 Uploaded document: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`,
          timestamp: new Date(),
          fileName: file.name,
          isUpload: true
        };
        setMessages(prev => [...prev, docMessage]);
        
        addSystemMessage(`✅ Document uploaded and indexed. ${result.chunks_indexed || 0} chunks processed.`);
      }

      // Auto-fill offence number if detected and not already set
      if (result.detected_offence_number && !offenceNumber) {
        setOffenceNumber(result.detected_offence_number);
        addSystemMessage(`🔍 Detected offence number: ${result.detected_offence_number}`);
      }

      setUploadProgress(100);
      setTimeout(() => setUploadProgress(0), 2000); // Hide progress after 2 seconds

    } catch (error) {
      // Remove temporary message and add error message
      setMessages(prev => prev.filter(msg => !msg.isTemporary));
      
      const errorMsg = error.message;
      
      // Check if it's a Tesseract error
      if (errorMsg.includes('Tesseract') || errorMsg.includes('OCR')) {
        addSystemMessage(`❌ ${errorMsg}\n\n📥 To upload images, please install Tesseract OCR:\n1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n2. Install to: C:\\Program Files\\Tesseract-OCR\n3. Restart your terminal\n\n✅ PDF, DOCX, TXT files work without Tesseract!`);
      } else {
        addSystemMessage(`❌ Upload failed: ${errorMsg}`);
      }
      
      console.error('Upload error:', error);
      setUploadProgress(0);
    }
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleFileUpload(file);
      setShowUploadMenu(false);
    }
  };

  // Handle different file type uploads
  const handleImageUpload = () => {
    imageInputRef.current?.click();
  };

  const handlePDFUpload = () => {
    pdfInputRef.current?.click();
  };

  const handleDocUpload = () => {
    docInputRef.current?.click();
  };

  const handleTextUpload = () => {
    textInputRef.current?.click();
  };

  // Get language name from code
  const getLanguageName = (code) => {
    const languages = {
      'en': 'English',
      'fr': 'French',
      'es': 'Spanish',
      'hi': 'Hindi',
      'pa': 'Punjabi',
      'zh': 'Chinese'
    };
    return languages[code] || code;
  };

  // Get country name
  const getCountryName = (code) => {
    return code === 'CA' ? 'Canada' : code === 'US' ? 'United States' : code;
  };

  // Handle voice transcript
  const handleVoiceTranscript = async (transcript) => {
    setInput(transcript);
    setShowVoiceChat(false);
    
    // Auto-send the transcribed message
    setTimeout(() => {
      const sendButton = document.querySelector('.send-btn');
      if (sendButton) sendButton.click();
    }, 500);
  };

  // Handle chat message send
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    let conversationId = currentChatId;
    if (!conversationId && user) {
      try {
        conversationId = await createConversation();
      } catch (error) {
        console.error('Failed to create conversation:', error);
      }
    }

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    if (conversationId) {
      persistMessage(conversationId, userMessage);
    }
    const question = input.trim();
    setInput('');
    setLoading(true);
    setLoadingStage('Searching documents...');

    try {
      // Build request payload with preferences
      const payload = {
        message: question,
        offence_number: offenceNumber || undefined,
        top_k: 5
      };

      // Add preferences if available
      if (preferences) {
        if (preferences.language) {
          payload.language = preferences.language.code;
        }
        if (preferences.country) {
          payload.country = preferences.country;
        }
        if (preferences.province) {
          payload.province = preferences.province;
        }
      }

      // Add law type filtering with scope
      if (lawTypeSelection) {
        payload.law_category = lawTypeSelection.category;
        payload.law_type = lawTypeSelection.lawType;
        payload.jurisdiction = lawTypeSelection.jurisdiction;
        payload.law_scope = lawTypeSelection.scope; // Add scope for strict filtering
      }

      // Add timeout warning after 10 seconds
      const timeoutWarning = setTimeout(() => {
        setLoadingStage('Generating response (this may take a moment)...');
      }, 10000);

      const response = await fetch(`${API_URL}/api/artillery/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status} ${response.statusText}`);
      }

      clearTimeout(timeoutWarning);
      setLoadingStage('Processing response...');
      const data = await response.json();

      const assistantMessage = {
        id: Date.now(),
        role: 'assistant',
        content: data.answer,
        answer: data.answer, // Also include as 'answer' for EnhancedLegalResponse compatibility
        citations: data.citations || [],
        chunks_used: data.chunks_used || 0,
        confidence: data.confidence || 0,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      if (conversationId) {
        persistMessage(conversationId, assistantMessage);
      }

      if (conversationId) {
        setSavedChats(prev =>
          prev.map(chat =>
            chat.id === conversationId
              ? { ...chat, last_message_at: new Date().toISOString() }
              : chat
          )
        );
      }

      // Chat history is now persisted via /api/profile/conversations

      // Auto-speak using FREE browser TTS if voice chat or auto-read is enabled
      if ((showVoiceChat || autoRead) && data.answer) {
        setTimeout(() => {
          if (window.voiceChatSpeak) {
            window.voiceChatSpeak(data.answer);
          } else {
            handleReadAloud(data.answer);
          }
        }, 500);
      }

    } catch (error) {
      clearTimeout(timeoutWarning);
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `❌ Sorry, I encountered an error: ${error.message}\n\nPlease make sure the backend is running and try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  };

  // Quick test functions for browser console
  useEffect(() => {
    window.testUpload = () => {
      const testFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      handleFileUpload(testFile);
    };

    window.testChat = () => {
      setInput('What are the penalties for speeding?');
      setTimeout(() => {
        const form = document.querySelector('form');
        if (form) form.requestSubmit();
      }, 100);
    };

    window.clearChat = () => {
      setMessages([]);
    };

    // Debug function to list all available voices
    window.listAndyVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      console.log('🎙️ Available voices for Andy:', voices.length);
      voices.forEach((voice, i) => {
        console.log(`${i + 1}. ${voice.name} (${voice.lang}) ${voice.default ? '⭐ DEFAULT' : ''}`);
      });
      
      // Group by language
      const byLang = {};
      voices.forEach(voice => {
        const lang = voice.lang.split('-')[0];
        if (!byLang[lang]) byLang[lang] = [];
        byLang[lang].push(voice.name);
      });
      console.log('📊 Voices by language:', byLang);
    };

    // Auto-load voices
    if (window.speechSynthesis) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        const voices = window.speechSynthesis.getVoices();
        console.log('🎙️ Andy loaded', voices.length, 'voices. Type listAndyVoices() to see them.');
      };
    }
  }, []);

  return (
    <div className="chat-interface">
      {/* Header - Simplified */}
      <div className="chat-header">
        <div className="header-left">
          <h1 className="legid-header-logo">LEGID</h1>
          <button className="new-chat-btn" onClick={handleNewChat} title="Start new chat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            New Chat
          </button>
        </div>
        <div className="header-right">
          {/* Andy TTS Controls */}
          <div className="tts-controls">
            <button 
              className={`tts-btn ${autoRead ? 'active' : ''}`}
              onClick={handleToggleAutoRead}
              title={autoRead ? 'Disable auto-read' : 'Enable auto-read'}
            >
              Andy {autoRead ? 'ON' : 'OFF'}
              {preferences && preferences.language && (
                <span className="tts-lang-badge">
                  {getLanguageName(preferences.language.code)}
                </span>
              )}
            </button>
          </div>

          <div className="offence-input">
            <label>Offence Number (optional):</label>
            <input
              type="text"
              value={offenceNumber}
              onChange={(e) => setOffenceNumber(e.target.value)}
              placeholder="e.g., 123456789"
              className="offence-field"
            />
          </div>

          {/* Profile & Logout */}
          {user && (
            <div className="profile-dropdown-container">
              <button 
                className="profile-btn"
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                title="Account settings"
              >
                <div className="profile-avatar">
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt="Profile" />
                  ) : (
                    <span>{(user.name || user.email || 'U').charAt(0).toUpperCase()}</span>
                  )}
                </div>
                <span className="profile-name">{user.name || user.email?.split('@')[0] || 'User'}</span>
                <svg className={`profile-chevron ${showProfileMenu ? 'open' : ''}`} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>

              {showProfileMenu && (
                <div className="profile-dropdown">
                  <div className="profile-dropdown-header">
                    <div className="profile-dropdown-avatar">
                      {user.avatar_url ? (
                        <img src={user.avatar_url} alt="Profile" />
                      ) : (
                        <span>{(user.name || user.email || 'U').charAt(0).toUpperCase()}</span>
                      )}
                    </div>
                    <div className="profile-dropdown-info">
                      <span className="profile-dropdown-name">{user.name || 'User'}</span>
                      <span className="profile-dropdown-email">{user.email}</span>
                      <span className="profile-dropdown-role">{user.role || 'Client'}</span>
                    </div>
                  </div>
                  <div className="profile-dropdown-divider"></div>
                  <button className="profile-dropdown-item" onClick={() => { setShowProfileMenu(false); }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    My Profile
                  </button>
                  <button className="profile-dropdown-item" onClick={() => { setShowProfileMenu(false); onResetPreferences && onResetPreferences(); }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="3"></circle>
                      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                    </svg>
                    Settings
                  </button>
                  <div className="profile-dropdown-divider"></div>
                  <button className="profile-dropdown-item logout-item" onClick={() => { setShowProfileMenu(false); onLogout && onLogout(); }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                      <polyline points="16 17 21 12 16 7"></polyline>
                      <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area with Sidebar */}
      <div className="chat-main-layout">
        {/* Left Sidebar - Using ChatSidebar Component */}
        <ChatSidebar
          savedChats={savedChats}
          currentChatId={currentChatId}
          onLoadChat={(chatId) => {
            loadConversationMessages(chatId);
          }}
          onNewChat={handleNewChat}
          onDeleteChat={(chatId) => {
            fetch(`${API_URL}/api/profile/conversations/${chatId}`, {
              method: 'DELETE',
              headers: getAuthHeaders()
            }).then(() => {
              const updated = savedChats.filter(c => c.id !== chatId);
              setSavedChats(updated);
              if (currentChatId === chatId) {
                setCurrentChatId(null);
                setMessages([]);
              }
            });
          }}
          onSearchChats={() => setShowChatHistory(true)}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          user={user}
          onLogout={onLogout}
          activeResource={activeResource}
          onResourceClick={handleResourceClick}
          onNavigate={onNavigate}
        />
        
        {/* Old Left Sidebar - Keeping for reference but will be replaced */}
        <div className="chat-sidebar-left" style={{ display: 'none' }}>
          {/* Current Context Display */}
          {preferences && lawTypeSelection && (
            <div className="context-display">
              <div className="context-text">
                Language: {getLanguageName(preferences.language?.code || 'en')} {preferences.country === 'CA' ? 'Canada' : 'United States'} {preferences.province || ''} <span className="law-type-highlight">{lawTypeSelection.lawType}</span>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          {lawTypeSelection && (
            <div className="sidebar-navigation">
              <button 
                className="nav-btn" 
                onClick={() => setShowRecentUpdates(true)} 
                title="View recent legal updates"
              >
                📰 Recent Updates
              </button>
              <button 
                className="nav-btn" 
                onClick={() => setShowCaseLookup(true)} 
                title="Search legal cases"
              >
                🔍 Case Lookup
              </button>
              <button 
                className="nav-btn" 
                onClick={() => setShowAmendmentGenerator(true)} 
                title="Generate legal amendments"
              >
                📝 Amendments
              </button>
              <button 
                className="nav-btn" 
                onClick={() => setShowDocumentGenerator(true)} 
                title="Generate legal documents"
              >
                📄 Documents
              </button>
              <button 
                className="nav-btn" 
                onClick={() => setShowChatHistory(true)} 
                title="Search chat history"
              >
                💬 History
              </button>
              {onChangeLawType && (
                <button className="nav-btn" onClick={onChangeLawType} title="Change law type">
                  🔄 Change Law Type
                </button>
              )}
              {onResetPreferences && (
                <button className="nav-btn" onClick={onResetPreferences} title="Change all settings">
                  ⚙️ Settings
                </button>
              )}
            </div>
          )}

          {/* Summary Buttons */}
          {messages.length > 2 && (
            <div className="summary-buttons">
              <button className="summary-btn ai-summary" onClick={() => setShowAISummary(true)} title="Generate AI case summary">
                AI Summary
              </button>
              <button className="summary-btn quick-summary" onClick={handleGenerateSummary} title="Generate quick summary">
                Quick Summary
              </button>
            </div>
          )}
        </div>

      {/* Progress Bar */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <span>Uploading... {uploadProgress}%</span>
        </div>
      )}

      {/* Case Lookup Modal */}
      {showCaseLookup && (
        <CaseLookup 
          onClose={() => setShowCaseLookup(false)}
          onCaseSelected={(caseItem) => {
            setInput(`Tell me more about ${caseItem.case_name}`);
            setShowCaseLookup(false);
          }}
        />
      )}

      {/* Amendment Generator Modal */}
      {showAmendmentGenerator && (
        <AmendmentGenerator 
          onClose={() => setShowAmendmentGenerator(false)}
          lawCategory={lawTypeSelection?.lawType}
        />
      )}

      {/* Document Generator Modal */}
      {showDocumentGenerator && (
        <DocumentGenerator 
          onClose={() => setShowDocumentGenerator(false)}
          lawCategory={lawTypeSelection?.lawType}
          userId={userId}
        />
      )}

      {/* Chat History Search Modal */}
      {showChatHistory && (
        <ChatHistorySearch 
          userId={userId}
          onClose={() => setShowChatHistory(false)}
          onMessageSelect={(message) => {
            setInput(message.message);
            setShowChatHistory(false);
          }}
          onLoadChat={(chatId) => {
            // Load the chat from localStorage
            const localChats = localStorage.getItem('legubot_chats');
            if (localChats) {
              const chats = JSON.parse(localChats);
              const chat = chats.find(c => c.id === chatId);
              if (chat) {
                setMessages(chat.messages || []);
                setCurrentChatId(chat.id);
                setShowChatHistory(false);
              }
            }
          }}
        />
      )}

      {/* AI Summary Modal */}
      {showAISummary && (
        <AISummaryModal
          messages={messages}
          metadata={{
            law_category: lawTypeSelection?.lawType,
            law_type: lawTypeSelection?.lawType,
            jurisdiction: lawTypeSelection?.jurisdiction,
            language: preferences?.language?.code,
            country: preferences?.country,
            province: preferences?.province
          }}
          onClose={() => setShowAISummary(false)}
        />
      )}

      {/* Voice Chat Component */}
      {showVoiceChat && (
        <VoiceChat 
          preferences={preferences}
          lawTypeSelection={lawTypeSelection}
          onTranscript={handleVoiceTranscript}
          onAutoReadToggle={(enabled) => {
            setAutoRead(enabled);
            if (enabled) {
              addSystemMessage('🔊 Auto-read enabled - Bot will read all responses aloud', true);
            } else {
              addSystemMessage('🔇 Auto-read disabled', true);
            }
          }}
        />
      )}

        {/* Main Chat Content */}
        <div className="chat-content">
          {/* Messages Area */}
          <div className="messages-container" ref={chatContainerRef}>
        {/* 🎯 Drag & Drop Overlay */}
        {isDragging && (
          <div className="drag-drop-overlay">
            <div className="drag-drop-content">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <h2>Drop files here</h2>
              <p>Images (JPG, PNG, BMP, TIFF) • Documents (PDF, DOCX, TXT, XLSX)</p>
            </div>
          </div>
        )}
        
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h2 className="welcome-legid-logo">LEGID</h2>
            <p className="welcome-tagline">Your Advanced Legal Intelligence Assistant</p>
             <p>Upload a legal document to get started, or ask me questions about legal matters.</p>
             
             {/* 🎯 Upload Instructions */}
             <div className="upload-instructions">
               <div className="upload-method">
                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                   <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                   <polyline points="17 8 12 3 7 8"></polyline>
                   <line x1="12" y1="3" x2="12" y2="15"></line>
                 </svg>
                 <span>Drag & drop files here</span>
               </div>
               <div className="upload-method">
                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                   <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                   <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                 </svg>
                 <span>Or press <kbd>Ctrl+V</kbd> to paste</span>
               </div>
               <div className="upload-method">
                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                   <circle cx="12" cy="12" r="10"></circle>
                   <line x1="12" y1="8" x2="12" y2="16"></line>
                   <line x1="8" y1="12" x2="16" y2="12"></line>
                 </svg>
                 <span>Or click the <strong>+</strong> button below</span>
               </div>
             </div>

             <div className="quick-actions">
               <button onClick={() => setInput('What are the penalties for speeding?')}>
                 Speeding Penalties
               </button>
               <button onClick={() => setInput('How do I dispute a traffic ticket?')}>
                 Dispute Process
               </button>
               <button onClick={() => setInput('What are demerit points?')}>
                 Demerit Points
               </button>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-bubble">
                {/* Enhanced Legal Response for structured answers */}
                {message.role === 'assistant' ? (
                  <>
                    <EnhancedLegalResponse response={message} />
                    {/* Show government resources if available */}
                    {message.governmentResources && message.governmentResources.length > 0 && (
                      <GovernmentResources 
                        resources={message.governmentResources} 
                        lawType={lawTypeSelection?.lawType || 'Selected Area'}
                        province={preferences?.province}
                      />
                    )}
                  </>
                ) : message.role === 'user' ? (
                  <div className="message-text">
                    {/* 🖼️ Show image preview if it's an upload with image */}
                    {message.imageUrl && (
                      <div className="uploaded-image-preview">
                        <img 
                          src={message.imageUrl} 
                          alt={message.fileName || 'Uploaded image'} 
                          className="preview-image"
                        />
                        <div className="image-info">
                          <span className="file-name">📎 {message.fileName}</span>
                          <span className="file-size">{message.fileSize}</span>
                        </div>
                      </div>
                    )}
                    {/* Show text content */}
                    {!message.imageUrl && message.content}
                  </div>
                ) : (
                  <div className="message-text system-text">
                    {message.content}
                  </div>
                )}

                {/* Message timestamp */}
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>

                {/* Message action buttons - only for assistant and user messages */}
                {(message.role === 'assistant' || message.role === 'user') && !message.isTemporary && (
                  <div className="message-actions">
                    <button 
                      className="action-btn" 
                      onClick={() => handleCopyMessage(message.content || message.answer)}
                      title="Copy message"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                      </svg>
                    </button>

                    {message.role === 'assistant' && (
                      <>
                        <button 
                          className={`action-btn ${message.liked ? 'active' : ''}`}
                          onClick={() => handleLikeMessage(message.id)}
                          title="Good response"
                        >
                          👍
                        </button>

                        <button 
                          className={`action-btn ${message.disliked ? 'active' : ''}`}
                          onClick={() => handleDislikeMessage(message.id)}
                          title="Bad response"
                        >
                          👎
                        </button>

                        <button 
                          className="action-btn" 
                          onClick={() => handleShareMessage(message.content || message.answer)}
                          title="Share"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <circle cx="18" cy="5" r="3"></circle>
                            <circle cx="6" cy="12" r="3"></circle>
                            <circle cx="18" cy="19" r="3"></circle>
                            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                          </svg>
                        </button>

                        <button 
                          className="action-btn" 
                          onClick={() => handleReadAloud(message.content || message.answer)}
                          title="Andy read aloud"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                          </svg>
                        </button>

                        <button 
                          className="action-btn" 
                          onClick={() => handleRegenerateResponse(message.id)}
                          title="Regenerate response"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="23 4 23 10 17 10"></polyline>
                            <polyline points="1 20 1 14 7 14"></polyline>
                            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                          </svg>
                        </button>

                        <button 
                          className="action-btn" 
                          onClick={(e) => setContextMenu({ x: e.clientX, y: e.clientY, messageId: message.id, content: message.content || message.answer })}
                          title="More options"
                        >
                          ⋯
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Typing indicator */}
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              {loadingStage && (
                <div className="loading-stage" style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#888' }}>
                  {loadingStage}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form className="input-area" onSubmit={handleSend}>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about legal documents or traffic laws..."
            className="chat-input"
            disabled={loading}
          />

          {/* Hidden file inputs for different types */}
          <input
            ref={imageInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".png,.jpg,.jpeg,.gif,.webp,.bmp,.tiff,.tif"
            style={{ display: 'none' }}
          />
          <input
            ref={pdfInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".pdf"
            style={{ display: 'none' }}
          />
          <input
            ref={docInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".doc,.docx,.xlsx,.xls"
            style={{ display: 'none' }}
          />
          <input
            ref={textInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".txt,.md"
            style={{ display: 'none' }}
          />

          {/* Plus icon for upload menu */}
          <div className="upload-menu-container">
            <button
              type="button"
              className="plus-upload-btn"
              onClick={() => setShowUploadMenu(!showUploadMenu)}
              disabled={loading}
              title="Upload document"
            >
              <span className="plus-icon">+</span>
            </button>

            {/* Upload menu dropdown */}
            {showUploadMenu && (
           <div className="upload-menu">
                <button
                  type="button"
                  className="upload-menu-item"
                  onClick={handleImageUpload}
                  title="Upload images - OCR will extract text automatically"
                >
                  <span className="menu-icon">🖼️</span>
                  <span>Image (OCR)</span>
                </button>
                 <button
                   type="button"
                   className="upload-menu-item"
                   onClick={handlePDFUpload}
                 >
                   <span className="menu-icon">PDF</span>
                   <span>PDF</span>
                 </button>
                 <button
                   type="button"
                   className="upload-menu-item"
                   onClick={handleDocUpload}
                 >
                   <span className="menu-icon">DOC</span>
                   <span>Document</span>
                 </button>
                 <button
                   type="button"
                   className="upload-menu-item"
                   onClick={handleTextUpload}
                 >
                   <span className="menu-icon">TXT</span>
                   <span>Text</span>
                 </button>
               </div>
            )}
          </div>

          {/* Voice Chat button */}
          <button
            type="button"
            className={`voice-input-btn ${showVoiceChat ? 'active' : ''}`}
            onClick={() => setShowVoiceChat(!showVoiceChat)}
            disabled={loading}
            title={showVoiceChat ? "Close voice chat" : "Voice chat"}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>

          {/* Send button */}
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || loading}
          >
             {loading ? '...' : 'Send'}
          </button>
        </div>

          <div className="input-footer">
            This is general information only, not legal advice. Consult a licensed lawyer for advice about your specific case.
          </div>
          </form>
        </div>
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div 
          className="context-menu"
          style={{ 
            position: 'fixed',
            top: `${contextMenu.y}px`,
            left: `${contextMenu.x}px`,
            zIndex: 1000
          }}
        >
          <button onClick={() => { handleBranchChat(contextMenu.messageId); setContextMenu(null); }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="6" y1="3" x2="6" y2="15"></line>
              <circle cx="18" cy="6" r="3"></circle>
              <circle cx="6" cy="18" r="3"></circle>
              <path d="M18 9a9 9 0 0 1-9 9"></path>
            </svg>
            Branch in new chat
          </button>
          <button onClick={() => { handleReadAloud(contextMenu.content); setContextMenu(null); }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
            Andy read aloud
          </button>
          <button onClick={() => { handleCopyMessage(contextMenu.content); setContextMenu(null); }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            Copy message
          </button>
          <button onClick={() => setContextMenu(null)} style={{ color: '#ff6b6b' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            Report message
           </button>
         </div>
       )}

       {/* Recent Updates Modal */}
       {showRecentUpdates && lawTypeSelection && (
         <RecentUpdates 
           lawType={lawTypeSelection.lawType}
           jurisdiction={lawTypeSelection.jurisdiction}
           onClose={() => setShowRecentUpdates(false)}
         />
       )}
     </div>
   );
};

export default ChatInterface;