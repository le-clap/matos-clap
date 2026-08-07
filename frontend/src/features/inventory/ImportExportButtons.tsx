import { Download, TriangleAlert, Upload } from 'lucide-react';
import { useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { useToast } from '@/components/ui/Toast';
import { downloadCsv, importCsv } from '@/lib/csv';

const LABELS = {
  categories: { file: 'categories.csv', noun: 'catégories' },
  catalogs: { file: 'catalogues.csv', noun: 'catalogues' },
  items: { file: 'articles.csv', noun: 'articles' },
};

export function ImportExportButtons({ entity }: { entity: 'categories' | 'catalogs' | 'items' }) {
  const qc = useQueryClient();
  const toast = useToast();
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState<'export' | 'import' | null>(null);
  const [errors, setErrors] = useState<string[] | null>(null);

  const cfg = LABELS[entity];

  const onExport = async () => {
    setBusy('export');
    try {
      await downloadCsv(`/api/io/${entity}/export`, cfg.file);
    } catch {
      toast.error('Export impossible');
    } finally {
      setBusy(null);
    }
  };

  const onPick = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ''; // allow re-importing the same filename
    if (!file) return;
    setBusy('import');
    try {
      const result = await importCsv(`/api/io/${entity}/import`, file);
      if (result.ok) {
        toast.success('Import réussi', `${result.created} créé(s), ${result.updated} mis à jour`);
        qc.invalidateQueries({ queryKey: ['categories'] });
        qc.invalidateQueries({ queryKey: ['catalogs'] });
        qc.invalidateQueries({ queryKey: ['items'] });
      } else {
        setErrors(result.errors);
      }
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" onClick={onExport} loading={busy === 'export'}>
        <Download className="size-4" /> Exporter
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => inputRef.current?.click()}
        loading={busy === 'import'}
      >
        <Upload className="size-4" /> Importer
      </Button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        className="hidden"
        onChange={onPick}
      />

      <Modal
        open={errors !== null}
        onClose={() => setErrors(null)}
        title="Import impossible"
        description={`Aucune donnée n'a été enregistrée. Corrigez les ${cfg.noun} puis réessayez.`}
        footer={
          <Button variant="ghost" onClick={() => setErrors(null)}>
            Fermer
          </Button>
        }
      >
        <div className="flex items-start gap-2.5 rounded-lg border border-danger/30 bg-danger-bg px-3 py-2.5 text-sm text-brand-200">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <span>{errors?.length} erreur(s) détectée(s) :</span>
        </div>
        <ul className="mt-3 max-h-72 space-y-1.5 overflow-y-auto text-sm text-content-muted">
          {errors?.map((err, i) => (
            <li key={i} className="rounded-md bg-surface-raised px-3 py-1.5">
              {err}
            </li>
          ))}
        </ul>
      </Modal>
    </div>
  );
}
