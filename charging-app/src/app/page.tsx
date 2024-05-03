"use client"
import Link from "next/link";
import { AvailableList } from "@/components/AvailableList";
import Admin from "@/pages/admin";
import { useEffect, useState } from "react";
import { StationLocationDTO } from "./dto";
import { ChargingStatus } from "@/components/ChargingStatus";
import { getChargingStations, getUserChargingStations, postBookChargingStation } from "./api";

export default function Page() {
  const [stations, setStations] = useState<StationLocationDTO[]>([]);
  const [bookedStation, setBookedStation] = useState<StationLocationDTO>({} as StationLocationDTO);

  useEffect(() => {
    // Make into request
    getUserChargingStations().
      then((data) => {
        setStations(data.stations);
        setBookedStation(data.booked_station);
      })
    .catch((error) => {
      console.error(error);
    });

  }, []);

  function book(station: StationLocationDTO) {
    //TODO add to backend
    postBookChargingStation(station.id)     
    .then((data) => {
      setStations(data.stations);
      setBookedStation(data.booked_station);
      })
    .catch((error) => {
      console.error(error);
    });
  }
  return (
    <div className="container mx-auto">
      <div className="flex justify-center mt-6">
        <Link href="/admin">
          <div className="btn btn-primary">Admin</div>
        </Link>
      </div>
      <ChargingStatus />
      <AvailableList data={stations} bookFunction={book} bookedStation={bookedStation}/>
    </div>
  );
}
