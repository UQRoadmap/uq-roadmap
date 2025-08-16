import { Button } from "@/components/button";

export default function Example() {
  return (
    <>
      {/*
        This example requires updating your template:

        ```
        <html class="h-full">
        <body class="h-full">
        ```
      */}
      <main className="grid min-h-full place-items-center px-6 py-24 sm:py-32 lg:px-8">
        <div className="text-center">
          <p className="text-base font-semibold text-accent">404</p>
          <h1 className="mt-4 text-5xl font-semibold tracking-tight text-balance sm:text-7xl">
            We&apos;re a bit lost
          </h1>
          <p className="mt-6 text-lg font-medium text-pretty  sm:text-xl/8">
            Let&apos;s take you home.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Button
              accent
              href="/"
              className=""
            >
              Go back home
            </Button>
            <a href="#" className="text-sm font-semibold">
              Report an issue <span aria-hidden="true">&rarr;</span>
            </a>
          </div>
        </div>
      </main>
    </>
  )
}