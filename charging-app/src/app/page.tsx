"use client"
import Link from "next/link";
import { AvailableList } from "@/components/AvailableList";
import Admin from "@/pages/admin";
import { useEffect, useState } from "react";
import { StationLocationDTO, BookingDTO, StationDTO, ChargingStatusDTO } from "./dto";
import { ChargingStatus } from "@/components/ChargingStatus";
import { getChargingStations, getUserChargingStations, postBookChargingStation, postLeavebooking, postStartCharging, postStopCharging } from "./api";
import { Booking } from "@/components/Booking";

export default function Page() {
  const [stations, setStations] = useState<StationLocationDTO[]>([]);
  const [booking, setBooking] = useState<BookingDTO | undefined>();
  const [chargingStatus, setChargingStatus] = useState<ChargingStatusDTO | undefined>();
  const [bookedStation, setBookedStation] = useState<StationLocationDTO | undefined>({} as StationLocationDTO);

  useEffect(() => {
    // Make into request
    getUserChargingStations().
      then((data) => {
        setStations(data.stations);
        setBooking(data.booking);
        setChargingStatus(data.charging_status);
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

  function leaveBook() {
    postLeavebooking()     
    .then((data) => {
      setStations(data);
      setBooking(undefined);
      setBookedStation({} as StationLocationDTO);
      })
    .catch((error) => {
      console.error(error);
    });
  }

  function startCharging() {
    postStartCharging()     
    .then((data) => {
      setChargingStatus(data.charging_status);
      setBooking(undefined);
      setBookedStation({} as StationLocationDTO);
      setStations(data.stations);
      })
    .catch((error) => {
      console.error(error);
    });
  }

  function stopCharging() {
    postStopCharging()     
    .then((data) => {
      setChargingStatus(undefined);
      setBooking(undefined);
      setBookedStation({} as StationLocationDTO);
      setStations(data.stations);
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

      <ChargingStatus status={chargingStatus} stopChargingFunction={stopCharging} />
      <Booking booking={booking} leaveBookingFunction={leaveBook} startChargingFunction={startCharging}/>
      <AvailableList data={stations} bookFunction={book} bookedStation={bookedStation}/>
    </div>
  );
}
