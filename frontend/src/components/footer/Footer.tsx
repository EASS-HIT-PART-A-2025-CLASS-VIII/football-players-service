import { Github, Linkedin } from "lucide-react";
import "./Footer.css";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    {
      icon: Linkedin,
      href: "https://www.linkedin.com/in/ziv-ashkenazi/",
      label: "LinkedIn",
      ariaLabel: "Visit LinkedIn profile",
    },
    {
      icon: Github,
      href: "https://github.com/ziv9529",
      label: "GitHub",
      ariaLabel: "Visit GitHub profile",
    },
  ];

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <p className="footer-text">
              © {currentYear} Football Player Service. All rights reserved.
            </p>
          </div>

          <div className="footer-section">
            <div className="social-links">
              {socialLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <a
                    key={link.label}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                    aria-label={link.ariaLabel}
                    title={link.label}
                  >
                    <Icon size={20} strokeWidth={1.5} />
                  </a>
                );
              })}
            </div>
          </div>
        </div>

        <div className="footer-divider"></div>
      </div>
    </footer>
  );
};

export default Footer;
