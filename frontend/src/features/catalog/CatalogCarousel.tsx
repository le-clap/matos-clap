import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import type { CatalogImagePublic } from '@/client';
import { Button } from '@/components/ui/Button';

export function CatalogCarousel({ images }: { images: CatalogImagePublic[] }) {
  const [index, setIndex] = useState(0);

  if (images.length === 0) {
    return <img src="/placeholder.jpg" alt="" className="size-full object-cover" loading="lazy" />;
  }

  const current = Math.min(index, images.length - 1);

  return (
    <div className="relative size-full overflow-hidden">
      <img
        src={images[current].image_path}
        alt=""
        className="size-full object-cover"
        loading="lazy"
      />
      {images.length > 1 && (
        <>
          <Button
            variant="outline"
            size="icon-sm"
            className="absolute left-2 top-1/2 -translate-y-1/2 border-border bg-ink-950/70 backdrop-blur hover:bg-ink-950/90"
            aria-label="Image précédente"
            onClick={() => setIndex((n) => (n - 1 + images.length) % images.length)}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon-sm"
            className="absolute right-2 top-1/2 -translate-y-1/2 border-border bg-ink-950/70 backdrop-blur hover:bg-ink-950/90"
            aria-label="Image suivante"
            onClick={() => setIndex((n) => (n + 1) % images.length)}
          >
            <ChevronRight className="size-4" />
          </Button>
          <div className="absolute bottom-2 left-1/2 flex -translate-x-1/2 gap-1.5">
            {images.map((image, n) => (
              <button
                key={image.id}
                type="button"
                aria-label={`Image ${n + 1}`}
                onClick={() => setIndex(n)}
                className={`size-1.5 rounded-full transition-colors ${
                  n === current ? 'bg-white' : 'bg-white/40'
                }`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
