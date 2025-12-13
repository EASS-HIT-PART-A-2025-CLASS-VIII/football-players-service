import { createBrowserRouter } from "react-router-dom";
import RootLayout from "../layouts/RootLayout";
import HomePage from "../pages/home/HomePage";
import PlayersPage from "../pages/players/PlayersPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: "players",
        element: <PlayersPage />,
      },
    ],
  },
]);
