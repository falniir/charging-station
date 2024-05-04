"use client"
import * as React from "react"
import { BookingDTO } from "@/app/dto" 
import { Button } from "./ui/button";
 
type BookingProps = {
  booking: BookingDTO | undefined;
  leaveBookingFunction: () => void;
  startChargingFunction: () => void;
}

export function Booking({booking, leaveBookingFunction, startChargingFunction}: BookingProps) {
    if(booking == null) return;
    return (
    <div className="border p-2 bg-muted">
      <h1 className="text-xl">Booking</h1>
      <p className="text-l">
        <b>{booking.station.name}</b> Posisisjon i kø {booking.position}
      </p>
      <Button
            onClick={() => leaveBookingFunction()}
          >
            Forlat booking
      </Button>

      <Button
          onClick={() => startChargingFunction()}
        >
          Start lading
        </Button>
    </div>
  )
}