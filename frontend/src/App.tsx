/**
 * Main application component with React Router integration.
 */

import { AppRouter } from "@/router";
import "./App.css";

/**
 * Root application component.
 * Wires up the routing system to the main application.
 */
function App() {
  return <AppRouter />;
}

export default App;

