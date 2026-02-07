// import CardNav from '@/components/CardNav'
import StaggeredMenu from '@/components/StaggeredMenu';
import ColorBends from "@/components/ColorBends.tsx";
// import DotGrid from '@/components/DotGrid.tsx';

// import logo from '@/assets/Logo CLAP.png';


const App = () => {
  const menuItems = [
  { label: 'Home', ariaLabel: 'Go to home page', link: '/' },
  { label: 'About', ariaLabel: 'Learn about us', link: '/about' },
  { label: 'Services', ariaLabel: 'View our services', link: '/services' },
  { label: 'Contact', ariaLabel: 'Get in touch', link: '/contact' }
];

const socialItems = [
  { label: 'Twitter', link: 'https://twitter.com' },
  { label: 'GitHub', link: 'https://github.com' },
  { label: 'LinkedIn', link: 'https://linkedin.com' }
];

  return (
      <div className="relative min-h-screen w-full">

        {/*<div style={{ width: '100%', height: '1080px', position: 'relative'}}*/}
        {/*  <DotGrid*/}
        {/*  dotSize={5}*/}
        {/*  gap={15}*/}
        {/*  baseColor="#271E37"*/}
        {/*  activeColor="#5227FF"*/}
        {/*  proximity={120}*/}
        {/*  shockRadius={250}*/}
        {/*  shockStrength={5}*/}
        {/*  resistance={750}*/}
        {/*  returnDuration={1.5}*/}
        {/*  />*/}
        {/*</div>*/}

        <div style={{ width: '100%', height: '1080px', position: 'relative' }}>
            <ColorBends
                rotation={0}
                speed={0.2}
                colors={["#e01b24","#a51d2d"]}
                autoRotate={0}
                scale={1}
                frequency={1}
                warpStrength={1}
                mouseInfluence={1}
                parallax={0.5}
                noise={0.1}
            />
        </div>

        <main style={{ height: '100px', background: '#1a1a1a' }}>

          <StaggeredMenu
            position="right"
            items={menuItems}
            socialItems={socialItems}
            displaySocials
            displayItemNumbering={true}
            menuButtonColor="#000"
            openMenuButtonColor="#000"
            changeMenuColorOnOpen={true}
            colors={['#B19EEF', '#5227FF']}
            logoUrl="/src/assets/logos/Logo CLAP.png"
            accentColor="#5227FF"
            isFixed={true}
            onMenuOpen={() => console.log('Menu opened')}
            onMenuClose={() => console.log('Menu closed')}
          />
        </main>
        </div>
  );
};

export default App;