
export type StationDTO = {
    available: boolean;
}
export type StationLocationDTO = {
    id: number;
    name: string;
    available_stations: number;
    total_stations: number;
};
  

export type ChargingStatusDTO = {
    charging_percent: number;
};