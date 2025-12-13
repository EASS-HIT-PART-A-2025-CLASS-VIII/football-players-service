import { axiosInstance } from ".";
import type { Player, PlayerCreate } from "../types";

const PREFIX = "players";

// READ
export const getPlayers = async (): Promise<Player[]> => {
  try {
    const response = await axiosInstance.get(`/${PREFIX}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching players:", error);
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
  data: PlayerCreate
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
