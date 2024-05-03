"use client"
import * as React from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ChargingStatusDTO, StationLocationDTO } from "@/app/dto" 
 
type ChargingStatusProps = {
}

const charging_status = {
  charging_status: 0.6,
  station: {
    id: 4,
    name: 'YX Kjøpmannsgata',
    available_chargers: 0,
    total_chargers: 2,
    queue_count:10,
  },
  started_datetime: new Date(),
  current_price: 20,
} as ChargingStatusDTO;

export function ChargingStatus({}: ChargingStatusProps) {
    return (
    <Card>
      <CardHeader>
          <CardTitle>Charging status</CardTitle>
        </CardHeader>
        <CardContent>
            <div className="text-xs text-muted-foreground">
                    Prosent
              </div>
        <div className="text-xs text-muted-foreground">
                    Pris
                  </div>
                  <div className="text-xs text-muted-foreground">
                   Stasjon
                  </div>
        </CardContent>
    </Card>
  )
}