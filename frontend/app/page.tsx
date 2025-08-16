import Image from 'next/image'
import appImage from "@/public/app-image.jpg"
import { Button } from '@/components/button'
import { ArrowRightIcon } from '@heroicons/react/16/solid'

export default function Example() {

  return (
    <div>
          <div className="py-24 sm:py-32 lg:pb-40">
            <div className="px-6 lg:px-8">
              <div className="mx-auto max-w-2xl text-center">
                <h1 className="text-5xl font-semibold tracking-tight text-balance sm:text-7xl">
                  Plan your degree with confidence
                </h1>
                <p className="mt-8 text-lg font-medium text-pretty sm:text-xl/8">
                  Why read through pages of requirements, when you have a simple plan showing everything you need to complete 
                </p>
                <div className="mt-10 flex items-center justify-center gap-x-6">
                  <Button
                    accent
                    href="/start/"
                    className=""
                  >
                    Get started
                  </Button>
                  <a href="#" className="text-sm/6 font-semibold group">
                    Learn more{' '}
                    <span aria-hidden="true" className="inline-block transition-transform duration-200 ease-out group-hover:translate-x-1">
                      <ArrowRightIcon className='w-3 '/>
                    </span>
                  </a>
                </div>
              </div>
              <div className="my-16 sm:mt-24">
                <div className="-m-2 rounded-xl bg-white/2.5 p-2 ring-1 ring-white/10 ring-inset lg:-m-4 lg:rounded-2xl lg:p-4">
                  <Image
                    alt="UQ Roadmap Planner"
                    src={appImage}
                    width={2432}
                    height={1442}
                    className="mx-auto w-full rounded-md bg-white/5 shadow-2xl ring-1 ring-white/10"
                  />
                </div>
              </div>
            </div>
          </div>
    </div>
  )
}
