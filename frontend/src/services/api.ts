import { axiosInstance } from ".";
import type {
  Player,
  PlayerCreate,
  ScoutResponse,
  TaskStatus,
  PlayerFilters,
  FilterOptions,
} from "../types";

const PREFIX = "players";

interface PaginatedResponse {
  data: Player[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

// AUTH
export const login = async (
  username: string,
  password: string,
): Promise<LoginResponse> => {
  try {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await axiosInstance.post("/token", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error logging in:", error);
    throw error;
  }
};

// READ
export const getPlayers = async (
  page: number = 1,
  limit: number = 10,
  filters?: PlayerFilters,
): Promise<PaginatedResponse> => {
  try {
    const params: any = { page, limit };

    // Add filter parameters if provided
    if (filters?.name) params.name = filters.name;
    if (filters?.minPrice !== undefined) params.min_price = filters.minPrice;
    if (filters?.maxPrice !== undefined) params.max_price = filters.maxPrice;
    if (filters?.country) params.country = filters.country;
    if (filters?.club) params.club = filters.club;
    if (filters?.league) params.league = filters.league;
    if (filters?.status) params.status = filters.status;

    const response = await axiosInstance.get(`/${PREFIX}`, { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching players:", error);
    throw error;
  }
};

export const getFilterOptions = async (): Promise<FilterOptions> => {
  try {
    const response = await axiosInstance.get(`/${PREFIX}/filter-options`);
    return response.data;
  } catch (error) {
    console.error("Error fetching filter options:", error);
    throw error;
  }
};

export const getPlayer = async (id: number): Promise<Player> => {
  try {
    const response = await axiosInstance.get(`/${PREFIX}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching player ${id}:`, error);
    throw error;
  }
};

// CREATE
export const createPlayer = async (data: PlayerCreate): Promise<Player> => {
  try {
    const response = await axiosInstance.post(`/${PREFIX}`, data);
    return response.data;
  } catch (error) {
    console.error("Error creating player:", error);
    throw error;
  }
};

// UPDATE
export const updatePlayer = async (
  id: number,
  data: PlayerCreate,
): Promise<Player> => {
  try {
    const response = await axiosInstance.put(`/${PREFIX}/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating player ${id}:`, error);
    throw error;
  }
};

// DELETE
export const deletePlayer = async (id: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/${PREFIX}/${id}`);
  } catch (error) {
    console.error(`Error deleting player ${id}:`, error);
    throw error;
  }
};

// AI SCOUT
export const scoutPlayer = async (id: number): Promise<ScoutResponse> => {
  try {
    const response = await axiosInstance.post(`/${PREFIX}/${id}/scout`);
    return response.data;
  } catch (error) {
    console.error(`Error scouting player ${id}:`, error);
    throw error;
  }
};

export const getTaskStatus = async (taskId: string): Promise<TaskStatus> => {
  try {
    const response = await axiosInstance.get(`/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching task status ${taskId}:`, error);
    throw error;
  }
};
