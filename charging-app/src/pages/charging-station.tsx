"use client"
import "tailwindcss/tailwind.css";
import "/src/app/globals.css";
import { Button } from "@/components/ui/button";
import { SheetTrigger, SheetContent, Sheet } from "@/components/ui/sheet";
import Link from "next/link";
import {
  BreadcrumbLink,
  BreadcrumbItem,
  BreadcrumbSeparator,
  BreadcrumbPage,
  BreadcrumbList,
  Breadcrumb,
} from "@/components/ui/breadcrumb";
import {
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
  DropdownMenuContent,
  DropdownMenu,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import {
  CardTitle,
  CardDescription,
  CardHeader,
  CardContent,
  Card,
} from "@/components/ui/card";

import { RocketIcon } from "@radix-ui/react-icons"
 
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"

import { Progress } from "@/components/ui/progress";
import { JSX, SVGProps, useEffect, useState } from "react";
import { BookingDTO, ChargingStatusDTO, DashboardDTO, StationDTO, StationLocationDTO } from "@/app/dto";
import { getUserChargingStations } from "@/app/api";
import { postStartCharging, postStopCharging, postLeavebooking } from "@/app/api";
import { routeModule } from "next/dist/build/templates/app-page";
import router from "next/router";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { useSearchParams } from 'next/navigation'


export default function ChargingStation() {
  const [chargingStatus, setChargingStatus] = useState<ChargingStatusDTO | undefined>();
  const [bookedStation, setBookedStation] = useState<StationDTO | undefined>();
  const [booking, setBooking] = useState<BookingDTO | undefined>();
  const [dashboard, setDashboard] = useState<DashboardDTO | undefined>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getUserChargingStations();
        setBooking(data.booking);
        setChargingStatus(data.charging_status);
        setDashboard(data);
      } catch (error) {
        console.error(error);
      }
    };
    


    fetchData();

    const intervalId = setInterval(fetchData, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  //Gets query from the URL: /charging-station?id=2 in this case id=2 as a number
  const searchParams = useSearchParams();
  const id = searchParams?.get("id");



  // console.log("chargingStatus:", chargingStatus);
  // console.log("bookedStation:", bookedStation);
  // console.log("booking:", booking);
  // console.log("dashboard:", dashboard);
  // console.log("chargingStatus:", chargingStatus);
  // console.log("bookedStation:", bookedStation);
  // console.log("booking:", booking);
  // console.log("dashboard:", dashboard);
// 0 is not charging, 1 is charging, 2 overcharging, 3 completed, 4 completed overcharged
  function showChargingState() {

    if (dashboard?.charging_status.state === 0) {
      return "Not Charging";
    } else if (dashboard?.charging_status.state === 1) {
      return "Charging";
    } else if (dashboard?.charging_status.state === 2) {
      return "Overcharging";
    } else if (dashboard?.charging_status.state === 3) {
      return "Completed";
    } else if (dashboard?.charging_status.state === 4) {
      return "Completed Overcharged";
    } else {
      return "Unknown";
    }
  }

  async function postLeaveBookingAndRedirect() {
    postLeavebooking();
    router.push("/");
  }

  console.log("dashboard:", dashboard);
  console.log("Funds", dashboard?.funds);
  console.log("Price", dashboard?.charging_status.price);
  console.log("Charging Status", chargingStatus);

  function postStartChargingAndCheckFunds() {
    
    if (dashboard?.funds === undefined) {
      alert("Funds or Price is undefined");
      return;
    }
    if (dashboard?.funds < 0) {
      alert("Not enough funds");
      return;
    }

    if ((dashboard?.funds ?? 0) >= (chargingStatus?.price ?? 0)) {
      postStartCharging();
      console.log("Funds", dashboard?.funds);
    } else {
     alert("Not enough funds");
    }
  }

  return (
    <div key="1" className="flex min-h-screen w-full flex-col bg-muted/40">
      <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
          <Sheet>
            <SheetTrigger asChild>
              <Button className="sm:hidden" size="icon" variant="outline">
                <PanelLeftIcon className="h-5 w-5" />
                <span className="sr-only">Toggle Menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent className="sm:max-w-xs" side="left">
              <nav className="grid gap-6 text-lg font-medium">
                <Link
                  className="group flex h-10 w-10 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:text-base"
                  href="#"
                >
                  <BatteryChargingIcon className="h-5 w-5 transition-all group-hover:scale-110" />
                  <span className="sr-only">Charging Stations</span>
                </Link>
                <Link
                  className="flex items-center gap-4 px-2.5 text-foreground"
                  href="#"
                >
                  <CarIcon className="h-5 w-5" />
                  My Car
                </Link>
                <Link
                  className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                  href="#"
                >
                  <BatteryChargingIcon className="h-5 w-5" />
                  Charging Status
                </Link>
                <Link
                  className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                  href="#"
                >
                  <SettingsIcon className="h-5 w-5" />
                  Settings
                </Link>
              </nav>
            </SheetContent>
          </Sheet>
          <Breadcrumb className="hidden md:flex">
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href="/">Charging Stations</Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Station { dashboard?.booking?.station?.id}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="relative ml-auto flex-1 md:grow-0" />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                className="overflow-hidden rounded-full"
                size="icon"
                variant="outline"
              >
                <img
                  alt="Avatar"
                  className="overflow-hidden rounded-full"
                  height={36}
                  src="/placeholder.svg"
                  style={{
                    aspectRatio: "36/36",
                    objectFit: "cover",
                  }}
                  width={36}
                />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Support</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Logout</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>
        <main className="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8">
          <div className="mx-auto grid max-w-[59rem] flex-1 auto-rows-max gap-4">
            <div className="flex items-center gap-4">
              <Button className="h-7 w-7" size="icon" variant="outline">
                <ChevronLeftIcon className="h-4 w-4" />
                <span className="sr-only">Back</span>
              </Button>
              <h1 className="flex-1 shrink-0 whitespace-nowrap text-xl font-semibold tracking-tight sm:grow-0">
                Charging Station
              </h1>
              <Badge className="ml-auto sm:ml-0" variant="outline">
                Available
              </Badge>
              <div className="hidden items-center gap-2 md:ml-auto md:flex">
                <Button size="sm" variant="outline" onClick={postStartChargingAndCheckFunds}>
                  Start Charging
                </Button>
                <Button size="sm" variant="outline" onClick={postStopCharging}>
                  Stop Charging
                </Button>
                <Button size="sm" onClick={postLeaveBookingAndRedirect}>Leave Booking</Button>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-[1fr_250px] lg:grid-cols-3 lg:gap-8">
              <div className="grid auto-rows-max items-start gap-4 lg:col-span-2 lg:gap-8">
                <Card x-chunk="dashboard-07-chunk-0">
                  <CardHeader>
                    <CardTitle>Charging Status</CardTitle>
                    <CardDescription>
                      Current status of your EV charging.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-6">
                      <div className="grid gap-3">
                      <div className="flex items-center justify-between">
                          <span>Available Funds</span>
                          <span className="font-semibold">{dashboard?.funds + "$"}</span>
                        </div>
                      <div className="flex items-center justify-between">
                          <span>Price</span>
                          <span className="font-semibold">{dashboard?.charging_status.price}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Charger</span>
                          <span className="font-semibold">{dashboard?.charging_status.charger}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Start Time</span>
                          <span className="font-semibold">{dashboard?.charging_status.start_time as unknown as String}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Charging Status</span>
                          <span className="font-semibold">{showChargingState()}</span>
                        </div>
                        <Progress value={dashboard?.charging_status?.percent as number} />
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Estimated Time Remaining</span>
                          <span className="font-semibold">45 min</span>
                        </div>
                        <Progress value={55} />
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Charging Rate</span>
                          <span className="font-semibold">22 kW</span>
                        </div>
                        <Progress value={80} />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card x-chunk="dashboard-07-chunk-1">
                  <CardHeader>
                    <CardTitle>My Car</CardTitle>
                    <CardDescription>
                      Details about your connected vehicle.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-6">
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Make</span>
                          <span className="font-semibold">Tesla</span>
                        </div>
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Model</span>
                          <span className="font-semibold">Model 3</span>
                        </div>
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Battery Capacity</span>
                          <span className="font-semibold">75 kWh</span>
                        </div>
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Odometer</span>
                          <span className="font-semibold">45,678 mi</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              <div className="grid auto-rows-max items-start gap-4 lg:gap-8">
                <Card x-chunk="dashboard-07-chunk-3">
                  <CardHeader>
                    <CardTitle>Booking Details</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-6">
                      <div className="grid gap-3">
                      <div className="flex items-center justify-between">
                          <span>Queue Position:</span>
                          <span className="font-semibold">{booking?.position ?? 0}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Available Stations</span>
                          <span className="font-semibold">{dashboard?.stations[id]?.available_chargers ?? 0}</span>
                        </div>
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Location</span>
                          <span className="font-semibold">
                            Trondheim
                          </span>
                        </div>
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Connector Type</span>
                          <span className="font-semibold">CCS</span>
                        </div>
                      </div>
                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <span>Max Power</span>
                          <span className="font-semibold">50 kW</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
            <div className="flex items-center justify-center gap-2 md:hidden">
              <Button size="sm" variant="outline">
                Start Charging
              </Button>
              <Button size="sm">View Details</Button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function BatteryChargingIcon(
  props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>
) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M15 7h1a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2" />
      <path d="M6 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h1" />
      <path d="m11 7-3 5h4l-3 5" />
      <line x1="22" x2="22" y1="11" y2="13" />
    </svg>
  );
}

function CarIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
      <circle cx="7" cy="17" r="2" />
      <path d="M9 17h6" />
      <circle cx="17" cy="17" r="2" />
    </svg>
  );
}

function ChevronLeftIcon(
  props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>
) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m15 18-6-6 6-6" />
    </svg>
  );
}

function PanelLeftIcon(
  props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>
) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
      <line x1="9" x2="9" y1="3" y2="21" />
    </svg>
  );
}

function SettingsIcon(
  props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>
) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}