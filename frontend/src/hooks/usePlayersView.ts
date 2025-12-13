import { useState } from "react";
import { usePlayers } from "./usePlayers";
import type { Player, PlayerCreate } from "../types";

export const usePlayersView = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | undefined>();

  const { players, editingPlayer, status, mutations } = usePlayers(editingId);

  const handleOpenCreate = () => {
    setEditingId(undefined);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (player: Player) => {
    setEditingId(player.id);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingId(undefined);
  };

  const handleSubmit = async (data: PlayerCreate) => {
    try {
      if (editingId) {
        await mutations.update({ id: editingId, data });
      } else {
        await mutations.create(data);
      }
      handleCloseModal();
    } catch (error) {
      console.error("Failed to save player", error);
    }
  };

  const handleDeleteClick = (id: number) => {
    mutations.delete(id);
  };

  return {
    state: {
      players,
      editingPlayer,
      isModalOpen,
      status,
    },
    actions: {
      openCreate: handleOpenCreate,
      openEdit: handleOpenEdit,
      closeModal: handleCloseModal,
      submitForm: handleSubmit,
      deletePlayer: handleDeleteClick,
    },
  };
};
