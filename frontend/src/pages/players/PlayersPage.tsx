import "./PlayersPage.css";
import PlayerFormModal from "../../components/playerFormModal/PlayerFormModal";
import PlayerCard from "../../components/player/PlayerCard";
import PlayersHeader from "../../components/playerHeader/PlayersHeader";
import { ErrorView, LoadingView } from "../../components/stateViews/StateViews";
import { usePlayersView } from "../../hooks/usePlayersView";

const PlayersPage = () => {
  const { state, actions } = usePlayersView();

  const { players, editingPlayer, isModalOpen, status } = state;

  return (
    <div className="players-page">
      <PlayersHeader
        count={players.length}
        onAdd={actions.openCreate}
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
        <div className="players-grid">
          {players.map((player, index) => (
            <PlayerCard
              key={player.id}
              player={player}
              index={index}
              onEdit={() => actions.openEdit(player)}
              onDelete={() => actions.deletePlayer(player.id)}
              isLoading={status.isGlobalLoading}
            />
          ))}
        </div>
      )}

      <PlayerFormModal
        isOpen={isModalOpen}
        onClose={actions.closeModal}
        onSubmit={actions.submitForm}
        initialData={editingPlayer}
        isLoading={status.isSaving}
      />
    </div>
  );
};

export default PlayersPage;
