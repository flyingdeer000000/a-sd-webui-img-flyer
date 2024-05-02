@echo off

set "input_dir=%~1"
set "output_dir=%~2"

if "%input_dir%"=="" (
    echo Input directory not provided.
    exit /b
)

if "%output_dir%"=="" (
    echo Output directory not provided.
    exit /b
)

mkdir "%output_dir%" 2>nul

for %%F in ("%input_dir%\*.wav") do (
    ffmpeg -i "%%F" -filter_complex "[0:a]asplit=2[out1][out2]" -map "[out1]" "%output_dir%\%%~nF_part1.wav" -map "[out2]" "%output_dir%\%%~nF_part2.wav"
)