"use client"
import Image from "next/image";
import { AvailableList } from "@/components/AvailableList";
import { useEffect, useState } from "react";
import { StationLocationDTO } from "./dto";
import { ChargingStatus } from "@/components/ChargingStatus";

const data: StationLocationDTO[] = [
  {
    id: 0,
    name: 'Shell Klæbu',
    available_stations: 3,
    total_stations: 4,
    queue_count:0,
  },
  {
    id: 1,
    name: 'Shell Midtbyen',
    available_stations: 0,
    total_stations: 4,
    queue_count:2,
  },
  {
    id: 2,
    name: 'Exxon Nidarosdomen',
    available_stations: 3,
    total_stations: 10,
    queue_count:2,
  },
  {
    id: 3,
    name: 'Statoil',
    available_stations: 10,
    total_stations: 10,
    queue_count:2,
  },
  {
    id: 4,
    name: 'YX Kjøpmannsgata',
    available_stations: 0,
    total_stations: 2,
    queue_count:10,
  },
]

export default function Home() {
  const [stations, setStations] = useState<StationLocationDTO[]>([]);
  const [bookedStation, setBookedStation] = useState<StationLocationDTO>({} as StationLocationDTO);

  useEffect(() => {
    // Make into request
    setStations(data);
  }, []);

  function book(station: StationLocationDTO) {
    //TODO add to backend

    if (bookedStation != station) {
      setStations(stations.map((s , i) => {
        if (s.id == station.id) {
          s.queue_count += 1;
        } else if(s.id == bookedStation.id) {
          s.queue_count -= 1;
        }
        return s;
      }));
      setBookedStation(station);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <ChargingStatus/>
      <AvailableList data={stations} bookFunction={book} bookedStation={bookedStation}/>
    </main>
  );
}
