import { useState } from "react";
import { usePlayers } from "./usePlayers";
import type { Player, PlayerCreate } from "../types";

export const usePlayersView = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | undefined>();
  const [currentPage, setCurrentPage] = useState(1);
  const PAGE_SIZE = 12;

  const { players, total, pages, editingPlayer, status, mutations } =
    usePlayers(editingId, currentPage, PAGE_SIZE);

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
      // Reset to first page after creation/update
      setCurrentPage(1);
    } catch (error) {
      console.error("Failed to save player", error);
    }
  };

  const handleDeleteClick = (id: number) => {
    mutations.delete(id);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return {
    state: {
      players,
      total,
      pages,
      currentPage,
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
      setPage: handlePageChange,
    },
  };
};
