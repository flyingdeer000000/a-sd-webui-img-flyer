@echo off

set "input_dir=%~1"
set "output_dir=%~2"

if "%input_dir%"=="" (
    echo Input directory not provided.
    exit /b
)

if "%output_dir%"=="" (
    set "output_dir=%input_dir%\output"
)

mkdir "%output_dir%" 2>nul

for %%F in ("%input_dir%\*.wav") do (
    setlocal enabledelayedexpansion
    for /F "usebackq" %%A in (`ffprobe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 "%%F"`) do (
        set "duration=%%A"
        set /A "half_duration=!duration!/2"
    )

    echo [ * ] Duration: !duration!
    echo [ * ] Half Duration: !half_duration!

    ffmpeg -i "%%F" -ss 0 -t !half_duration! -c copy "%output_dir%\%%~nF_part1.wav"
    ffmpeg -i "%%F" -ss !half_duration! -c copy "%output_dir%\%%~nF_part2.wav"
    endlocal
)