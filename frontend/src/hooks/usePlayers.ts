import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createPlayer,
  deletePlayer,
  getPlayer,
  getPlayers,
  updatePlayer,
  getFilterOptions,
} from "../services/api";
import type { PlayerCreate, PlayerFilters } from "../types";

export const usePlayers = (
  editingId?: number,
  page: number = 1,
  limit: number = 10,
  filters?: PlayerFilters,
) => {
  const queryClient = useQueryClient();

  // 1. Main List Query with Pagination and Filters
  const playersQuery = useQuery({
    queryKey: ["players", page, limit, filters],
    queryFn: () => getPlayers(page, limit, filters),
  });

  // 2. Filter Options Query
  const filterOptionsQuery = useQuery({
    queryKey: ["filter-options"],
    queryFn: getFilterOptions,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // 3. Single Player Query (Only runs if we have an ID)
  const singlePlayerQuery = useQuery({
    queryKey: ["player", editingId],
    queryFn: () => getPlayer(editingId!),
    enabled: !!editingId,
  });

  // 3. Shared Invalidation Logic
  const invalidatePlayers = () =>
    queryClient.invalidateQueries({ queryKey: ["players"] });

  // 4. Mutations
  const createMutation = useMutation({
    mutationFn: createPlayer,
    onSuccess: invalidatePlayers,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: PlayerCreate }) =>
      updatePlayer(id, data),
    onSuccess: invalidatePlayers,
  });

  const deleteMutation = useMutation({
    mutationFn: deletePlayer,
    onSuccess: invalidatePlayers,
  });

  // Derived Loading State (is something happening?)
  const isGlobalLoading =
    playersQuery.isLoading ||
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending;

  return {
    players: playersQuery.data?.data ?? [],
    total: playersQuery.data?.total ?? 0,
    pages: playersQuery.data?.pages ?? 1,
    editingPlayer: singlePlayerQuery.data,
    filterOptions: filterOptionsQuery.data,
    status: {
      isLoading: playersQuery.isLoading,
      isError: playersQuery.isError,
      error: playersQuery.error,
      isGlobalLoading,
      isSaving: createMutation.isPending || updateMutation.isPending,
    },
    mutations: {
      create: createMutation.mutateAsync,
      update: updateMutation.mutateAsync,
      delete: deleteMutation.mutateAsync,
    },
    refresh: invalidatePlayers,
  };
};
