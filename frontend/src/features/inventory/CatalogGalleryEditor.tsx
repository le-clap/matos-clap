import { ChevronLeft, ChevronRight, Image as ImageIcon, ImagePlus, Trash2, X } from 'lucide-react';
import { type Dispatch, type SetStateAction, useEffect, useRef, useState } from 'react';
import { useToast } from '@/components/ui/Toast';
import { cn } from '@/lib/utils';

const ACCEPTED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'];
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

export type GalleryItem =
  | { kind: 'existing'; id: number; image_path: string }
  | { kind: 'new'; key: string; file: File; previewUrl: string };

export function CatalogGalleryEditor({
  gallery,
  onChange,
}: {
  gallery: GalleryItem[];
  onChange: Dispatch<SetStateAction<GalleryItem[]>>;
}) {
  const toast = useToast();
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [overIndex, setOverIndex] = useState<number | null>(null);
  const [filesOver, setFilesOver] = useState(false);

  // Revoke any pending preview URLs on unmount, whether the form was saved or cancelled.
  const galleryRef = useRef(gallery);
  useEffect(() => {
    galleryRef.current = gallery;
  });
  useEffect(
    () => () => {
      for (const item of galleryRef.current) {
        if (item.kind === 'new') URL.revokeObjectURL(item.previewUrl);
      }
    },
    [],
  );

  const addFiles = (files: File[]) => {
    const valid = files.filter(
      (file) => ACCEPTED_IMAGE_TYPES.includes(file.type) && file.size <= MAX_IMAGE_BYTES,
    );
    const skipped = files.length - valid.length;
    if (skipped > 0) {
      toast.toast({
        tone: 'warning',
        title: skipped === 1 ? '1 fichier ignoré' : `${skipped} fichiers ignorés`,
        description: 'Formats acceptés : PNG, JPEG, WebP ou GIF, 5 Mo maximum.',
      });
    }
    onChange((prev) => [
      ...prev,
      ...valid.map((file) => ({
        kind: 'new' as const,
        key: crypto.randomUUID(),
        file,
        previewUrl: URL.createObjectURL(file),
      })),
    ]);
  };

  const remove = (index: number) => {
    onChange((prev) => {
      const item = prev[index];
      if (item.kind === 'new') URL.revokeObjectURL(item.previewUrl);
      return prev.filter((_, i) => i !== index);
    });
  };

  const moveTo = (from: number, to: number) => {
    onChange((prev) => {
      if (from === to || to < 0 || to >= prev.length) return prev;
      const reordered = [...prev];
      reordered.splice(to, 0, ...reordered.splice(from, 1));
      return reordered;
    });
  };

  const endDrag = () => {
    setDragIndex(null);
    setOverIndex(null);
  };

  return (
    <div
      className={cn(
        '-m-1 flex flex-wrap gap-3 rounded-xl p-1 outline-2 outline-transparent outline-dashed',
        filesOver && 'bg-surface-raised outline-primary/60',
      )}
      onDragOver={(e) => {
        if (!e.dataTransfer.types.includes('Files')) return;
        e.preventDefault();
        setFilesOver(true);
      }}
      onDragLeave={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setFilesOver(false);
      }}
      onDrop={(e) => {
        if (!e.dataTransfer.types.includes('Files')) return;
        e.preventDefault();
        setFilesOver(false);
        addFiles(Array.from(e.dataTransfer.files));
      }}
    >
      {gallery.map((item, index) => (
        <div
          key={item.kind === 'existing' ? item.id : item.key}
          draggable
          onDragStart={(e) => {
            e.dataTransfer.effectAllowed = 'move';
            // Firefox won't start a drag without some data set.
            e.dataTransfer.setData('application/x-catalog-image', '');
            setDragIndex(index);
          }}
          onDragOver={(e) => {
            if (dragIndex === null) return;
            e.preventDefault();
            setOverIndex(index);
          }}
          onDrop={(e) => {
            if (dragIndex === null) return;
            e.preventDefault();
            moveTo(dragIndex, index);
            endDrag();
          }}
          onDragEnd={endDrag}
          className={cn(
            'relative size-20 shrink-0 cursor-grab rounded-lg active:cursor-grabbing motion-safe:transition-opacity',
            dragIndex === index && 'opacity-40',
            overIndex === index && dragIndex !== index && 'ring-2 ring-primary/60',
          )}
        >
          <img
            src={item.kind === 'existing' ? item.image_path : item.previewUrl}
            alt=""
            draggable={false}
            className={cn(
              'size-full rounded-lg border object-cover',
              item.kind === 'new' ? 'border-dashed border-border-strong' : 'border-border',
            )}
          />
          <div className="absolute inset-x-0 bottom-0 flex justify-center gap-0.5 rounded-b-lg bg-ink-950/70 py-0.5 backdrop-blur">
            <button
              type="button"
              aria-label="Déplacer avant"
              disabled={index === 0}
              onClick={() => moveTo(index, index - 1)}
              className="rounded p-0.5 text-white disabled:opacity-30"
            >
              <ChevronLeft className="size-3.5" />
            </button>
            <button
              type="button"
              aria-label="Déplacer après"
              disabled={index === gallery.length - 1}
              onClick={() => moveTo(index, index + 1)}
              className="rounded p-0.5 text-white disabled:opacity-30"
            >
              <ChevronRight className="size-3.5" />
            </button>
            <button
              type="button"
              aria-label={item.kind === 'existing' ? "Supprimer l'image" : 'Retirer'}
              onClick={() => remove(index)}
              className="rounded p-0.5 text-white"
            >
              {item.kind === 'existing' ? (
                <Trash2 className="size-3.5" />
              ) : (
                <X className="size-3.5" />
              )}
            </button>
          </div>
        </div>
      ))}
      {gallery.length === 0 && (
        <div className="flex size-20 shrink-0 items-center justify-center rounded-lg border border-border bg-surface-raised text-content-faint">
          <ImageIcon className="size-6" />
        </div>
      )}
      <label className="flex size-20 shrink-0 cursor-pointer flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-border text-content-faint transition-colors hover:border-border-strong hover:text-content-muted">
        <ImagePlus className="size-5" />
        <span className="text-[11px] font-medium">Ajouter</span>
        <input
          type="file"
          accept={ACCEPTED_IMAGE_TYPES.join(',')}
          multiple
          className="hidden"
          onChange={(e) => {
            addFiles(Array.from(e.target.files ?? []));
            e.target.value = '';
          }}
        />
      </label>
    </div>
  );
}
