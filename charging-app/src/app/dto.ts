
export type StationDTO = {
    available: boolean;
}
export type StationLocationDTO = {
    id: number;
    name: string;
    available_chargers: number;
    total_chargers: number;
    queue_count: number;
};
  
export type ChargingStatusDTO = {
    charger: string;
    price: number;
    start_time: Date;
    percentage: number;
}

export type BookingDTO = {
    position: number;
    register_time: Date;
    station: StationLocationDTO;
}

export type DashboardDTO = {
    booking: BookingDTO;
    charging_status:ChargingStatusDTO;
    stations: StationLocationDTO[];
    funds: number;
}