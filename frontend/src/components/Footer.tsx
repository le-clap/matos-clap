import { Github, Instagram, Linkedin } from 'lucide-react';
import clapLogo from '@/assets/logos/Logo CLAP.png'; // Adjust path if necessary

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full bg-zinc-950 text-zinc-400 border-t border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 py-12 md:py-16 lg:py-18">

        {/* Top Section: Logo & Tagline */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-8">
          <div className="flex items-center gap-3">
            <img src={clapLogo} alt="Logo CLAP" className="h-10 w-auto opacity-90" />
            <span className="text-xl font-bold text-white tracking-tight">LE CLAP</span>
          </div>
          <p className="text-sm md:text-base max-w-md text-zinc-500">
            Plateforme de gestion et d'emprunt de matériel audiovisuel.
          </p>
        </div>

        {/* Middle Section: Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 border-b border-zinc-800 pb-12 mb-8">

          {/* Column 1: Navigation */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Navigation</h3>
            <a href="/" className="hover:text-[#5227FF] transition-colors duration-200">Accueil</a>
            <a href="/inventory" className="hover:text-[#5227FF] transition-colors duration-200">Inventaire</a>
            <a href="/my-loans" className="hover:text-[#5227FF] transition-colors duration-200">Mes Emprunts</a>
            <a href="/new-loan" className="hover:text-[#5227FF] transition-colors duration-200">Réserver</a>
          </div>

          {/* Column 2: Support */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Aide</h3>
            <a href="/contact" className="hover:text-[#5227FF] transition-colors duration-200">Nous contacter</a>
            <a href="/faq" className="hover:text-[#5227FF] transition-colors duration-200">FAQ</a>
            <a href="/conditions" className="hover:text-[#5227FF] transition-colors duration-200">Conditions d'emprunt</a>
          </div>

          {/* Column 3: Legal */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Légal</h3>
            <a href="/privacy" className="hover:text-[#5227FF] transition-colors duration-200">Confidentialité</a>
            <a href="/terms" className="hover:text-[#5227FF] transition-colors duration-200">Mentions Légales</a>
          </div>

          {/* Column 4: Socials */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Suivez-nous !</h3>
            <div className="flex gap-4 ">
              <a href="https://github.com/le-clap" target="_blank" rel="noreferrer" className="bg-zinc-800 p-2 rounded-full hover:bg-[#5227FF] hover:text-white transition-all duration-300">
                <Github size={20} />
              </a>
              <a href="https://www.linkedin.com/company/clap-centrale-lille/" target="_blank" rel="noreferrer" className="bg-zinc-800 p-2 rounded-full hover:bg-[#5227FF] hover:text-white transition-all duration-300">
                <Linkedin size={20} />
              </a>
              <a href="https://www.instagram.com/le_clap_/" target="_blank" rel="noreferrer" className="bg-zinc-800 p-2 rounded-full hover:bg-[#5227FF] hover:text-white transition-all duration-300">
                <Instagram size={20} />
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Section: Copyright */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-medium text-zinc-600">
          <p>&copy; {currentYear} Le CLAP. Tous droits réservés.</p>
          <div className="flex gap-6">
            <span className="flex items-center gap-2">
               <span className="w-2 h-2 rounded-full bg-green-500"></span>
               System Online
            </span>
            <p>Made with ❤️ by Le CLAP</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;