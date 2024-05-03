"use client"
import Link from "next/link";
import { AvailableList } from "@/components/AvailableList";
import Admin from "@/pages/admin";
import { useEffect, useState } from "react";
import { StationLocationDTO, BookingDTO } from "./dto";
import { ChargingStatus } from "@/components/ChargingStatus";
import { getChargingStations, getUserChargingStations, postBookChargingStation } from "./api";
import { Booking } from "@/components/Booking";

export default function Page() {
  const [stations, setStations] = useState<StationLocationDTO[]>([]);
  const [booking, setBooking] = useState<BookingDTO>();
  const [bookedStation, setBookedStation] = useState<StationLocationDTO>({} as StationLocationDTO);

  useEffect(() => {
    // Make into request
    getUserChargingStations().
      then((data) => {
        setStations(data.stations);
        setBooking(data.booking);
        if (data.booking) {

          setBookedStation(data.booking.station);
        }
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
      setBooking(data.booking);
      if (data.booking) {
        setBookedStation(data.booking.station);
      }
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
      <Booking booking={booking}/>
      <AvailableList data={stations} bookFunction={book} bookedStation={bookedStation}/>
    </div>
  );
}
