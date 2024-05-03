"use client"
import * as React from "react"
import { BookingDTO, ChargingStatusDTO } from "@/app/dto" 
import { Button } from "./ui/button";
 
type ChargingProps = {
  status: ChargingStatusDTO | undefined;
  stopChargingFunction: () => void;
}

export function ChargingStatus({status, stopChargingFunction}: ChargingProps) {
    if(status == null) {
      console.log("lol");
      return;
    }
    return (
    <div className="border p-3 bg-danger">
      <h1 className="text-xl">Ladestatus</h1>
      <p className="text-l">
        <b>{status.charger}</b>
      </p>
      <p className="text-l">
        pris: {status.price}
      </p>
      <Button
            onClick={() => stopChargingFunction()}
          >
            Stop Lading
      </Button>
    </div>
  )
}