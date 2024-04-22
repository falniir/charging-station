
export type StationDTO = {
    available: boolean;
}
export type StationLocationDTO = {
    id: number;
    name: string;
    available_stations: number;
    total_stations: number;
    queue_count: number;
};
  

export type ChargingStatusDTO = {
    charging_percent: number;
};