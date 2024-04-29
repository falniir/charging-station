"use client";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState } from "react";
import { StationLocationDTO } from "./dto";
import { ChargingStatus } from "@/components/ChargingStatus";
import { AvailableList } from "@/components/AvailableList";

const data: StationLocationDTO[] = [
  {
    id: 0,
    name: "Shell Klæbu",
    available_stations: 3,
    total_stations: 4,
    queue_count: 0,
  },
  {
    id: 1,
    name: "Shell Midtbyen",
    available_stations: 0,
    total_stations: 4,
    queue_count: 2,
  },
  {
    id: 2,
    name: "Exxon Nidarosdomen",
    available_stations: 3,
    total_stations: 10,
    queue_count: 2,
  },
  {
    id: 3,
    name: "Statoil",
    available_stations: 10,
    total_stations: 10,
    queue_count: 2,
  },
  {
    id: 4,
    name: "YX Kjøpmannsgata",
    available_stations: 0,
    total_stations: 2,
    queue_count: 10,
  },
];

export default function Page() {
  const [stations, setStations] = useState<StationLocationDTO[]>([]);
  const [bookedStation, setBookedStation] = useState<StationLocationDTO>(
    {} as StationLocationDTO
  );

  useEffect(() => {
    setStations(data);
  }, []);

  function book(station: StationLocationDTO) {
    if (bookedStation != station) {
      setStations(
        stations.map((s) => {
          if (s.id === station.id) {
            s.queue_count += 1;
          } else if (s.id === bookedStation.id) {
            s.queue_count -= 1;
          }
          return s;
        })
      );
      setBookedStation(station);
    }
  }

  return (
    <div className="container mx-auto">
      <div className="flex justify-center mt-6">
        <Link legacyBehavior href="/admin">
          <a className="btn btn-primary">Admin</a>
        </Link>
      </div>
      <ChargingStatus />
      <AvailableList
        data={stations}
        bookFunction={book}
        bookedStation={bookedStation}
      />
    </div>
  );
}
