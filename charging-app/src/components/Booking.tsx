"use client"
import * as React from "react"
import { BookingDTO } from "@/app/dto" 
 
type BookingProps = {
  booking: BookingDTO;
}

export function Booking({booking}: BookingProps) {
    if(booking == null) return;
    return (
    <div className="border p-2 bg-muted">
      <h1 className="text-xl">Booking</h1>
      <p className="text-l">
        <b>{booking.station.name}</b> Posisisjon i kø {booking.position}
      </p>
    </div>
  )
}