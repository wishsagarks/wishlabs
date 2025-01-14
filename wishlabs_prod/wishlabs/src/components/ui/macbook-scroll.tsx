"use client";
import React, { useEffect, useRef, useState } from "react";
import { MotionValue, motion, useScroll, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";
import {
  IconBrightnessDown,
  IconBrightnessUp,
  IconCaretRightFilled,
  IconCaretUpFilled,
  IconChevronUp,
  IconMicrophone,
  IconMoon,
  IconPlayerSkipForward,
  IconPlayerTrackNext,
  IconPlayerTrackPrev,
  IconTable,
  IconVolume,
  IconVolume2,
  IconVolume3,
} from "@tabler/icons-react";
import { IconSearch } from "@tabler/icons-react";
import { IconWorld } from "@tabler/icons-react";
import { IconCommand } from "@tabler/icons-react";
import { IconCaretLeftFilled } from "@tabler/icons-react";
import { IconCaretDownFilled } from "@tabler/icons-react";
import Image from "next/image";

export const MacbookScroll = ({
  src,
  showGradient,
  title,
  badge,
}: {
  src?: string;
  showGradient?: boolean;
  title?: string | React.ReactNode;
  badge?: React.ReactNode;
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    if (window && window.innerWidth < 768) {
      setIsMobile(true);
    }
  }, []);

  const scaleX = useTransform(
    scrollYProgress,
    [0, 0.3],
    [1.2, isMobile ? 1 : 1.5]
  );
  const scaleY = useTransform(
    scrollYProgress,
    [0, 0.3],
    [0.6, isMobile ? 1 : 1.5]
  );
  const translate = useTransform(scrollYProgress, [0, 1], [0, 1500]);
  const rotate = useTransform(scrollYProgress, [0.1, 0.12, 0.3], [-28, -28, 0]);
  const textTransform = useTransform(scrollYProgress, [0, 0.3], [0, 100]);
  const textOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);

  return (
    <div
      ref={ref}
      className="min-h-[200vh]  flex flex-col items-center py-0 md:py-80 justify-start flex-shrink-0 [perspective:800px] transform md:scale-100  scale-[0.35] sm:scale-50"
    >
      <motion.h2
        style={{
          translateY: textTransform,
          opacity: textOpacity,
        }}
        className="dark:text-white text-neutral-800 text-3xl font-bold mb-20 text-center"
      >
        {title || (
          <span>
            This Macbook is built with Tailwindcss. <br /> No kidding.
          </span>
        )}
      </motion.h2>
      {/* Lid */}
      <Lid
        src={src}
        scaleX={scaleX}
        scaleY={scaleY}
        rotate={rotate}
        translate={translate}
      />
      {/* Base area */}
      <div className="h-[22rem] w-[32rem] bg-gray-200 dark:bg-[#272729] rounded-2xl overflow-hidden relative -z-10">
        {/* above keyboard bar */}
        <div className="h-10 w-full relative">
          <div className="absolute inset-x-0 mx-auto w-[80%] h-4 bg-[#050505]" />
        </div>
        <div className="flex relative">
          <div className="mx-auto w-[10%] overflow-hidden  h-full">
            <SpeakerGrid />
          </div>
          <div className="mx-auto w-[80%] h-full">
            <Keypad />
          </div>
          <div className="mx-auto w-[10%] overflow-hidden  h-full">
            <SpeakerGrid />
          </div>
        </div>
        <Trackpad />
        <div className="h-2 w-20 mx-auto inset-x-0 absolute bottom-0 bg-gradient-to-t from-[#272729] to-[#050505] rounded-tr-3xl rounded-tl-3xl" />
        {showGradient && (
          <div className="h-40 w-full absolute bottom-0 inset-x-0 bg-gradient-to-t dark:from-black from-white via-white dark:via-black to-transparent z-50"></div>
        )}
        {badge && <div className="absolute bottom-4 left-4">{badge}</div>}
      </div>
    </div>
  );
};

export const Lid = ({
  scaleX,
  scaleY,
  rotate,
  translate,
  src,
}: {
  scaleX: MotionValue<number>;
  scaleY: MotionValue<number>;
  rotate: MotionValue<number>;
  translate: MotionValue<number>;
  src?: string;
}) => {
  return (
    <div className="relative [perspective:800px]">
      <div
        style={{
          transform: "perspective(800px) rotateX(-25deg) translateZ(0px)",
          transformOrigin: "bottom",
          transformStyle: "preserve-3d",
        }}
        className="h-[12rem] w-[32rem] bg-[#010101] rounded-2xl p-2 relative"
      >
        <div
          style={{
            boxShadow: "0px 2px 0px 2px var(--neutral-900) inset",
          }}
          className="absolute inset-0 bg-[#010101] rounded-lg flex items-center justify-center"
        >
          <span className="text-white">
            <WishlabLogo />
          </span>
        </div>
      </div>
      <motion.div
        style={{
          scaleX: scaleX,
          scaleY: scaleY,
          rotateX: rotate,
          translateY: translate,
          transformStyle: "preserve-3d",
          transformOrigin: "top",
        }}
        className="h-96 w-[32rem] absolute inset-0 bg-[#010101] rounded-2xl p-2"
      >
        <div className="absolute inset-0 bg-[#272729] rounded-lg" />
        <Image
          src={src as string}
          alt="aceternity logo"
          fill
          className="object-cover object-left-top absolute rounded-lg inset-0 h-full w-full"
        />
      </motion.div>
    </div>
  );
};

export const Trackpad = () => {
  return (
    <div
      className="w-[40%] mx-auto h-32  rounded-xl my-1"
      style={{
        boxShadow: "0px 0px 1px 1px #00000020 inset",
      }}
    ></div>
  );
};

export const Keypad = () => {
  return (
    <div className="h-full rounded-md bg-[#050505] mx-1 p-1">
      {/* First Row */}
      <Row>
        <KBtn
          className="w-10 items-end justify-start pl-[4px] pb-[2px]"
          childrenClassName="items-start"
        >
          esc
        </KBtn>
        <KBtn>
          <IconBrightnessDown className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F1</span>
        </KBtn>

        <KBtn>
          <IconBrightnessUp className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F2</span>
        </KBtn>
        <KBtn>
          <IconTable className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F3</span>
        </KBtn>
        <KBtn>
          <IconSearch className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F4</span>
        </KBtn>
        <KBtn>
          <IconMicrophone className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F5</span>
        </KBtn>
        <KBtn>
          <IconMoon className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F6</span>
        </KBtn>
        <KBtn>
          <IconPlayerTrackPrev className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F7</span>
        </KBtn>
        <KBtn>
          <IconPlayerSkipForward className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F8</span>
        </KBtn>
        <KBtn>
          <IconPlayerTrackNext className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F8</span>
        </KBtn>
        <KBtn>
          <IconVolume3 className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F10</span>
        </KBtn>
        <KBtn>
          <IconVolume2 className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F11</span>
        </KBtn>
        <KBtn>
          <IconVolume className="h-[6px] w-[6px]" />
          <span className="inline-block mt-1">F12</span>
        </KBtn>
        <KBtn>
          <div className="h-4 w-4 rounded-full  bg-gradient-to-b from-20% from-neutral-900 via-black via-50% to-neutral-900 to-95% p-px">
            <div className="bg-black h-full w-full rounded-full" />
          </div>
        </KBtn>
      </Row>

      {/* Second row */}
      <Row>
        <KBtn>
          <span className="block">~</span>
          <span className="block mt-1">`</span>
        </KBtn>

        <KBtn>
          <span className="block ">!</span>
          <span className="block">1</span>
        </KBtn>
        <KBtn>
          <span className="block">@</span>
          <span className="block">2</span>
        </KBtn>
        <KBtn>
          <span className="block">#</span>
          <span className="block">3</span>
        </KBtn>
        <KBtn>
          <span className="block">$</span>
          <span className="block">4</span>
        </KBtn>
        <KBtn>
          <span className="block">%</span>
          <span className="block">5</span>
        </KBtn>
        <KBtn>
          <span className="block">^</span>
          <span className="block">6</span>
        </KBtn>
        <KBtn>
          <span className="block">&</span>
          <span className="block">7</span>
        </KBtn>
        <KBtn>
          <span className="block">*</span>
          <span className="block">8</span>
        </KBtn>
        <KBtn>
          <span className="block">(</span>
          <span className="block">9</span>
        </KBtn>
        <KBtn>
          <span className="block">)</span>
          <span className="block">0</span>
        </KBtn>
        <KBtn>
          <span className="block">&mdash;</span>
          <span className="block">_</span>
        </KBtn>
        <KBtn>
          <span className="block">+</span>
          <span className="block"> = </span>
        </KBtn>
        <KBtn
          className="w-10 items-end justify-end pr-[4px] pb-[2px]"
          childrenClassName="items-end"
        >
          delete
        </KBtn>
      </Row>

      {/* Third row */}
      <Row>
        <KBtn
          className="w-10 items-end justify-start pl-[4px] pb-[2px]"
          childrenClassName="items-start"
        >
          tab
        </KBtn>
        <KBtn>
          <span className="block">Q</span>
        </KBtn>

        <KBtn>
          <span className="block">W</span>
        </KBtn>
        <KBtn>
          <span className="block">E</span>
        </KBtn>
        <KBtn>
          <span className="block">R</span>
        </KBtn>
        <KBtn>
          <span className="block">T</span>
        </KBtn>
        <KBtn>
          <span className="block">Y</span>
        </KBtn>
        <KBtn>
          <span className="block">U</span>
        </KBtn>
        <KBtn>
          <span className="block">I</span>
        </KBtn>
        <KBtn>
          <span className="block">O</span>
        </KBtn>
        <KBtn>
          <span className="block">P</span>
        </KBtn>
        <KBtn>
          <span className="block">{`{`}</span>
          <span className="block">{`[`}</span>
        </KBtn>
        <KBtn>
          <span className="block">{`}`}</span>
          <span className="block">{`]`}</span>
        </KBtn>
        <KBtn>
          <span className="block">{`|`}</span>
          <span className="block">{`\\`}</span>
        </KBtn>
      </Row>

      {/* Fourth Row */}
      <Row>
        <KBtn
          className="w-[2.8rem] items-end justify-start pl-[4px] pb-[2px]"
          childrenClassName="items-start"
        >
          caps lock
        </KBtn>
        <KBtn>
          <span className="block">A</span>
        </KBtn>

        <KBtn>
          <span className="block">S</span>
        </KBtn>
        <KBtn>
          <span className="block">D</span>
        </KBtn>
        <KBtn>
          <span className="block">F</span>
        </KBtn>
        <KBtn>
          <span className="block">G</span>
        </KBtn>
        <KBtn>
          <span className="block">H</span>
        </KBtn>
        <KBtn>
          <span className="block">J</span>
        </KBtn>
        <KBtn>
          <span className="block">K</span>
        </KBtn>
        <KBtn>
          <span className="block">L</span>
        </KBtn>
        <KBtn>
          <span className="block">{`:`}</span>
          <span className="block">{`;`}</span>
        </KBtn>
        <KBtn>
          <span className="block">{`"`}</span>
          <span className="block">{`'`}</span>
        </KBtn>
        <KBtn
          className="w-[2.85rem] items-end justify-end pr-[4px] pb-[2px]"
          childrenClassName="items-end"
        >
          return
        </KBtn>
      </Row>

      {/* Fifth Row */}
      <Row>
        <KBtn
          className="w-[3.65rem] items-end justify-start pl-[4px] pb-[2px]"
          childrenClassName="items-start"
        >
          shift
        </KBtn>
        <KBtn>
          <span className="block">Z</span>
        </KBtn>
        <KBtn>
          <span className="block">X</span>
        </KBtn>
        <KBtn>
          <span className="block">C</span>
        </KBtn>
        <KBtn>
          <span className="block">V</span>
        </KBtn>
        <KBtn>
          <span className="block">B</span>
        </KBtn>
        <KBtn>
          <span className="block">N</span>
        </KBtn>
        <KBtn>
          <span className="block">M</span>
        </KBtn>
        <KBtn>
          <span className="block">{`<`}</span>
          <span className="block">{`,`}</span>
        </KBtn>
        <KBtn>
          <span className="block">{`>`}</span>
          <span className="block">{`.`}</span>
        </KBtn>{" "}
        <KBtn>
          <span className="block">{`?`}</span>
          <span className="block">{`/`}</span>
        </KBtn>
        <KBtn
          className="w-[3.65rem] items-end justify-end pr-[4px] pb-[2px]"
          childrenClassName="items-end"
        >
          shift
        </KBtn>
      </Row>

      {/* sixth Row */}
      <Row>
        <KBtn className="" childrenClassName="h-full justify-between py-[4px]">
          <div className="flex justify-end w-full pr-1">
            <span className="block">fn</span>
          </div>
          <div className="flex justify-start w-full pl-1">
            <IconWorld className="h-[6px] w-[6px]" />
          </div>
        </KBtn>
        <KBtn className="" childrenClassName="h-full justify-between py-[4px]">
          <div className="flex justify-end w-full pr-1">
            <IconChevronUp className="h-[6px] w-[6px]" />
          </div>
          <div className="flex justify-start w-full pl-1">
            <span className="block">control</span>
          </div>
        </KBtn>
        <KBtn className="" childrenClassName="h-full justify-between py-[4px]">
          <div className="flex justify-end w-full pr-1">
            <OptionKey className="h-[6px] w-[6px]" />
          </div>
          <div className="flex justify-start w-full pl-1">
            <span className="block">option</span>
          </div>
        </KBtn>
        <KBtn
          className="w-8"
          childrenClassName="h-full justify-between py-[4px]"
        >
          <div className="flex justify-end w-full pr-1">
            <IconCommand className="h-[6px] w-[6px]" />
          </div>
          <div className="flex justify-start w-full pl-1">
            <span className="block">command</span>
          </div>
        </KBtn>
        <KBtn className="w-[8.2rem]"></KBtn>
        <KBtn
          className="w-8"
          childrenClassName="h-full justify-between py-[4px]"
        >
          <div className="flex justify-start w-full pl-1">
            <IconCommand className="h-[6px] w-[6px]" />
          </div>
          <div className="flex justify-start w-full pl-1">
            <span className="block">command</span>
          </div>
        </KBtn>
        <KBtn className="" childrenClassName="h-full justify-between py-[4px]">
          <div className="flex justify-start w-full pl-1">
            <OptionKey className="h-[6px] w-[6px]" />
          </div>
          <div className="flex justify-start w-full pl-1">
            <span className="block">option</span>
          </div>
        </KBtn>
        <div className="w-[4.9rem] mt-[2px] h-6 p-[0.5px] rounded-[4px] flex flex-col justify-end items-center">
          <KBtn className="w-6 h-3">
            <IconCaretUpFilled className="h-[6px] w-[6px]" />
          </KBtn>
          <div className="flex">
            <KBtn className="w-6 h-3">
              <IconCaretLeftFilled className="h-[6px] w-[6px]" />
            </KBtn>
            <KBtn className="w-6 h-3">
              <IconCaretDownFilled className="h-[6px] w-[6px]" />
            </KBtn>
            <KBtn className="w-6 h-3">
              <IconCaretRightFilled className="h-[6px] w-[6px]" />
            </KBtn>
          </div>
        </div>
      </Row>
    </div>
  );
};
export const KBtn = ({
  className,
  children,
  childrenClassName,
  backlit = true,
}: {
  className?: string;
  children?: React.ReactNode;
  childrenClassName?: string;
  backlit?: boolean;
}) => {
  return (
    <div
      className={cn(
        "p-[0.5px] rounded-[4px]",
        backlit && "bg-white/[0.2] shadow-xl shadow-white"
      )}
    >
      <div
        className={cn(
          "h-6 w-6 bg-[#0A090D] rounded-[3.5px] flex items-center justify-center",
          className
        )}
        style={{
          boxShadow:
            "0px -0.5px 2px 0 #0D0D0F inset, -0.5px 0px 2px 0 #0D0D0F inset",
        }}
      >
        <div
          className={cn(
            "text-neutral-200 text-[5px] w-full flex justify-center items-center flex-col",
            childrenClassName,
            backlit && "text-white"
          )}
        >
          {children}
        </div>
      </div>
    </div>
  );
};

export const Row = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex gap-[2px] mb-[2px] w-full flex-shrink-0">
      {children}
    </div>
  );
};

export const SpeakerGrid = () => {
  return (
    <div
      className="flex px-[0.5px] gap-[2px] mt-2 h-40"
      style={{
        backgroundImage:
          "radial-gradient(circle, #08080A 0.5px, transparent 0.5px)",
        backgroundSize: "3px 3px",
      }}
    ></div>
  );
};

export const OptionKey = ({ className }: { className: string }) => {
  return (
    <svg
      fill="none"
      version="1.1"
      id="icon"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 32 32"
      className={className}
    >
      <rect
        stroke="currentColor"
        strokeWidth={2}
        x="18"
        y="5"
        width="10"
        height="2"
      />
      <polygon
        stroke="currentColor"
        strokeWidth={2}
        points="10.6,5 4,5 4,7 9.4,7 18.4,27 28,27 28,25 19.6,25 "
      />
      <rect
        id="_Transparent_Rectangle_"
        className="st0"
        width="32"
        height="32"
        stroke="none"
      />
    </svg>
  );
};

const WishlabLogo = () => {
  return (
    <svg
      width="166"
      height="165"
      viewBox="0 0 165 166"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="h-3 w-3 text-white"
    >
      <path d="M0 0 C1.46972378 0.00747007 2.9394576 0.01315938 4.40919495 0.01715088 C8.25796513 0.03234724 12.10612148 0.07157569 15.95465088 0.1159668 C19.88960468 0.15705018 23.82465869 0.17518963 27.75976562 0.1953125 C35.46642421 0.23807715 43.17257888 0.30625387 50.87890625 0.390625 C50.74207695 1.84314773 50.59834354 3.29502131 50.45166016 4.74658203 C50.3723526 5.55515656 50.29304504 6.36373108 50.21133423 7.19680786 C49.80962087 9.84786524 49.07834106 11.30460149 47.25390625 13.265625 C46.78726563 13.79929687 46.320625 14.33296875 45.83984375 14.8828125 C39.68441253 19.61587316 33.83170457 19.80574365 26.3515625 19.68359375 C24.86818642 19.67722649 24.86818642 19.67722649 23.35484314 19.67073059 C20.21674616 19.65402629 17.07930697 19.61638915 13.94140625 19.578125 C11.80534786 19.56306751 9.66927934 19.54938097 7.53320312 19.53710938 C2.31488223 19.50414993 -2.90305875 19.45403338 -8.12109375 19.390625 C-8.1122113 20.27488159 -8.10332886 21.15913818 -8.09417725 22.07019043 C-8.01384183 30.42641461 -7.95303329 38.78250803 -7.91384506 47.13903046 C-7.89302022 51.43465221 -7.8647968 55.72995335 -7.81933594 60.02539062 C-7.77569477 64.17512641 -7.7519183 68.3245549 -7.74158478 72.47450256 C-7.73422602 74.05327691 -7.71985623 75.63203551 -7.69817352 77.2106781 C-7.56606575 87.23268626 -7.67163778 94.52726615 -14.80859375 102.328125 C-18.0154081 104.32482073 -19.23535798 104.70896449 -22.828125 105.01953125 C-24.03625854 105.13083374 -24.03625854 105.13083374 -25.26879883 105.24438477 C-25.88005615 105.29264404 -26.49131348 105.34090332 -27.12109375 105.390625 C-27.23709802 93.40320099 -27.32586548 81.41591119 -27.38015461 69.42803955 C-27.40621475 63.86116669 -27.44154792 58.29467872 -27.49829102 52.72802734 C-27.55273772 47.35283643 -27.58254123 41.97801504 -27.59547997 36.60256958 C-27.60469707 34.55488267 -27.62269612 32.50721529 -27.64974403 30.45968628 C-27.68620236 27.58466367 -27.69103206 24.7111552 -27.6887207 21.8359375 C-27.70669708 20.99508102 -27.72467346 20.15422455 -27.74319458 19.28788757 C-27.69034538 13.18653496 -25.9814339 9.12315978 -22.12109375 4.390625 C-15.73077975 -1.1264277 -8.00266927 -0.11975984 0 0 Z " fill="#FFFFFF" transform="translate(27.12109375,-0.390625)"/>
      <path d="M0 0 C4.00517396 1.60373148 6.6771098 4.42113986 9.640625 7.4453125 C10.16767029 7.97518768 10.69471558 8.50506287 11.23773193 9.05099487 C12.91325675 10.73767825 14.58167722 12.43119564 16.25 14.125 C17.38755851 15.27259388 18.52557436 16.41973461 19.6640625 17.56640625 C22.44803465 20.37238137 25.2256576 23.18450464 28 26 C23.37508621 31.55439924 18.44639036 36.68525669 13.3203125 41.77734375 C12.50754852 42.58869278 11.69478455 43.40004181 10.85739136 44.23597717 C8.28228262 46.8055259 5.7037038 49.37155968 3.125 51.9375 C1.36956054 53.68791929 -0.38565017 55.438568 -2.140625 57.18945312 C-6.42444082 61.46229302 -10.71110472 65.73225899 -15 70 C-18.43300299 68.51856023 -20.67171483 66.58138096 -23.30957031 63.94921875 C-24.15013977 63.11495361 -24.99070923 62.28068848 -25.85675049 61.42114258 C-26.75480408 60.51904053 -27.65285767 59.61693848 -28.578125 58.6875 C-29.96798615 57.30050903 -29.96798615 57.30050903 -31.38592529 55.88549805 C-33.3425837 53.93178301 -35.29559143 51.97450889 -37.24609375 50.01464844 C-39.75015854 47.49915795 -42.26313724 44.99279451 -44.7788887 42.48899841 C-47.17515944 40.1016736 -49.5638015 37.70677812 -51.953125 35.3125 C-52.85927551 34.41039795 -53.76542603 33.5082959 -54.69903564 32.57885742 C-55.52699646 31.74459229 -56.35495728 30.91032715 -57.20800781 30.05078125 C-57.94206848 29.31512939 -58.67612915 28.57947754 -59.43243408 27.8215332 C-61 26 -61 26 -61 24 C-45.96073888 21.47419654 -45.96073888 21.47419654 -39.56054688 25.55566406 C-34.87827009 29.54798319 -30.91005235 34.13730942 -26.94775391 38.82861328 C-23.91342439 42.2113316 -20.50038213 45.11245989 -17 48 C-14.05258428 46.66059606 -11.86592907 45.16010392 -9.50390625 42.953125 C-8.86259766 42.355 -8.22128906 41.756875 -7.56054688 41.140625 C-6.90119141 40.51671875 -6.24183594 39.8928125 -5.5625 39.25 C-4.57926758 38.33734375 -4.57926758 38.33734375 -3.57617188 37.40625 C0.25868701 33.8060214 3.72393933 30.11559067 7 26 C4.77122275 23.35426499 4.77122275 23.35426499 2 21 C-0.77858383 21 -1.69326262 21.72612734 -3.75 23.5625 C-4.1625 24.036875 -4.575 24.51125 -5 25 C-4.34 26.98 -3.68 28.96 -3 31 C-5.97 33.97 -8.94 36.94 -12 40 C-13.12044744 38.87955256 -14.23918133 37.75736229 -15.3515625 36.62890625 C-16.59239401 35.40277654 -17.8634895 34.20715964 -19.1484375 33.02734375 C-19.88320312 32.33769531 -20.61796875 31.64804688 -21.375 30.9375 C-22.08398438 30.28652344 -22.79296875 29.63554688 -23.5234375 28.96484375 C-25 27 -25 27 -24.98046875 25.0234375 C-23.69716781 22.37503158 -22.05447124 20.73184787 -19.9375 18.6875 C-19.12410156 17.89988281 -18.31070313 17.11226562 -17.47265625 16.30078125 C-14.67963552 13.70190414 -11.82560308 11.19007533 -8.9296875 8.70703125 C-5.81053864 5.94778419 -2.90248778 2.98412025 0 0 Z " fill="#CFAC22" transform="translate(100,35)"/>
      <path d="M0 0 C1.15371094 0.29003906 2.30742187 0.58007812 3.49609375 0.87890625 C2.01266375 4.32567625 0.06559187 6.55233926 -2.58642578 9.18847656 C-3.4271463 10.02904602 -4.26786682 10.86961548 -5.13406372 11.73565674 C-6.04243988 12.63371033 -6.95081604 13.53176392 -7.88671875 14.45703125 C-8.81612274 15.38360535 -9.74552673 16.31017944 -10.70309448 17.26483154 C-13.16794475 19.72206414 -15.63874291 22.17322986 -18.11083984 24.62316895 C-20.6348139 27.12664434 -23.15310013 29.63582688 -25.671875 32.14453125 C-30.61034222 37.0615815 -35.55511825 41.97224413 -40.50390625 46.87890625 C-44.50765056 45.04198236 -47.22348559 42.38772709 -50.25390625 39.25390625 C-50.76050781 38.73828125 -51.26710938 38.22265625 -51.7890625 37.69140625 C-53.03194527 36.42507286 -54.26855901 35.15259185 -55.50390625 33.87890625 C-54.09545907 30.6636632 -52.40045839 28.55706757 -49.87890625 26.12890625 C-48.93144531 25.20851563 -48.93144531 25.20851563 -47.96484375 24.26953125 C-47.48273438 23.810625 -47.000625 23.35171875 -46.50390625 22.87890625 C-44.85390625 23.86890625 -43.20390625 24.85890625 -41.50390625 25.87890625 C-40.85131836 25.12158203 -40.19873047 24.36425781 -39.52636719 23.58398438 C-16.54560345 -2.75186752 -16.54560345 -2.75186752 0 0 Z " fill="#CFAC22" transform="translate(159.50390625,58.12109375)"/>
      <path d="M0 0 C0.79198288 0.0028299 1.58396576 0.00565979 2.39994812 0.00857544 C4.91652874 0.01972387 7.43274664 0.04481828 9.94921875 0.0703125 C11.66080213 0.08034921 13.37239112 0.08947386 15.08398438 0.09765625 C19.26836781 0.11964569 23.45248189 0.15413842 27.63671875 0.1953125 C27.3694202 1.78190142 27.08799498 3.36611383 26.80078125 4.94921875 C26.64561035 5.8316626 26.49043945 6.71410645 26.33056641 7.62329102 C25.2266975 11.71521886 23.04962364 14.71140296 19.63671875 17.1953125 C13.90789475 19.70026431 9.41200037 20.6210976 3.19921875 20.48828125 C2.43367676 20.48403641 1.66813477 20.47979156 0.87939453 20.47541809 C-1.53520812 20.45879578 -3.94893636 20.42117756 -6.36328125 20.3828125 C-8.01300867 20.36774428 -9.66274934 20.35405964 -11.3125 20.34179688 C-15.32975745 20.30894667 -19.34637177 20.25728223 -23.36328125 20.1953125 C-22.62794838 13.04787702 -21.43250874 9.02844557 -15.92578125 3.9453125 C-10.69639148 0.37402193 -6.23032424 -0.08443904 0 0 Z " fill="#F57618" transform="translate(43.36328125,36.8046875)"/>

    </svg>
  );
};
