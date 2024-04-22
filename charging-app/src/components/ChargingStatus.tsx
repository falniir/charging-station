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
  data_started
} as ChargingStatusDTO;

export function ChargingStatus({}: ChargingStatusProps) {
    return (
    <Card>
      <CardHeader>
          <CardTitle>Charging status</CardTitle>
        </CardHeader>
        <CardContent>

        </CardContent>
    </Card>
  )
}