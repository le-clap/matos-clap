import { Link } from 'react-router-dom';

export function LegalNoticePage() {
  return (
    <div className="mx-auto min-h-screen max-w-3xl px-4 py-10 sm:px-6">
      <Link to="/" className="text-sm text-content-muted hover:text-content">
        ← Retour
      </Link>
      <h1 className="mt-4 text-3xl font-bold tracking-tight">Mentions légales</h1>

      <div className="mt-8 space-y-8 text-sm leading-relaxed text-content-muted">
        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Responsable du site</h2>
          <p>
            C.L.A.P Centrale Lille, Commission de Centrale Lille Associations, Association Loi 1901.
            <br />
            Contact :{' '}
            <a className="text-primary hover:underline" href="mailto:clap.eclille@gmail.com">
              clap.eclille@gmail.com
            </a>
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">
            Éditeur et directeur de la publication
          </h2>
          <p>
            Le site Matos CLAP est édité par le C.L.A.P Centrale Lille. Le directeur de la
            publication est le représentant légal du C.L.A.P Centrale Lille.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Développement</h2>
          <p>Ce site a été développé par David Marembert et Yacine Hachiba en 2026.</p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Hébergement</h2>
          <p>
            Rézoléo, Association Loi 1901.
            <br />
            400 Avenue Paul Langevin, 59650 Villeneuve-d'Ascq
            <br />
            Contact :{' '}
            <a className="text-primary hover:underline" href="mailto:contact@rezoleo.fr">
              contact@rezoleo.fr
            </a>
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Données personnelles</h2>
          <p>
            Lors de la connexion via Centrale Lille Associations, votre nom, identifiant et adresse
            e-mail sont enregistrés, ainsi que vos demandes et prêts de matériel. Ces données
            servent uniquement à la gestion des prêts et ne sont pas transmises à des tiers.
            Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de
            suppression en écrivant à{' '}
            <a className="text-primary hover:underline" href="mailto:clap.eclille@gmail.com">
              clap.eclille@gmail.com
            </a>
            .
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Cookies</h2>
          <p>
            Le site utilise uniquement un cookie de session, strictement nécessaire à
            l'authentification. Aucun cookie publicitaire ou de suivi n'est déposé.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Propriété intellectuelle</h2>
          <p>
            Le logo et les contenus du site sont la propriété du C.L.A.P Centrale Lille, sauf
            mention contraire. Toute reproduction sans autorisation est interdite.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-content">Responsabilité</h2>
          <p>
            Le C.L.A.P Centrale Lille s'efforce de maintenir les informations du site exactes et à
            jour, mais ne saurait être tenu responsable d'erreurs, d'omissions ou d'une
            indisponibilité temporaire du service.
          </p>
        </section>
      </div>
    </div>
  );
}
