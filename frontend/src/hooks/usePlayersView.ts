import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { usePlayers } from "./usePlayers";
import type {
  Player,
  PlayerCreate,
  PlayerFilters,
  PlayingStatus,
} from "../types";

export const usePlayersView = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | undefined>();

  // Initialize state from URL params
  const [currentPage, setCurrentPage] = useState(() => {
    const page = searchParams.get("page");
    return page ? parseInt(page, 10) : 1;
  });

  const [filters, setFilters] = useState<PlayerFilters>(() => {
    const urlFilters: PlayerFilters = {};
    const name = searchParams.get("name");
    const minPrice = searchParams.get("minPrice");
    const maxPrice = searchParams.get("maxPrice");
    const country = searchParams.get("country");
    const club = searchParams.get("club");
    const league = searchParams.get("league");
    const status = searchParams.get("status");

    if (name) urlFilters.name = name;
    if (minPrice) urlFilters.minPrice = parseInt(minPrice, 10);
    if (maxPrice) urlFilters.maxPrice = parseInt(maxPrice, 10);
    if (country) urlFilters.country = country;
    if (club) urlFilters.club = club;
    if (league) urlFilters.league = league;
    if (status) urlFilters.status = status as PlayingStatus;

    return urlFilters;
  });

  const PAGE_SIZE = 12;

  // Update URL when filters or page change
  useEffect(() => {
    const params = new URLSearchParams();

    if (currentPage > 1) params.set("page", currentPage.toString());
    if (filters.name) params.set("name", filters.name);
    if (filters.minPrice !== undefined)
      params.set("minPrice", filters.minPrice.toString());
    if (filters.maxPrice !== undefined)
      params.set("maxPrice", filters.maxPrice.toString());
    if (filters.country) params.set("country", filters.country);
    if (filters.club) params.set("club", filters.club);
    if (filters.league) params.set("league", filters.league);
    if (filters.status) params.set("status", filters.status);

    setSearchParams(params, { replace: true });
  }, [filters, currentPage, setSearchParams]);

  const {
    players,
    total,
    pages,
    editingPlayer,
    filterOptions,
    status,
    mutations,
    refresh,
  } = usePlayers(editingId, currentPage, PAGE_SIZE, filters);

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

  const handleFiltersChange = useCallback((newFilters: PlayerFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters({});
    setCurrentPage(1);
  }, []);

  const handleClearField = useCallback((field: keyof PlayerFilters) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      delete newFilters[field];
      return newFilters;
    });
    setCurrentPage(1); // Reset to first page when filter changes
  }, []);

  return {
    state: {
      players,
      total,
      pages,
      currentPage,
      editingPlayer,
      isModalOpen,
      filters,
      filterOptions,
      status,
    },
    actions: {
      openCreate: handleOpenCreate,
      openEdit: handleOpenEdit,
      closeModal: handleCloseModal,
      submitForm: handleSubmit,
      deletePlayer: handleDeleteClick,
      setPage: handlePageChange,
      setFilters: handleFiltersChange,
      clearFilters: handleClearFilters,
      clearField: handleClearField,
      refresh,
    },
  };
};
