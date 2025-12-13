import { Outlet } from "react-router-dom";
import Navbar from "../components/navbar/Navbar";
import "./RootLayout.css";

const RootLayout = () => {
  return (
    <div className="root-layout">
      <Navbar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default RootLayout;
