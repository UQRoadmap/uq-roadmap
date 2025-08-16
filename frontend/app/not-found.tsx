import { Button } from "@/components/button";
import { ArrowRightIcon } from "@heroicons/react/16/solid";

export default function Example() {
  return (
    <div className="min-h-screen grid place-items-center px-6 py-24 sm:py-32 lg:px-8">
      <div className="text-center">
        <p className="text-base font-semibold text-accent">404</p>
        <h1 className="mt-4 text-5xl font-semibold tracking-tight text-balance sm:text-7xl">
          We&apos;ve hit a dead end
        </h1>
        <p className="mt-6 text-lg font-medium text-pretty sm:text-xl/8">
          Let&apos;s take you home.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Button accent href="/" className="">
            Go back home
          </Button>
          <a href="#" className="text-sm/6 font-semibold group">
            Report an issue{" "}
            <span
              aria-hidden="true"
              className="inline-block transition-transform duration-200 ease-out group-hover:translate-x-1"
            >
              <ArrowRightIcon className="w-3" />
            </span>
          </a>
        </div>
      </div>
    </div>
  );
}
