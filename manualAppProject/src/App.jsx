

import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import IndexPage from "./pages/Index.jsx"
import QueryPage from "./pages/Query.jsx"
import Layout from "./pages/Layout.jsx"
import AboutPage from "./pages/About.jsx"
import ManualPage from "./pages/Manual.jsx"
import UsersPage from "./pages/UsersPage.jsx"
import { Navigate } from 'react-router-dom';

// browser router hook - gör att man slipper importera till main
// och slipper lägga till header och footer manuellt.
// children visar att sidorna ska ligga i layout


function ProtectedRoute({ element }) {
  const savedUser = localStorage.getItem('user');
  return savedUser ? element : <Navigate to="/" />;
}

const router = createBrowserRouter([

  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <IndexPage />

      },


      {
        path: "query",
        element: <QueryPage />,
      },

      {
        path: "manual",
        element: <ManualPage />,
      },

      {
        path: "about",
        element: <AboutPage />,
      },

      {
        path: "userspage",
        element: <ProtectedRoute element={<UsersPage />} />,
      },


    ],
  },
])


function App() {
  return <RouterProvider router={router} />;
}

export default App;