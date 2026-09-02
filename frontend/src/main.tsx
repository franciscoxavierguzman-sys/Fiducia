import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  BarChart3,
  CheckCircle2,
  CreditCard,
  Eye,
  History,
  Inbox,
  LogIn,
  LogOut,
  Plus,
  Search,
  Send,
  ShieldCheck,
  X,
  UserCircle,
  Users,
} from 'lucide-react';
import fiduciaLogo from './assets/fiducia-logo.png';
import './styles.css';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const tokenStorageKey = 'fiducia_access_token';

const paymentMethods = [
  { value: 'DEBIT_CARD', label: 'Tarjeta' },
  { value: 'BANK_TRANSFER', label: 'Transferencia bancaria' },
  { value: 'DIGITAL_WALLET', label: 'Billetera digital' },
];
const guatemalaBanks = [
  'Agromercantil de Guatemala, S.A.',
  'Banco Azteca de Guatemala, S.A.',
  'Banco Credicorp, S.A.',
  'Banco Cuscatlan Guatemala, S.A.',
  'Banco de America Central, S.A.',
  'Banco de Antigua, S.A.',
  'Banco de Desarrollo Rural, S.A.',
  'Banco de los Trabajadores',
  'Banco Ficohsa Guatemala, S.A.',
  'Banco G&T Continental, S.A.',
  'Banco Inmobiliario, S.A.',
  'Banco Industrial, S.A.',
  'Banco Internacional, S.A.',
  'Banco INV, S.A.',
  'Banco Multimoney, S.A.',
  'Banco Nexa, S.A.',
  'Banco Promerica, S.A.',
  'Citibank, N.A. Sucursal Guatemala',
  'Credito Hipotecario Nacional de Guatemala',
  'Vivibanco, S.A.',
];
const cardIssuers = ['Visa', 'Mastercard', 'American Express'];
const fundingCurrencyOptions = [
  { value: 'USD', label: 'Dolares (USD)' },
  { value: 'GTQ', label: 'Quetzales (GTQ)' },
];
const accountTypeOptions = [
  { value: 'Ahorro', label: 'Ahorro' },
  { value: 'Monetario', label: 'Monetario' },
];
const deliveryMethods = [
  { value: 'BANK_DEPOSIT', label: 'Deposito bancario' },
  { value: 'TRANSFER', label: 'Transferencia' },
  { value: 'WALLET', label: 'Billetera' },
  { value: 'CASH_PICKUP', label: 'Retiro' },
];
const statusLabels: Record<string, string> = {
  CREATED: 'Creada',
  VALIDATING: 'Validando',
  RISK_ANALYSIS: 'Analizando riesgo',
  APPROVED: 'Aprobada',
  PROCESSING: 'Procesando',
  AVAILABLE: 'Disponible',
  COMPLETED: 'Completada',
  REVIEW_REQUIRED: 'Requiere revision',
  REJECTED: 'Rechazada',
};
const sampleRiskFeatures = {
  account_age_days: 28,
  transaction_count: 2,
  source_amount: 980.0,
  commission_rate: 0.0225,
  commission_amount: 22.05,
  total_debit_amount: 1002.05,
  exchange_rate: 7.8,
  destination_amount: 7644.0,
  linked_user: 0,
  transactions_last_24h: 2,
  transactions_last_7d: 4,
  transactions_last_30d: 6,
  avg_transaction_amount: 260.0,
  max_transaction_amount: 400.0,
  new_beneficiary_flag: 1,
  beneficiary_age_days: 2,
  countries_used_last_30d: 3,
  failed_transactions: 1,
  transaction_hour: 2,
  weekend_flag: 1,
  amount_vs_user_average: 3.77,
  transaction_velocity_24h: 2,
  transaction_velocity_7d: 4,
  unusual_hour_flag: 1,
  new_corridor_flag: 1,
  country_diversity_30d: 3,
  failed_transaction_ratio: 0.5,
  historical_avg_amount: 260.0,
  historical_max_amount: 400.0,
  origin_country: 'Estados Unidos',
  destination_country: 'Guatemala',
  source_currency: 'USD',
  destination_currency: 'GTQ',
  delivery_method: 'BANK_DEPOSIT',
  funding_method: 'BANK_TRANSFER',
  relationship: 'Amigo / Amiga',
  amount_bucket: '500-999',
};

type Role = { id: number; name: string; description: string };
type User = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  country: string;
  document_type: string | null;
  fictitious_document_id: string | null;
  birth_date: string | null;
  occupation: string | null;
  must_change_password: boolean;
  role: Role;
};
type FundingSource = {
  id: number;
  user_id: number;
  type: string;
  display_name: string;
  provider: string | null;
  last_four: string;
  account_type: string | null;
  card_expiry: string | null;
  currency: string;
  is_default: boolean;
  is_active: boolean;
};
type BeneficiaryRelationship = { id: number; name: string; is_active: boolean };
type TrackingResult = {
  remittance_number: string;
  origin_country: string;
  destination_country: string;
  source_amount: string;
  source_currency: string;
  destination_amount: string;
  destination_currency: string;
  delivery_method: string;
  status: string;
  created_at: string;
  timeline: Array<{ previous_status: string | null; new_status: string; changed_at: string; reason: string | null }>;
};
type Beneficiary = {
  id: number;
  beneficiary_user_id: number | null;
  first_name: string;
  last_name: string;
  email: string | null;
  relationship: string;
  country: string;
  currency: string;
  department: string;
  municipality: string;
  delivery_method: string;
  bank_name: string | null;
  account_type: string | null;
  account_last_four: string | null;
  city: string | null;
  is_active: boolean;
};
type Simulation = {
  beneficiary_id: number;
  beneficiary_user_id: number | null;
  origin_country: string;
  destination_country: string;
  source_amount: string;
  source_currency: string;
  amount: string;
  currency: string;
  commission_rate: string;
  commission_amount: string;
  total_amount: string;
  total_debit_amount: string;
  total_debit_currency: string;
  exchange_rate: string;
  exchange_rate_source: string;
  destination_currency: string;
  destination_amount: string;
  payment_method: string;
  delivery_method: string;
  estimated_delivery: string;
  is_exchange_rate_simulated: boolean;
};
type Corridor = {
  id: number;
  origin_country: string;
  destination_country: string;
  origin_currency: string;
  destination_currency: string;
  min_amount: string;
  max_amount: string;
  estimated_delivery: string;
};
type Transaction = Simulation & {
  id: number;
  transaction_id: string;
  remittance_number: string;
  remittance_uuid: string | null;
  sender_id: number;
  beneficiary_user_id: number | null;
  funding_source_id: number | null;
  status: string;
  rule_score: string | null;
  ml_probability: string | null;
  anomaly_score: string | null;
  final_risk_score: string | null;
  risk_level: string | null;
  model_version: string | null;
  created_at: string;
  updated_at: string;
  beneficiary: Beneficiary;
  sender: User;
};
type AnalyticsSummary = {
  total_remittances: number;
  volume_usd_equivalent: string;
  commission_usd_equivalent: string;
  average_ticket_usd_equivalent: string;
  top_corridor: string | null;
  synthetic_fraud_cases: number;
};
type AnalyticsDistributionItem = { label: string; count: number; amount?: string | null; currency?: string | null };
type AnalyticsTimeSeriesPoint = {
  period: string;
  count: number;
  volume_usd_equivalent: string;
  commission_usd_equivalent: string;
};
type RiskModelInfo = {
  available: boolean;
  model_name: string | null;
  model_version: string | null;
  algorithm: string | null;
  selected_model: string | null;
  trained_at: string | null;
  threshold: number | null;
  features: string[];
  dataset_hash: string | null;
  message: string | null;
};
type RiskMetrics = {
  selected_model: string;
  comparison: Array<{
    model: string;
    algorithm: string;
    training_time_seconds: number;
    threshold: number;
    test: {
      precision: number;
      recall: number;
      f1: number;
      roc_auc: number;
      pr_auc: number;
      brier_score: number;
      confusion_matrix: number[][];
    };
  }>;
  feature_importance: Array<{ feature: string; importance: number; method?: string }>;
};
type RiskPrediction = {
  ml_probability: number;
  model_version: string;
  threshold: number;
  classification: string;
  classification_label: string;
  top_features: Array<{ feature: string; importance: number; method?: string }>;
};
type RiskEngineInfo = {
  version: string;
  aggregation_strategy: string;
  weights: Record<string, number>;
  risk_band_thresholds: Record<string, number>;
  rules_version: string;
  ml_model_version: string | null;
  ml_threshold: number | null;
  anomaly_model_version: string | null;
  anomaly_available: boolean;
};
type RiskDashboardMetrics = {
  total_assessments: number;
  low_risk: number;
  medium_risk: number;
  high_risk: number;
  pending_review: number;
  reviewed: number;
  approved: number;
  escalated: number;
  rejected: number;
  average_rule_score: number | null;
  average_ml_probability: number | null;
  average_anomaly_score: number | null;
  average_final_risk_score: number | null;
  top_triggered_rules: Array<{ rule_code: string; count: number }>;
};
type RiskAssessment = {
  id: number;
  remittance_id: number;
  assessment_sequence: number;
  rule_score: string | null;
  rules_version: string | null;
  triggered_rules_json: Array<Record<string, string | number>> | null;
  ml_probability: string | null;
  ml_model_version: string | null;
  ml_threshold: string | null;
  anomaly_score: string | null;
  anomaly_model_version: string | null;
  final_risk_score: string | null;
  risk_band: string;
  recommended_action: string;
  risk_engine_version: string;
  weights_json: Record<string, number> | null;
  signal_status_json: Record<string, string> | null;
  explanations_json: string[] | null;
  evaluated_at: string;
  review_status: string;
  reviewed_by: number | null;
  review_decision: string | null;
  review_reason: string | null;
  reviewed_at: string | null;
  remittance_number?: string | null;
  sender_name?: string;
  beneficiary_name?: string;
  origin_country?: string;
  destination_country?: string;
  source_amount?: string;
  source_currency?: string;
  status?: string;
  created_at?: string;
};
type ForecastPoint = {
  period: string;
  predicted: string;
  lower_80: string | null;
  upper_80: string | null;
  lower_95: string | null;
  upper_95: string | null;
};
type HistoricalForecastPoint = { period: string; value: string };
type ForecastResponse = {
  model_version: string;
  selected_model: string;
  target: string;
  granularity: string;
  horizon: number;
  currency: string | null;
  historical: HistoricalForecastPoint[];
  forecast: ForecastPoint[];
  metrics: { mae: number; rmse: number; wape: number; smape?: number | null };
  data_type: string;
  interval_method: string;
  warning: string | null;
};
type ForecastSummary = {
  model_version: string;
  go_decision: string;
  records: number;
  weeks_covered: number;
  months_covered: number;
  latest_period: string;
  next_4_weeks_count: string;
  next_4_weeks_amount_usd: string;
  count_wape: number;
  amount_wape: number;
  drift_status: string;
  data_type: string;
};
type ForecastCorridor = {
  corridor: string;
  historical_volume: number;
  historical_amount_usd: string;
  forecast_volume_next_4w: string;
  forecast_amount_usd_next_4w: string;
  status: string;
};
type BIOverview = {
  current: Record<string, number | string | null>;
  previous: Record<string, number | string | null> | null;
  changes: Record<string, { absolute_change: number | string | null; percentage_change: string | null }>;
};
type BITrendPoint = {
  period: string;
  remittances: number;
  amount_usd_equivalent: string;
  commission_revenue_usd_equivalent: string;
};
type BICorridor = {
  corridor: string;
  remittance_count: number;
  total_amount_usd_equivalent: string;
  average_ticket_usd_equivalent: string | null;
  commission_revenue_usd_equivalent: string;
  completion_rate: string | null;
  risk_distribution: Array<{ risk_band: string; label: string; count: number; share: string | null }>;
};
type BICustomers = {
  active_clients: number;
  new_clients: number;
  returning_clients: number;
  repeat_senders: number;
  repeat_sender_rate: string | null;
  remittances_per_client: string | null;
  average_amount_per_client_usd_equivalent: string | null;
};
type BIOperations = {
  status_distribution: Array<{ status: string; label: string; count: number }>;
  processing_remittances: number;
  available_remittances: number;
  completed_remittances: number;
  review_required: number;
  rejected_remittances: number;
};
type BIRisk = {
  assessment_count: number;
  risk_distribution: Array<{ risk_band: string; label: string; count: number; share: string | null }>;
  average_final_risk_score: string | null;
  manual_reviews: number;
  review_count: number;
  approved_reviews: number;
  escalated_reviews: number;
  rejected_reviews: number;
};
type BIForecast = {
  model_version: string;
  go_decision: string;
  horizon: number;
  next_4_weeks_count: string;
  next_4_weeks_amount_usd: string;
  drift_status: string;
  data_type: string;
};
type BIExecutiveSummary = {
  highlights: Array<{ priority: 'INFO' | 'ATTENTION'; code: string; message: string; source_kpis: string[] }>;
  attention_points: Array<{ priority: 'INFO' | 'ATTENTION'; code: string; message: string; source_kpis: string[] }>;
  forecast_outlook: BIForecast;
};
type BlockchainInfo = {
  blockchain_engine_version: string;
  hash_algorithm: string;
  difficulty: number;
  total_blocks: number;
  total_evidence: number;
  genesis_hash: string | null;
  last_block_hash: string | null;
  chain_valid: boolean;
  supported_schema_versions: string[];
};
type BlockchainMetrics = {
  total_blocks: number;
  total_evidence: number;
  blocks_by_event_type: Record<string, number>;
  chain_valid: boolean;
  last_block_timestamp: string | null;
  average_mining_time_ms: number | null;
};
type BlockchainBlock = {
  block_index: number;
  timestamp: string;
  event_type: string;
  entity_type: string;
  entity_reference: string;
  evidence_hash: string;
  previous_hash: string;
  nonce: number;
  difficulty: number;
  block_hash: string;
  schema_version: string;
  idempotency_key: string;
  record_status: string;
  mining_time_ms: number;
  created_at: string;
};
type BlockchainValidation = {
  valid: boolean;
  blocks_checked: number;
  errors: Array<{ block_index: number; code: string }>;
};
type BlockchainVerification = {
  status: string;
  verified: number;
  mismatches: Array<{ block_index: number; expected_hash?: string; recorded_hash?: string }>;
};
type BlockchainOverview = {
  info: BlockchainInfo;
  metrics: BlockchainMetrics;
  blocks: BlockchainBlock[];
};
type AssistantChatMessage = {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  intent?: string | null;
  provider?: string | null;
  tools_used_json?: string[] | null;
  sources_json?: Array<Record<string, unknown>> | null;
  created_at?: string;
};
type AssistantChatResponse = {
  conversation_id: number;
  message_id: number;
  answer: string;
  intent: string;
  provider: string;
  tools_used: string[];
  sources: Array<Record<string, unknown>>;
  source_types: string[];
  warnings: string[];
  generated_at: string;
};
type AssistantConversation = {
  id: number;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};
type AssistantConversationDetail = AssistantConversation & {
  messages: AssistantChatMessage[];
};
type View =
  | 'dashboard'
  | 'assistant'
  | 'beneficiaries'
  | 'funding'
  | 'new-remittance'
  | 'sent'
  | 'received'
  | 'tracking'
  | 'profile'
  | 'detail'
  | 'bi'
  | 'analytics'
  | 'risk'
  | 'risk-review'
  | 'blockchain'
  | 'forecasting'
  | 'password-change';
type AuthMode = 'login' | 'register' | 'forgot';
type MessageType = 'error' | 'success';
type RegisterFormState = {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  country: string;
  document_type: string;
  fictitious_document_id: string;
  birth_date: string;
  password: string;
  confirm_password: string;
  occupation: string;
  terms_accepted: boolean;
  human_check_accepted: boolean;
};

class ApiRequestError extends Error {
  constructor(public code: string, public status: number) {
    super(code);
  }
}

function App() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [authMode, setAuthMode] = React.useState<AuthMode>('login');
  const [currentUser, setCurrentUser] = React.useState<User | null>(null);
  const [token, setToken] = React.useState<string | null>(null);
  const [view, setView] = React.useState<View>('dashboard');
  const [beneficiaries, setBeneficiaries] = React.useState<Beneficiary[]>([]);
  const [transactions, setTransactions] = React.useState<Transaction[]>([]);
  const [receivedTransactions, setReceivedTransactions] = React.useState<Transaction[]>([]);
  const [fundingSources, setFundingSources] = React.useState<FundingSource[]>([]);
  const [relationships, setRelationships] = React.useState<BeneficiaryRelationship[]>([]);
  const [corridors, setCorridors] = React.useState<Corridor[]>([]);
  const [selectedTransaction, setSelectedTransaction] = React.useState<Transaction | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [messageType, setMessageType] = React.useState<MessageType>('error');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isCheckingSession, setIsCheckingSession] = React.useState(true);
  const canViewAnalytics = currentUser?.role.name === 'ADMIN' || currentUser?.role.name === 'RISK_ANALYST';

  React.useEffect(() => {
    const internalViews: View[] = ['bi', 'analytics', 'forecasting', 'risk', 'risk-review', 'blockchain'];
    if (currentUser && !canViewAnalytics && internalViews.includes(view)) {
      setView('dashboard');
      showMessage('Esta vista esta reservada para perfiles internos autorizados.', 'error');
    }
  }, [canViewAnalytics, currentUser, view]);

  React.useEffect(() => {
    const storedToken = window.localStorage.getItem(tokenStorageKey);
    if (!storedToken) {
      setIsCheckingSession(false);
      return;
    }
    setToken(storedToken);
    validateSession(storedToken).finally(() => setIsCheckingSession(false));
  }, []);

  async function apiRequest<T>(path: string, options: RequestInit = {}, authToken = token): Promise<T> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (authToken) headers.Authorization = `Bearer ${authToken}`;
    const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers: { ...headers, ...options.headers } });
    if (!response.ok) {
      let code = 'REQUEST_FAILED';
      try {
        const body = await response.json();
        code = body.detail?.code ?? code;
      } catch {
        // Keep default code when the backend returns non-JSON.
      }
      throw new ApiRequestError(code, response.status);
    }
    return (await response.json()) as T;
  }

  async function validateSession(authToken: string): Promise<boolean> {
    try {
      const user = await apiRequest<User>('/users/me', {}, authToken);
      setCurrentUser(user);
      if (user.must_change_password) setView('password-change');
      await refreshClientData(authToken);
      return true;
    } catch {
      window.localStorage.removeItem(tokenStorageKey);
      setCurrentUser(null);
      setToken(null);
      showMessage(
        'La sesion fue aceptada, pero el backend activo no tiene disponibles los modulos de Remesas. Reinicia FastAPI con la version actualizada.',
        'error',
      );
      return false;
    }
  }

  async function refreshClientData(authToken = token) {
    if (!authToken) return;
    const [beneficiaryData, transactionData, receivedData, fundingData, corridorData, relationshipData] = await Promise.all([
      apiRequest<Beneficiary[]>('/beneficiaries', {}, authToken),
      apiRequest<Transaction[]>('/transactions/sent', {}, authToken),
      apiRequest<Transaction[]>('/transactions/received', {}, authToken),
      apiRequest<FundingSource[]>('/funding-sources', {}, authToken),
      apiRequest<Corridor[]>('/remittances/corridors', {}, authToken),
      apiRequest<BeneficiaryRelationship[]>('/catalogs/beneficiary-relationships', {}, authToken),
    ]);
    setBeneficiaries(beneficiaryData);
    setTransactions(transactionData);
    setReceivedTransactions(receivedData);
    setFundingSources(fundingData);
    setCorridors(corridorData);
    setRelationships(relationshipData);
  }

  async function handleLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setMessage(null);
    try {
      const body = await apiRequest<{ access_token: string; must_change_password: boolean }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      window.localStorage.setItem(tokenStorageKey, body.access_token);
      setToken(body.access_token);
      const sessionReady = await validateSession(body.access_token);
      if (!sessionReady) return;
      if (body.must_change_password) {
        setView('password-change');
        showMessage('Ingresa una nueva contrasena para completar la recuperacion.', 'success');
      } else {
        setView('dashboard');
        showMessage('Sesion iniciada correctamente.', 'success');
      }
    } catch (error) {
      const code = error instanceof Error ? error.message : '';
      if (code === 'INVALID_CREDENTIALS') {
        showMessage('Correo o contrasena incorrectos. Revisa tus credenciales e intenta de nuevo.', 'error');
      } else {
        showMessage('No hay conexion con el backend. Confirma que FastAPI este ejecutandose en el puerto 8000.', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    window.localStorage.removeItem(tokenStorageKey);
    setToken(null);
    setCurrentUser(null);
    setPassword('');
    setBeneficiaries([]);
    setTransactions([]);
    setReceivedTransactions([]);
    setFundingSources([]);
    setRelationships([]);
    setSelectedTransaction(null);
    setView('dashboard');
    showMessage('Sesion cerrada correctamente.', 'success');
  }

  function showMessage(text: string, type: MessageType) {
    setMessage(text);
    setMessageType(type);
  }

  async function handleTransactionCreated(transaction: Transaction) {
    await refreshClientData();
    setSelectedTransaction(transaction);
    setView('detail');
    showMessage('Remesa creada correctamente.', 'success');
  }

  async function handleReceiveTransaction(transaction: Transaction) {
    try {
      const updated = await request<Transaction>(`/transactions/${transaction.id}/receive`, { method: 'POST' });
      await refreshClientData();
      setSelectedTransaction(updated);
      showMessage('Remesa recibida correctamente.', 'success');
    } catch {
      showMessage('No se pudo completar la recepcion. Verifica que la remesa siga disponible.', 'error');
    }
  }

  return (
    <main className="min-h-screen bg-fiducia-cloud text-fiducia-ink">
      <Header currentUser={currentUser} onLogout={handleLogout} />
      {currentUser ? (
        <section className="mx-auto max-w-7xl px-6 py-8">
          {!currentUser.must_change_password ? (
          <nav className="mb-6 flex flex-wrap gap-2">
            <NavButton active={view === 'dashboard'} onClick={() => setView('dashboard')} label="Inicio" />
            <NavButton active={view === 'assistant'} onClick={() => setView('assistant')} label="Asistente" />
            <NavButton active={view === 'new-remittance'} onClick={() => setView('new-remittance')} label="Enviar remesa" />
            <NavButton active={view === 'sent'} onClick={() => setView('sent')} label="Remesas enviadas" />
            <NavButton active={view === 'received'} onClick={() => setView('received')} label="Remesas recibidas" />
            <NavButton active={view === 'beneficiaries'} onClick={() => setView('beneficiaries')} label="Beneficiarios" />
            <NavButton active={view === 'funding'} onClick={() => setView('funding')} label="Metodos de pago" />
            <NavButton active={view === 'tracking'} onClick={() => setView('tracking')} label="Rastrear remesa" />
            {canViewAnalytics ? (
              <NavButton active={view === 'bi'} onClick={() => setView('bi')} label="Inteligencia de negocio" />
            ) : null}
            {canViewAnalytics ? (
              <NavButton active={view === 'analytics'} onClick={() => setView('analytics')} label="Analitica" />
            ) : null}
            {canViewAnalytics ? (
              <NavButton active={view === 'forecasting'} onClick={() => setView('forecasting')} label="Analitica predictiva" />
            ) : null}
            {canViewAnalytics ? (
              <NavButton active={view === 'risk'} onClick={() => setView('risk')} label="Inteligencia de riesgo" />
            ) : null}
            {canViewAnalytics ? (
              <NavButton active={view === 'risk-review'} onClick={() => setView('risk-review')} label="Revision de riesgo" />
            ) : null}
            {canViewAnalytics ? (
              <NavButton active={view === 'blockchain'} onClick={() => setView('blockchain')} label="Trazabilidad blockchain" />
            ) : null}
            <NavButton active={view === 'profile'} onClick={() => setView('profile')} label="Mi perfil" />
          </nav>
          ) : null}
          {message ? <StatusMessage message={message} type={messageType} /> : null}
          {currentUser.must_change_password ? (
            <PasswordChangeView
              onChanged={(user) => {
                setCurrentUser(user);
                setPassword('');
                setView('dashboard');
                showMessage('Contrasena actualizada correctamente.', 'success');
              }}
              showMessage={showMessage}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'dashboard' ? (
            <Dashboard
              user={currentUser}
              beneficiaries={beneficiaries}
              transactions={transactions}
              receivedTransactions={receivedTransactions}
              fundingSources={fundingSources}
              onNewRemittance={() => setView('new-remittance')}
              onSent={() => setView('sent')}
              onReceived={() => setView('received')}
              onFunding={() => setView('funding')}
              onTracking={() => setView('tracking')}
              onProfile={() => setView('profile')}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'assistant' ? <AssistantView user={currentUser} /> : null}
          {!currentUser.must_change_password && view === 'beneficiaries' ? (
            <BeneficiariesView
              beneficiaries={beneficiaries}
              corridors={corridors}
              relationships={relationships}
              onCreated={() => refreshClientData()}
              showMessage={showMessage}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'new-remittance' ? (
            <NewRemittanceView
              beneficiaries={beneficiaries.filter((beneficiary) => beneficiary.is_active)}
              fundingSources={fundingSources.filter((source) => source.is_active)}
              corridors={corridors}
              showMessage={showMessage}
              onCreated={handleTransactionCreated}
              onManageBeneficiaries={() => setView('beneficiaries')}
              onManageFunding={() => setView('funding')}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'funding' ? (
            <FundingSourcesView
              user={currentUser}
              fundingSources={fundingSources}
              onChanged={() => refreshClientData()}
              showMessage={showMessage}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'tracking' ? <TrackingView showMessage={showMessage} /> : null}
          {!currentUser.must_change_password && view === 'bi' && canViewAnalytics ? <BusinessIntelligenceView /> : null}
          {!currentUser.must_change_password && view === 'analytics' && canViewAnalytics ? <AnalyticsView /> : null}
          {!currentUser.must_change_password && view === 'forecasting' && canViewAnalytics ? <ForecastingView /> : null}
          {!currentUser.must_change_password && view === 'risk' && canViewAnalytics ? <RiskIntelligenceView /> : null}
          {!currentUser.must_change_password && view === 'risk-review' && canViewAnalytics ? <RiskReviewView showMessage={showMessage} /> : null}
          {!currentUser.must_change_password && view === 'blockchain' && canViewAnalytics ? <BlockchainView user={currentUser} transactions={[...transactions, ...receivedTransactions]} /> : null}
          {!currentUser.must_change_password && view === 'profile' ? (
            <ProfileView user={currentUser} onUpdated={(user) => setCurrentUser(user)} showMessage={showMessage} />
          ) : null}
          {!currentUser.must_change_password && view === 'sent' ? (
            <HistoryView
              title="Remesas enviadas"
              emptyText="Aun no has enviado remesas."
              mode="sent"
              transactions={transactions}
              onOpen={(transaction) => {
                setSelectedTransaction(transaction);
                setView('detail');
              }}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'received' ? (
            <HistoryView
              title="Remesas recibidas"
              emptyText="Aun no tienes remesas recibidas."
              mode="received"
              transactions={receivedTransactions}
              onOpen={(transaction) => {
                setSelectedTransaction(transaction);
                setView('detail');
              }}
            />
          ) : null}
          {!currentUser.must_change_password && view === 'detail' && selectedTransaction ? (
            <TransactionDetail currentUser={currentUser} transaction={selectedTransaction} onReceive={handleReceiveTransaction} />
          ) : null}
        </section>
      ) : (
        <LandingLogin
          email={email}
          password={password}
          isLoading={isLoading}
          isCheckingSession={isCheckingSession}
          message={message}
          messageType={messageType}
          authMode={authMode}
          setAuthMode={setAuthMode}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onLogin={handleLogin}
        />
      )}
      <DemoFooter />
    </main>
  );
}

function Header({ currentUser, onLogout }: { currentUser: User | null; onLogout: () => void }) {
  return (
    <section className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <img
          src={fiduciaLogo}
          alt="FIDUCIA - Plataforma de remesas inteligentes"
          className="h-12 w-auto max-w-[220px] object-contain sm:h-14 sm:max-w-[280px]"
        />
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-fiducia-mint px-4 py-2 text-sm font-medium text-fiducia-teal">
            IA + Analítica
          </span>
          {currentUser ? (
            <button className="secondary-button inline-flex items-center gap-2" type="button" onClick={onLogout}>
              <LogOut size={16} />
              Salir
            </button>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function LandingLogin(props: {
  email: string;
  password: string;
  isLoading: boolean;
  isCheckingSession: boolean;
  message: string | null;
  messageType: MessageType;
  authMode: AuthMode;
  setAuthMode: (mode: AuthMode) => void;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onLogin: (event: React.FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="mx-auto grid max-w-6xl gap-8 px-6 py-12 lg:grid-cols-[1.2fr_0.8fr]">
      <div className="flex flex-col justify-center">
        <img
          src={fiduciaLogo}
          alt="FIDUCIA - Plataforma de remesas inteligentes"
          className="mb-8 w-full max-w-xl object-contain"
        />
        <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-fiducia-teal">
          Remesas digitales con analitica e IA
        </p>
        <h1 className="max-w-3xl text-4xl font-bold leading-tight text-fiducia-navy md:text-5xl">
          Envia mas. Paga menos. Decide mejor.
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
          Plataforma para gestionar beneficiarios, cotizar envios, crear remesas y consultar historial.
        </p>
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <Feature icon={<ShieldCheck />} title="Seguridad base" text="JWT, roles y contrasenas hasheadas." />
          <Feature icon={<Users />} title="Beneficiarios" text="Registro propio y administracion segura." />
          <Feature icon={<BarChart3 />} title="Remesas" text="Cotizacion y trazabilidad." />
        </div>
      </div>
      {props.authMode === 'login' ? <LoginPanel {...props} /> : null}
      {props.authMode === 'forgot' ? <ForgotPasswordPanel setAuthMode={props.setAuthMode} /> : null}
      {props.authMode === 'register' ? <RegisterPanel setAuthMode={props.setAuthMode} /> : null}
    </section>
  );
}

function LoginPanel({
  email,
  password,
  isLoading,
  isCheckingSession,
  message,
  messageType,
  setAuthMode,
  onEmailChange,
  onPasswordChange,
  onLogin,
}: {
  email: string;
  password: string;
  isLoading: boolean;
  isCheckingSession: boolean;
  message: string | null;
  messageType: MessageType;
  setAuthMode: (mode: AuthMode) => void;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onLogin: (event: React.FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="panel">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
          <LogIn size={20} />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-fiducia-navy">Acceso seguro</h2>
          <p className="text-sm text-slate-500">Portal de clientes FIDUCIA</p>
        </div>
      </div>
      <form className="space-y-4" onSubmit={onLogin}>
        <TextInput label="Correo electronico" type="email" value={email} onChange={onEmailChange} placeholder="ana@example.com" />
        <TextInput label="Contrasena" type="password" value={password} onChange={onPasswordChange} placeholder="Minimo 8 caracteres" />
        <button className="primary-button w-full" type="submit" disabled={isLoading || isCheckingSession}>
          {isLoading || isCheckingSession ? 'Validando...' : 'Iniciar sesion'}
        </button>
      </form>
      <button className="mt-4 w-full text-sm font-semibold text-fiducia-teal" type="button" onClick={() => setAuthMode('register')}>
        Crear cuenta
      </button>
      <button className="mt-3 w-full text-sm font-semibold text-slate-500 hover:text-fiducia-teal" type="button" onClick={() => setAuthMode('forgot')}>
        Olvide mi contrasena
      </button>
      {message ? <StatusMessage message={message} type={messageType} /> : null}
    </div>
  );
}

function ForgotPasswordPanel({ setAuthMode }: { setAuthMode: (mode: AuthMode) => void }) {
  const [email, setEmail] = React.useState('');
  const [isSending, setIsSending] = React.useState(false);
  const [message, setMessage] = React.useState<string | null>(null);
  const [messageType, setMessageType] = React.useState<MessageType>('success');

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSending(true);
    setMessage(null);
    try {
      const response = await request<{ message: string; temporary_password?: string | null }>('/auth/password/forgot', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
      setMessage(
        response.temporary_password
          ? `${response.message} En esta demo, la contrasena temporal enviada es: ${response.temporary_password}`
          : response.message,
      );
      setMessageType('success');
    } catch {
      setMessage('No se pudo procesar la recuperacion. Verifica el correo e intenta de nuevo.');
      setMessageType('error');
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="panel self-start">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
          <ShieldCheck size={20} />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-fiducia-navy">Recuperar acceso</h2>
          <p className="text-sm text-slate-500">Enviaremos una contrasena temporal al correo registrado.</p>
        </div>
      </div>
      <form className="space-y-4" onSubmit={submit}>
        <TextInput label="Correo electronico" type="email" value={email} onChange={setEmail} placeholder="tu@email.com" />
        <button className="primary-button w-full" type="submit" disabled={isSending}>
          {isSending ? 'Enviando...' : 'Enviar recuperacion'}
        </button>
      </form>
      <button className="mt-4 w-full text-sm font-semibold text-fiducia-teal" type="button" onClick={() => setAuthMode('login')}>
        Volver al login
      </button>
      {message ? <StatusMessage message={message} type={messageType} /> : null}
      <p className="mt-6 border-t border-slate-100 pt-4 text-center text-xs leading-5 text-slate-400">
        Acceso protegido para gestionar remesas, beneficiarios y trazabilidad.
      </p>
    </div>
  );
}

function RegisterPanel({ setAuthMode }: { setAuthMode: (mode: AuthMode) => void }) {
  const [form, setForm] = React.useState<RegisterFormState>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    country: 'Guatemala',
    document_type: 'DPI',
    fictitious_document_id: '',
    birth_date: '',
    password: '',
    confirm_password: '',
    occupation: '',
    terms_accepted: false,
    human_check_accepted: false,
  });
  const [isSaving, setIsSaving] = React.useState(false);
  const [message, setMessage] = React.useState<string | null>(null);
  const [messageType, setMessageType] = React.useState<MessageType>('error');
  const [isTermsOpen, setIsTermsOpen] = React.useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationMessage = validateRegisterForm(form);
    if (validationMessage) {
      setMessage(validationMessage);
      setMessageType('error');
      return;
    }
    setIsSaving(true);
    setMessage(null);
    try {
      await request('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          birth_date: form.birth_date || null,
          occupation: form.occupation || null,
        }),
      });
      setMessage('Cuenta creada. Ya puedes iniciar sesion.');
      setMessageType('success');
      setTimeout(() => setAuthMode('login'), 700);
    } catch (error) {
      const code = error instanceof ApiRequestError ? error.code : 'CONNECTION_ERROR';
      setMessage(getRegisterErrorMessage(code));
      setMessageType('error');
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="panel">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
          <UserCircle size={20} />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-fiducia-navy">Crear cuenta</h2>
          <p className="text-sm text-slate-500">Registro de cliente FIDUCIA</p>
        </div>
      </div>
      <form className="grid gap-4" onSubmit={submit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput label="Nombre" value={form.first_name} onChange={(value) => setForm({ ...form, first_name: value })} />
          <TextInput label="Apellido" value={form.last_name} onChange={(value) => setForm({ ...form, last_name: value })} />
        </div>
        <TextInput label="Correo electronico" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} />
        <TextInput label="Telefono" value={form.phone} onChange={(value) => setForm({ ...form, phone: value })} />
        <SelectInput label="Pais" value={form.country} options={getCountryOptions([])} onChange={(value) => setForm({ ...form, country: value })} />
        <TextInput label="Ocupacion" value={form.occupation} onChange={(value) => setForm({ ...form, occupation: value })} required={false} />
        <div className="grid gap-4 sm:grid-cols-[0.8fr_1.2fr]">
          <SelectInput
            label="Tipo de documento"
            value={form.document_type}
            options={[
              { value: 'DPI', label: 'DPI' },
              { value: 'PASSPORT', label: 'Pasaporte' },
            ]}
            onChange={(value) => setForm({ ...form, document_type: value, fictitious_document_id: '' })}
          />
          <TextInput
            label="No. de documento"
            value={form.fictitious_document_id}
            maxLength={form.document_type === 'DPI' ? 13 : 20}
            placeholder={form.document_type === 'DPI' ? '13 digitos' : 'Pasaporte ficticio'}
            onChange={(value) =>
              setForm({
                ...form,
                fictitious_document_id:
                  form.document_type === 'DPI' ? value.replace(/\D/g, '').slice(0, 13) : value.toUpperCase(),
              })
            }
          />
        </div>
        <TextInput
          label="Fecha de nacimiento"
          type="date"
          value={form.birth_date}
          onChange={(value) => setForm({ ...form, birth_date: value })}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput label="Contrasena" type="password" value={form.password} onChange={(value) => setForm({ ...form, password: value })} minLength={8} />
          <TextInput label="Confirmar contrasena" type="password" value={form.confirm_password} onChange={(value) => setForm({ ...form, confirm_password: value })} minLength={8} />
        </div>
        <p className="-mt-2 text-xs leading-5 text-slate-500">Usa minimo 8 caracteres e incluye letras y numeros.</p>
        <button
          className={`flex items-center justify-between rounded-md border px-4 py-3 text-left transition ${
            form.human_check_accepted ? 'border-emerald-300 bg-emerald-50' : 'border-slate-300 bg-white'
          }`}
          type="button"
          onClick={() => setForm({ ...form, human_check_accepted: !form.human_check_accepted })}
        >
          <span className="flex items-center gap-3 text-sm text-slate-700">
            <span
              className={`flex h-7 w-7 items-center justify-center border ${
                form.human_check_accepted ? 'border-fiducia-teal bg-fiducia-teal text-white' : 'border-slate-500 bg-white'
              }`}
            >
              {form.human_check_accepted ? <CheckCircle2 size={18} /> : null}
            </span>
            No soy un robot
          </span>
          <span className="text-right text-xs font-semibold text-slate-500">FIDUCIA<br />seguridad</span>
        </button>
        <label className="flex items-center gap-3 text-sm text-slate-600">
          <input
            className="h-5 w-5"
            type="checkbox"
            checked={form.terms_accepted}
            onChange={(event) => setForm({ ...form, terms_accepted: event.target.checked })}
          />
          <span>
            Acepto los{' '}
            <button
              className="font-semibold text-fiducia-teal underline-offset-2 hover:underline"
              type="button"
              onClick={() => setIsTermsOpen(true)}
            >
              terminos y condiciones
            </button>
            .
          </span>
        </label>
        <button className="primary-button" type="submit" disabled={isSaving}>
          {isSaving ? 'Creando...' : 'Registrarme'}
        </button>
      </form>
      <button className="mt-4 w-full text-sm font-semibold text-fiducia-teal" type="button" onClick={() => setAuthMode('login')}>
        Volver al login
      </button>
      {message ? <StatusMessage message={message} type={messageType} /> : null}
      {isTermsOpen ? <TermsModal onClose={() => setIsTermsOpen(false)} /> : null}
    </div>
  );
}

function PasswordChangeView({ onChanged, showMessage }: { onChanged: (user: User) => void; showMessage: (text: string, type: MessageType) => void }) {
  const [newPassword, setNewPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [isSaving, setIsSaving] = React.useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (newPassword.length < 8) {
      showMessage('La nueva contrasena debe tener minimo 8 caracteres.', 'error');
      return;
    }
    if (!/[A-Za-z]/.test(newPassword) || !/\d/.test(newPassword)) {
      showMessage('La nueva contrasena debe incluir letras y numeros.', 'error');
      return;
    }
    if (newPassword !== confirmPassword) {
      showMessage('La confirmacion de contrasena no coincide.', 'error');
      return;
    }
    setIsSaving(true);
    try {
      const user = await request<User>('/auth/password/change', {
        method: 'POST',
        body: JSON.stringify({ new_password: newPassword, confirm_password: confirmPassword }),
      });
      onChanged(user);
    } catch {
      showMessage('No se pudo actualizar la contrasena. Intenta nuevamente.', 'error');
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="panel mx-auto max-w-xl">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
          <ShieldCheck size={20} />
        </div>
        <div>
          <h1 className="section-title">Crear nueva contrasena</h1>
          <p className="text-sm text-slate-500">Por seguridad, debes definir una nueva contrasena antes de continuar.</p>
        </div>
      </div>
      <form className="grid gap-4" onSubmit={submit}>
        <TextInput label="Nueva contrasena" type="password" value={newPassword} onChange={setNewPassword} minLength={8} />
        <TextInput label="Confirmar nueva contrasena" type="password" value={confirmPassword} onChange={setConfirmPassword} minLength={8} />
        <p className="-mt-2 text-xs leading-5 text-slate-500">Usa minimo 8 caracteres e incluye letras y numeros.</p>
        <button className="primary-button" type="submit" disabled={isSaving}>
          {isSaving ? 'Actualizando...' : 'Guardar nueva contrasena'}
        </button>
      </form>
    </section>
  );
}

function Dashboard({
  user,
  beneficiaries,
  transactions,
  receivedTransactions,
  fundingSources,
  onNewRemittance,
  onSent,
  onReceived,
  onFunding,
  onTracking,
  onProfile,
}: {
  user: User;
  beneficiaries: Beneficiary[];
  transactions: Transaction[];
  receivedTransactions: Transaction[];
  fundingSources: FundingSource[];
  onNewRemittance: () => void;
  onSent: () => void;
  onReceived: () => void;
  onFunding: () => void;
  onTracking: () => void;
  onProfile: () => void;
}) {
  const latest = [...transactions, ...receivedTransactions].sort(
    (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
  )[0];
  return (
    <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="panel">
        <p className="text-sm font-semibold uppercase tracking-widest text-fiducia-teal">Inicio cliente</p>
        <h1 className="mt-3 text-3xl font-bold text-fiducia-navy">Hola, {user.first_name}</h1>
        <p className="mt-3 text-slate-600">Envia, consulta y recibe remesas desde un solo lugar.</p>
        <div className="mt-6 grid gap-3 sm:grid-cols-4">
          <Metric label="Beneficiarios" value={beneficiaries.length.toString()} />
          <Metric label="Enviadas" value={transactions.length.toString()} />
          <Metric label="Recibidas" value={receivedTransactions.length.toString()} />
          <Metric label="Metodos de pago" value={fundingSources.length.toString()} />
        </div>
        <p className="mt-4 text-sm text-slate-500">Ultimo estado: {latest ? statusLabels[latest.status] : 'Sin remesas'}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button className="primary-button inline-flex items-center gap-2" type="button" onClick={onNewRemittance}>
            <Send size={18} />
            Enviar remesa
          </button>
          <button className="secondary-button inline-flex items-center gap-2" type="button" onClick={onSent}>
            <History size={18} />
            Remesas enviadas
          </button>
          <button className="secondary-button inline-flex items-center gap-2" type="button" onClick={onReceived}>
            <Inbox size={18} />
            Remesas recibidas
          </button>
          <button className="secondary-button inline-flex items-center gap-2" type="button" onClick={onFunding}>
            <CreditCard size={18} />
            Metodos de pago
          </button>
          <button className="secondary-button inline-flex items-center gap-2" type="button" onClick={onTracking}>
            <Search size={18} />
            Rastrear remesa
          </button>
          <button className="secondary-button inline-flex items-center gap-2" type="button" onClick={onProfile}>
            <UserCircle size={18} />
            Mi perfil
          </button>
        </div>
      </section>
      <section className="panel">
        <h2 className="section-title">Ultimas remesas enviadas</h2>
        <TransactionTable transactions={transactions.slice(0, 5)} compact mode="sent" />
      </section>
    </div>
  );
}

function AssistantView({ user }: { user: User }) {
  const [conversations, setConversations] = React.useState<AssistantConversation[]>([]);
  const [conversationId, setConversationId] = React.useState<number | null>(null);
  const [messages, setMessages] = React.useState<AssistantChatMessage[]>([]);
  const [input, setInput] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [lastSources, setLastSources] = React.useState<string[]>([]);

  React.useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    try {
      const data = await request<AssistantConversation[]>('/assistant/conversations');
      setConversations(data);
    } catch {
      setConversations([]);
    }
  }

  async function openConversation(id: number) {
    setError(null);
    try {
      const detail = await request<AssistantConversationDetail>(`/assistant/conversations/${id}`);
      setConversationId(detail.id);
      setMessages(detail.messages);
      setLastSources([]);
    } catch {
      setError('No se pudo abrir esta conversacion.');
    }
  }

  function newConversation() {
    setConversationId(null);
    setMessages([]);
    setInput('');
    setLastSources([]);
    setError(null);
  }

  async function sendMessage(messageText = input) {
    const clean = messageText.trim();
    if (!clean) return;
    const userMessage: AssistantChatMessage = { role: 'user', content: clean };
    setMessages((current) => [...current, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);
    try {
      const response = await request<AssistantChatResponse>('/assistant/chat', {
        method: 'POST',
        body: JSON.stringify({ conversation_id: conversationId, message: clean }),
      });
      setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        {
          id: response.message_id,
          role: 'assistant',
          content: response.answer,
          intent: response.intent,
          provider: response.provider,
          sources_json: response.sources,
          created_at: response.generated_at,
        },
      ]);
      setLastSources(response.source_types);
      await loadConversations();
    } catch {
      setError('No se pudo obtener respuesta del asistente. Intenta de nuevo.');
      setMessages((current) => current.filter((item) => item !== userMessage));
    } finally {
      setIsLoading(false);
    }
  }

  const suggestions = assistantSuggestions(user.role.name);

  return (
    <section className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <aside className="panel h-fit">
        <div className="flex items-center justify-between gap-3">
          <h2 className="section-title">Asistente</h2>
          <button className="icon-button" type="button" onClick={newConversation} title="Nueva conversacion">
            <Plus size={16} />
          </button>
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-500">Consultas informativas sobre datos autorizados de FIDUCIA.</p>
        <div className="mt-5 grid gap-2">
          {conversations.length === 0 ? <p className="text-sm text-slate-500">Sin conversaciones previas.</p> : null}
          {conversations.slice(0, 8).map((conversation) => (
            <button
              className={conversationId === conversation.id ? 'nav-button-active text-left' : 'nav-button text-left'}
              type="button"
              key={conversation.id}
              onClick={() => openConversation(conversation.id)}
            >
              {conversation.title}
            </button>
          ))}
        </div>
      </aside>

      <section className="panel min-h-[620px]">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 pb-5">
          <div>
            <h1 className="section-title">Asistente FIDUCIA</h1>
            <p className="mt-1 text-sm text-slate-500">Responde con fuentes internas y respeta los permisos de tu perfil.</p>
          </div>
          <span className="rounded-full bg-fiducia-mint px-3 py-1 text-sm font-semibold text-fiducia-teal">Informativo</span>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {messages.length === 0
            ? suggestions.map((suggestion) => (
                <button className="rounded-md border border-slate-200 bg-slate-50 p-3 text-left text-sm text-fiducia-navy transition hover:border-fiducia-teal" type="button" key={suggestion} onClick={() => sendMessage(suggestion)}>
                  {suggestion}
                </button>
              ))
            : null}
        </div>

        <div className="mt-6 max-h-[380px] space-y-4 overflow-y-auto pr-2">
          {messages.map((message, index) => (
            <div className={message.role === 'user' ? 'ml-auto max-w-[85%] rounded-lg bg-fiducia-teal p-4 text-white' : 'max-w-[88%] rounded-lg border border-slate-200 bg-white p-4 text-fiducia-ink'} key={`${message.role}-${message.id ?? index}`}>
              <p className="whitespace-pre-line text-sm leading-6">{message.content}</p>
              {message.role === 'assistant' && message.intent ? (
                <p className="mt-3 text-xs text-slate-400">Intencion: {assistantIntentLabel(message.intent)}</p>
              ) : null}
            </div>
          ))}
          {isLoading ? <div className="max-w-[88%] rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">Consultando datos autorizados...</div> : null}
        </div>

        {error ? <div className="mt-4"><StatusMessage message={error} type="error" /></div> : null}
        {lastSources.length > 0 ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {lastSources.map((source) => (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600" key={source}>
                Basado en {assistantSourceLabel(source)}
              </span>
            ))}
          </div>
        ) : null}

        <form
          className="mt-5 flex flex-col gap-3 border-t border-slate-200 pt-5 sm:flex-row"
          onSubmit={(event) => {
            event.preventDefault();
            sendMessage();
          }}
        >
          <input
            className="min-h-[44px] flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none transition focus:border-fiducia-teal focus:ring-2 focus:ring-fiducia-mint"
            value={input}
            maxLength={3000}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Escribe una consulta sobre tus remesas o datos autorizados"
          />
          <button className="primary-button inline-flex items-center justify-center gap-2" type="submit" disabled={isLoading || !input.trim()}>
            <Send size={16} />
            Enviar
          </button>
        </form>
        <p className="mt-3 text-xs leading-5 text-slate-400">
          Las respuestas del asistente son informativas y no sustituyen decisiones financieras o de riesgo.
        </p>
      </section>
    </section>
  );
}

function AnalyticsView() {
  const [summary, setSummary] = React.useState<AnalyticsSummary | null>(null);
  const [overTime, setOverTime] = React.useState<AnalyticsTimeSeriesPoint[]>([]);
  const [corridors, setCorridors] = React.useState<AnalyticsDistributionItem[]>([]);
  const [statuses, setStatuses] = React.useState<AnalyticsDistributionItem[]>([]);
  const [currencies, setCurrencies] = React.useState<AnalyticsDistributionItem[]>([]);
  const [methods, setMethods] = React.useState<{
    funding_methods: AnalyticsDistributionItem[];
    delivery_methods: AnalyticsDistributionItem[];
  } | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let isMounted = true;
    async function loadAnalytics() {
      setIsLoading(true);
      setError(null);
      try {
        const [summaryData, timeData, corridorData, statusData, currencyData, methodData] = await Promise.all([
          request<AnalyticsSummary>('/analytics/summary'),
          request<AnalyticsTimeSeriesPoint[]>('/analytics/remittances-over-time'),
          request<AnalyticsDistributionItem[]>('/analytics/top-corridors'),
          request<AnalyticsDistributionItem[]>('/analytics/status-distribution'),
          request<AnalyticsDistributionItem[]>('/analytics/currency-distribution'),
          request<{ funding_methods: AnalyticsDistributionItem[]; delivery_methods: AnalyticsDistributionItem[] }>(
            '/analytics/method-distribution',
          ),
        ]);
        if (!isMounted) return;
        setSummary(summaryData);
        setOverTime(timeData);
        setCorridors(corridorData);
        setStatuses(statusData);
        setCurrencies(currencyData);
        setMethods(methodData);
      } catch {
        if (isMounted) setError('No se pudo cargar la analitica. Verifica que tu usuario tenga permisos de analista o administrador.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadAnalytics();
    return () => {
      isMounted = false;
    };
  }, []);

  if (isLoading) return <section className="panel text-sm text-slate-600">Cargando analitica...</section>;
  if (error) return <StatusMessage message={error} type="error" />;

  return (
    <div className="grid gap-6">
      <section className="panel">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
            <BarChart3 size={20} />
          </div>
          <div>
            <h1 className="section-title">Analitica</h1>
            <p className="text-sm text-slate-500">Indicadores descriptivos de la operacion transaccional.</p>
          </div>
        </div>
        {summary ? (
          <div className="mt-6 grid gap-3 md:grid-cols-5">
            <Metric label="Total remesas" value={summary.total_remittances.toString()} />
            <Metric label="Volumen USD eq." value={`USD ${formatMoney(summary.volume_usd_equivalent)}`} />
            <Metric label="Comision USD eq." value={`USD ${formatMoney(summary.commission_usd_equivalent)}`} />
            <Metric label="Ticket promedio" value={`USD ${formatMoney(summary.average_ticket_usd_equivalent)}`} />
            <Metric label="Corredor principal" value={summary.top_corridor ?? 'Sin datos'} />
          </div>
        ) : null}
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <AnalyticsPanel title="Remesas por periodo">
          <SimpleBarChart
            items={overTime.map((item) => ({ label: item.period, value: item.count, detail: `USD ${formatMoney(item.volume_usd_equivalent)}` }))}
          />
        </AnalyticsPanel>
        <AnalyticsPanel title="Principales corredores">
          <SimpleBarChart
            items={corridors.map((item) => ({
              label: item.label,
              value: item.count,
              detail: item.amount ? `USD ${formatMoney(item.amount)}` : undefined,
            }))}
          />
        </AnalyticsPanel>
        <AnalyticsPanel title="Distribucion por estado">
          <SimpleBarChart items={statuses.map((item) => ({ label: statusLabels[item.label] ?? item.label, value: item.count }))} />
        </AnalyticsPanel>
        <AnalyticsPanel title="Monedas y metodos">
          <div className="grid gap-4 md:grid-cols-3">
            <MiniList title="Monedas" items={currencies.map((item) => `${item.label}: ${item.count}`)} />
            <MiniList title="Fondeo" items={(methods?.funding_methods ?? []).map((item) => `${paymentLabel(item.label)}: ${item.count}`)} />
            <MiniList title="Entrega" items={(methods?.delivery_methods ?? []).map((item) => `${deliveryLabel(item.label)}: ${item.count}`)} />
          </div>
        </AnalyticsPanel>
      </section>
    </div>
  );
}

function BusinessIntelligenceView() {
  const [overview, setOverview] = React.useState<BIOverview | null>(null);
  const [trends, setTrends] = React.useState<BITrendPoint[]>([]);
  const [corridors, setCorridors] = React.useState<BICorridor[]>([]);
  const [customers, setCustomers] = React.useState<BICustomers | null>(null);
  const [operations, setOperations] = React.useState<BIOperations | null>(null);
  const [risk, setRisk] = React.useState<BIRisk | null>(null);
  const [forecast, setForecast] = React.useState<BIForecast | null>(null);
  const [summary, setSummary] = React.useState<BIExecutiveSummary | null>(null);
  const [metricMode, setMetricMode] = React.useState<'remittances' | 'amount'>('remittances');
  const [sortBy, setSortBy] = React.useState<'commission' | 'count' | 'amount'>('commission');
  const [filters, setFilters] = React.useState({
    date_from: '',
    date_to: '',
    origin_country: '',
    destination_country: '',
    currency: '',
    status: '',
  });
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    loadBI();
  }, []);

  const query = React.useMemo(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (!value) return;
      params.set(key, key === 'date_to' ? `${value}T23:59:59` : key === 'date_from' ? `${value}T00:00:00` : value);
    });
    return params.toString() ? `?${params.toString()}` : '';
  }, [filters]);

  async function loadBI() {
    setIsLoading(true);
    setError(null);
    try {
      const [overviewData, trendData, corridorData, customerData, operationData, riskData, forecastData, summaryData] = await Promise.all([
        request<BIOverview>(`/bi/overview${query}`),
        request<BITrendPoint[]>(`/bi/trends${query}`),
        request<BICorridor[]>(`/bi/corridors${query}`),
        request<BICustomers>(`/bi/customers${query}`),
        request<BIOperations>(`/bi/operations${query}`),
        request<BIRisk>(`/bi/risk${query}`),
        request<BIForecast>('/bi/forecast'),
        request<BIExecutiveSummary>(`/bi/executive-summary${query}`),
      ]);
      setOverview(overviewData);
      setTrends(trendData);
      setCorridors(corridorData);
      setCustomers(customerData);
      setOperations(operationData);
      setRisk(riskData);
      setForecast(forecastData);
      setSummary(summaryData);
    } catch {
      setError('No se pudo cargar Inteligencia de negocio. Verifica permisos y disponibilidad del backend.');
    } finally {
      setIsLoading(false);
    }
  }

  async function downloadBiCsv(kind: 'kpis' | 'corridors') {
    const token = window.localStorage.getItem(tokenStorageKey);
    const response = await fetch(`${apiBaseUrl}/bi/exports/${kind}.csv${query}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      setError('No se pudo exportar el CSV con los filtros actuales.');
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = kind === 'kpis' ? 'fiducia-kpis.csv' : 'fiducia-corredores.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  }

  if (isLoading) return <section className="panel text-sm text-slate-600">Cargando inteligencia de negocio...</section>;
  if (error) return <StatusMessage message={error} type="error" />;

  const current = overview?.current ?? {};
  const changes = overview?.changes ?? {};
  const sortedCorridors = [...corridors].sort((a, b) => {
    if (sortBy === 'count') return b.remittance_count - a.remittance_count;
    if (sortBy === 'amount') return Number(b.total_amount_usd_equivalent) - Number(a.total_amount_usd_equivalent);
    return Number(b.commission_revenue_usd_equivalent) - Number(a.commission_revenue_usd_equivalent);
  });
  const trendBars = trends.map((item) => ({
    label: item.period,
    value: metricMode === 'remittances' ? item.remittances : Number(item.amount_usd_equivalent),
    detail: metricMode === 'remittances' ? `${item.remittances} remesas` : `USD ${formatMoney(item.amount_usd_equivalent)}`,
  }));
  const revenueBars = trends.map((item) => ({
    label: item.period,
    value: Number(item.commission_revenue_usd_equivalent),
    detail: `USD ${formatMoney(item.commission_revenue_usd_equivalent)}`,
  }));

  return (
    <div className="grid gap-6">
      <section className="panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
              <BarChart3 size={20} />
            </div>
            <div>
              <h1 className="section-title">Inteligencia de negocio</h1>
              <p className="text-sm text-slate-500">Indicadores y analitica ejecutiva</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="secondary-button" type="button" onClick={() => downloadBiCsv('kpis')}>
              Exportar KPIs
            </button>
            <button className="secondary-button" type="button" onClick={() => downloadBiCsv('corridors')}>
              Exportar corredores
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-3 md:grid-cols-6">
          <TextInput label="Desde" type="date" value={filters.date_from} onChange={(value) => setFilters({ ...filters, date_from: value })} required={false} />
          <TextInput label="Hasta" type="date" value={filters.date_to} onChange={(value) => setFilters({ ...filters, date_to: value })} required={false} />
          <SelectInput
            label="Origen"
            value={filters.origin_country}
            onChange={(value) => setFilters({ ...filters, origin_country: value })}
            options={[
              { value: '', label: 'Todos' },
              { value: 'Estados Unidos', label: 'Estados Unidos' },
              { value: 'Guatemala', label: 'Guatemala' },
            ]}
          />
          <SelectInput
            label="Destino"
            value={filters.destination_country}
            onChange={(value) => setFilters({ ...filters, destination_country: value })}
            options={[
              { value: '', label: 'Todos' },
              { value: 'Guatemala', label: 'Guatemala' },
              { value: 'Estados Unidos', label: 'Estados Unidos' },
            ]}
          />
          <SelectInput
            label="Moneda"
            value={filters.currency}
            onChange={(value) => setFilters({ ...filters, currency: value })}
            options={[
              { value: '', label: 'Todas' },
              { value: 'USD', label: 'USD' },
              { value: 'GTQ', label: 'GTQ' },
            ]}
          />
          <div className="flex items-end">
            <button className="primary-button w-full" type="button" onClick={loadBI}>
              Aplicar
            </button>
          </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-4">
        <ExecutiveMetric label="Remesas" value={String(current.total_remittances ?? 0)} change={changes.total_remittances?.percentage_change} />
        <ExecutiveMetric label="Monto movilizado" value={`USD ${formatMaybeMoney(current.total_amount_usd_equivalent)}`} change={changes.total_amount_usd_equivalent?.percentage_change} />
        <ExecutiveMetric label="Ingresos por comision" value={`USD ${formatMaybeMoney(current.total_commission_revenue_usd_equivalent)}`} change={changes.total_commission_revenue_usd_equivalent?.percentage_change} />
        <ExecutiveMetric label="Ticket promedio" value={`USD ${formatMaybeMoney(current.average_ticket_usd_equivalent)}`} change={changes.average_ticket_usd_equivalent?.percentage_change} />
      </section>

      <section className="grid gap-3 md:grid-cols-4">
        <Metric label="Clientes activos" value={String(current.active_clients ?? 0)} />
        <Metric label="Tasa de finalizacion" value={formatPercentValue(current.completion_rate)} />
        <Metric label="Remesas en revision" value={String(operations?.review_required ?? 0)} />
        <Metric label="Corredores activos" value={String(current.active_corridors ?? 0)} />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <AnalyticsPanel title="Tendencia principal">
          <div className="mb-4 flex gap-2">
            <button className={metricMode === 'remittances' ? 'nav-button-active' : 'nav-button'} type="button" onClick={() => setMetricMode('remittances')}>
              Remesas
            </button>
            <button className={metricMode === 'amount' ? 'nav-button-active' : 'nav-button'} type="button" onClick={() => setMetricMode('amount')}>
              Monto
            </button>
          </div>
          <SimpleBarChart items={trendBars} />
        </AnalyticsPanel>

        <AnalyticsPanel title="Ingresos por comision">
          <SimpleBarChart items={revenueBars} />
          <div className="mt-5">
            <MiniList
              title="Top corredores por revenue"
              items={sortedCorridors.slice(0, 3).map((item) => `${item.corridor}: USD ${formatMoney(item.commission_revenue_usd_equivalent)}`)}
            />
          </div>
        </AnalyticsPanel>
      </section>

      <AnalyticsPanel title="Indicadores destacados">
        <div className="grid gap-3 md:grid-cols-2">
          {(summary?.highlights ?? []).map((item) => (
            <div className="rounded-lg border border-slate-200 bg-white p-4" key={item.code}>
              <p className={item.priority === 'ATTENTION' ? 'text-sm font-semibold text-amber-700' : 'text-sm font-semibold text-fiducia-teal'}>
                {item.priority}
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">{item.message}</p>
            </div>
          ))}
        </div>
      </AnalyticsPanel>

      <AnalyticsPanel title="Corredores">
        <div className="mb-4 max-w-xs">
          <SelectInput
            label="Ordenar por"
            value={sortBy}
            onChange={(value) => setSortBy(value as 'commission' | 'count' | 'amount')}
            options={[
              { value: 'commission', label: 'Ingresos por comision' },
              { value: 'count', label: 'Volumen de remesas' },
              { value: 'amount', label: 'Monto movilizado' },
            ]}
          />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-slate-500">
              <tr>
                <th className="py-2 pr-3">Corredor</th>
                <th className="py-2 pr-3">Remesas</th>
                <th className="py-2 pr-3">Monto</th>
                <th className="py-2 pr-3">Ticket</th>
                <th className="py-2 pr-3">Revenue</th>
                <th className="py-2 pr-3">Finalizacion</th>
                <th className="py-2 pr-3">Riesgo alto</th>
              </tr>
            </thead>
            <tbody>
              {sortedCorridors.map((item) => (
                <tr className="border-t border-slate-100" key={item.corridor}>
                  <td className="py-2 pr-3 font-semibold text-fiducia-navy">{item.corridor}</td>
                  <td className="py-2 pr-3">{item.remittance_count}</td>
                  <td className="py-2 pr-3">USD {formatMoney(item.total_amount_usd_equivalent)}</td>
                  <td className="py-2 pr-3">USD {formatMaybeMoney(item.average_ticket_usd_equivalent)}</td>
                  <td className="py-2 pr-3">USD {formatMoney(item.commission_revenue_usd_equivalent)}</td>
                  <td className="py-2 pr-3">{formatPercentValue(item.completion_rate)}</td>
                  <td className="py-2 pr-3">{formatPercentValue(item.risk_distribution.find((riskItem) => riskItem.risk_band === 'HIGH')?.share)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AnalyticsPanel>

      <section className="grid gap-6 lg:grid-cols-3">
        <AnalyticsPanel title="Clientes">
          <MiniList
            title="Agregado"
            items={[
              `Activos: ${customers?.active_clients ?? 0}`,
              `Nuevos: ${customers?.new_clients ?? 0}`,
              `Recurrentes: ${customers?.returning_clients ?? 0}`,
              `Remesas por cliente: ${formatMaybeRatio(customers?.remittances_per_client)}`,
              `Repeat sender rate: ${formatPercentValue(customers?.repeat_sender_rate)}`,
            ]}
          />
        </AnalyticsPanel>
        <AnalyticsPanel title="Operaciones">
          <SimpleBarChart items={(operations?.status_distribution ?? []).map((item) => ({ label: item.label, value: item.count, detail: String(item.count) }))} />
        </AnalyticsPanel>
        <AnalyticsPanel title="Riesgo agregado">
          <SimpleBarChart items={(risk?.risk_distribution ?? []).map((item) => ({ label: item.label, value: item.count, detail: `${item.count} (${formatPercentValue(item.share)})` }))} />
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <Metric label="Score promedio" value={formatMaybeRatio(risk?.average_final_risk_score)} />
            <Metric label="Revisiones" value={String(risk?.review_count ?? 0)} />
          </div>
        </AnalyticsPanel>
      </section>

      <AnalyticsPanel title="Perspectiva proximas semanas">
        <div className="grid gap-3 md:grid-cols-5">
          <Metric label="Modelo" value={forecast?.model_version ?? 'N/D'} />
          <Metric label="Estado" value={forecast?.go_decision ?? 'N/D'} />
          <Metric label="Horizonte" value={`${forecast?.horizon ?? 4} semanas`} />
          <Metric label="Volumen 4s" value={formatMaybeMoney(forecast?.next_4_weeks_count)} />
          <Metric label="Monto 4s" value={`USD ${formatMaybeMoney(forecast?.next_4_weeks_amount_usd)}`} />
        </div>
        <p className="mt-4 text-sm leading-6 text-slate-500">
          Forecast experimental/conditional. Se muestra como perspectiva de planificacion y no modifica decisiones de riesgo.
        </p>
      </AnalyticsPanel>
    </div>
  );
}

function RiskIntelligenceView() {
  const [modelInfo, setModelInfo] = React.useState<RiskModelInfo | null>(null);
  const [engineInfo, setEngineInfo] = React.useState<RiskEngineInfo | null>(null);
  const [dashboard, setDashboard] = React.useState<RiskDashboardMetrics | null>(null);
  const [metrics, setMetrics] = React.useState<RiskMetrics | null>(null);
  const [prediction, setPrediction] = React.useState<RiskPrediction | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPredicting, setIsPredicting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let isMounted = true;
    async function loadRisk() {
      setIsLoading(true);
      setError(null);
      try {
        const [infoData, engineData, dashboardData] = await Promise.all([
          request<RiskModelInfo>('/risk/ml/model-info'),
          request<RiskEngineInfo>('/risk/engine-info'),
          request<RiskDashboardMetrics>('/risk/dashboard'),
        ]);
        const metricsData = infoData.available ? await request<RiskMetrics>('/risk/ml/metrics') : null;
        if (!isMounted) return;
        setModelInfo(infoData);
        setEngineInfo(engineData);
        setDashboard(dashboardData);
        setMetrics(metricsData);
      } catch {
        if (isMounted) setError('No se pudo cargar inteligencia de riesgo. Verifica permisos y artefactos del modelo.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadRisk();
    return () => {
      isMounted = false;
    };
  }, []);

  async function evaluateExample() {
    setIsPredicting(true);
    setPrediction(null);
    try {
      const result = await request<RiskPrediction>('/risk/ml/predict', {
        method: 'POST',
        body: JSON.stringify({ features: sampleRiskFeatures }),
      });
      setPrediction(result);
    } catch {
      setError('No se pudo evaluar la observacion de ejemplo. Revisa que el modelo este disponible.');
    } finally {
      setIsPredicting(false);
    }
  }

  if (isLoading) return <section className="panel text-sm text-slate-600">Cargando inteligencia de riesgo...</section>;
  if (error) return <StatusMessage message={error} type="error" />;

  const selected = metrics?.comparison.find((item) => item.model === metrics.selected_model);
  const matrix = selected?.test.confusion_matrix ?? [];

  return (
    <div className="grid gap-6">
      <section className="panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
              <ShieldCheck size={20} />
            </div>
            <div>
              <h1 className="section-title">Inteligencia de riesgo</h1>
              <p className="text-sm text-slate-500">Motor de senales para apoyar revision interna.</p>
            </div>
          </div>
          <button className="primary-button" type="button" onClick={evaluateExample} disabled={isPredicting || !modelInfo?.available}>
            {isPredicting ? 'Evaluando...' : 'Evaluar ejemplo'}
          </button>
        </div>
        {modelInfo?.available ? (
          <div className="mt-6 grid gap-3 md:grid-cols-6">
            <Metric label="Risk Engine" value={engineInfo?.version ?? 'N/D'} />
            <Metric label="Modelo ML" value={modelInfo.model_version ?? 'N/D'} />
            <Metric label="PR-AUC" value={selected ? formatRatio(selected.test.pr_auc) : 'N/D'} />
            <Metric label="Recall" value={selected ? formatRatio(selected.test.recall) : 'N/D'} />
            <Metric label="Precision" value={selected ? formatRatio(selected.test.precision) : 'N/D'} />
            <Metric label="Threshold" value={modelInfo.threshold?.toString() ?? 'N/D'} />
          </div>
        ) : (
          <EmptyState text={modelInfo?.message ?? 'Modelo no disponible.'} />
        )}
      </section>

      {prediction ? (
        <section className="panel">
          <h2 className="section-title">Resultado de ejemplo</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-4">
            <Metric label="Probabilidad ML" value={formatRatio(prediction.ml_probability)} />
            <Metric label="Clasificacion" value={prediction.classification_label} />
            <Metric label="Threshold" value={prediction.threshold.toString()} />
            <Metric label="Version" value={prediction.model_version} />
          </div>
          <p className="mt-4 text-sm text-slate-500">
            La salida es una probabilidad estimada de riesgo; no confirma fraude ni bloquea operaciones.
          </p>
        </section>
      ) : null}

      <section className="panel">
        <h2 className="section-title">Operacion del motor</h2>
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          <Metric label="Evaluaciones" value={(dashboard?.total_assessments ?? 0).toString()} />
          <Metric label="Pendientes" value={(dashboard?.pending_review ?? 0).toString()} />
          <Metric label="Riesgo medio" value={(dashboard?.medium_risk ?? 0).toString()} />
          <Metric label="Riesgo alto" value={(dashboard?.high_risk ?? 0).toString()} />
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <MiniList
            title="Promedios"
            items={[
              `Reglas: ${formatNullableScore(dashboard?.average_rule_score)}`,
              `ML: ${dashboard?.average_ml_probability == null ? 'N/D' : formatRatio(dashboard.average_ml_probability)}`,
              `Anomalia: ${formatNullableScore(dashboard?.average_anomaly_score)}`,
              `Final: ${formatNullableScore(dashboard?.average_final_risk_score)}`,
            ]}
          />
          <MiniList
            title="Versiones"
            items={[
              `Reglas: ${engineInfo?.rules_version ?? 'N/D'}`,
              `Anomalias: ${engineInfo?.anomaly_model_version ?? 'N/D'}`,
              `ML: ${engineInfo?.ml_model_version ?? 'N/D'}`,
            ]}
          />
          <MiniList
            title="Reglas frecuentes"
            items={(dashboard?.top_triggered_rules ?? []).map((item) => `${item.rule_code}: ${item.count}`)}
          />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <AnalyticsPanel title="Comparacion de modelos">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="py-2 pr-3">Modelo</th>
                  <th className="py-2 pr-3">Precision</th>
                  <th className="py-2 pr-3">Recall</th>
                  <th className="py-2 pr-3">F1</th>
                  <th className="py-2 pr-3">PR-AUC</th>
                  <th className="py-2 pr-3">Threshold</th>
                </tr>
              </thead>
              <tbody>
                {(metrics?.comparison ?? []).map((item) => (
                  <tr className="border-t border-slate-100" key={item.model}>
                    <td className="py-2 pr-3 font-semibold text-fiducia-navy">{item.model}</td>
                    <td className="py-2 pr-3">{formatRatio(item.test.precision)}</td>
                    <td className="py-2 pr-3">{formatRatio(item.test.recall)}</td>
                    <td className="py-2 pr-3">{formatRatio(item.test.f1)}</td>
                    <td className="py-2 pr-3">{formatRatio(item.test.pr_auc)}</td>
                    <td className="py-2 pr-3">{item.threshold}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </AnalyticsPanel>
        <AnalyticsPanel title="Variables relevantes">
          <SimpleBarChart
            items={(metrics?.feature_importance ?? []).slice(0, 8).map((item) => ({
              label: item.feature,
              value: Math.max(0.001, Math.abs(item.importance)),
              detail: item.importance.toFixed(4),
            }))}
          />
        </AnalyticsPanel>
        <AnalyticsPanel title="Matriz de confusion">
          <div className="grid max-w-sm grid-cols-2 gap-3 text-center text-sm">
            <Metric label="TN" value={(matrix[0]?.[0] ?? 0).toString()} />
            <Metric label="FP" value={(matrix[0]?.[1] ?? 0).toString()} />
            <Metric label="FN" value={(matrix[1]?.[0] ?? 0).toString()} />
            <Metric label="TP" value={(matrix[1]?.[1] ?? 0).toString()} />
          </div>
        </AnalyticsPanel>
        <AnalyticsPanel title="Uso previsto">
          <p className="text-sm leading-7 text-slate-600">
            El motor combina reglas, probabilidad ML y comportamiento atipico. Recomienda revision interna cuando corresponde,
            pero no confirma fraude ni bloquea operaciones de forma automatica.
          </p>
        </AnalyticsPanel>
      </section>
    </div>
  );
}

function describeRequestFailure(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 401) return 'sesion expirada o token invalido';
    if (error.status === 403) return 'permisos insuficientes para este perfil';
    return `backend respondio ${error.status} (${error.code})`;
  }
  if (error instanceof Error) return `${error.name}: ${error.message}`;
  return 'error de conexion no identificado';
}

function BlockchainView({ user, transactions }: { user: User; transactions: Transaction[] }) {
  const [info, setInfo] = React.useState<BlockchainInfo | null>(null);
  const [metrics, setMetrics] = React.useState<BlockchainMetrics | null>(null);
  const [blocks, setBlocks] = React.useState<BlockchainBlock[]>([]);
  const [validation, setValidation] = React.useState<BlockchainValidation | null>(null);
  const [selectedBlock, setSelectedBlock] = React.useState<BlockchainBlock | null>(null);
  const [remittanceId, setRemittanceId] = React.useState(transactions[0]?.id.toString() ?? '');
  const [history, setHistory] = React.useState<BlockchainBlock[]>([]);
  const [verification, setVerification] = React.useState<BlockchainVerification | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isVerifying, setIsVerifying] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const isAdmin = user.role.name === 'ADMIN';

  React.useEffect(() => {
    let isMounted = true;
    async function loadBlockchain() {
      setIsLoading(true);
      setError(null);
      try {
        const overview = await request<BlockchainOverview>('/blockchain/overview');
        if (!isMounted) return;
        setInfo(overview.info);
        setMetrics(overview.metrics);
        setBlocks(overview.blocks);
        setSelectedBlock(overview.blocks[overview.blocks.length - 1] ?? null);
        if (isAdmin) {
          try {
            const validationData = await request<BlockchainValidation>('/blockchain/validate');
            if (isMounted) setValidation(validationData);
          } catch (validationError) {
            setError(`No se pudo cargar la validacion completa. Detalle: ${describeRequestFailure(validationError)}`);
          }
        }
      } catch (loadError) {
        if (isMounted) setError(`No se pudo cargar la trazabilidad blockchain. Detalle: ${describeRequestFailure(loadError)}`);
      }
      if (isMounted) setIsLoading(false);
    }
    loadBlockchain();
    return () => {
      isMounted = false;
    };
  }, [isAdmin]);

  async function verifyRemittance() {
    const id = Number(remittanceId);
    if (!Number.isInteger(id) || id <= 0) {
      setError('Ingresa un identificador de remesa valido.');
      return;
    }
    setIsVerifying(true);
    setError(null);
    try {
      const [verificationData, historyData] = await Promise.all([
        request<BlockchainVerification>(`/blockchain/verify/${id}`),
        request<BlockchainBlock[]>(`/blockchain/transactions/${id}/history`),
      ]);
      setVerification(verificationData);
      setHistory(historyData);
    } catch {
      setVerification(null);
      setHistory([]);
      setError('No se encontro trazabilidad para esa remesa o tu perfil no tiene acceso.');
    } finally {
      setIsVerifying(false);
    }
  }

  if (isLoading) return <section className="panel text-sm text-slate-600">Cargando trazabilidad blockchain...</section>;
  if (error && blocks.length === 0) return <StatusMessage message={error} type="error" />;

  return (
    <div className="grid gap-6">
      {error ? <StatusMessage message={error} type="error" /> : null}
      <section className="panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
              <ShieldCheck size={20} />
            </div>
            <div>
              <h1 className="section-title">Trazabilidad blockchain</h1>
              <p className="text-sm text-slate-500">Evidencia verificable de eventos operativos sin exponer datos personales.</p>
            </div>
          </div>
          <span className={info?.chain_valid ? 'rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700' : 'rounded-full bg-red-50 px-3 py-1 text-sm font-semibold text-red-700'}>
            {info?.chain_valid ? 'Cadena integra' : 'Revision requerida'}
          </span>
        </div>
        <div className="mt-6 grid gap-3 md:grid-cols-5">
          <Metric label="Bloques" value={(metrics?.total_blocks ?? 0).toString()} />
          <Metric label="Evidencias" value={(metrics?.total_evidence ?? 0).toString()} />
          <Metric label="Dificultad" value={(info?.difficulty ?? 0).toString()} />
          <Metric label="Algoritmo" value={info?.hash_algorithm ?? 'N/D'} />
          <Metric label="Ultimo bloque" value={`#${Math.max(0, (info?.total_blocks ?? 1) - 1)}`} />
        </div>
        <p className="mt-4 break-all text-xs leading-6 text-slate-500">Ultimo hash: {info?.last_block_hash ?? 'N/D'}</p>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <AnalyticsPanel title="Explorador de bloques">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-500">
                <tr>
                  <th className="py-2 pr-3">Bloque</th>
                  <th className="py-2 pr-3">Evento</th>
                  <th className="py-2 pr-3">Referencia</th>
                  <th className="py-2 pr-3">Hash</th>
                  <th className="py-2 pr-3">Detalle</th>
                </tr>
              </thead>
              <tbody>
                {blocks.map((block) => (
                  <tr className="border-t border-slate-100" key={block.block_index}>
                    <td className="py-2 pr-3 font-semibold text-fiducia-navy">#{block.block_index}</td>
                    <td className="py-2 pr-3">{blockchainEventLabel(block.event_type)}</td>
                    <td className="py-2 pr-3">{block.entity_reference}</td>
                    <td className="py-2 pr-3 font-mono">{shortHash(block.block_hash)}</td>
                    <td className="py-2 pr-3">
                      <button className="icon-button" type="button" onClick={() => setSelectedBlock(block)} title="Ver bloque">
                        <Eye size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </AnalyticsPanel>

        <AnalyticsPanel title="Detalle del bloque">
          {selectedBlock ? (
            <div className="space-y-3">
              <SummaryRow label="Indice" value={`#${selectedBlock.block_index}`} />
              <SummaryRow label="Evento" value={blockchainEventLabel(selectedBlock.event_type)} />
              <SummaryRow label="Esquema" value={selectedBlock.schema_version} />
              <SummaryRow label="Nonce" value={selectedBlock.nonce.toString()} />
              <SummaryRow label="Minado" value={`${selectedBlock.mining_time_ms} ms`} />
              <p className="break-all rounded-md border border-slate-200 bg-slate-50 p-3 font-mono text-xs text-slate-600">
                Evidencia: {selectedBlock.evidence_hash}
              </p>
              <p className="break-all rounded-md border border-slate-200 bg-slate-50 p-3 font-mono text-xs text-slate-600">
                Bloque: {selectedBlock.block_hash}
              </p>
            </div>
          ) : (
            <EmptyState text="Selecciona un bloque para revisar su evidencia." />
          )}
        </AnalyticsPanel>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <AnalyticsPanel title="Verificacion por remesa">
          <div className="grid gap-3">
            <TextInput label="ID interno de remesa" value={remittanceId} onChange={setRemittanceId} placeholder="Ej. 1" />
            <button className="primary-button inline-flex items-center justify-center gap-2" type="button" onClick={verifyRemittance} disabled={isVerifying}>
              <Search size={16} />
              {isVerifying ? 'Verificando...' : 'Verificar evidencia'}
            </button>
          </div>
          {verification ? (
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <Metric label="Estado" value={verification.status} />
              <Metric label="Evidencias validas" value={verification.verified.toString()} />
              <Metric label="Alertas" value={verification.mismatches.length.toString()} />
            </div>
          ) : null}
          {history.length > 0 ? (
            <div className="mt-5 space-y-3">
              {history.map((block) => (
                <div className="rounded-md border border-slate-200 bg-white p-3" key={block.block_index}>
                  <p className="text-sm font-semibold text-fiducia-navy">#{block.block_index} · {blockchainEventLabel(block.event_type)}</p>
                  <p className="mt-1 break-all font-mono text-xs text-slate-500">{shortHash(block.block_hash)}</p>
                </div>
              ))}
            </div>
          ) : null}
        </AnalyticsPanel>

        <AnalyticsPanel title="Integridad de cadena">
          {isAdmin && validation ? (
            <div className="space-y-3">
              <SummaryRow label="Bloques revisados" value={validation.blocks_checked.toString()} />
              <SummaryRow label="Resultado" value={validation.valid ? 'Cadena valida' : 'Inconsistencias detectadas'} />
              {validation.errors.length > 0 ? (
                <MiniList title="Alertas" items={validation.errors.map((item) => `Bloque #${item.block_index}: ${item.code}`)} />
              ) : (
                <EmptyState text="No se detectaron alteraciones en hashes, enlaces ni prueba de trabajo." />
              )}
            </div>
          ) : (
            <p className="text-sm leading-7 text-slate-600">
              La validacion completa de la cadena esta reservada para administradores. Los analistas pueden consultar bloques,
              historial y verificacion de remesas como evidencia de apoyo.
            </p>
          )}
          <div className="mt-5 grid gap-3">
            {['Evento operativo', 'Evidencia canonica', 'Hash SHA-256', 'Bloque enlazado', 'Verificacion'].map((step, index) => (
              <div className="flex items-center gap-3 rounded-md border border-slate-200 bg-slate-50 p-3" key={step}>
                <CheckCircle2 className="text-fiducia-teal" size={18} />
                <span className="text-sm font-semibold text-fiducia-navy">{index + 1}. {step}</span>
              </div>
            ))}
          </div>
        </AnalyticsPanel>
      </section>
    </div>
  );
}

function ForecastingView() {
  const [summary, setSummary] = React.useState<ForecastSummary | null>(null);
  const [volume, setVolume] = React.useState<ForecastResponse | null>(null);
  const [amount, setAmount] = React.useState<ForecastResponse | null>(null);
  const [corridors, setCorridors] = React.useState<ForecastCorridor[]>([]);
  const [horizon, setHorizon] = React.useState('8');
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    loadForecasts(horizon);
  }, [horizon]);

  async function loadForecasts(selectedHorizon: string) {
    setIsLoading(true);
    setError(null);
    try {
      const [summaryData, volumeData, amountData, corridorData] = await Promise.all([
        request<ForecastSummary>('/forecasting/summary'),
        request<ForecastResponse>(`/forecasting/volume?horizon=${selectedHorizon}`),
        request<ForecastResponse>(`/forecasting/amount?horizon=${selectedHorizon}`),
        request<ForecastCorridor[]>('/forecasting/corridors?horizon=4'),
      ]);
      setSummary(summaryData);
      setVolume(volumeData);
      setAmount(amountData);
      setCorridors(corridorData);
    } catch {
      setError('No se pudo cargar la analitica predictiva. Verifica que los artefactos de forecasting existan.');
    } finally {
      setIsLoading(false);
    }
  }

  if (isLoading) return <section className="panel text-sm text-slate-600">Cargando analitica predictiva...</section>;
  if (error) return <StatusMessage message={error} type="error" />;

  const volumeBars = [
    ...(volume?.historical ?? []).slice(-8).map((item) => ({ label: shortPeriod(item.period), value: Number(item.value), detail: `Obs. ${formatMoney(item.value)}` })),
    ...(volume?.forecast ?? []).map((item) => ({ label: shortPeriod(item.period), value: Number(item.predicted), detail: `Est. ${formatMoney(item.predicted)}` })),
  ];
  const amountBars = [
    ...(amount?.historical ?? []).slice(-8).map((item) => ({ label: shortPeriod(item.period), value: Number(item.value), detail: `USD ${formatMoney(item.value)}` })),
    ...(amount?.forecast ?? []).map((item) => ({ label: shortPeriod(item.period), value: Number(item.predicted), detail: `USD ${formatMoney(item.predicted)}` })),
  ];

  return (
    <div className="grid gap-6">
      <section className="panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fiducia-teal text-white">
              <BarChart3 size={20} />
            </div>
            <div>
              <h1 className="section-title">Analitica predictiva</h1>
              <p className="text-sm text-slate-500">Pronostico experimental basado en datos sinteticos agregados.</p>
            </div>
          </div>
          <SelectInput
            label="Horizonte"
            value={horizon}
            onChange={setHorizon}
            options={[
              { value: '4', label: '4 semanas' },
              { value: '8', label: '8 semanas' },
              { value: '12', label: '12 semanas' },
            ]}
          />
        </div>
        <div className="mt-6 grid gap-3 md:grid-cols-5">
          <Metric label="Modelo" value={summary?.model_version ?? 'N/D'} />
          <Metric label="Decision datos" value={summary?.go_decision ?? 'N/D'} />
          <Metric label="Semanas" value={(summary?.weeks_covered ?? 0).toString()} />
          <Metric label="Drift" value={summary?.drift_status ?? 'N/D'} />
          <Metric label="WAPE volumen" value={summary ? formatRatio(summary.count_wape) : 'N/D'} />
        </div>
        <p className="mt-4 text-sm leading-6 text-slate-500">
          Las cifras son estimaciones para planificacion operativa. No modifican riesgo, pagos ni decisiones sobre remesas.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <AnalyticsPanel title="Pronostico de volumen">
          <div className="grid gap-3 md:grid-cols-2">
            <Metric label="Proximas 4 semanas" value={summary ? formatMoney(summary.next_4_weeks_count) : 'N/D'} />
            <Metric label="Modelo seleccionado" value={volume?.selected_model ?? 'N/D'} />
          </div>
          <div className="mt-5">
            <SimpleBarChart items={volumeBars} />
          </div>
          <ForecastTable forecast={volume?.forecast ?? []} valuePrefix="" />
        </AnalyticsPanel>

        <AnalyticsPanel title="Pronostico de monto">
          <div className="grid gap-3 md:grid-cols-2">
            <Metric label="Proximas 4 semanas" value={summary ? `USD ${formatMoney(summary.next_4_weeks_amount_usd)}` : 'N/D'} />
            <Metric label="WAPE monto" value={summary ? formatRatio(summary.amount_wape) : 'N/D'} />
          </div>
          <div className="mt-5">
            <SimpleBarChart items={amountBars} />
          </div>
          <ForecastTable forecast={amount?.forecast ?? []} valuePrefix="USD " />
        </AnalyticsPanel>
      </section>

      <AnalyticsPanel title="Corredores principales">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-slate-500">
              <tr>
                <th className="py-2 pr-3">Corredor</th>
                <th className="py-2 pr-3">Historico</th>
                <th className="py-2 pr-3">Forecast 4s</th>
                <th className="py-2 pr-3">Monto forecast</th>
              </tr>
            </thead>
            <tbody>
              {corridors.map((item) => (
                <tr className="border-t border-slate-100" key={item.corridor}>
                  <td className="py-2 pr-3 font-semibold text-fiducia-navy">{item.corridor}</td>
                  <td className="py-2 pr-3">{item.historical_volume}</td>
                  <td className="py-2 pr-3">{formatMoney(item.forecast_volume_next_4w)}</td>
                  <td className="py-2 pr-3">USD {formatMoney(item.forecast_amount_usd_next_4w)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AnalyticsPanel>
    </div>
  );
}

function ForecastTable({ forecast, valuePrefix }: { forecast: ForecastPoint[]; valuePrefix: string }) {
  if (forecast.length === 0) return null;
  return (
    <div className="mt-5 overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-slate-500">
          <tr>
            <th className="py-2 pr-3">Periodo</th>
            <th className="py-2 pr-3">Estimado</th>
            <th className="py-2 pr-3">80%</th>
            <th className="py-2 pr-3">95%</th>
          </tr>
        </thead>
        <tbody>
          {forecast.map((item) => (
            <tr className="border-t border-slate-100" key={item.period}>
              <td className="py-2 pr-3">{shortPeriod(item.period)}</td>
              <td className="py-2 pr-3 font-semibold text-fiducia-navy">{valuePrefix}{formatMoney(item.predicted)}</td>
              <td className="py-2 pr-3">{valuePrefix}{formatMoney(item.lower_80 ?? 0)} - {valuePrefix}{formatMoney(item.upper_80 ?? 0)}</td>
              <td className="py-2 pr-3">{valuePrefix}{formatMoney(item.lower_95 ?? 0)} - {valuePrefix}{formatMoney(item.upper_95 ?? 0)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RiskReviewView({ showMessage }: { showMessage: (message: string, type: MessageType) => void }) {
  const [assessments, setAssessments] = React.useState<RiskAssessment[]>([]);
  const [selected, setSelected] = React.useState<RiskAssessment | null>(null);
  const [decision, setDecision] = React.useState('APPROVE');
  const [reason, setReason] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(true);
  const [isSaving, setIsSaving] = React.useState(false);

  React.useEffect(() => {
    loadAssessments();
  }, []);

  async function loadAssessments() {
    setIsLoading(true);
    try {
      const data = await request<RiskAssessment[]>('/risk/assessments');
      setAssessments(data);
      setSelected((current) => current ?? data[0] ?? null);
    } catch {
      showMessage('No se pudo cargar la cola de revision de riesgo.', 'error');
    } finally {
      setIsLoading(false);
    }
  }

  async function submitReview(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    if ((decision === 'ESCALATE' || decision === 'REJECT') && !reason.trim()) {
      showMessage('Agrega una justificacion para escalar o rechazar.', 'error');
      return;
    }
    setIsSaving(true);
    try {
      const updated = await request<RiskAssessment>(`/risk/assessments/${selected.id}/review`, {
        method: 'POST',
        body: JSON.stringify({ decision, reason: reason.trim() || null }),
      });
      setAssessments((items) => items.map((item) => (item.id === updated.id ? { ...item, ...updated } : item)));
      setSelected((current) => (current?.id === updated.id ? { ...current, ...updated } : current));
      setReason('');
      showMessage('Decision de riesgo registrada correctamente.', 'success');
    } catch {
      showMessage('No se pudo registrar la decision de riesgo.', 'error');
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) return <section className="panel text-sm text-slate-600">Cargando revision de riesgo...</section>;

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <section className="panel">
        <h1 className="section-title">Revision de riesgo</h1>
        {assessments.length === 0 ? (
          <EmptyState text="Aun no hay evaluaciones de riesgo registradas." />
        ) : (
          <div className="mt-5 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="py-2 pr-3">Remesa</th>
                  <th className="py-2 pr-3">Fecha</th>
                  <th className="py-2 pr-3">Monto</th>
                  <th className="py-2 pr-3">Final</th>
                  <th className="py-2 pr-3">Banda</th>
                  <th className="py-2 pr-3">Accion</th>
                  <th className="py-2 pr-3">Revision</th>
                </tr>
              </thead>
              <tbody>
                {assessments.map((assessment) => (
                  <tr
                    className={`cursor-pointer border-t border-slate-100 ${selected?.id === assessment.id ? 'bg-fiducia-mint/40' : ''}`}
                    key={assessment.id}
                    onClick={() => setSelected(assessment)}
                  >
                    <td className="py-2 pr-3 font-semibold text-fiducia-navy">{assessment.remittance_number ?? `#${assessment.remittance_id}`}</td>
                    <td className="py-2 pr-3">{formatDate(assessment.evaluated_at)}</td>
                    <td className="py-2 pr-3">{assessment.source_currency ?? ''} {formatMoney(assessment.source_amount ?? 0)}</td>
                    <td className="py-2 pr-3">{formatNullableScore(assessment.final_risk_score)}</td>
                    <td className="py-2 pr-3">{riskBandLabel(assessment.risk_band)}</td>
                    <td className="py-2 pr-3">{recommendedActionLabel(assessment.recommended_action)}</td>
                    <td className="py-2 pr-3">{reviewStatusLabel(assessment.review_status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="panel">
        <h2 className="section-title">Detalle de evaluacion</h2>
        {!selected ? (
          <EmptyState text="Selecciona una evaluacion para ver el detalle." />
        ) : (
          <div className="mt-5 space-y-5">
            <div className="grid gap-3 sm:grid-cols-3">
              <Metric label="Final" value={formatNullableScore(selected.final_risk_score)} />
              <Metric label="Banda" value={riskBandLabel(selected.risk_band)} />
              <Metric label="Accion" value={recommendedActionLabel(selected.recommended_action)} />
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <Metric label="Reglas" value={formatNullableScore(selected.rule_score)} />
              <Metric label="ML" value={selected.ml_probability == null ? 'N/D' : formatRatio(Number(selected.ml_probability))} />
              <Metric label="Anomalia" value={formatNullableScore(selected.anomaly_score)} />
            </div>
            <MiniList
              title="Reglas activadas"
              items={(selected.triggered_rules_json ?? []).map((rule) => `${rule.rule_code}: ${rule.reason}`)}
            />
            <MiniList title="Explicacion" items={selected.explanations_json ?? []} />
            <MiniList
              title="Versiones"
              items={[
                `Risk Engine: ${selected.risk_engine_version}`,
                `Reglas: ${selected.rules_version ?? 'N/D'}`,
                `ML: ${selected.ml_model_version ?? 'N/D'} / threshold ${selected.ml_threshold ?? 'N/D'}`,
                `Anomalias: ${selected.anomaly_model_version ?? 'N/D'}`,
              ]}
            />
            <form className="grid gap-3" onSubmit={submitReview}>
              <SelectInput
                label="Decision del analista"
                value={decision}
                onChange={setDecision}
                options={[
                  { value: 'APPROVE', label: 'Aprobar internamente' },
                  { value: 'ESCALATE', label: 'Escalar revision' },
                  { value: 'REJECT', label: 'Rechazar internamente' },
                ]}
              />
              <TextInput label="Justificacion" value={reason} onChange={setReason} placeholder="Comentario de revision" />
              <button className="primary-button" type="submit" disabled={isSaving}>
                {isSaving ? 'Guardando...' : 'Registrar decision'}
              </button>
            </form>
          </div>
        )}
      </section>
    </div>
  );
}

function BeneficiariesView({
  beneficiaries,
  corridors,
  relationships,
  onCreated,
  showMessage,
}: {
  beneficiaries: Beneficiary[];
  corridors: Corridor[];
  relationships: BeneficiaryRelationship[];
  onCreated: () => Promise<void>;
  showMessage: (message: string, type: MessageType) => void;
}) {
  const countryOptions = getCountryOptions(corridors);
  const [form, setForm] = React.useState({
    first_name: '',
    last_name: '',
    email: '',
    relationship: relationships[0]?.name ?? 'Padre / Madre',
    relationship_id: relationships[0]?.id?.toString() ?? '',
    relationship_other: '',
    country: 'Guatemala',
    currency: 'GTQ',
    city: '',
    department: 'Guatemala',
    municipality: 'Guatemala',
    delivery_method: 'BANK_DEPOSIT',
    bank_name: '',
    account_type: 'Ahorro',
    account_number: '',
    account_last_four: '',
  });
  const [isSaving, setIsSaving] = React.useState(false);

  React.useEffect(() => {
    if (!form.relationship_id && relationships.length > 0) {
      setForm((current) => ({
        ...current,
        relationship_id: relationships[0].id.toString(),
        relationship: relationships[0].name,
      }));
    }
  }, [form.relationship_id, relationships]);

  async function createBeneficiary(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    try {
      await request('/beneficiaries', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          relationship_id: form.relationship_id ? Number(form.relationship_id) : null,
          relationship_other: form.relationship_other || null,
          city: form.country === 'Guatemala' ? null : form.city,
          department: form.country === 'Guatemala' ? form.department : 'N/A',
          municipality: form.country === 'Guatemala' ? form.municipality : 'N/A',
          email: form.email || null,
          bank_name: form.bank_name || null,
          account_type: form.account_type || null,
          account_last_four: form.account_number ? form.account_number.slice(-4) : null,
        }),
      });
      setForm({
        first_name: '',
        last_name: '',
        email: '',
        relationship: relationships[0]?.name ?? 'Padre / Madre',
        relationship_id: relationships[0]?.id?.toString() ?? '',
        relationship_other: '',
        country: 'Guatemala',
        currency: 'GTQ',
        city: '',
        department: 'Guatemala',
        municipality: 'Guatemala',
        delivery_method: 'BANK_DEPOSIT',
        bank_name: '',
        account_type: 'Ahorro',
        account_number: '',
        account_last_four: '',
      });
      await onCreated();
      showMessage('Beneficiario creado correctamente.', 'success');
    } catch (error) {
      const code = error instanceof ApiRequestError ? error.code : 'REQUEST_FAILED';
      showMessage(getBeneficiaryErrorMessage(code), 'error');
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="panel">
        <h2 className="section-title">Nuevo beneficiario</h2>
        <form className="mt-5 grid gap-4" onSubmit={createBeneficiary}>
          <div className="grid gap-4 sm:grid-cols-2">
            <TextInput label="Nombre" value={form.first_name} onChange={(value) => setForm({ ...form, first_name: value })} />
            <TextInput label="Apellido" value={form.last_name} onChange={(value) => setForm({ ...form, last_name: value })} />
          </div>
          <TextInput
            label="Correo de cuenta FIDUCIA del beneficiario"
            type="email"
            value={form.email}
            onChange={(value) => setForm({ ...form, email: value })}
            placeholder="beneficiario@example.com"
            required={false}
          />
          <SelectInput
            label="Relacion"
            value={form.relationship_id}
            options={relationships.map((relationship) => ({ value: relationship.id.toString(), label: relationship.name }))}
            onChange={(value) => {
              const selected = relationships.find((relationship) => relationship.id.toString() === value);
              setForm({ ...form, relationship_id: value, relationship: selected?.name ?? form.relationship });
            }}
          />
          {form.relationship === 'Otro' ? (
            <TextInput
              label="Descripcion de relacion"
              value={form.relationship_other}
              onChange={(value) => setForm({ ...form, relationship_other: value })}
              required={false}
            />
          ) : null}
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectInput
              label="Pais del beneficiario"
              value={form.country}
              options={countryOptions}
              onChange={(value) => {
                const selected = countryOptions.find((country) => country.value === value);
                setForm({ ...form, country: value, currency: selected?.currency ?? 'GTQ', city: '', department: '', municipality: '' });
              }}
            />
            <TextInput label="Moneda" value={form.currency} onChange={(value) => setForm({ ...form, currency: value.toUpperCase() })} maxLength={3} />
          </div>
          {form.country === 'Guatemala' ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <SelectInput
                label="Departamento"
                value={form.department}
                options={guatemalaDepartmentOptions()}
                onChange={(value) => setForm({ ...form, department: value, municipality: guatemalaMunicipalityOptions(value)[0]?.value ?? '' })}
              />
              <SelectInput
                label="Municipio"
                value={form.municipality}
                options={guatemalaMunicipalityOptions(form.department)}
                onChange={(value) => setForm({ ...form, municipality: value })}
              />
            </div>
          ) : (
            <TextInput label="Ciudad" value={form.city} onChange={(value) => setForm({ ...form, city: value })} />
          )}
          <SelectInput label="Metodo de entrega" value={form.delivery_method} options={deliveryMethods} onChange={(value) => setForm({ ...form, delivery_method: value })} />
          <div className="grid gap-4 sm:grid-cols-3">
            <TextInput label="Banco" value={form.bank_name} onChange={(value) => setForm({ ...form, bank_name: value })} />
            <SelectInput label="Tipo de cuenta" value={form.account_type} options={accountTypeOptions} onChange={(value) => setForm({ ...form, account_type: value })} />
            <TextInput
              label="Numero de cuenta"
              value={form.account_number}
              maxLength={30}
              onChange={(value) => setForm({ ...form, account_number: value.replace(/\D/g, '') })}
            />
          </div>
          <button className="primary-button inline-flex items-center justify-center gap-2" type="submit" disabled={isSaving}>
            <Plus size={18} />
            {isSaving ? 'Guardando...' : 'Crear beneficiario'}
          </button>
        </form>
      </section>
      <section className="panel">
        <h2 className="section-title">Mis beneficiarios</h2>
        <div className="mt-4 grid gap-3">
          {beneficiaries.length === 0 ? <EmptyState text="Aun no tienes beneficiarios registrados." /> : null}
          {beneficiaries.map((beneficiary) => (
            <div className="rounded-lg border border-slate-200 p-4" key={beneficiary.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-fiducia-navy">
                    {beneficiary.first_name} {beneficiary.last_name}
                  </p>
                  <p className="text-sm text-slate-600">
                    {beneficiary.relationship} - {beneficiary.country} ({beneficiary.currency})
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {beneficiary.email
                      ? beneficiary.beneficiary_user_id
                        ? `Vinculado a ${beneficiary.email}`
                        : `Correo pendiente de vincular: ${beneficiary.email}`
                      : 'Sin cuenta FIDUCIA vinculada'}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {beneficiary.department}, {beneficiary.municipality} - {deliveryLabel(beneficiary.delivery_method)}
                  </p>
                </div>
                <span className="rounded-full bg-fiducia-mint px-3 py-1 text-xs font-semibold text-fiducia-teal">
                  {beneficiary.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function NewRemittanceView({
  beneficiaries,
  fundingSources,
  corridors,
  showMessage,
  onCreated,
  onManageBeneficiaries,
  onManageFunding,
}: {
  beneficiaries: Beneficiary[];
  fundingSources: FundingSource[];
  corridors: Corridor[];
  showMessage: (message: string, type: MessageType) => void;
  onCreated: (transaction: Transaction) => Promise<void>;
  onManageBeneficiaries: () => void;
  onManageFunding: () => void;
}) {
  const originOptions = Array.from(new Set(corridors.map((corridor) => corridor.origin_country))).map((country) => ({
    value: country,
    label: country,
  }));
  const initialOrigin = originOptions[0]?.value ?? 'Estados Unidos';
  const initialDestinations = corridors.filter((corridor) => corridor.origin_country === initialOrigin);
  const initialCorridor = initialDestinations[0];
  const [form, setForm] = React.useState({
    beneficiary_id: '',
    origin_country: initialOrigin,
    destination_country: initialCorridor?.destination_country ?? 'Guatemala',
    amount: '',
    currency: initialCorridor?.origin_currency ?? 'USD',
    funding_source_id: '',
    payment_method: 'BANK_TRANSFER',
    delivery_method: 'BANK_DEPOSIT',
  });
  const [simulation, setSimulation] = React.useState<Simulation | null>(null);
  const [isSimulating, setIsSimulating] = React.useState(false);
  const [isCreating, setIsCreating] = React.useState(false);

  const destinationOptions = corridors
    .filter((corridor) => corridor.origin_country === form.origin_country)
    .map((corridor) => ({ value: corridor.destination_country, label: corridor.destination_country }));
  const selectedCorridor = corridors.find(
    (corridor) => corridor.origin_country === form.origin_country && corridor.destination_country === form.destination_country,
  );
  const requiredFundingCurrency = selectedCorridor?.origin_currency ?? form.currency;
  const acceptsGtqPayment = selectedCorridor?.origin_currency === 'USD' && selectedCorridor.destination_currency === 'GTQ';
  const compatibleFundingCurrencies = acceptsGtqPayment ? ['USD', 'GTQ'] : [requiredFundingCurrency];
  const compatibleBeneficiaries = beneficiaries.filter((beneficiary) => beneficiary.country === form.destination_country);
  const compatibleFundingSources = fundingSources.filter((source) => compatibleFundingCurrencies.includes(source.currency));

  React.useEffect(() => {
    const corridor = corridors.find(
      (item) => item.origin_country === form.origin_country && item.destination_country === form.destination_country,
    );
    const compatible = beneficiaries.filter((beneficiary) => beneficiary.country === form.destination_country);
    setForm((current) => ({
      ...current,
      currency: corridor?.origin_currency ?? current.currency,
      beneficiary_id: compatible.some((beneficiary) => beneficiary.id.toString() === current.beneficiary_id)
        ? current.beneficiary_id
        : compatible[0]?.id.toString() ?? '',
      funding_source_id: fundingSources.some((source) => {
        const expectedCurrency = corridor?.origin_currency ?? current.currency;
        const allowedCurrencies =
          corridor?.origin_currency === 'USD' && corridor.destination_currency === 'GTQ' ? ['USD', 'GTQ'] : [expectedCurrency];
        return source.id.toString() === current.funding_source_id && allowedCurrencies.includes(source.currency);
      })
        ? current.funding_source_id
        : fundingSources.find((source) => {
            const expectedCurrency = corridor?.origin_currency ?? current.currency;
            const allowedCurrencies =
              corridor?.origin_currency === 'USD' && corridor.destination_currency === 'GTQ' ? ['USD', 'GTQ'] : [expectedCurrency];
            return allowedCurrencies.includes(source.currency);
          })?.id.toString() ?? '',
    }));
  }, [beneficiaries, corridors, fundingSources, form.origin_country, form.destination_country]);

  async function simulate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSimulation(null);
    if (!form.beneficiary_id) {
      showMessage('Primero registra o selecciona un beneficiario activo.', 'error');
      return;
    }
    if (!form.funding_source_id) {
      showMessage(`Agrega o selecciona un metodo de pago en ${compatibleFundingCurrencies.join(' o ')} para esta ruta.`, 'error');
      return;
    }
    const selectedFundingSource = fundingSources.find((source) => source.id.toString() === form.funding_source_id);
    setIsSimulating(true);
    try {
      const result = await request<Simulation>('/remittances/simulate', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          beneficiary_id: Number(form.beneficiary_id),
          funding_source_id: Number(form.funding_source_id),
          payment_method: paymentMethodForFundingSource(selectedFundingSource?.type ?? form.payment_method),
        }),
      });
      setSimulation(result);
      showMessage('Cotizacion generada correctamente.', 'success');
    } catch (error) {
      const code = error instanceof ApiRequestError ? error.code : 'REQUEST_FAILED';
      showMessage(getRemittanceErrorMessage(code), 'error');
    } finally {
      setIsSimulating(false);
    }
  }

  async function confirmTransaction() {
    setIsCreating(true);
    const selectedFundingSource = fundingSources.find((source) => source.id.toString() === form.funding_source_id);
    try {
      const transaction = await request<Transaction>('/transactions', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          beneficiary_id: Number(form.beneficiary_id),
          funding_source_id: Number(form.funding_source_id),
          payment_method: paymentMethodForFundingSource(selectedFundingSource?.type ?? form.payment_method),
        }),
      });
      setSimulation(null);
      await onCreated(transaction);
    } catch {
      showMessage('No se pudo enviar la remesa.', 'error');
    } finally {
      setIsCreating(false);
    }
  }

  if (beneficiaries.length === 0) {
    return (
      <section className="panel">
        <h2 className="section-title">Nueva remesa</h2>
        <EmptyState text="Necesitas registrar al menos un beneficiario activo antes de enviar una remesa." />
        <button className="primary-button mt-4" type="button" onClick={onManageBeneficiaries}>
          Registrar beneficiario
        </button>
      </section>
    );
  }

  if (fundingSources.length === 0) {
    return (
      <section className="panel">
        <h2 className="section-title">Enviar remesa</h2>
        <EmptyState text="Necesitas agregar al menos un metodo de pago antes de cotizar una remesa." />
        <button className="primary-button mt-4" type="button" onClick={onManageFunding}>
          Agregar metodo de pago
        </button>
      </section>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="panel">
        <h2 className="section-title">Enviar remesa</h2>
        <form className="mt-5 grid gap-4" onSubmit={simulate}>
          <SelectInput
            label="Desde"
            value={form.origin_country}
            options={originOptions}
            onChange={(value) => {
              const next = corridors.find((corridor) => corridor.origin_country === value);
              setForm({
                ...form,
                origin_country: value,
                destination_country: next?.destination_country ?? '',
                currency: next?.origin_currency ?? form.currency,
                beneficiary_id: '',
                funding_source_id: '',
              });
              setSimulation(null);
            }}
          />
          <SelectInput
            label="Para"
            value={form.destination_country}
            options={destinationOptions}
            onChange={(value) => {
              const next = corridors.find(
                (corridor) => corridor.origin_country === form.origin_country && corridor.destination_country === value,
              );
              setForm({ ...form, destination_country: value, currency: next?.origin_currency ?? form.currency, beneficiary_id: '' });
              setSimulation(null);
            }}
          />
          <SelectInput
            label="Beneficiario compatible"
            value={form.beneficiary_id}
            options={compatibleBeneficiaries.map((b) => ({ value: b.id.toString(), label: `${b.first_name} ${b.last_name}` }))}
            onChange={(value) => setForm({ ...form, beneficiary_id: value })}
          />
          <TextInput label={`Tu envias (${selectedCorridor?.origin_currency ?? form.currency})`} value={form.amount} onChange={(value) => setForm({ ...form, amount: value })} />
          <SelectInput
            label="Metodo de pago"
            value={form.funding_source_id}
            options={compatibleFundingSources.map((source) => ({
              value: source.id.toString(),
              label: `${fundingSourceTypeLabel(source.type)} •••• ${source.last_four} (${source.currency})`,
            }))}
            onChange={(value) => setForm({ ...form, funding_source_id: value })}
          />
          {compatibleFundingSources.length === 0 ? (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm leading-6 text-amber-900">
              No tienes metodos activos en {compatibleFundingCurrencies.join(' o ')} para esta ruta.
              <button className="ml-2 font-semibold text-fiducia-teal underline-offset-2 hover:underline" type="button" onClick={onManageFunding}>
                Agregar metodo
              </button>
            </div>
          ) : null}
          <SelectInput label="Metodo de entrega" value={form.delivery_method} options={deliveryMethods} onChange={(value) => setForm({ ...form, delivery_method: value })} />
          <button className="primary-button" type="submit" disabled={isSimulating}>
            {isSimulating ? 'Cotizando...' : 'Cotizar envio'}
          </button>
        </form>
      </section>
      <section className="panel">
        <h2 className="section-title">Resumen de cotizacion</h2>
        {simulation ? (
          <div className="mt-4 grid gap-3">
            <SummaryRow label="Ruta" value={`${simulation.origin_country} -> ${simulation.destination_country}`} />
            <SummaryRow label="Tu envias" value={`${simulation.source_currency} ${formatMoney(simulation.source_amount)}`} />
            <SummaryRow label="Comision 2.25 %" value={`${simulation.source_currency} ${formatMoney(simulation.commission_amount)}`} />
            <SummaryRow label="Total a debitar" value={`${simulation.total_debit_currency} ${formatMoney(simulation.total_debit_amount)}`} />
            <SummaryRow
              label="Tipo de cambio"
              value={`${simulation.source_currency} -> ${simulation.destination_currency}: ${formatMoney(simulation.exchange_rate)}`}
            />
            <p className="-mt-1 text-xs leading-5 text-slate-500">
              Referencia: {simulation.exchange_rate_source}
              {simulation.is_exchange_rate_simulated ? ' con respaldo local' : ''}
            </p>
            <SummaryRow label="Beneficiario recibe" value={`${simulation.destination_currency} ${formatMoney(simulation.destination_amount)}`} />
            <SummaryRow label="Entrega estimada" value={simulation.estimated_delivery} />
            <SummaryRow label="Metodo de entrega" value={deliveryLabel(simulation.delivery_method)} />
            <button className="primary-button mt-3 inline-flex items-center justify-center gap-2" type="button" onClick={confirmTransaction} disabled={isCreating}>
              <CheckCircle2 size={18} />
              {isCreating ? 'Enviando...' : 'Confirmar envio'}
            </button>
          </div>
        ) : (
          <EmptyState text="Ingresa los datos y genera una cotizacion para ver el resumen antes de confirmar." />
        )}
      </section>
    </div>
  );
}

function HistoryView({
  title,
  emptyText,
  mode,
  transactions,
  onOpen,
}: {
  title: string;
  emptyText: string;
  mode: 'sent' | 'received';
  transactions: Transaction[];
  onOpen: (transaction: Transaction) => void;
}) {
  const [statusFilter, setStatusFilter] = React.useState('ALL');
  const filteredTransactions =
    statusFilter === 'ALL' ? transactions : transactions.filter((transaction) => transaction.status === statusFilter);
  return (
    <section className="panel">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="section-title">{title}</h2>
        {mode === 'received' ? (
          <select
            className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-fiducia-teal focus:ring-2 focus:ring-fiducia-mint"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="ALL">Todas</option>
            <option value="AVAILABLE">Disponibles</option>
            <option value="COMPLETED">Completadas</option>
          </select>
        ) : null}
      </div>
      <TransactionTable transactions={filteredTransactions} onOpen={onOpen} mode={mode} emptyText={emptyText} />
    </section>
  );
}

function TransactionTable({
  transactions,
  compact = false,
  mode,
  emptyText = 'Aun no hay remesas registradas.',
  onOpen,
}: {
  transactions: Transaction[];
  compact?: boolean;
  mode: 'sent' | 'received';
  emptyText?: string;
  onOpen?: (transaction: Transaction) => void;
}) {
  if (transactions.length === 0) return <EmptyState text={emptyText} />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-slate-500">
            <th className="py-3 pr-4 font-semibold">Remesa</th>
            <th className="py-3 pr-4 font-semibold">{mode === 'received' ? 'Remitente' : 'Beneficiario'}</th>
            <th className="py-3 pr-4 font-semibold">Ruta</th>
            {!compact ? <th className="py-3 pr-4 font-semibold">Fecha</th> : null}
            <th className="py-3 pr-4 font-semibold">Enviado</th>
            <th className="py-3 pr-4 font-semibold">Recibido</th>
            <th className="py-3 pr-4 font-semibold">Estado</th>
            {onOpen ? <th className="py-3 font-semibold">Detalle</th> : null}
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr className="border-b border-slate-100" key={transaction.id}>
              <td className="py-3 pr-4 font-semibold text-fiducia-navy">{transaction.transaction_id}</td>
              <td className="py-3 pr-4">
                {mode === 'received'
                  ? `${transaction.sender.first_name} ${transaction.sender.last_name}`
                  : `${transaction.beneficiary.first_name} ${transaction.beneficiary.last_name}`}
              </td>
              <td className="py-3 pr-4">
                {transaction.origin_country} {'->'} {transaction.destination_country}
              </td>
              {!compact ? <td className="py-3 pr-4">{formatDate(transaction.created_at)}</td> : null}
              <td className="py-3 pr-4">{transaction.source_currency} {formatMoney(transaction.source_amount)}</td>
              <td className="py-3 pr-4">{transaction.destination_currency} {formatMoney(transaction.destination_amount)}</td>
              <td className="py-3 pr-4">{statusLabels[transaction.status] ?? transaction.status}</td>
              {onOpen ? (
                <td className="py-3">
                  <button className="icon-button" type="button" onClick={() => onOpen(transaction)} title="Ver detalle">
                    <Eye size={17} />
                  </button>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TransactionDetail({
  currentUser,
  transaction,
  onReceive,
}: {
  currentUser: User;
  transaction: Transaction;
  onReceive: (transaction: Transaction) => Promise<void>;
}) {
  const [isReceiving, setIsReceiving] = React.useState(false);
  const canReceive = transaction.status === 'AVAILABLE' && transaction.beneficiary_user_id === currentUser.id;
  const receiveLabel = receiveActionLabel(transaction.delivery_method);
  const destinationCurrency = resolveCurrency(transaction.destination_currency, transaction.destination_country);
  const sourceCurrency = resolveCurrency(transaction.source_currency, transaction.origin_country);
  const totalDebitCurrency = resolveCurrency(transaction.total_debit_currency, transaction.origin_country);

  async function handleReceive() {
    setIsReceiving(true);
    try {
      await onReceive(transaction);
    } finally {
      setIsReceiving(false);
    }
  }

  function printReceipt() {
    const receipt = buildReceiptHtml(transaction);
    const printWindow = window.open('', '_blank', 'width=820,height=980');
    if (!printWindow) return;
    printWindow.document.write(receipt);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  }

  return (
    <section className="panel">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-fiducia-teal">Detalle de remesa</p>
          <h2 className="mt-2 text-2xl font-bold text-fiducia-navy">{transaction.transaction_id}</h2>
        </div>
        <button className="secondary-button" type="button" onClick={printReceipt}>
          Imprimir comprobante
        </button>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <SummaryRow label="Remitente" value={`${transaction.sender.first_name} ${transaction.sender.last_name}`} />
        <SummaryRow label="Beneficiario" value={`${transaction.beneficiary.first_name} ${transaction.beneficiary.last_name}`} />
        <SummaryRow label="Fecha" value={formatDate(transaction.created_at)} />
        <SummaryRow label="Pais origen" value={transaction.origin_country} />
        <SummaryRow label="Pais destino" value={transaction.destination_country} />
        <SummaryRow label="Monto enviado" value={`${sourceCurrency.code} ${formatMoney(transaction.source_amount)}`} />
        <SummaryRow label="Comision" value={`${sourceCurrency.code} ${formatMoney(transaction.commission_amount)}`} />
        <SummaryRow label="Costo total" value={`${sourceCurrency.code} ${formatMoney(transaction.total_amount)}`} />
        <SummaryRow label="Total debitado" value={`${totalDebitCurrency.code} ${formatMoney(transaction.total_debit_amount)}`} />
        <SummaryRow
          label="Tipo de cambio"
          value={`${sourceCurrency.code} -> ${destinationCurrency.label}: ${formatMoney(transaction.exchange_rate)}`}
        />
        <SummaryRow label="Monto recibido estimado" value={`${destinationCurrency.label} ${formatMoney(transaction.destination_amount)}`} />
        <SummaryRow label="Metodo de pago" value={paymentLabel(transaction.payment_method)} />
        <SummaryRow label="Metodo de entrega" value={deliveryLabel(transaction.delivery_method)} />
        <SummaryRow label="Estado" value={statusLabels[transaction.status] ?? transaction.status} />
      </div>
      {canReceive ? (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <h3 className="font-semibold text-emerald-900">Remesa disponible</h3>
          <p className="mt-2 text-sm text-emerald-800">
            {transaction.sender.first_name} te envio {destinationCurrency.label} {formatMoney(transaction.destination_amount)}.
          </p>
          <button className="primary-button mt-4 inline-flex items-center gap-2" type="button" onClick={handleReceive} disabled={isReceiving}>
            <CheckCircle2 size={18} />
            {isReceiving ? 'Confirmando...' : receiveLabel}
          </button>
        </div>
      ) : null}
    </section>
  );
}

function FundingSourcesView({
  user,
  fundingSources,
  onChanged,
  showMessage,
}: {
  user: User;
  fundingSources: FundingSource[];
  onChanged: () => Promise<void>;
  showMessage: (message: string, type: MessageType) => void;
}) {
  const [form, setForm] = React.useState({
    type: 'CARD',
    display_name: '',
    provider: cardIssuers[0],
    account_type: 'Ahorro',
    account_number: '',
    card_number: '',
    card_expiry: '',
    card_cvv: '',
    last_four: '',
    currency: 'USD',
    is_default: false,
  });
  const [isSaving, setIsSaving] = React.useState(false);
  const isCard = form.type === 'CARD';
  const isBankAccount = form.type === 'BANK_ACCOUNT';
  const providerLabel = isBankAccount ? 'Banco' : isCard ? 'Emisor Tarjeta' : 'Proveedor';
  const displayNameLabel = isCard ? 'Nombre en tarjeta' : isBankAccount ? 'Nombre de cuenta' : 'Nombre visible';

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationMessage = validateFundingSourceForm(form, user);
    if (validationMessage) {
      showMessage(validationMessage, 'error');
      return;
    }
    setIsSaving(true);
    try {
      await request('/funding-sources', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          provider: form.provider || null,
          last_four: form.type === 'BANK_ACCOUNT' ? form.account_number.slice(-4) : form.card_number.slice(-4),
        }),
      });
      setForm({
        type: 'CARD',
        display_name: '',
        provider: cardIssuers[0],
        account_type: 'Ahorro',
        account_number: '',
        card_number: '',
        card_expiry: '',
        card_cvv: '',
        last_four: '',
        currency: 'USD',
        is_default: false,
      });
      await onChanged();
      showMessage('Metodo de pago agregado correctamente.', 'success');
    } catch {
      showMessage('No se pudo agregar el metodo de pago. Revisa emisor, moneda y ultimos 4 digitos.', 'error');
    } finally {
      setIsSaving(false);
    }
  }

  async function setDefault(source: FundingSource) {
    await request(`/funding-sources/${source.id}/default`, { method: 'POST' });
    await onChanged();
    showMessage('Metodo predeterminado actualizado.', 'success');
  }

  async function deactivate(source: FundingSource) {
    await request(`/funding-sources/${source.id}`, { method: 'PATCH', body: JSON.stringify({ is_active: false }) });
    await onChanged();
    showMessage('Metodo de pago desactivado.', 'success');
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="panel">
        <h2 className="section-title">Nuevo metodo de pago</h2>
        <form className="mt-5 grid gap-4" onSubmit={submit}>
          <SelectInput
            label="Tipo"
            value={form.type}
            options={[
              { value: 'CARD', label: 'Tarjeta de credito' },
              { value: 'BANK_ACCOUNT', label: 'Cuenta bancaria' },
              { value: 'DIGITAL_WALLET', label: 'Billetera digital' },
            ]}
            onChange={(value) =>
              setForm({
                ...form,
                type: value,
                provider: value === 'BANK_ACCOUNT' ? guatemalaBanks[0] : value === 'CARD' ? cardIssuers[0] : '',
                account_type: 'Ahorro',
                account_number: '',
                card_number: '',
                card_expiry: '',
                card_cvv: '',
                last_four: '',
              })
            }
          />
          <TextInput label={displayNameLabel} value={form.display_name} onChange={(value) => setForm({ ...form, display_name: value })} />
          {isBankAccount ? (
            <SelectInput
              label={providerLabel}
              value={form.provider}
              options={guatemalaBanks.map((bank) => ({ value: bank, label: bank }))}
              onChange={(value) => setForm({ ...form, provider: value })}
            />
          ) : null}
          {isCard ? (
            <SelectInput
              label={providerLabel}
              value={form.provider}
              options={cardIssuers.map((issuer) => ({ value: issuer, label: issuer }))}
              onChange={(value) => setForm({ ...form, provider: value })}
            />
          ) : null}
          {!isBankAccount && !isCard ? (
            <TextInput label={providerLabel} value={form.provider} onChange={(value) => setForm({ ...form, provider: value })} required={false} />
          ) : null}
          {isBankAccount ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <SelectInput label="Tipo de cuenta" value={form.account_type} options={accountTypeOptions} onChange={(value) => setForm({ ...form, account_type: value })} />
              <TextInput
                label="Numero de cuenta"
                value={form.account_number}
                maxLength={30}
                onChange={(value) => setForm({ ...form, account_number: value.replace(/\D/g, '') })}
              />
            </div>
          ) : null}
          {isCard ? (
            <div className="grid gap-4 sm:grid-cols-3">
              <TextInput
                label="Numero de tarjeta"
                value={form.card_number}
                maxLength={19}
                onChange={(value) => setForm({ ...form, card_number: value.replace(/\D/g, '') })}
              />
              <TextInput
                label="Vencimiento"
                value={form.card_expiry}
                maxLength={5}
                placeholder="MM/AA"
                onChange={(value) => setForm({ ...form, card_expiry: formatCardExpiry(value) })}
              />
              <TextInput
                label="CVV"
                value={form.card_cvv}
                maxLength={4}
                onChange={(value) => setForm({ ...form, card_cvv: value.replace(/\D/g, '') })}
              />
            </div>
          ) : null}
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectInput label="Moneda" value={form.currency} options={fundingCurrencyOptions} onChange={(value) => setForm({ ...form, currency: value })} />
          </div>
          <label className="flex items-start gap-2 text-sm text-slate-600">
            <input
              className="mt-1"
              type="checkbox"
              checked={form.is_default}
              onChange={(event) => setForm({ ...form, is_default: event.target.checked })}
            />
            Usar como metodo predeterminado
          </label>
          <button className="primary-button inline-flex items-center justify-center gap-2" type="submit" disabled={isSaving}>
            <CreditCard size={18} />
            {isSaving ? 'Guardando...' : 'Agregar metodo'}
          </button>
        </form>
      </section>
      <section className="panel">
        <h2 className="section-title">Mis metodos de pago</h2>
        <div className="mt-4 grid gap-3">
          {fundingSources.length === 0 ? <EmptyState text="Aun no tienes metodos de pago registrados." /> : null}
          {fundingSources.map((source) => (
            <div className="rounded-lg border border-slate-200 p-4" key={source.id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-fiducia-navy">
                    {fundingSourceTypeLabel(source.type)} •••• {source.last_four}
                  </p>
                  <p className="text-sm text-slate-600">
                    {source.display_name} - {source.currency}
                  </p>
                  {source.account_type ? <p className="text-sm text-slate-500">Cuenta {source.account_type}</p> : null}
                  {source.card_expiry ? <p className="text-sm text-slate-500">Vence {source.card_expiry}</p> : null}
                  <p className="text-sm text-slate-500">{source.provider ?? 'Proveedor'}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-fiducia-mint px-3 py-1 text-xs font-semibold text-fiducia-teal">
                    {source.is_default ? 'Predeterminado' : source.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                  {!source.is_default && source.is_active ? (
                    <button className="secondary-button" type="button" onClick={() => setDefault(source)}>
                      Predeterminar
                    </button>
                  ) : null}
                  {source.is_active ? (
                    <button className="secondary-button" type="button" onClick={() => deactivate(source)}>
                      Desactivar
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function TrackingView({ showMessage }: { showMessage: (message: string, type: MessageType) => void }) {
  const [remittanceNumber, setRemittanceNumber] = React.useState('');
  const [tracking, setTracking] = React.useState<TrackingResult | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setTracking(null);
    try {
      const result = await request<TrackingResult>(`/tracking/${encodeURIComponent(remittanceNumber.trim())}`);
      setTracking(result);
      showMessage('Remesa encontrada.', 'success');
    } catch {
      showMessage('No se encontro una remesa accesible con ese numero.', 'error');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2 className="section-title">Rastrear remesa</h2>
      <form className="mt-5 flex flex-col gap-3 sm:flex-row" onSubmit={submit}>
        <TextInput label="Numero de remesa" value={remittanceNumber} onChange={setRemittanceNumber} placeholder="FID-2026-000001" />
        <button className="primary-button mt-6 inline-flex items-center justify-center gap-2" type="submit" disabled={isLoading}>
          <Search size={18} />
          {isLoading ? 'Buscando...' : 'Rastrear'}
        </button>
      </form>
      {tracking ? (
        <div className="mt-6 grid gap-4">
          <div className="grid gap-4 md:grid-cols-2">
            <SummaryRow label="Numero" value={tracking.remittance_number} />
            <SummaryRow label="Estado" value={statusLabels[tracking.status] ?? tracking.status} />
            <SummaryRow label="Ruta" value={`${tracking.origin_country} -> ${tracking.destination_country}`} />
            <SummaryRow label="Monto recibido" value={`${tracking.destination_currency} ${formatMoney(tracking.destination_amount)}`} />
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <h3 className="font-semibold text-fiducia-navy">Seguimiento</h3>
            <div className="mt-4 grid gap-3">
              {tracking.timeline.map((item, index) => (
                <div className="border-l-2 border-fiducia-teal pl-4" key={`${item.new_status}-${index}`}>
                  <p className="font-semibold text-fiducia-navy">{statusLabels[item.new_status] ?? item.new_status}</p>
                  <p className="text-sm text-slate-500">{formatDate(item.changed_at)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function ProfileView({
  user,
  onUpdated,
  showMessage,
}: {
  user: User;
  onUpdated: (user: User) => void;
  showMessage: (message: string, type: MessageType) => void;
}) {
  const [form, setForm] = React.useState({
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    phone: user.phone,
    country: user.country,
    document_type: user.document_type ?? 'DPI',
    fictitious_document_id: user.fictitious_document_id ?? '',
    birth_date: user.birth_date ?? '',
    occupation: user.occupation ?? '',
  });
  const [isSaving, setIsSaving] = React.useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    try {
      const updated = await request<User>('/users/me', {
        method: 'PATCH',
        body: JSON.stringify({
          ...form,
          birth_date: form.birth_date || null,
          occupation: form.occupation || null,
        }),
      });
      onUpdated(updated);
      showMessage('Perfil actualizado correctamente.', 'success');
    } catch (error) {
      const code = error instanceof ApiRequestError ? error.code : 'REQUEST_FAILED';
      showMessage(code === 'EMAIL_ALREADY_REGISTERED' ? 'Ese correo ya esta registrado por otro usuario.' : 'No se pudo actualizar el perfil.', 'error');
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="panel">
      <h2 className="section-title">Mi perfil</h2>
      <form className="mt-5 grid gap-4" onSubmit={submit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput label="Nombre" value={form.first_name} onChange={(value) => setForm({ ...form, first_name: value })} />
          <TextInput label="Apellido" value={form.last_name} onChange={(value) => setForm({ ...form, last_name: value })} />
        </div>
        <TextInput label="Correo electronico" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} />
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput label="Telefono" value={form.phone} onChange={(value) => setForm({ ...form, phone: value })} />
          <SelectInput label="Pais" value={form.country} options={getCountryOptions([])} onChange={(value) => setForm({ ...form, country: value })} />
        </div>
        <div className="grid gap-4 sm:grid-cols-[0.8fr_1.2fr]">
          <SelectInput
            label="Tipo de documento"
            value={form.document_type}
            options={[
              { value: 'DPI', label: 'DPI' },
              { value: 'PASSPORT', label: 'Pasaporte' },
            ]}
            onChange={(value) => setForm({ ...form, document_type: value })}
          />
          <TextInput
            label="No. de documento"
            value={form.fictitious_document_id}
            maxLength={form.document_type === 'DPI' ? 13 : 20}
            onChange={(value) =>
              setForm({
                ...form,
                fictitious_document_id:
                  form.document_type === 'DPI' ? value.replace(/\D/g, '').slice(0, 13) : value.toUpperCase(),
              })
            }
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <TextInput label="Fecha de nacimiento" type="date" value={form.birth_date} onChange={(value) => setForm({ ...form, birth_date: value })} required={false} />
          <TextInput label="Ocupacion" value={form.occupation} onChange={(value) => setForm({ ...form, occupation: value })} required={false} />
        </div>
        <button className="primary-button" type="submit" disabled={isSaving}>
          {isSaving ? 'Guardando...' : 'Guardar perfil'}
        </button>
      </form>
    </section>
  );
}

async function request<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const token = window.localStorage.getItem(tokenStorageKey);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers: { ...headers, ...options.headers } });
  if (!response.ok) {
    let code = 'REQUEST_FAILED';
    try {
      const body = await response.json();
      code = body.detail?.code ?? code;
    } catch {
      // Keep default code when the backend returns non-JSON.
    }
    throw new ApiRequestError(code, response.status);
  }
  return (await response.json()) as T;
}

function NavButton({ active, label, onClick }: { active: boolean; label: string; onClick: () => void }) {
  return (
    <button className={active ? 'nav-button-active' : 'nav-button'} type="button" onClick={onClick}>
      {label}
    </button>
  );
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  maxLength,
  minLength,
  required = true,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  maxLength?: number;
  minLength?: number;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      <input
        className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none transition focus:border-fiducia-teal focus:ring-2 focus:ring-fiducia-mint"
        type={type}
        value={value}
        placeholder={placeholder}
        maxLength={maxLength}
        minLength={minLength}
        onChange={(event) => onChange(event.target.value)}
        required={required}
      />
    </label>
  );
}

function SelectInput({ label, value, options, onChange }: { label: string; value: string; options: Array<{ value: string; label: string }>; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      <select
        className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none transition focus:border-fiducia-teal focus:ring-2 focus:ring-fiducia-mint"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-md border border-slate-200 bg-white px-4 py-3">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-right text-sm font-semibold text-fiducia-navy">{value}</span>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-fiducia-navy">{value}</p>
    </div>
  );
}

function ExecutiveMetric({ label, value, change }: { label: string; value: string; change?: string | null }) {
  const numericChange = change == null ? null : Number(change);
  const changeLabel = numericChange == null ? 'Sin periodo previo' : `${numericChange >= 0 ? '+' : ''}${(numericChange * 100).toLocaleString('es-GT', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-fiducia-navy">{value}</p>
      <p className={numericChange != null && numericChange < 0 ? 'mt-2 text-sm font-semibold text-amber-700' : 'mt-2 text-sm font-semibold text-fiducia-teal'}>
        {changeLabel}
      </p>
    </div>
  );
}

function AnalyticsPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <h2 className="section-title">{title}</h2>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function SimpleBarChart({ items }: { items: Array<{ label: string; value: number; detail?: string }> }) {
  const maxValue = Math.max(1, ...items.map((item) => item.value));
  if (items.length === 0) return <EmptyState text="Aun no hay datos suficientes para graficar." />;
  return (
    <div className="space-y-3">
      {items.slice(0, 8).map((item) => (
        <div className="grid gap-2" key={item.label}>
          <div className="flex items-center justify-between gap-4 text-sm">
            <span className="truncate text-slate-600">{item.label}</span>
            <span className="font-semibold text-fiducia-navy">{item.detail ?? item.value}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-fiducia-teal" style={{ width: `${Math.max(6, (item.value / maxValue) * 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function MiniList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-sm font-semibold text-fiducia-navy">{title}</p>
      <div className="mt-3 space-y-2">
        {items.length === 0 ? <p className="text-sm text-slate-500">Sin datos</p> : null}
        {items.map((item) => (
          <p className="text-sm text-slate-600" key={item}>
            {item}
          </p>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">{text}</div>;
}

function StatusMessage({ message, type }: { message: string; type: MessageType }) {
  const classes = type === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-red-200 bg-red-50 text-red-800';
  return <div className={`mb-4 rounded-md border p-3 text-sm leading-6 ${classes}`}>{message}</div>;
}

function TermsModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 px-4 py-8">
      <div className="max-h-[82vh] w-full max-w-2xl overflow-hidden rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <h2 className="text-lg font-semibold text-fiducia-navy">Terminos y condiciones</h2>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Cerrar terminos">
            <X size={18} />
          </button>
        </div>
        <div className="max-h-[64vh] overflow-y-auto px-5 py-5 text-sm leading-7 text-slate-600">
          <p className="mb-4 text-base font-semibold text-fiducia-navy">
            Lee cuidadosamente las condiciones de uso de FIDUCIA antes de continuar.
          </p>
          <p>
            FIDUCIA permite registrar usuarios, administrar beneficiarios, cotizar envios y consultar movimientos dentro de un
            entorno de demostracion controlado. La informacion ingresada debe ser veraz para efectos de prueba y no debe incluir
            datos bancarios reales, claves personales de terceros ni informacion sensible innecesaria.
          </p>
          <p className="mt-4">
            Las cotizaciones, comisiones, tiempos estimados y tipos de cambio presentados tienen fines de validacion funcional.
            Pueden variar segun configuracion interna, corredor, moneda, metodo de pago y metodo de entrega seleccionado.
          </p>
          <p className="mt-4">
            Al crear una cuenta aceptas que FIDUCIA procese los datos ingresados para autenticar la sesion, validar formularios,
            mostrar historiales, registrar auditoria operativa y mantener trazabilidad de las remesas creadas en la plataforma.
          </p>
          <p className="mt-4">
            El usuario es responsable de custodiar sus credenciales. FIDUCIA puede bloquear operaciones cuando detecte datos
            incompletos, documentos invalidos, beneficiarios inconsistentes o intentos de acceso no autorizados.
          </p>
          <p className="mt-4">
            Estos terminos son referenciales y forman parte de la experiencia de validacion del sistema. No reemplazan contratos,
            politicas regulatorias ni documentos legales de una entidad financiera autorizada.
          </p>
        </div>
        <div className="border-t border-slate-200 px-5 py-4 text-right">
          <button className="primary-button" type="button" onClick={onClose}>
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}

function DemoFooter() {
  return (
    <footer className="mx-auto max-w-7xl px-6 pb-6 text-center text-xs leading-5 text-slate-400">
      FIDUCIA es un prototipo tecnologico desarrollado con fines educativos y de investigacion. No constituye una entidad financiera ni un servicio real de remesas.
    </footer>
  );
}

function getRegisterErrorMessage(code: string) {
  if (code === 'EMAIL_ALREADY_REGISTERED') return 'Este correo ya esta registrado. Usa otro correo o vuelve al login.';
  if (code === 'INVALID_COUNTRY') return 'Selecciona un pais habilitado para operar en FIDUCIA.';
  if (code === 'INVALID_ROLE') return 'No se pudo asignar el perfil de cliente. Intenta de nuevo.';
  if (code === 'ROLE_NOT_FOUND') return 'La configuracion inicial de roles no esta disponible. Reinicia el backend.';
  if (code === 'REQUEST_FAILED') return 'No se pudo crear la cuenta. Verifica los datos requeridos antes de continuar.';
  return 'No se pudo crear la cuenta. Revisa documento, fecha de nacimiento, contrasena, terminos y verificacion.';
}

function getBeneficiaryErrorMessage(code: string) {
  if (code === 'CITY_REQUIRED') return 'Ingresa la ciudad del beneficiario para paises fuera de Guatemala.';
  if (code === 'INVALID_GUATEMALA_LOCATION') return 'Selecciona un departamento y municipio validos de Guatemala.';
  if (code === 'INVALID_RELATIONSHIP') return 'Selecciona una relacion valida para el beneficiario.';
  if (code === 'REQUEST_FAILED') return 'No se pudo crear el beneficiario. Revisa correo, ubicacion y ultimos 4 digitos.';
  return 'No se pudo crear el beneficiario. Revisa los datos ingresados.';
}

function getRemittanceErrorMessage(code: string) {
  if (code === 'INVALID_FUNDING_SOURCE') {
    return 'El metodo de pago no fue aceptado por el backend activo. Reinicia FIDUCIA para cargar la version que permite pagar en GTQ.';
  }
  if (code === 'INVALID_CURRENCY') return 'La moneda del envio no corresponde a la ruta seleccionada.';
  if (code === 'INCOMPATIBLE_BENEFICIARY') return 'El beneficiario no corresponde al pais destino seleccionado.';
  if (code === 'EXCHANGE_RATE_NOT_FOUND') return 'No hay tipo de cambio disponible para esta ruta.';
  if (code === 'AMOUNT_OUT_OF_RANGE') return 'El monto esta fuera del rango permitido para esta ruta.';
  return 'No se pudo cotizar la remesa. Revisa monto, pais, moneda, beneficiario y metodo de pago.';
}

function validateFundingSourceForm(form: {
  type: string;
  display_name: string;
  provider: string;
  account_type: string;
  account_number: string;
  card_number: string;
  card_expiry: string;
  card_cvv: string;
  last_four: string;
  currency: string;
}, user: User) {
  if (!['USD', 'GTQ'].includes(form.currency)) return 'Selecciona dolares o quetzales como moneda.';
  if (form.type === 'BANK_ACCOUNT') {
    if (!guatemalaBanks.includes(form.provider)) return 'Selecciona un banco de Guatemala.';
    if (!accountTypeOptions.some((option) => option.value === form.account_type)) return 'Selecciona si la cuenta es de ahorro o monetaria.';
    if (!/^\d{6,30}$/.test(form.account_number)) return 'Ingresa el numero completo de cuenta con al menos 6 digitos.';
    if (!cardNameMatchesUser(form.display_name, user)) {
      return 'El nombre de la cuenta debe incluir al menos un nombre y un apellido de tu perfil.';
    }
  }
  if (form.type === 'CARD') {
    if (!cardIssuers.includes(form.provider)) return 'Selecciona Visa, Mastercard o American Express.';
    if (!/^\d{13,19}$/.test(form.card_number)) return 'Ingresa el numero completo de tarjeta con 13 a 19 digitos.';
    if (!isValidCardExpiry(form.card_expiry)) return 'Ingresa una fecha de vencimiento valida en formato MM/AA.';
    if (!/^\d{3,4}$/.test(form.card_cvv)) return 'Ingresa un CVV valido de 3 o 4 digitos.';
    if (!cardNameMatchesUser(form.display_name, user)) {
      return 'El nombre en tarjeta debe incluir al menos un nombre y un apellido de tu perfil.';
    }
  }
  return null;
}

function cardNameMatchesUser(cardName: string, user: User) {
  const normalizedCardName = normalizeForComparison(cardName);
  const firstNames = normalizeForComparison(user.first_name).split(' ').filter(Boolean);
  const lastNames = normalizeForComparison(user.last_name).split(' ').filter(Boolean);
  const includesFirstName = firstNames.some((name) => normalizedCardName.includes(name));
  const includesLastName = lastNames.some((name) => normalizedCardName.includes(name));
  return includesFirstName && includesLastName;
}

function normalizeForComparison(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function formatCardExpiry(value: string) {
  const digits = value.replace(/\D/g, '').slice(0, 4);
  if (digits.length <= 2) return digits;
  return `${digits.slice(0, 2)}/${digits.slice(2)}`;
}

function isValidCardExpiry(value: string) {
  if (!/^\d{2}\/\d{2}$/.test(value)) return false;
  const month = Number(value.slice(0, 2));
  return month >= 1 && month <= 12;
}

function validateRegisterForm(form: RegisterFormState) {
  if (form.document_type === 'DPI' && !/^\d{13}$/.test(form.fictitious_document_id)) {
    return 'El DPI debe tener exactamente 13 digitos.';
  }
  if (form.document_type === 'PASSPORT' && !/^[A-Z0-9-]{6,20}$/.test(form.fictitious_document_id)) {
    return 'El pasaporte debe tener entre 6 y 20 caracteres alfanumericos.';
  }
  if (!form.birth_date) return 'Ingresa la fecha de nacimiento.';
  if (new Date(form.birth_date) >= new Date()) return 'La fecha de nacimiento debe ser anterior a la fecha actual.';
  if (form.password.length < 8) return 'La contrasena debe tener minimo 8 caracteres.';
  if (!/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) {
    return 'La contrasena debe incluir letras y numeros.';
  }
  if (form.password !== form.confirm_password) return 'La confirmacion de contrasena no coincide.';
  if (!form.human_check_accepted) return 'Marca la verificacion humana para continuar.';
  if (!form.terms_accepted) return 'Debes aceptar los terminos y condiciones para crear la cuenta.';
  return null;
}

function Feature({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 text-fiducia-teal">{icon}</div>
      <h3 className="font-semibold text-fiducia-navy">{title}</h3>
      <p className="mt-1 text-sm leading-6 text-slate-600">{text}</p>
    </div>
  );
}

function formatMaybeMoney(value: string | number | null | undefined) {
  if (value === null || value === undefined) return 'N/D';
  return formatMoney(value);
}

function formatPercentValue(value: string | number | null | undefined) {
  if (value === null || value === undefined) return 'N/D';
  return `${(Number(value) * 100).toLocaleString('es-GT', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
}

function formatMaybeRatio(value: string | number | null | undefined) {
  if (value === null || value === undefined) return 'N/D';
  return Number(value).toLocaleString('es-GT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatMoney(value: string | number) {
  return Number(value).toLocaleString('es-GT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatRatio(value: number) {
  return `${(value * 100).toLocaleString('es-GT', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
}

function formatNullableScore(value: string | number | null | undefined) {
  if (value === null || value === undefined) return 'N/D';
  return Number(value).toLocaleString('es-GT', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

function shortHash(value: string | null | undefined) {
  if (!value) return 'N/D';
  return `${value.slice(0, 10)}...${value.slice(-8)}`;
}

function blockchainEventLabel(eventType: string) {
  const labels: Record<string, string> = {
    GENESIS: 'Genesis',
    REMITTANCE_CREATED: 'Remesa creada',
    RISK_ASSESSMENT_RECORDED: 'Riesgo registrado',
    REMITTANCE_AVAILABLE: 'Remesa disponible',
    REMITTANCE_COMPLETED: 'Remesa completada',
  };
  return labels[eventType] ?? eventType;
}

function assistantSuggestions(role: string) {
  if (role === 'ADMIN') {
    return [
      'Resume los KPIs principales.',
      'Cuales son los corredores principales?',
      'Que proyecta el forecast?',
      'La cadena blockchain es valida?',
    ];
  }
  if (role === 'RISK_ANALYST') {
    return [
      'Que evaluaciones requieren revision?',
      'Explicame una evaluacion de riesgo.',
      'Cuales son las principales senales?',
      'Verifica blockchain de la ultima remesa.',
    ];
  }
  return [
    'Cual es el estado de mi ultima remesa?',
    'Cuanto pague de comision?',
    'Como agrego un beneficiario?',
    'Que significa Disponible?',
  ];
}

function assistantIntentLabel(intent: string) {
  const labels: Record<string, string> = {
    GENERAL_HELP: 'Soporte',
    MY_REMITTANCES: 'Mis remesas',
    REMITTANCE_STATUS: 'Estado de remesa',
    REMITTANCE_FEES: 'Comisiones',
    BI_OVERVIEW: 'Resumen BI',
    BI_CORRIDORS: 'Corredores',
    BI_CUSTOMERS: 'Clientes',
    FORECAST_SUMMARY: 'Forecast',
    RISK_QUEUE: 'Riesgo',
    RISK_EXPLANATION: 'Explicacion de riesgo',
    BLOCKCHAIN_TRACE: 'Trazabilidad',
    BLOCKCHAIN_VERIFY: 'Verificacion blockchain',
    OUT_OF_SCOPE: 'Fuera de alcance',
  };
  return labels[intent] ?? intent;
}

function assistantSourceLabel(source: string) {
  const labels: Record<string, string> = {
    remittance: 'Remesas',
    risk_assessment: 'Riesgo',
    bi: 'BI',
    forecast: 'Forecast',
    blockchain: 'Blockchain',
    knowledge: 'Ayuda FIDUCIA',
  };
  return labels[source] ?? source;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('es-GT', { dateStyle: 'short', timeStyle: 'short' });
}

function shortPeriod(value: string) {
  return new Date(value).toLocaleDateString('es-GT', { month: 'short', day: '2-digit' });
}

function riskBandLabel(value: string) {
  if (value === 'LOW') return 'Bajo';
  if (value === 'MEDIUM') return 'Medio';
  if (value === 'HIGH') return 'Alto';
  return 'No disponible';
}

function recommendedActionLabel(value: string) {
  if (value === 'CONTINUE') return 'Continuar';
  if (value === 'REVIEW') return 'Revisar';
  if (value === 'MANUAL_REVIEW') return 'Revision manual';
  return value;
}

function reviewStatusLabel(value: string) {
  if (value === 'PENDING') return 'Pendiente';
  if (value === 'REVIEWED') return 'Revisada';
  if (value === 'NOT_REQUIRED') return 'No requerida';
  return value;
}

function deliveryLabel(value: string) {
  return deliveryMethods.find((method) => method.value === value)?.label ?? value;
}

function paymentLabel(value: string) {
  return paymentMethods.find((method) => method.value === value)?.label ?? value;
}

function paymentMethodForFundingSource(value: string) {
  if (value === 'CARD') return 'DEBIT_CARD';
  if (value === 'BANK_ACCOUNT') return 'BANK_TRANSFER';
  if (value === 'DIGITAL_WALLET') return 'DIGITAL_WALLET';
  return value;
}

function resolveCurrency(value: string | null | undefined, country?: string) {
  const fallback = country === 'Guatemala' ? 'GTQ' : value || 'USD';
  const code = value || fallback;
  if (code === 'GTQ') return { code, label: 'Quetzales (GTQ)' };
  if (code === 'USD') return { code, label: 'Dolares (USD)' };
  return { code, label: code };
}

function buildReceiptHtml(transaction: Transaction) {
  const sourceCurrency = resolveCurrency(transaction.source_currency, transaction.origin_country);
  const destinationCurrency = resolveCurrency(transaction.destination_currency, transaction.destination_country);
  const debitCurrency = resolveCurrency(transaction.total_debit_currency, transaction.origin_country);
  const receiptDate = formatDate(transaction.created_at);
  const rows = [
    ['No. de remesa', transaction.transaction_id],
    ['Fecha', receiptDate],
    ['Remitente', `${transaction.sender.first_name} ${transaction.sender.last_name}`],
    ['Beneficiario', `${transaction.beneficiary.first_name} ${transaction.beneficiary.last_name}`],
    ['Ruta', `${transaction.origin_country} -> ${transaction.destination_country}`],
    ['Monto enviado', `${sourceCurrency.code} ${formatMoney(transaction.source_amount)}`],
    ['Comision', `${sourceCurrency.code} ${formatMoney(transaction.commission_amount)}`],
    ['Costo total', `${sourceCurrency.code} ${formatMoney(transaction.total_amount)}`],
    ['Total debitado', `${debitCurrency.code} ${formatMoney(transaction.total_debit_amount)}`],
    ['Tipo de cambio', `${sourceCurrency.code} -> ${destinationCurrency.label}: ${formatMoney(transaction.exchange_rate)}`],
    ['Monto a recibir', `${destinationCurrency.label} ${formatMoney(transaction.destination_amount)}`],
    ['Metodo de pago', paymentLabel(transaction.payment_method)],
    ['Metodo de entrega', deliveryLabel(transaction.delivery_method)],
    ['Estado', statusLabels[transaction.status] ?? transaction.status],
  ];
  return `
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <title>Comprobante ${escapeHtml(transaction.transaction_id)}</title>
    <style>
      body { font-family: Arial, sans-serif; color: #0b2d4d; margin: 40px; }
      .receipt { max-width: 760px; margin: 0 auto; border: 1px solid #d6e0ea; border-radius: 10px; padding: 28px; }
      .brand { display: flex; justify-content: space-between; gap: 24px; border-bottom: 1px solid #d6e0ea; padding-bottom: 18px; margin-bottom: 22px; }
      h1 { margin: 0; font-size: 28px; }
      h2 { margin: 4px 0 0; font-size: 16px; color: #52677a; font-weight: 500; }
      table { width: 100%; border-collapse: collapse; }
      td { border-bottom: 1px solid #edf2f7; padding: 11px 0; font-size: 14px; }
      td:first-child { color: #52677a; }
      td:last-child { text-align: right; font-weight: 700; }
      .note { margin-top: 22px; color: #52677a; font-size: 12px; line-height: 1.6; }
      @media print { body { margin: 0; } .receipt { border: 0; } }
    </style>
  </head>
  <body>
    <main class="receipt">
      <div class="brand">
        <div>
          <h1>FIDUCIA</h1>
          <h2>Comprobante de remesa</h2>
        </div>
        <strong>${escapeHtml(transaction.transaction_id)}</strong>
      </div>
      <table>
        <tbody>
          ${rows.map(([label, value]) => `<tr><td>${escapeHtml(label)}</td><td>${escapeHtml(value)}</td></tr>`).join('')}
        </tbody>
      </table>
      <p class="note">Este comprobante refleja la informacion registrada en FIDUCIA al momento de la operacion.</p>
    </main>
  </body>
</html>`;
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function fundingSourceTypeLabel(value: string) {
  if (value === 'CARD') return 'Tarjeta';
  if (value === 'BANK_ACCOUNT') return 'Cuenta bancaria';
  if (value === 'DIGITAL_WALLET') return 'Billetera digital';
  return value;
}

function receiveActionLabel(value: string) {
  if (value === 'CASH_PICKUP') return 'Cobrar remesa';
  if (value === 'WALLET') return 'Confirmar acreditacion';
  if (value === 'BANK_DEPOSIT' || value === 'TRANSFER') return 'Confirmar recepcion';
  return 'Recibir remesa';
}

function getCountryOptions(corridors: Corridor[]) {
  const countries = new Map<string, string>();
  corridors.forEach((corridor) => {
    countries.set(corridor.origin_country, corridor.origin_currency);
    countries.set(corridor.destination_country, corridor.destination_currency);
  });
  if (countries.size === 0) {
    countries.set('Guatemala', 'GTQ');
    countries.set('Estados Unidos', 'USD');
  }
  return Array.from(countries.entries()).map(([country, currency]) => ({ value: country, label: `${country} (${currency})`, currency }));
}

const guatemalaLocations: Record<string, string[]> = {
  Guatemala: ['Guatemala', 'Mixco', 'Villa Nueva'],
  Sacatepequez: ['Antigua Guatemala', 'Ciudad Vieja', 'Jocotenango'],
  Quetzaltenango: ['Quetzaltenango', 'Coatepeque', 'Olintepeque'],
  Escuintla: ['Escuintla', 'Santa Lucia Cotzumalguapa', 'Palin'],
};

function guatemalaDepartmentOptions() {
  return Object.keys(guatemalaLocations).map((department) => ({ value: department, label: department }));
}

function guatemalaMunicipalityOptions(department: string) {
  const municipalities = guatemalaLocations[department] ?? guatemalaLocations.Guatemala;
  return municipalities.map((municipality) => ({ value: municipality, label: municipality }));
}

export default App;

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
