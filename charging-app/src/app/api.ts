import axios, { AxiosResponse } from 'axios';
import { DashboardDTO, StationLocationDTO } from './dto';

const BACKEND_DOMAIN = 'http://localhost:8000/';
export async function getChargingStations(): Promise<StationLocationDTO> {
    const url = BACKEND_DOMAIN + 'stations/';
    const response = await axios.get<StationLocationDTO>(url);
  
    return response.data;
}

export async function getUserChargingStations():  Promise<DashboardDTO> {
    const url = BACKEND_DOMAIN + 'dashboard/user/';
    const response = await axios.get<DashboardDTO>(url);
  
    return response.data;
}


export async function postBookChargingStation(id: number): Promise<DashboardDTO> {
    const url = BACKEND_DOMAIN + `stations/book/${id}/`;
    const response = await axios.post<DashboardDTO>(url);

    return response.data;
}
