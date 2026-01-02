import "./PaginationControls.css";

interface PaginationControlsProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
}

const PaginationControls = ({
  currentPage,
  totalPages,
  onPageChange,
  disabled = false,
}: PaginationControlsProps) => {
  if (totalPages <= 1) return null;

  const pageNumbers: (number | string)[] = [];
  const maxPagesToShow = 5;

  if (totalPages <= maxPagesToShow) {
    // Show all pages
    for (let i = 1; i <= totalPages; i++) {
      pageNumbers.push(i);
    }
  } else {
    // Show first, last, and pages around current
    pageNumbers.push(1);

    const startPage = Math.max(2, currentPage - 1);
    const endPage = Math.min(totalPages - 1, currentPage + 1);

    if (startPage > 2) {
      pageNumbers.push("...");
    }

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(i);
    }

    if (endPage < totalPages - 1) {
      pageNumbers.push("...");
    }

    pageNumbers.push(totalPages);
  }

  return (
    <div className="pagination-controls">
      <button
        className="pagination-btn pagination-arrow"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1 || disabled}
        title="Previous page"
      >
        ← Back
      </button>

      <div className="pagination-pages">
        {pageNumbers.map((pageNum, idx) => (
          <button
            key={idx}
            className={`pagination-page ${
              pageNum === currentPage ? "active" : ""
            } ${pageNum === "..." ? "ellipsis" : ""}`}
            onClick={() => {
              if (typeof pageNum === "number") {
                onPageChange(pageNum);
              }
            }}
            disabled={pageNum === "..." || disabled}
          >
            {pageNum}
          </button>
        ))}
      </div>

      <button
        className="pagination-btn pagination-arrow"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages || disabled}
        title="Next page"
      >
        Next →
      </button>
    </div>
  );
};

export default PaginationControls;
