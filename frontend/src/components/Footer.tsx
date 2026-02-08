import {Github, Instagram, Linkedin} from 'lucide-react';
import clapLogo from '@/assets/logos/Logo CLAP.png'; // Adjust path if necessary
import RezoleoLogoWhite from '@/assets/logos/LogoRezoleoWhite.svg';
import React from 'react';
import {useNavigate} from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  const navigate = useNavigate();

  const handleNavigation = (path: string) => (e: React.MouseEvent) => {
    if (path.startsWith('/')) {
    e.preventDefault(); // Bloque le rechargement standard du navigateur
    navigate(path);     // Utilise le routeur React
    window.scrollTo(0, 0); // Remonte en haut de page après le clic
    }
  };

  return (
    <footer className="w-full bg-zinc-950 text-zinc-400 border-t border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 py-12 md:py-16 lg:py-18">

        {/* Top Section: Logo & Tagline */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-8">
          <div className="flex items-center gap-3">
            <img src={clapLogo} alt="Logo CLAP" className="h-10 w-auto"/>
            <span className="text-xl font-bold text-white tracking-tight drop-shadow-2xl">LE CLAP</span>

            <div className="h-6 w-0.5 rounded-full bg-gray-600 "></div>

            <img src={RezoleoLogoWhite} alt="Logo Rezoleo" className="h-10 mb-1 w-auto"/>
            <span className="text-3xl font-[Oceanic_Drift_Laser_Italic] tracking-wide text-white">Rezoleo</span>
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
            <div className="flex gap-10">
              <div className="flex flex-col gap-4">
                <a href="/" className="hover:text-[#5227FF] transition-colors duration-200"
                   onClick={handleNavigation('/')}>Accueil</a>
                <a href="/inventory" className="hover:text-[#5227FF] transition-colors duration-200"
                   onClick={handleNavigation('/inventory')}>Inventaire</a>
                <a href="/my-loans" className="hover:text-[#5227FF] transition-colors duration-200"
                   onClick={handleNavigation('/my-loans')}>Mes Emprunts</a>
                <a href="/new-loan" className="hover:text-[#5227FF] transition-colors duration-200"
                   onClick={handleNavigation('/new-loan')}>Réserver</a>
              </div>
              <div className="flex flex-col gap-4">
                <a href="https://my.le-clap.fr/" className="hover:text-[#5227FF] transition-colors duration-200"
                   onClick={handleNavigation('https://my.le-clap.fr/')}>MyCLAP</a>
              </div>
            </div>

          </div>

          {/* Column 2: Support */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Aide</h3>
            <a href="/contact" className="hover:text-[#5227FF] transition-colors duration-200"
               onClick={handleNavigation('/contact')}>Nous contacter</a>
            <a href="/faq" className="hover:text-[#5227FF] transition-colors duration-200"
               onClick={handleNavigation('/faq')}>FAQ</a>
            <a href="/conditions" className="hover:text-[#5227FF] transition-colors duration-200"
               onClick={handleNavigation('/conditions')}>Conditions
              d'emprunt</a>
          </div>

          {/* Column 3: Legal */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Légal</h3>
            <a href="/privacy" className="hover:text-[#5227FF] transition-colors duration-200"
               onClick={handleNavigation('/privacy')}>Confidentialité</a>
            <a href="/terms" className="hover:text-[#5227FF] transition-colors duration-200"
               onClick={handleNavigation('/terms')}>Mentions Légales</a>
          </div>

          {/* Column 4: Socials */}
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-white tracking-wide">Suivez-nous !</h3>
            <div className="flex gap-4 ">
              <a href="https://github.com/le-clap" target="_blank" rel="noreferrer"
                 className="bg-zinc-800 p-2 rounded-full hover:bg-[#5227FF] hover:text-white transition-all duration-300">
                <Github size={20}/>
              </a>
              <a href="https://www.linkedin.com/company/clap-centrale-lille/" target="_blank" rel="noreferrer"
                 className="bg-zinc-800 p-2 rounded-full hover:bg-[#5227FF] hover:text-white transition-all duration-300">
                <Linkedin size={20}/>
              </a>
              <a href="https://www.instagram.com/le_clap_/" target="_blank" rel="noreferrer"
                 className="bg-zinc-800 p-2 rounded-full hover:bg-[#5227FF] hover:text-white transition-all duration-300">
                <Instagram size={20}/>
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Section: Copyright */}
        <div className="flex flex-col md:flex-row justify-between items-start gap-4 text-xs font-medium text-zinc-600">
          <div className="flex flex-col gap-2">
            <p>&copy; {currentYear} Le CLAP (Centrale Lille Audiovisuel Production). Tous droits réservés.</p>
            <p>&copy; {currentYear} Rezoleo. Tous droits réservés.</p>
          </div>
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