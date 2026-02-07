import './App.css'
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import Hello from './components/Hello'


function App() {

    return (
        <Router>
            <div className="app-container">
                <header>
                    <h1>Site d'emprunt du CLAP</h1>
                </header>
                <main>
                    <Routes>
                        <Route path="/" element={<Hello />}/>
                    </Routes>
                </main>
            </div>
        </Router>
    )
}

export default App
