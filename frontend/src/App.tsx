import { Editor } from './components/Editor';

function App() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f8fafc',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      <div style={{
        flex: '1',
        padding: '40px 48px',
        maxWidth: '1400px',
        width: '100%',
        margin: '0 auto',
        boxSizing: 'border-box'
      }}>
        <header style={{ marginBottom: '40px' }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#0f172a',
            margin: 0,
            letterSpacing: '-0.02em'
          }}>
            GentleGiraffe <span style={{ color: '#94a3b8', fontWeight: '400' }}>Academic Review</span>
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#64748b',
            marginTop: '8px'
          }}>
            Constructive Feedback Assistant
          </p>
        </header>

        <main>
          <Editor />
        </main>
      </div>

      <footer style={{
        padding: '20px 48px',
        borderTop: '1px solid #e2e8f0',
        textAlign: 'center',
        backgroundColor: '#f8fafc'
      }}>
        <p style={{
          fontSize: '13px',
          color: '#94a3b8',
          margin: 0
        }}>
          Made with ❤️ by <span style={{ fontWeight: '500', color: '#64748b' }}>ScaDS AI Lab</span>
        </p>
      </footer>
    </div>
  );
}

export default App;
