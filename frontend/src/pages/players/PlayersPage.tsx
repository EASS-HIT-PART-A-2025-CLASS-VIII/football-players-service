import { useState } from "react";
import "./PlayersPage.css";
import PlayerFormModal from "../../components/playerFormModal/PlayerFormModal";
import PlayerCard from "../../components/player/PlayerCard";
import PlayersHeader from "../../components/playerHeader/PlayersHeader";
import PaginationControls from "../../components/paginationControls/PaginationControls";
import ScoutReportModal from "../../components/scoutReportModal/ScoutReportModal";
import PlayerFilters from "../../components/playerFilters/PlayerFilters";
import { ErrorView, LoadingView } from "../../components/stateViews/StateViews";
import { usePlayersView } from "../../hooks/usePlayersView";

const PlayersPage = () => {
  const { state, actions } = usePlayersView();
  const [scoutingPlayerId, setScoutingPlayerId] = useState<number | null>(null);

  const {
    players,
    pages,
    currentPage,
    editingPlayer,
    isModalOpen,
    filters,
    filterOptions,
    status,
  } = state;

  // Derive from live players array so it auto-updates after refresh
  const scoutingPlayer =
    scoutingPlayerId !== null
      ? (players.find((p) => p.id === scoutingPlayerId) ?? null)
      : null;

  return (
    <div className="players-page">
      <PlayersHeader
        count={state.total}
        onAdd={actions.openCreate}
        disabled={status.isGlobalLoading}
      />

      <PlayerFilters
        filters={filters}
        filterOptions={filterOptions}
        onFiltersChange={actions.setFilters}
        onClear={actions.clearFilters}
        onClearField={actions.clearField}
        disabled={status.isGlobalLoading}
      />

      {status.isLoading && <LoadingView />}

      {status.isError && (
        <ErrorView
          error={status.error}
          onRetry={() => window.location.reload()}
        />
      )}

      {!status.isLoading && !status.isError && (
        <>
          <div className="players-grid">
            {players.map((player, index) => (
              <PlayerCard
                key={player.id}
                player={player}
                index={index}
                onEdit={() => actions.openEdit(player)}
                onDelete={() => actions.deletePlayer(player.id)}
                onScout={() => setScoutingPlayerId(player.id)}
                isLoading={status.isGlobalLoading}
              />
            ))}
          </div>

          <PaginationControls
            currentPage={currentPage}
            totalPages={pages}
            onPageChange={actions.setPage}
            disabled={status.isGlobalLoading}
          />
        </>
      )}

      <PlayerFormModal
        isOpen={isModalOpen}
        onClose={actions.closeModal}
        onSubmit={actions.submitForm}
        initialData={editingPlayer}
        isLoading={status.isSaving}
      />

      {scoutingPlayer && (
        <ScoutReportModal
          player={scoutingPlayer}
          onClose={() => setScoutingPlayerId(null)}
          onReportGenerated={actions.refresh}
        />
      )}
    </div>
  );
};

export default PlayersPage;
