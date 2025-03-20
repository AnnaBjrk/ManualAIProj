import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import IndexPage from "./pages/Index.jsx"
import QueryPage from "./pages/Query.jsx"
import Layout from "./pages/Layout.jsx"
import AboutPage from "./pages/About.jsx"
import SearchPage from "./pages/Search.jsx"
import UsersPage from "./pages/UsersPage.jsx"
import AdminPage from "./pages/AdminPage.jsx"
import PartnerPage from "./pages/PartnerPage.jsx"
import { Navigate } from 'react-router-dom';

// Basic protected route that checks if user is logged in
function ProtectedRoute({ element }) {
  const savedUser = localStorage.getItem('user');
  return savedUser ? element : <Navigate to="/" />;
}

// Admin-only protected route
function AdminRoute({ element }) {
  const savedUser = localStorage.getItem('user');
  if (!savedUser) return <Navigate to="/" />;

  const user = JSON.parse(savedUser);
  return user.isAdmin ? element : <Navigate to="/userspage" />;
}

// Partner-only protected route
function PartnerRoute({ element }) {
  const savedUser = localStorage.getItem('user');
  if (!savedUser) return <Navigate to="/" />;

  const user = JSON.parse(savedUser);
  return user.isPartner ? element : <Navigate to="/userspage" />;
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
        path: "search",
        element: <SearchPage />,
      },
      {
        path: "about",
        element: <AboutPage />,
      },
      {
        path: "userspage",
        element: <ProtectedRoute element={<UsersPage />} />,
      },
      {
        path: "adminpage",
        element: <AdminRoute element={<AdminPage />} />,
      },
      {
        path: "partnerpage",
        element: <PartnerRoute element={<PartnerPage />} />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;