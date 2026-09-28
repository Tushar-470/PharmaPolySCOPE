import React, { useEffect, useState, useRef } from 'react';
import { Button, Badge, Modal, Drawer, EmptyState, LoadingState } from '../components/ui';
import { ScientificValue } from '../components/scientific';
import { Plus, Search, Eye, Trash2, FlaskConical, AlertTriangle, SlidersHorizontal } from 'lucide-react';
import { fetchPolymers, createPolymer, deletePolymer } from '../api';

const fmt = (val: any, decimals = 1, fallback = '-') => {
  if (val === null || val === undefined || val === '') return fallback;
  const n = Number(val);
  return !isNaN(n) ? n.toFixed(decimals) : String(val);
};

export default function PolymerLibrary() {
  const [polymers, setPolymers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedPolymerDetail, setSelectedPolymerDetail] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [density, setDensity] = useState<'compact' | 'regular' | 'relaxed'>('compact');
  const [saving, setSaving] = useState(false);

  // Column visibility state (Pure scientific parameters)
  const [visibleColumns, setVisibleColumns] = useState({
    abbr: true,
    family: true,
    class: true,
    mn: true,
    tg: true,
    density: true,
    hsp: true,
  });
  const [showColumnMenu, setShowColumnMenu] = useState(false);
  const columnMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (columnMenuRef.current && !columnMenuRef.current.contains(event.target as Node)) {
        setShowColumnMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const [formData, setFormData] = useState({
    polymer_id: '',
    polymer_name: '',
    abbreviation: '',
    polymer_family: 'vinylic',
    polymer_class: 'neutral',
    regulatory_status: 'FDA_IID',
    supplier: '',
    catalog_number: '',
    batch_number: '',
    mn_da: undefined as number | undefined,
    mw_da: 50000,
    pdi: 1.25,
    tg_k: 441.15,
    tg_source: 'experimental_dsc',
    density_g_cm3: 1.20,
    density_source: 'literature',
    hsp_delta_d: 17.4,
    hsp_delta_p: 8.2,
    hsp_delta_h: 11.7,
    hsp_source: 'hoftyzer_van_krevelen',
    monomer_smiles: 'C1CCN(C1=O)C=C',
    spray_drying_suitability: 'good',
    hygroscopicity: 'slightly',
    validation_status: 'draft'
  });

const N8_CORE_POLYMER_IDS = new Set([
  'POL-0001', 'POL-0002', 'POL-0003', 'POL-0004',
  'POL-0005', 'POL-0006', 'POL-0007', 'POL-0008'
]);

  const loadPolymers = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await fetchPolymers(true);
      const coreOnly = Array.isArray(data)
        ? data.filter((p: any) => N8_CORE_POLYMER_IDS.has(p.polymer_id || p.id))
              .sort((a: any, b: any) => (a.polymer_id || a.id).localeCompare(b.polymer_id || b.id))
        : [];
      setPolymers(coreOnly);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to load polymers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolymers();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    // Comprehensive client-side validation
    if (!formData.polymer_id?.trim()) {
      setErrorMsg('Polymer ID is required.');
      return;
    }
    if (!formData.polymer_name?.trim()) {
      setErrorMsg('Polymer Name is required.');
      return;
    }
    if (!formData.abbreviation?.trim()) {
      setErrorMsg('Abbreviation is required.');
      return;
    }
    if (!formData.polymer_family?.trim()) {
      setErrorMsg('Polymer Family is required.');
      return;
    }
    if (!formData.polymer_class?.trim()) {
      setErrorMsg('Polymer Class is required.');
      return;
    }
    if (!formData.monomer_smiles?.trim()) {
      setErrorMsg('Repeat Unit SMILES is required.');
      return;
    }

    const mnStr = formData.mn_da !== undefined && formData.mn_da !== null ? String(formData.mn_da).trim() : '';
    let parsedMn: number | undefined = undefined;
    if (mnStr !== '') {
      const mn = Number(mnStr);
      if (isNaN(mn) || mn <= 0) {
        setErrorMsg('Number-Average Mn must be a valid positive number (> 0 Da) when provided.');
        return;
      }
      parsedMn = mn;
    }

    const tg = Number(formData.tg_k);
    if (isNaN(tg) || tg <= 0) {
      setErrorMsg('Glass Transition Tg must be a valid positive number (K).');
      return;
    }

    const dens = Number(formData.density_g_cm3);
    if (isNaN(dens) || dens <= 0) {
      setErrorMsg('Bulk Density is required and must be a valid positive number (g/cm³).');
      return;
    }

    const dD = Number(formData.hsp_delta_d);
    const dP = Number(formData.hsp_delta_p);
    const dH = Number(formData.hsp_delta_h);
    if (isNaN(dD) || dD < 0 || isNaN(dP) || dP < 0 || isNaN(dH) || dH < 0) {
      setErrorMsg('Hansen solubility parameters (δD, δP, δH) must be valid non-negative numbers.');
      return;
    }

    setSaving(true);
    try {
      await createPolymer({
        ...formData,
        polymer_id: formData.polymer_id.trim(),
        polymer_name: formData.polymer_name.trim(),
        abbreviation: formData.abbreviation.trim(),
        polymer_family: formData.polymer_family.trim(),
        polymer_class: formData.polymer_class.trim(),
        monomer_smiles: formData.monomer_smiles.trim(),
        mn_da: parsedMn,
        mw_da: formData.mw_da ? Number(formData.mw_da) : undefined,
        pdi: Number(formData.pdi) || 1.2,
        tg_k: tg,
        density_g_cm3: dens,
        hsp_delta_d: dD,
        hsp_delta_p: dP,
        hsp_delta_h: dH,
      });
      setShowAddModal(false);
      loadPolymers();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create polymer carrier.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(`Delete user polymer '${id}'? This cannot be undone.`)) return;
    try {
      await deletePolymer(id);
      loadPolymers();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to delete polymer carrier.');
    }
  };

  const filteredPolymers = polymers.filter(p => {
    const id = p.polymer_id || p.id || '';
    const name = p.polymer_name || p.fullName || '';
    const abbr = p.abbreviation || '';
    const num = id.replace(/\D/g, '').replace(/^0+/, '');
    const q = searchTerm.trim().toLowerCase();
    return id.toLowerCase().includes(q) || 
           name.toLowerCase().includes(q) ||
           abbr.toLowerCase().includes(q) ||
           num === q ||
           `pol-${num}` === q;
  });

  return (
    <div className="page-container">
      <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <FlaskConical size={24} style={{ color: 'var(--color-primary-action)' }} />
            <h1 className="title" style={{ margin: 0 }}>Polymer Excipient Library (N=8)</h1>
          </div>
          <p style={{ color: 'var(--color-secondary-text)', margin: 0 }}>
            Verified 8-polymer ASD carrier cohort with authoritative experimental and calculated descriptors (POL-0001 through POL-0008)
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Column Visibility Control */}
          <div className="column-visibility-dropdown" ref={columnMenuRef}>
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={() => setShowColumnMenu(!showColumnMenu)}
              icon={<SlidersHorizontal size={13} />}
            >
              Columns
            </Button>
            {showColumnMenu && (
              <div className="dropdown-menu">
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-muted-text)', textTransform: 'uppercase', marginBottom: '6px', padding: '2px 6px' }}>
                  Toggle Columns
                </div>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.abbr} onChange={e => setVisibleColumns({ ...visibleColumns, abbr: e.target.checked })} />
                  <span>Abbreviation</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.family} onChange={e => setVisibleColumns({ ...visibleColumns, family: e.target.checked })} />
                  <span>Chemical Family</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.class} onChange={e => setVisibleColumns({ ...visibleColumns, class: e.target.checked })} />
                  <span>Functional Class</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.mn} onChange={e => setVisibleColumns({ ...visibleColumns, mn: e.target.checked })} />
                  <span>Molecular Weight Mn</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.tg} onChange={e => setVisibleColumns({ ...visibleColumns, tg: e.target.checked })} />
                  <span>Glass Transition Tg</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.density} onChange={e => setVisibleColumns({ ...visibleColumns, density: e.target.checked })} />
                  <span>Bulk Density</span>
                </label>
                <label className="dropdown-item">
                  <input type="checkbox" checked={visibleColumns.hsp} onChange={e => setVisibleColumns({ ...visibleColumns, hsp: e.target.checked })} />
                  <span>HSP (δD / δP / δH)</span>
                </label>
              </div>
            )}
          </div>

          {/* Density Toggle */}
          <div className="density-toggle">
            <span style={{ fontSize: '11px', textTransform: 'uppercase', marginRight: '4px' }}>Density:</span>
            <button className={density === 'compact' ? 'active' : ''} onClick={() => setDensity('compact')}>Compact</button>
            <button className={density === 'regular' ? 'active' : ''} onClick={() => setDensity('regular')}>Regular</button>
            <button className={density === 'relaxed' ? 'active' : ''} onClick={() => setDensity('relaxed')}>Relaxed</button>
          </div>

          <Button onClick={() => setShowAddModal(true)} icon={<Plus size={16} />}>
            Add Polymer Carrier
          </Button>
        </div>
      </div>

      <div className="card" style={{ padding: '0.75rem 1rem', marginBottom: '1.5rem' }}>
        <div style={{ position: 'relative', maxWidth: '400px' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-muted-text)' }} />
          <input 
            type="text" 
            placeholder="Search polymers by name, abbr, or ID..." 
            style={{ paddingLeft: '32px', height: '36px' }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {errorMsg && (
        <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <LoadingState message="Loading polymer excipient library..." rows={5} />
      ) : filteredPolymers.length === 0 ? (
        <EmptyState title="No polymers found" description="Try adjusting your search or add a new polymer carrier." />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container">
            <table className={`table-${density}`}>
              <thead>
                <tr>
                  <th className="sticky-col-1">POLYMER ID</th>
                  <th className="sticky-col-2">POLYMER NAME</th>
                  {visibleColumns.abbr && <th>ABBR</th>}
                  {visibleColumns.family && <th>FAMILY</th>}
                  {visibleColumns.class && <th>CLASS</th>}
                  {visibleColumns.mn && <th className="numeric">MN (DA)</th>}
                  {visibleColumns.tg && <th className="numeric">TG (K)</th>}
                  {visibleColumns.density && <th className="numeric">DENSITY (G/CM³)</th>}
                  {visibleColumns.hsp && <th className="numeric">HSP (δD / δP / δH)</th>}
                  <th style={{ textAlign: 'right' }}>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {filteredPolymers.map(p => {
                  const pId = p.polymer_id || p.id;
                  const pName = p.polymer_name || p.fullName;
                  const abbr = p.abbreviation || 'N/A';
                  const family = p.polymer_family || p.family || 'Vinylic';
                  const pClass = p.polymer_class || p.class || 'Neutral';
                  const mn = p.mn_da ?? p.mn;
                  const tg = p.tg_k ?? p.tg;
                  const densityVal = p.density_g_cm3 ?? p.density;
                  const dD = p.hsp_delta_d ?? p.hspD ?? 0;
                  const dP = p.hsp_delta_p ?? p.hspP ?? 0;
                  const dH = p.hsp_delta_h ?? p.hspH ?? 0;
                  const num = pId.replace(/\D/g, '').replace(/^0+/, '');
                  const isRef = p.is_reference ?? (p.status === 'Reference');

                  return (
                    <tr key={pId}>
                      <td className="mono sticky-col-1" style={{ fontWeight: 600 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ 
                            fontSize: '11px', 
                            fontWeight: 700, 
                            backgroundColor: 'var(--color-primary-action)', 
                            color: '#fff', 
                            padding: '1px 6px', 
                            borderRadius: '4px' 
                          }}>
                            #{num}
                          </span>
                          <span>{pId}</span>
                        </div>
                      </td>
                      <td className="sticky-col-2"><strong>{pName}</strong></td>
                      {visibleColumns.abbr && <td><span className="mono" style={{ fontSize: '12px' }}>{abbr}</span></td>}
                      {visibleColumns.family && <td style={{ fontSize: '12px', color: 'var(--color-secondary-text)' }}>{family}</td>}
                      {visibleColumns.class && <td style={{ fontSize: '12px', color: 'var(--color-secondary-text)' }}>{pClass}</td>}
                      {visibleColumns.mn && <td className="numeric">{typeof mn === 'number' && !isNaN(mn) ? mn.toLocaleString() : (mn ?? 'N/A')}</td>}
                      {visibleColumns.tg && <td className="numeric">{fmt(tg, 1)}</td>}
                      {visibleColumns.density && <td className="numeric">{fmt(densityVal, 3)}</td>}
                      {visibleColumns.hsp && <td className="numeric">{fmt(dD, 1)} / {fmt(dP, 1)} / {fmt(dH, 1)}</td>}
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                          <Button variant="secondary" size="sm" onClick={() => setSelectedPolymerDetail(p)}>
                            View
                          </Button>
                          {!isRef && (
                            <Button variant="danger" size="sm" onClick={() => handleDelete(pId)}>
                              <Trash2 size={13} />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Polymer Detail Drawer */}
      <Drawer 
        isOpen={!!selectedPolymerDetail} 
        onClose={() => setSelectedPolymerDetail(null)}
        title={selectedPolymerDetail?.polymer_name || selectedPolymerDetail?.fullName || 'Polymer Details'}
        width={480}
      >
        {selectedPolymerDetail && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span className="mono" style={{ fontWeight: 600, color: 'var(--color-primary-action)' }}>
                {selectedPolymerDetail.polymer_id || selectedPolymerDetail.id}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--color-muted-text)' }}>
                ({selectedPolymerDetail.abbreviation || 'N/A'})
              </span>
            </div>

            <div className="form-section">
              <div className="form-section-title">Identity & Classification</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '13px' }}>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>FAMILY</span><strong>{selectedPolymerDetail.polymer_family || selectedPolymerDetail.family || 'Vinylic'}</strong></div>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>CLASS</span><strong>{selectedPolymerDetail.polymer_class || selectedPolymerDetail.class || 'Neutral'}</strong></div>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>REGULATORY</span><strong>{selectedPolymerDetail.regulatory_status || 'FDA_IID'}</strong></div>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>SUPPLIER</span><strong>{selectedPolymerDetail.supplier || 'Standard / Generic'}</strong></div>
                <div style={{ gridColumn: 'span 2' }}>
                  <span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>REPEAT UNIT SMILES</span>
                  <div className="mono" style={{ fontSize: '11px', background: 'var(--color-surface-subtle)', padding: '6px', borderRadius: '4px', wordBreak: 'break-all' }}>
                    {selectedPolymerDetail.monomer_smiles || 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Thermophysical & Molecular Properties</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <ScientificValue label="Number-Average Mn" value={selectedPolymerDetail.mn_da ?? null} unit={selectedPolymerDetail.mn_da != null ? 'Da' : undefined} precision={0} />
                <ScientificValue label="Weight-Average Mw" value={selectedPolymerDetail.mw_da} unit="Da" precision={0} />
                <ScientificValue label="Glass Transition Tg" value={selectedPolymerDetail.tg_k} unit="K" precision={1} />
                <ScientificValue label="Bulk Density" value={selectedPolymerDetail.density_g_cm3} unit="g/cm³" precision={3} />
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Hansen Solubility Parameters (H-V-K)</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <ScientificValue label="Dispersion (δD)" value={selectedPolymerDetail.hsp_delta_d} unit="MPa½" precision={1} />
                <ScientificValue label="Polar (δP)" value={selectedPolymerDetail.hsp_delta_p} unit="MPa½" precision={1} />
                <ScientificValue label="H-Bonding (δH)" value={selectedPolymerDetail.hsp_delta_h} unit="MPa½" precision={1} />
                <ScientificValue label="Total HSP (δt)" value={selectedPolymerDetail.hsp_total} unit="MPa½" precision={1} />
              </div>
            </div>

            <div className="form-section" style={{ borderBottom: 'none' }}>
              <div className="form-section-title">ASD Processability & Properties</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '13px' }}>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>SPRAY DRYING</span><strong>{selectedPolymerDetail.spray_drying_suitability || 'Good'}</strong></div>
                <div><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>HYGROSCOPICITY</span><strong>{selectedPolymerDetail.hygroscopicity || 'Slightly'}</strong></div>
                <div style={{ gridColumn: 'span 2' }}><span style={{ color: 'var(--color-muted-text)', display: 'block', fontSize: '11px' }}>HSP METHOD</span><strong>Hoftyzer-Van Krevelen Group Contribution</strong></div>
              </div>
            </div>
          </div>
        )}
      </Drawer>

      {/* Add Polymer Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add Polymer Carrier" size="wide">
        <form onSubmit={handleSave}>
          <div className="form-section">
            <div className="form-section-title">1. Polymer Identity</div>
            <div className="form-grid form-grid-3">
              <div className="form-group">
                <label className="form-label">Polymer ID <span className="required">*</span></label>
                <input required type="text" placeholder="e.g. POL-008-2026" value={formData.polymer_id} onChange={e => setFormData({ ...formData, polymer_id: e.target.value })} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="form-label">Polymer Name <span className="required">*</span></label>
                <input required type="text" placeholder="Full chemical name (e.g. Hypromellose Acetate Succinate)" value={formData.polymer_name} onChange={e => setFormData({ ...formData, polymer_name: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Abbreviation <span className="required">*</span></label>
                <input required type="text" placeholder="e.g. HPMC_AS" value={formData.abbreviation} onChange={e => setFormData({ ...formData, abbreviation: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Chemical Family <span className="required">*</span></label>
                <select value={formData.polymer_family} onChange={e => setFormData({ ...formData, polymer_family: e.target.value })}>
                  <option value="Cellulosic">Cellulosic</option>
                  <option value="Vinylic">Vinylic</option>
                  <option value="Acrylic">Acrylic</option>
                  <option value="Polyether">Polyether</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Functional Class <span className="required">*</span></label>
                <select value={formData.polymer_class} onChange={e => setFormData({ ...formData, polymer_class: e.target.value })}>
                  <option value="Neutral">Neutral</option>
                  <option value="Enteric / Anionic">Enteric / Anionic</option>
                  <option value="Amphiphilic">Amphiphilic</option>
                  <option value="Cationic">Cationic</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">2. Monomer & Molecular Structure</div>
            <div className="form-grid form-grid-2">
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="form-label">Repeat Unit SMILES <span className="required">*</span></label>
                <input required type="text" placeholder="Monomer repeat unit SMILES" value={formData.monomer_smiles} onChange={e => setFormData({ ...formData, monomer_smiles: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Number-Average Mn <span className="unit">(Da, Optional)</span></label>
                <input type="number" min="1" step="1" placeholder="Optional (leave blank if unavailable)" value={formData.mn_da ?? ''} onChange={e => setFormData({ ...formData, mn_da: e.target.value ? parseFloat(e.target.value) : undefined })} />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">3. Thermophysical Properties</div>
            <div className="form-grid form-grid-2">
              <div className="form-group">
                <label className="form-label">Glass Transition Tg <span className="unit">(K)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="1" placeholder="e.g. 441.15" value={formData.tg_k} onChange={e => setFormData({ ...formData, tg_k: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">Bulk Density <span className="unit">(g/cm³)</span> <span className="required">*</span></label>
                <input required type="number" step="0.001" min="0.01" placeholder="e.g. 1.200" value={formData.density_g_cm3} onChange={e => setFormData({ ...formData, density_g_cm3: parseFloat(e.target.value) })} />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">4. Hansen Solubility Parameters (H-V-K)</div>
            <div className="form-grid form-grid-3">
              <div className="form-group">
                <label className="form-label">δD <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0" placeholder="e.g. 17.4" value={formData.hsp_delta_d} onChange={e => setFormData({ ...formData, hsp_delta_d: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">δP <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0" placeholder="e.g. 8.2" value={formData.hsp_delta_p} onChange={e => setFormData({ ...formData, hsp_delta_p: parseFloat(e.target.value) })} />
              </div>
              <div className="form-group">
                <label className="form-label">δH <span className="unit">(MPa½)</span> <span className="required">*</span></label>
                <input required type="number" step="0.1" min="0" placeholder="e.g. 11.7" value={formData.hsp_delta_h} onChange={e => setFormData({ ...formData, hsp_delta_h: parseFloat(e.target.value) })} />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <Button variant="secondary" type="button" onClick={() => setShowAddModal(false)}>Cancel</Button>
            <Button variant="primary" type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save Polymer Carrier'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
