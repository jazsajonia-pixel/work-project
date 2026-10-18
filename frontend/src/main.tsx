import React, { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  AlertCircle,
  ArrowRight,
  CalendarDays,
  Check,
  CheckCircle2,
  CircleHelp,
  FileCheck2,
  FileText,
  Download,
  Filter,
  ImagePlus,
  LayoutDashboard,
  LoaderCircle,
  LockKeyhole,
  Menu,
  Paperclip,
  Plus,
  RefreshCw,
  Search,
  ScanSearch,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  Trash2,
  Upload,
  X,
  Car,
  Eye,
} from 'lucide-react';
import './style.css';

const API = (import.meta.env.VITE_API_BASE_URL || '/api').replace(//$/, '');
const H = { 'X-Dev-User': import.meta.env.VITE_DEV_USER || 'admin' };

async function api(path: string, options: any = {}) {
  const headers = {
    ...H,
    ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers || {}),
  };
  const response = await fetch(API + path, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw data;
  return data;
}

type Batch = {
  batch_id: string;
  title: string;
  preparation_date: string;
  incident_date: string;
  incident_time: string;
  location: string;
  period_start: string;
  period_end: string;
  operational_info: string;
  notes: string;
  status: string;
};

type UploadRecord = {
  id: number;
  batch_id: string;
  vehicle_id: number | null;
  kind: 'PHOTO' | 'DOCUMENT';
  filename: string;
  content_type: string;
  primary_image: number;
  document_type: string;
};

type Vehicle = {
  id: number;
  batch_id: string;
  category: string;
  make: string;
  vehicle_type: string;
  model: string;
  plate_or_sticker: string;
  chassis_number: string;
  motor_number: string;
  color: string;
  recovery_date: string;
  recovery_place: string;
  recovering_unit: string;
  mode_of_recovery: string;
  violation: string;
  status: string;
  driver_name: string;
  driver_address: string;
  owner_name: string;
  owner_address: string;
  notes: string;
  review_status: string;
};

const newBatch = (): Batch => ({
  batch_id: '',
  title: '',
  preparation_date: '',
  incident_date: '',
  incident_time: '',
  location: '',
  period_start: '',
  period_end: '',
  operational_info: '',
  notes: '',
  status: 'Draft',
});

const navItems = [
  ['Overview', LayoutDashboard],
  ['New Batch', Plus],
  ['Vehicle Records', Car],
  ['Generated Drafts', FileText],
  ['Templates', Settings],
] as const;

const today = new Date().toLocaleDateString();

type NoteKind = 'ok' | 'warn' | 'error';

// Run background work over a list with a small concurrency limit so
// photo review never saturates the connection the user is working on.
async function mapLimit<T>(items: T[], limit: number, worker: (item: T) => Promise<void>) {
  let cursor = 0;
  const runners = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (cursor < items.length) {
      const item = items[cursor];
      cursor += 1;
      await worker(item);
    }
  });
  await Promise.all(runners);
}

function App() {
  const [tab, setTab] = useState('Overview');
  const [dashboard, setDashboard] = useState<any>({});
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [batch, setBatch] = useState<Batch>(newBatch());
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [uploads, setUploads] = useState<UploadRecord[]>([]);
  const [message, setMessage] = useState<{ text: string; kind: NoteKind } | null>(null);
  const [warnings, setWarnings] = useState<any>({});
  const [busy, setBusy] = useState('');
  const [aiReview, setAiReview] = useState({ state: 'idle', total: 0, done: 0, errors: 0 });
  const [aiResults, setAiResults] = useState<Record<number, any>>({});
  const [drafts, setDrafts] = useState<any[]>([]);
  const [draftsLoading, setDraftsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messageTimer = useRef<number | undefined>(undefined);

  const note = useCallback((text: string, kind: NoteKind = 'ok') => setMessage({ text, kind }), []);

  const loadDashboard = useCallback(async () => {
    try {
      setDashboard(await api('/dashboard'));
    } catch (error: any) {
      note(error.detail || 'The dashboard could not be loaded.', 'error');
    } finally {
      setDashboardLoading(false);
    }
  }, [note]);

  const loadBatch = useCallback(async (id: string) => {
    const [loadedBatch, loadedVehicles, loadedUploads] = await Promise.all([
      api('/batches/' + id),
      api('/batches/' + id + '/vehicles'),
      api('/batches/' + id + '/uploads'),
    ]);
    setBatch(loadedBatch);
    setVehicles(loadedVehicles);
    setUploads(loadedUploads);
    setWarnings({});
    setAiReview({ state: 'idle', total: 0, done: 0, errors: 0 });
    setAiResults({});
    setTab('Batch');
  }, []);

  const loadDrafts = useCallback(async () => {
    setDraftsLoading(true);
    try {
      setDrafts(await api('/drafts'));
    } catch (error: any) {
      note(error.detail || 'The draft center could not be loaded.', 'error');
    } finally {
      setDraftsLoading(false);
    }
  }, [note]);

  const navigateTab = useCallback((next: string) => {
    setTab(next);
    setSidebarOpen(false);
    if (next === 'Generated Drafts') void loadDrafts();
  }, [loadDrafts]);

  const dismissMessage = useCallback(() => setMessage(null), []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    if (!message) return;
    window.clearTimeout(messageTimer.current);
    messageTimer.current = window.setTimeout(() => setMessage(null), 6500);
    return () => window.clearTimeout(messageTimer.current);
  }, [message]);

  const openBatch = useCallback(async (id: string) => {
    setBusy('Opening batch…');
    try {
      await loadBatch(id);
    } catch (error: any) {
      note(error.detail || 'Unable to open this batch.', 'error');
    } finally {
      setBusy('');
    }
  }, [loadBatch, note]);

  const saveBatch = useCallback(async (submitted: Batch) => {
    setBusy('Saving batch…');
    try {
      let saved: Batch;
      try {
        saved = await api('/batches', { method: 'POST', body: JSON.stringify(submitted) });
      } catch (error: any) {
        if (!submitted.batch_id) throw error;
        saved = await api('/batches/' + submitted.batch_id, { method: 'PUT', body: JSON.stringify(submitted) });
      }
      await Promise.all([loadBatch(saved.batch_id), loadDashboard()]);
      note('Batch saved. Start by uploading all vehicle photos for this operation.');
    } catch (error: any) {
      note(error.detail || 'Unable to save this batch.', 'error');
    } finally {
      setBusy('');
    }
  }, [loadBatch, loadDashboard, note]);

  const addVehicle = useCallback(async () => {
    if (!batch.batch_id) return;
    setBusy('Adding vehicle record…');
    try {
      const vehicle = await api('/batches/' + batch.batch_id + '/vehicles', {
        method: 'POST',
        body: JSON.stringify({
          category: 'MC',
          recovery_date: batch.incident_date,
          recovery_place: batch.location,
        }),
      });
      setVehicles((current) => [...current, vehicle]);
      note('New vehicle record added. Fill in its details, then match its photos below.');
    } catch (error: any) {
      note(error.detail || 'Unable to add a vehicle record.', 'error');
    } finally {
      setBusy('');
    }
  }, [batch.batch_id, batch.incident_date, batch.location, note]);

  const reviewPhotos = useCallback(async (photos: UploadRecord[]) => {
    let done = 0;
    let errors = 0;
    await mapLimit(photos, 3, async (photo) => {
      try {
        const result = await api('/uploads/' + photo.id + '/analyze', { method: 'POST' });
        setAiResults((current) => ({ ...current, [photo.id]: result }));
      } catch {
        errors += 1;
      } finally {
        done += 1;
        setAiReview({ state: done === photos.length ? 'done' : 'running', total: photos.length, done, errors });
      }
    });
    if (errors) note('Photos are saved. ' + errors + ' photo review' + (errors === 1 ? '' : 's') + ' could not complete; you can continue manually.', 'warn');
    else note('Photo review finished. Match each photo to the correct vehicle when ready.');
  }, [note]);

  const uploadPhotos = useCallback(async (eventOrFiles: React.ChangeEvent<HTMLInputElement> | File[]) => {
    const files = Array.isArray(eventOrFiles) ? eventOrFiles : Array.from(eventOrFiles.target.files || []);
    if (!Array.isArray(eventOrFiles)) eventOrFiles.currentTarget.value = '';
    if (!files.length || !batch.batch_id) return;
    setBusy('Uploading ' + files.length + ' photo' + (files.length === 1 ? '' : 's') + '…');
    try {
      const form = new FormData();
      files.forEach((file) => form.append('files', file));
      const added: UploadRecord[] = await api('/batches/' + batch.batch_id + '/photos', {
        method: 'POST',
        body: form,
      });
      setUploads((current) => [...current, ...added]);
      note(added.length + ' photo' + (added.length === 1 ? '' : 's') + ' saved. Photo review is now running in the background.');
      setAiReview({ state: 'running', total: added.length, done: 0, errors: 0 });
      void reviewPhotos(added);
    } catch (error: any) {
      note(error.detail || 'Photo upload failed.', 'error');
    } finally {
      setBusy('');
    }
  }, [batch.batch_id, reviewPhotos, note]);

  const associatePhoto = useCallback(async (uploadId: number, vehicleId: string) => {
    setBusy('Saving photo match…');
    try {
      const updated = await api('/uploads/' + uploadId + '/associate?vehicle_id=' + (vehicleId || ''), { method: 'PATCH' });
      setUploads((current) => current.map((item) => (item.id === uploadId ? updated : item)));
    } catch (error: any) {
      note(error.detail || 'Unable to save the photo match.', 'error');
    } finally {
      setBusy('');
    }
  }, [note]);

  const makePrimary = useCallback(async (upload: UploadRecord) => {
    if (!upload.vehicle_id) return;
    setBusy('Marking primary photo…');
    try {
      const updated = await api('/uploads/' + upload.id + '/associate?vehicle_id=' + upload.vehicle_id + '&primary_image=true', { method: 'PATCH' });
      setUploads((current) => current.map((item) => {
        if (item.vehicle_id !== upload.vehicle_id || item.kind !== 'PHOTO') return item;
        return item.id === updated.id ? updated : { ...item, primary_image: 0 };
      }));
      note('Primary photo selected for this vehicle.');
    } catch (error: any) {
      note(error.detail || 'Unable to select the primary photo.', 'error');
    } finally {
      setBusy('');
    }
  }, [note]);

  const deleteUpload = useCallback(async (uploadId: number) => {
    setBusy('Removing file…');
    try {
      await api('/uploads/' + uploadId, { method: 'DELETE' });
      setUploads((current) => current.filter((item) => item.id !== uploadId));
      note('File removed.');
    } catch (error: any) {
      note(error.detail || 'Unable to remove this file.', 'error');
    } finally {
      setBusy('');
    }
  }, [note]);

  const attachDocument = useCallback(async (vehicleId: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.currentTarget.value = '';
    if (!file) return;
    setBusy('Saving optional document…');
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('document_type', 'Possessor ID/license');
      const saved = await api('/vehicles/' + vehicleId + '/attachments', { method: 'POST', body: form });
      setUploads((current) => [...current, saved]);
      note('Optional document saved to this vehicle.');
    } catch (error: any) {
      note(error.detail || 'Unable to save this document.', 'error');
    } finally {
      setBusy('');
    }
  }, [note]);

  const editVehicle = useCallback(async (vehicle: Vehicle) => {
    setBusy('Saving vehicle details…');
    try {
      const updated = await api('/vehicles/' + vehicle.id, { method: 'PUT', body: JSON.stringify(vehicle) });
      setVehicles((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      note('Vehicle details saved.');
    } catch (error: any) {
      note(error.detail || 'Unable to save vehicle details.', 'error');
    } finally {
      setBusy('');
    }
  }, [note]);

  const deleteVehicle = useCallback(async (vehicleId: number) => {
    if (!window.confirm('Remove this vehicle record? Its uploaded files will stay in the batch as unmatched files.')) return;
    setBusy('Removing vehicle record…');
    try {
      await api('/vehicles/' + vehicleId, { method: 'DELETE' });
      setVehicles((current) => current.filter((item) => item.id !== vehicleId));
      setUploads((current) => current.map((item) => item.vehicle_id === vehicleId ? { ...item, vehicle_id: null, primary_image: 0 } : item));
      note('Vehicle record removed. Its photos are still safe in the upload inbox.');
    } catch (error: any) {
      note(error.detail || 'Unable to remove this vehicle record.', 'error');
    } finally {
      setBusy('');
    }
  }, [note]);

  const validate = useCallback(async () => {
    setBusy('Checking required fields…');
    try {
      setWarnings(await api('/batches/' + batch.batch_id + '/validate'));
      note('Validation complete. Review only the items shown below.');
    } catch (error: any) {
      note(error.detail || 'Validation failed.', 'error');
    } finally {
      setBusy('');
    }
  }, [batch.batch_id, note]);

  const generate = useCallback(async (kind: string) => {
    setBusy('Preparing ' + kind + ' draft…');
    try {
      const result = await api('/batches/' + batch.batch_id + '/draft/' + kind, { method: 'POST' });
      note(kind + ' draft is ready: ' + result.validation_status);
      void loadDashboard();
    } catch (error: any) {
      setWarnings(error.detail || error);
      note('Resolve blocking items before generating a draft.', 'error');
    } finally {
      setBusy('');
    }
  }, [batch.batch_id, loadDashboard, note]);

  const goNew = useCallback(() => {
    setBatch(newBatch());
    setVehicles([]);
    setUploads([]);
    setWarnings({});
    note('Create one batch for the operation or reporting day.');
    setTab('New Batch');
  }, [note]);

  return (
    <div className="app-shell">
      <aside className={sidebarOpen ? 'sidebar open' : 'sidebar'}>
        <div className="brand-lockup">
          <div className="brand-mark"><ShieldCheck size={19} /></div>
          <div><strong>GSCHPT</strong><span>REPORTING DESK</span></div>
        </div>
        <nav className="nav-list" aria-label="Main navigation">
          {navItems.map(([name, Icon]) => (
            <button key={name} className={tab === name ? 'nav-item active' : 'nav-item'} onClick={() => navigateTab(name)}>
              <Icon size={17} /><span>{name}</span>
            </button>
          ))}
        </nav>
        <div className="privacy-badge"><LockKeyhole size={15} /><span>Private workspace<br /><small>Draft outputs only</small></span></div>
      </aside>
      {sidebarOpen && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}

      <main className="main-content">
        <header className="topbar">
          <div className="mobile-brand"><div className="brand-mark"><ShieldCheck size={17} /></div><strong>GSCHPT</strong></div>
          <div><div className="breadcrumb">OPERATIONS <span>/</span> {tab.toUpperCase()}</div><h1>{tab === 'Overview' ? 'Reporting dashboard' : tab}</h1></div>
          <div className="topbar-right"><span className="manila-dot" /> Asia/Manila <span className="today">{today}</span><button className="mobile-menu" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={19} /></button></div>
        </header>

        <div className="page-enter" key={tab}>
          {tab === 'Overview' && <Overview dashboard={dashboard} openBatch={openBatch} newBatch={goNew} loading={dashboardLoading} />}
          {tab === 'New Batch' && <BatchForm initialBatch={batch} save={saveBatch} busy={busy} />}
          {tab === 'Batch' && (
            <BatchWorkspace
              batch={batch}
              vehicles={vehicles}
              uploads={uploads}
              aiReview={aiReview}
              aiResults={aiResults}
              addVehicle={addVehicle}
              uploadPhotos={uploadPhotos}
              associatePhoto={associatePhoto}
              makePrimary={makePrimary}
              deleteUpload={deleteUpload}
              attachDocument={attachDocument}
              editVehicle={editVehicle}
              deleteVehicle={deleteVehicle}
              validate={validate}
              warnings={warnings}
              generate={generate}
              busy={busy}
            />
          )}
          {tab === 'Generated Drafts' && <DraftCenter drafts={drafts} refresh={loadDrafts} loading={draftsLoading} />}
          {['Vehicle Records', 'Templates'].includes(tab) && (
            <section className="empty-state card-surface"><div className="empty-icon"><Settings size={24} /></div><h2>{tab}</h2><p>Open a batch to review its records and private files. The workspace keeps your originals private and generates drafts only.</p></section>
          )}
        </div>
      </main>

      <div className="floating-stack">
        {message && (
          <div className={message.kind === 'error' ? 'toast error' : message.kind === 'warn' ? 'toast warn' : 'toast'} role="status">
            {message.kind === 'error' ? <AlertCircle size={16} /> : <Check size={16} />}
            <span>{message.text}</span>
            <button aria-label="Dismiss message" onClick={dismissMessage}><X size={15} /></button>
          </div>
        )}
        {busy && (
          <div className="busy-bar" role="status">
            <LoaderCircle size={15} className="spin" /> {busy}<small>Local save in progress</small>
          </div>
        )}
      </div>
    </div>
  );
}

const DraftCenter = memo(function DraftCenter({ drafts, refresh, loading }: any) {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [weeklyType, setWeeklyType] = useState('DOCX');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ text: string; kind: NoteKind } | null>(null);

  const downloadDraft = async (draft: any) => {
    try {
      const response = await fetch(API + '/drafts/' + draft.id + '/download', { headers: H });
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = draft.filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setNotice({ text: 'The private draft could not be downloaded.', kind: 'error' });
    }
  };

  const createWeekly = async () => {
    if (!start || !end) {
      setNotice({ text: 'Choose both dates for the reporting week.', kind: 'warn' });
      return;
    }
    setBusy(true);
    try {
      await api('/reports/weekly', { method: 'POST', body: JSON.stringify({ period_start: start, period_end: end, file_type: weeklyType }) });
      setNotice({ text: 'Weekly draft generated from all batches in that period.', kind: 'ok' });
      await refresh();
    } catch (error: any) {
      const detail = error.detail;
      setNotice({ text: detail?.message || detail || 'Weekly draft could not be generated.', kind: 'error' });
    } finally {
      setBusy(false);
    }
  };

  return <section className="draft-center-page">
    <div className="page-hero compact-hero"><div><div className="kicker"><span className="kicker-dot" /> OUTPUT CONTROL ROOM</div><h2>Drafts that are ready to download.</h2><p>Daily records stay separate. Weekly DOCX and PPTX drafts compile every batch inside the selected Asia/Manila period.</p></div><div className="hero-stat"><strong>{drafts.length}</strong><span>private drafts</span></div></div>
    <section className="card-surface weekly-builder"><div className="builder-copy"><div className="section-icon"><CalendarDays size={19} /></div><div><h3>Build a weekly report</h3><p>Select the scheduled week once. The system compiles all matching batches into one document or presentation.</p></div></div><div className="builder-controls"><label>From<input type="date" value={start} onChange={(event) => setStart(event.target.value)} /></label><label>To<input type="date" value={end} onChange={(event) => setEnd(event.target.value)} /></label><label>Format<select value={weeklyType} onChange={(event) => setWeeklyType(event.target.value)}><option value="DOCX">Weekly DOCX</option><option value="PPTX">Weekly PPTX</option></select></label><button className="button button-primary" onClick={createWeekly} disabled={busy}>{busy ? 'Building…' : 'Build weekly draft'} <ArrowRight size={15} /></button></div>{notice && <div className={notice.kind === 'error' ? 'inline-notice error' : notice.kind === 'warn' ? 'inline-notice warn' : 'inline-notice'}>{notice.kind === 'error' ? <AlertCircle size={15} /> : notice.kind === 'warn' ? <CircleHelp size={15} /> : <CheckCircle2 size={15} />} {notice.text}</div>}</section>
    <section className="card-surface draft-list-card"><div className="section-title"><div><div className="kicker">PRIVATE OUTPUTS</div><h2>Generated drafts</h2></div><button className="quiet-button" onClick={refresh} disabled={loading}><RefreshCw size={14} className={loading ? 'spin' : undefined} /> Refresh</button></div>
    {loading && drafts.length === 0 ? <div className="draft-list">{[0, 1, 2].map((index) => <div className="draft-row" key={index} aria-hidden="true"><div className="skeleton-block icon" /><div className="draft-row-copy"><strong className="skeleton-block w-80" /><span className="skeleton-block w-60" /></div></div>)}<div className="sr-only">Loading drafts…</div></div> : drafts.length === 0 ? <div className="blank-state"><FileText size={21} /><p>No drafts yet. Validate a batch or build a weekly report above.</p></div> : <div className="draft-list">{drafts.map((draft: any) => <div className="draft-row" key={draft.id}><div className="draft-file-icon"><FileText size={18} /></div><div className="draft-row-copy"><strong>{draft.filename}</strong><span>{draft.file_type} · {draft.validation_status} · {draft.generated_at}</span></div><button className="button button-secondary small-button" onClick={() => downloadDraft(draft)}><Download size={14} /> Download</button></div>)}</div>}</section>
  </section>;
});

const Overview = memo(function Overview({ dashboard, openBatch, newBatch: startNew, loading }: any) {
  return <>
    <section className="hero-panel">
      <div className="hero-copy"><div className="kicker"><span className="kicker-dot" /> REPORT PREPARATION</div><h2>Move from <em>collected files</em> to a clean draft.</h2><p>Upload the operation’s photos once, match them to vehicle records, then generate your daily or weekly report.</p><button className="button button-primary" onClick={startNew}><Plus size={17} /> Start a batch <ArrowRight size={16} /></button></div>
      <div className="hero-orbit"><div className="orbit-ring ring-one" /><div className="orbit-ring ring-two" /><div className="orbit-core"><FileCheck2 size={32} /><span>Draft<br />ready</span></div></div>
    </section>
    {loading ? <>
      <div className="stat-strip">
        {[0, 1, 2].map((index) => <div className="stat-card" key={index} aria-hidden="true"><div className="skeleton-block icon" /><div className="stat-copy"><span className="skeleton-block w-60" /><strong className="skeleton-block tall w-40" /></div></div>)}
      </div>
      <section className="card-surface recent-card">
        <div className="section-title"><div><div className="kicker">RECENT ACTIVITY</div><h2>Recent batches</h2></div></div>
        {[0, 1, 2].map((index) => <div className="recent-row" key={index} aria-hidden="true"><div className="skeleton-block icon" /><div className="recent-copy"><strong className="skeleton-block w-80" /><span className="skeleton-block w-60" /></div></div>)}
        <div className="sr-only">Loading dashboard…</div>
      </section>
    </> : <>
      <div className="stat-strip"><Stat label="Total batches" value={dashboard.total_batches || 0} icon={<LayoutDashboard size={17} />} /><Stat label="Drafts generated" value={dashboard.draft_reports || 0} icon={<FileText size={17} />} /><Stat label="Vehicles to review" value={dashboard.records_review || 0} icon={<Car size={17} />} /></div>
      <section className="card-surface recent-card"><div className="section-title"><div><div className="kicker">RECENT ACTIVITY</div><h2>Recent batches</h2></div><button className="quiet-button" onClick={startNew}><Plus size={15} /> New batch</button></div>{(dashboard.recent_batches || []).length ? (dashboard.recent_batches || []).map((item: any) => <div className="recent-row" key={item.batch_id}><div className="batch-avatar">{item.batch_id.slice(-2)}</div><div className="recent-copy"><strong>{item.title || item.batch_id}</strong><span>{item.batch_id} · {item.location} · prepared {item.preparation_date}</span></div><span className="status-chip">Draft</span><button className="link-button" onClick={() => openBatch(item.batch_id)}>Open <ArrowRight size={15} /></button></div>) : <div className="blank-state"><ImagePlus size={22} /><p>No batches yet. Start with one operation or reporting day.</p></div>}</section>
    </>}
  </>;
});

const Stat = memo(function Stat({ label, value, icon }: any) {
  return <div className="stat-card"><div className="stat-icon">{icon}</div><div><span>{label}</span><strong>{value}</strong></div></div>;
});

const BatchForm = memo(function BatchForm({ initialBatch, save, busy }: any) {
  const [draft, setDraft] = useState<Batch>(initialBatch);
  useEffect(() => setDraft(initialBatch), [initialBatch]);
  const update = (key: keyof Batch, value: string) => setDraft((current) => ({ ...current, [key]: value }));
  return <section className="form-layout"><div className="form-intro"><div className="kicker"><span className="kicker-dot" /> STEP 1 OF 3</div><h2>Create one operation batch.</h2><p>Keep all files from the same operation together. You can add vehicle records after the photos are safely uploaded.</p><div className="process-note"><CircleHelp size={17} /><span><strong>Preparation date</strong> is recorded automatically in Asia/Manila. It is separate from the incident date.</span></div></div><section className="card-surface form-card"><div className="card-heading"><div><span className="step-number">01</span><div><h3>Batch details</h3><p>Only the incident facts needed to start.</p></div></div></div><form onSubmit={(event) => { event.preventDefault(); void save(draft); }}><Field label="Batch ID" value={draft.batch_id} required onChange={(value: string) => update('batch_id', value)} placeholder="GSCHPT-2026-001" /><Field label="Short title or reference" value={draft.title} onChange={(value: string) => update('title', value)} placeholder="Weekly recovery operations" /><div className="field-grid"><Field label="Incident date" type="date" value={draft.incident_date} required onChange={(value: string) => update('incident_date', value)} /><Field label="Incident time" type="time" value={draft.incident_time} required onChange={(value: string) => update('incident_time', value)} /><Field label="Weekly period start" type="date" value={draft.period_start} onChange={(value: string) => update('period_start', value)} /><Field label="Weekly period end" type="date" value={draft.period_end} onChange={(value: string) => update('period_end', value)} /></div><Field label="Incident / recovery location" value={draft.location} required onChange={(value: string) => update('location', value)} placeholder="Barangay, city, province" /><FieldArea label="Operational information" value={draft.operational_info} onChange={(value: string) => update('operational_info', value)} placeholder="Optional count or operation notes" /><FieldArea label="Notes" value={draft.notes} onChange={(value: string) => update('notes', value)} placeholder="Optional" /><button className="button button-primary" disabled={Boolean(busy)}>{busy || 'Save and continue'} <ArrowRight size={16} /></button></form></section></section>;
});

const Field = memo(function Field({ label, value, onChange, type = 'text', required = false, placeholder = '' }: any) {
  return <label className="field-label">{label}{required && <span className="required-mark">Required</span>}<input required={required} type={type} value={value || ''} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} /></label>;
});

const FieldArea = memo(function FieldArea({ label, value, onChange, placeholder }: any) {
  return <label className="field-label">{label}<textarea value={value || ''} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} /></label>;
});

const BatchWorkspace = memo(function BatchWorkspace(props: any) {
  const { batch, vehicles, uploads, aiReview, aiResults, addVehicle, uploadPhotos, associatePhoto, makePrimary, deleteUpload, attachDocument, editVehicle, deleteVehicle, validate, warnings, generate, busy } = props;
  const [photoFilter, setPhotoFilter] = useState('all');
  const photos = useMemo(() => uploads.filter((item: UploadRecord) => item.kind === 'PHOTO'), [uploads]);
  const documents = useMemo(() => uploads.filter((item: UploadRecord) => item.kind === 'DOCUMENT'), [uploads]);
  const matchedPhotos = useMemo(() => photos.filter((item: UploadRecord) => item.vehicle_id), [photos]);
  const visiblePhotos = useMemo(() => photoFilter === 'matched' ? matchedPhotos : photoFilter === 'unmatched' ? photos.filter((item: UploadRecord) => !item.vehicle_id) : photos, [photoFilter, matchedPhotos, photos]);
  const readyCount = useMemo(() => vehicles.filter((vehicle: Vehicle) => vehicle.review_status === 'Reviewed').length, [vehicles]);
  const blocking = warnings.blocking || [];
  const review = warnings.review || [];
  return <section className="workspace-page">
    <div className="workspace-heading"><div><div className="kicker"><span className="kicker-dot" /> BATCH / {batch.batch_id}</div><h2>{batch.title || 'Untitled operation'}</h2><p>{batch.incident_date} at {batch.incident_time} · {batch.location} <span className="heading-separator">•</span> report period {batch.period_start || 'not set'} to {batch.period_end || 'not set'}</p></div><span className="draft-badge"><span /> Draft</span></div>
    <div className="stepper"><Step active done={photos.length > 0} number="1" title="Upload photos" /><div className="step-line" /><Step active={vehicles.length > 0} done={vehicles.length > 0} number="2" title="Match records" /><div className="step-line" /><Step active={Boolean(warnings.can_generate)} done={false} number="3" title="Generate drafts" /></div>
    <div className="readiness-strip"><div><span>PHOTOS</span><strong>{photos.length}</strong><small>{matchedPhotos.length} matched</small></div><div><span>VEHICLES</span><strong>{vehicles.length}</strong><small>{readyCount} reviewed</small></div><div><span>DOCUMENTS</span><strong>{documents.length}</strong><small>optional</small></div><div className={warnings.can_generate ? 'readiness-state ready' : 'readiness-state'}><CheckCircle2 size={16} /><span>{warnings.can_generate ? 'Ready to generate' : 'Run a check before generating'}</span></div></div>
    <div className="workspace-columns">
      <div className="workspace-main">
        <section className="card-surface upload-card"><div className="card-heading"><div><span className="step-number">01</span><div><h3>Upload all vehicle photos</h3><p>Do this once. You can match photos after everything is saved.</p></div></div><span className="count-pill">{photos.length} photo{photos.length === 1 ? '' : 's'}</span></div><label className="dropzone" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); void uploadPhotos(Array.from(event.dataTransfer.files)); }}><div className="dropzone-icon"><Upload size={21} /></div><div><strong>Drop photos here or choose files</strong><span>JPG, PNG or WebP · up to 20 MB each</span></div><span className="button button-secondary small-button">Choose files</span><input type="file" multiple accept="image/jpeg,image/png,image/webp" onChange={uploadPhotos} hidden /></label><p className="helper-line"><LockKeyhole size={14} /> Files are stored privately. <strong>Do not add ID/license files here.</strong> Add those only inside the vehicle they belong to.</p>{aiReview.state !== 'idle' && <AiStatus review={aiReview} />}{photos.length > 0 && <><div className="file-toolbar"><div><Filter size={14} /> Show</div><button className={photoFilter === 'all' ? 'filter-chip active' : 'filter-chip'} onClick={() => setPhotoFilter('all')}>All {photos.length}</button><button className={photoFilter === 'unmatched' ? 'filter-chip active' : 'filter-chip'} onClick={() => setPhotoFilter('unmatched')}>Unmatched {photos.length - matchedPhotos.length}</button><button className={photoFilter === 'matched' ? 'filter-chip active' : 'filter-chip'} onClick={() => setPhotoFilter('matched')}>Matched {matchedPhotos.length}</button></div><div className="file-list">{visiblePhotos.map((photo: UploadRecord) => <PhotoRow key={photo.id} photo={photo} vehicles={vehicles} result={aiResults[photo.id]} associate={associatePhoto} makePrimary={makePrimary} remove={deleteUpload} />)}{visiblePhotos.length === 0 && <div className="blank-state"><Search size={18} /><p>No files in this view.</p></div>}</div></>}{documents.length > 0 && <div className="document-summary"><Paperclip size={15} /><span>{documents.length} optional document{documents.length === 1 ? '' : 's'} attached to vehicle records</span></div>}</section>

        <section className="card-surface vehicle-card-section"><div className="card-heading"><div><span className="step-number">02</span><div><h3>Match and complete vehicles</h3><p>One record per actual vehicle — never one record per photo.</p></div></div><button className="button button-secondary small-button" onClick={addVehicle} disabled={Boolean(busy)}><Plus size={15} /> Add vehicle</button></div>{vehicles.length === 0 ? <div className="vehicle-empty"><div className="vehicle-empty-icon"><Car size={24} /></div><div><strong>Upload first, then add one record per vehicle.</strong><p>This keeps duplicate records out of your batch. Your photos are already safe above.</p></div><button className="link-button" onClick={addVehicle}>Add first vehicle <ArrowRight size={15} /></button></div> : <div className="vehicle-list">{vehicles.map((vehicle: Vehicle, index: number) => <VehicleCard key={vehicle.id} vehicle={vehicle} index={index} uploads={uploads} onSave={editVehicle} onDelete={deleteVehicle} attachDocument={attachDocument} busy={busy} />)}</div>}</section>
      </div>
      <aside className="generation-panel"><div className="generation-top"><div className="kicker"><span className="kicker-dot" /> STEP 3 OF 3</div><h3>Check, then generate</h3><p>Validation is instant and local. AI is not triggered by these buttons.</p></div><button className="button button-secondary full-button" onClick={validate} disabled={Boolean(busy)}><ScanSearch size={16} /> Check required fields</button>{blocking.length > 0 && <div className="validation-box error-box"><strong><AlertCircle size={15} /> Needs attention</strong>{blocking.map((item: string) => <span key={item}>{item}</span>)}</div>}{review.length > 0 && <div className="validation-box review-box"><strong><CircleHelp size={15} /> Review before submitting</strong>{review.map((item: string) => <span key={item}>{item}</span>)}</div>}{!blocking.length && !review.length && warnings.can_generate && <div className="validation-box success-box"><strong><Check size={15} /> Ready for draft generation</strong><span>All required fields are present.</span></div>}<div className="draft-actions"><button className="draft-button" onClick={() => generate('TXT')} disabled={Boolean(busy)}><FileText size={16} /><span><strong>Daily TXT</strong><small>Fast text draft</small></span><ArrowRight size={15} /></button><button className="draft-button" onClick={() => generate('DOCX')} disabled={Boolean(busy)}><FileCheck2 size={16} /><span><strong>Weekly DOCX</strong><small>Uses your master template</small></span><ArrowRight size={15} /></button><button className="draft-button" onClick={() => generate('PPTX')} disabled={Boolean(busy)}><Send size={16} /><span><strong>Weekly PPTX</strong><small>Uses your master template</small></span><ArrowRight size={15} /></button></div><div className="ai-boundary"><Sparkles size={15} /><div><strong>AI review happens after upload</strong><span>Matching, saving, validation and draft generation do not call AI.</span></div></div></aside>
    </div>
  </section>;
});

const Step = memo(function Step({ number, title, active, done }: any) {
  return <div className={active ? 'step active' : 'step'}><span className={done ? 'step-circle done' : 'step-circle'}>{done ? <Check size={13} /> : number}</span><span>{title}</span></div>;
});

const AiStatus = memo(function AiStatus({ review }: any) {
  const finished = review.state === 'done';
  return <div className={finished && !review.errors ? 'ai-status complete' : 'ai-status'}><div className="ai-status-icon">{finished ? <Check size={15} /> : <LoaderCircle size={15} className="spin" />}</div><div><strong>{finished ? 'Photo review finished' : 'Photo review is running in the background'}</strong><span>{review.done} of {review.total} files reviewed{review.errors ? ' · ' + review.errors + ' unavailable' : ''}. You can keep matching photos while this runs.</span></div></div>;
});

const PhotoRow = memo(function PhotoRow({ photo, vehicles, result, associate, makePrimary, remove }: any) {
  const summary = result ? (typeof result === 'string' ? result : result.summary || result.description || result.suggestion || 'Review result available') : '';
  const status = photo.primary_image ? 'Primary photo' : photo.vehicle_id ? 'Matched to a vehicle' : 'Needs matching';
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const urlRef = useRef<string | null>(null);

  const closePreview = useCallback(() => {
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    urlRef.current = null;
    setPreviewUrl(null);
    setPreviewLoading(false);
  }, []);

  useEffect(() => () => {
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
  }, []);

  const togglePreview = useCallback(async () => {
    if (previewLoading) return;
    if (previewUrl) { closePreview(); return; }
    setPreviewLoading(true);
    try {
      const response = await fetch(API + '/uploads/' + photo.id + '/download', { headers: H });
      if (!response.ok) throw new Error('Preview failed');
      const url = URL.createObjectURL(await response.blob());
      urlRef.current = url;
      setPreviewUrl(url);
    } catch {
      urlRef.current = null;
      setPreviewUrl(null);
    } finally {
      setPreviewLoading(false);
    }
  }, [photo.id, previewUrl, previewLoading, closePreview]);

  return <div className="photo-row">
    <button type="button" className={previewLoading ? 'photo-thumb loading' : 'photo-thumb'} aria-label={'Preview ' + photo.filename} title="Preview photo" onClick={() => void togglePreview()}>
      {previewUrl ? <Eye size={17} /> : previewLoading ? <LoaderCircle size={15} className="spin" /> : <ImagePlus size={17} />}
    </button>
    <div className="photo-details">
      <strong>{photo.filename}</strong>
      <span>{summary ? status + ' · ' + summary : status}</span>
    </div>
    <select aria-label={'Match ' + photo.filename + ' to a vehicle'} value={photo.vehicle_id || ''} onChange={(event) => associate(photo.id, event.target.value)}><option value="">Unmatched</option>{vehicles.map((vehicle: Vehicle, index: number) => <option key={vehicle.id} value={vehicle.id}>{index + 1}. {vehicle.category} · {vehicle.plate_or_sticker || 'No plate yet'}</option>)}</select>
    {photo.vehicle_id && <button className={photo.primary_image ? 'mini-action selected' : 'mini-action'} title="Use as primary photo" onClick={() => makePrimary(photo)}><Check size={14} /></button>}
    <button className="icon-button danger" aria-label={'Remove ' + photo.filename} onClick={() => remove(photo.id)}><Trash2 size={15} /></button>
    {previewUrl && <div className="photo-preview"><img src={previewUrl} alt={'Preview of ' + photo.filename} loading="lazy" /></div>}
  </div>;
});

const VehicleCard = memo(function VehicleCard({ vehicle, index, uploads, onSave, onDelete, attachDocument, busy }: any) {
  const [draft, setDraft] = useState<Vehicle>(vehicle);
  useEffect(() => setDraft(vehicle), [vehicle]);
  const vehiclePhotos = useMemo(() => uploads.filter((item: UploadRecord) => item.kind === 'PHOTO' && item.vehicle_id === vehicle.id), [uploads, vehicle.id]);
  const vehicleDocuments = useMemo(() => uploads.filter((item: UploadRecord) => item.kind === 'DOCUMENT' && item.vehicle_id === vehicle.id), [uploads, vehicle.id]);
  const update = (key: keyof Vehicle, value: string) => setDraft((current) => ({ ...current, [key]: value }));
  return <article className="vehicle-record"><div className="vehicle-record-head"><div className="record-index">{String(index + 1).padStart(2, '0')}</div><div><div className="record-title"><strong>Vehicle {index + 1}</strong><span className="category-chip">{draft.category || 'MC'}</span></div><span className="record-subtitle">{vehiclePhotos.length} matched photo{vehiclePhotos.length === 1 ? '' : 's'} · {vehicleDocuments.length} optional document{vehicleDocuments.length === 1 ? '' : 's'}</span></div><span className={draft.review_status === 'Reviewed' ? 'review-chip done' : 'review-chip'}>{draft.review_status === 'Reviewed' ? 'Reviewed' : 'Needs details'}</span><button className="icon-button danger record-delete" title="Remove vehicle record" aria-label="Remove vehicle record" onClick={() => onDelete(vehicle.id)}><Trash2 size={15} /></button></div><div className="vehicle-fields"><label>Category<select value={draft.category || 'MC'} onChange={(event) => update('category', event.target.value)}><option value="MC">MC · Motorcycle</option><option value="MV">MV · Motor vehicle</option></select></label><label>Make<input value={draft.make || ''} placeholder="e.g. Honda" onChange={(event) => update('make', event.target.value)} /></label><label>Model / type<input value={draft.model || ''} placeholder="e.g. Click 125" onChange={(event) => update('model', event.target.value)} /></label><label>Plate / sticker<input value={draft.plate_or_sticker || ''} placeholder="Optional" onChange={(event) => update('plate_or_sticker', event.target.value)} /></label><label>Recovery date<input type="date" value={draft.recovery_date || ''} onChange={(event) => update('recovery_date', event.target.value)} /></label><label>Recovery place<input value={draft.recovery_place || ''} placeholder="Location" onChange={(event) => update('recovery_place', event.target.value)} /></label></div><div className="vehicle-record-actions"><button className="button button-secondary small-button" onClick={() => onSave(draft)} disabled={Boolean(busy)}><Check size={14} /> Save details</button><details className="optional-details"><summary><Paperclip size={14} /> Optional identity document</summary><div className="optional-copy">Only add a possessor ID/license if you have it. This is not required to continue or generate a draft.</div><label className="document-upload"><Upload size={14} /> {vehicleDocuments.length ? 'Add another document' : 'Choose ID/license file'}<input type="file" accept="image/jpeg,image/png,image/webp,application/pdf" hidden onChange={(event) => attachDocument(vehicle.id, event)} /></label></details><span className="photo-count"><ImagePlus size={14} /> {vehiclePhotos.length} photo{vehiclePhotos.length === 1 ? '' : 's'} matched</span></div></article>;
});

createRoot(document.getElementById('root')!).render(<App />);
