EESchema Schematic File Version 4
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector:Raspberry_Pi_2_3 J?
U 1 1 613F9E78
P 5100 3400
F 0 "J?" H 5100 4878 50  0000 C CNN
F 1 "Raspberry_Pi_2_3" H 5100 4787 50  0000 C CNN
F 2 "" H 5100 3400 50  0001 C CNN
F 3 "https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf" H 5100 3400 50  0001 C CNN
	1    5100 3400
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x03_Female PIR_detector
U 1 1 613FA26E
P 8800 1600
F 0 "PIR_detector" H 8827 1626 50  0000 L CNN
F 1 "Conn_01x03_Female" H 8827 1535 50  0000 L CNN
F 2 "" H 8800 1600 50  0001 C CNN
F 3 "~" H 8800 1600 50  0001 C CNN
	1    8800 1600
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Female J?
U 1 1 613FA3D6
P 550 1600
F 0 "J?" H 444 1275 50  0000 C CNN
F 1 "Conn_01x02_Female" H 444 1366 50  0000 C CNN
F 2 "" H 550 1600 50  0001 C CNN
F 3 "~" H 550 1600 50  0001 C CNN
	1    550  1600
	-1   0    0    1   
$EndComp
Wire Wire Line
	5000 1500 5000 2100
Wire Wire Line
	3800 5050 4700 5050
Wire Wire Line
	4700 5050 4700 4700
Wire Wire Line
	5000 1500 7600 1500
Connection ~ 5000 1500
Wire Wire Line
	4700 5050 6900 5050
Wire Wire Line
	8500 5050 8500 3700
Wire Wire Line
	8500 1700 8600 1700
Connection ~ 4700 5050
$Comp
L Device:R_Small R?
U 1 1 613FA53A
P 8150 2350
F 0 "R?" H 8209 2396 50  0000 L CNN
F 1 "R_Small" H 8209 2305 50  0000 L CNN
F 2 "" H 8150 2350 50  0001 C CNN
F 3 "~" H 8150 2350 50  0001 C CNN
	1    8150 2350
	1    0    0    -1  
$EndComp
$Comp
L Device:R_Small R?
U 1 1 613FA5BE
P 8150 3400
F 0 "R?" H 8209 3446 50  0000 L CNN
F 1 "R_Small" H 8209 3355 50  0000 L CNN
F 2 "" H 8150 3400 50  0001 C CNN
F 3 "~" H 8150 3400 50  0001 C CNN
	1    8150 3400
	1    0    0    -1  
$EndComp
Wire Wire Line
	8150 2250 8150 1600
Wire Wire Line
	8150 1600 8600 1600
Wire Wire Line
	8150 3500 8150 3700
Wire Wire Line
	8150 3700 8500 3700
Connection ~ 8500 3700
Wire Wire Line
	8500 3700 8500 1700
Wire Wire Line
	3800 1600 3800 5050
$Comp
L Connector:Conn_01x03_Female Keyboard_Limit_Switches
U 1 1 613FB16C
P 3250 3800
F 0 "Keyboard_Limit_Switches" H 3144 3475 50  0000 C CNN
F 1 "Conn_01x03_Female" H 3144 3566 50  0000 C CNN
F 2 "" H 3250 3800 50  0001 C CNN
F 3 "~" H 3250 3800 50  0001 C CNN
	1    3250 3800
	-1   0    0    1   
$EndComp
Wire Wire Line
	3450 3700 4300 3700
Wire Wire Line
	3450 3800 4300 3800
Wire Wire Line
	3450 3900 4300 3900
Wire Wire Line
	750  1600 3800 1600
$Comp
L Transistor_FET:2N7000 Q?
U 1 1 614128E7
P 3050 5800
F 0 "Q?" H 3255 5754 50  0000 L CNN
F 1 "2N7000" H 3255 5845 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 3250 5725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N7000.pdf" H 3050 5800 50  0001 L CNN
	1    3050 5800
	-1   0    0    1   
$EndComp
$Comp
L Transistor_FET:2N7000 Q?
U 1 1 6141295B
P 2350 5800
F 0 "Q?" H 2555 5754 50  0000 L CNN
F 1 "2N7000" H 2555 5845 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 2550 5725 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N7000.pdf" H 2350 5800 50  0001 L CNN
	1    2350 5800
	-1   0    0    1   
$EndComp
Wire Wire Line
	2950 6200 2950 6000
Wire Wire Line
	2250 6000 2250 6100
Wire Wire Line
	4300 2900 2950 2900
Wire Wire Line
	2950 2900 2950 5600
Wire Wire Line
	4300 3600 2250 3600
Wire Wire Line
	2250 3600 2250 5600
Wire Wire Line
	5900 3300 6250 3300
Wire Wire Line
	6250 3300 6250 5300
$Comp
L Device:R_Small R?
U 1 1 614196B0
P 2950 2600
F 0 "R?" H 3009 2646 50  0000 L CNN
F 1 "10k" H 3009 2555 50  0000 L CNN
F 2 "" H 2950 2600 50  0001 C CNN
F 3 "~" H 2950 2600 50  0001 C CNN
	1    2950 2600
	1    0    0    -1  
$EndComp
$Comp
L Device:R_Small R?
U 1 1 61419718
P 2250 2600
F 0 "R?" H 2309 2646 50  0000 L CNN
F 1 "10k" H 2309 2555 50  0000 L CNN
F 2 "" H 2250 2600 50  0001 C CNN
F 3 "~" H 2250 2600 50  0001 C CNN
	1    2250 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	2950 2700 2950 2900
Connection ~ 2950 2900
Wire Wire Line
	2250 3600 2250 2700
Connection ~ 2250 3600
Wire Wire Line
	5200 2100 5200 1850
Wire Wire Line
	5200 1850 3250 1850
Wire Wire Line
	2250 2500 2250 1850
Wire Wire Line
	2950 2500 2950 1850
Connection ~ 2950 1850
Wire Wire Line
	2950 1850 2550 1850
$Comp
L Device:R_Small R?
U 1 1 61422164
P 2700 3150
F 0 "R?" H 2759 3196 50  0000 L CNN
F 1 "10k" H 2759 3105 50  0000 L CNN
F 2 "" H 2700 3150 50  0001 C CNN
F 3 "~" H 2700 3150 50  0001 C CNN
	1    2700 3150
	1    0    0    -1  
$EndComp
$Comp
L Device:R_Small R?
U 1 1 614221BC
P 2050 3150
F 0 "R?" H 2109 3196 50  0000 L CNN
F 1 "10k" H 2109 3105 50  0000 L CNN
F 2 "" H 2050 3150 50  0001 C CNN
F 3 "~" H 2050 3150 50  0001 C CNN
	1    2050 3150
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 3250 2700 6200
Wire Wire Line
	2700 6200 2950 6200
Wire Wire Line
	2050 3250 2050 6100
Wire Wire Line
	2050 6100 2250 6100
Wire Wire Line
	2050 3050 2050 1500
Connection ~ 2050 1500
Wire Wire Line
	2050 1500 2700 1500
Wire Wire Line
	2700 3050 2700 1500
Connection ~ 2700 1500
Wire Wire Line
	2700 1500 5000 1500
Wire Wire Line
	2550 5800 2550 1850
Connection ~ 2550 1850
Wire Wire Line
	2550 1850 2250 1850
Wire Wire Line
	3250 5800 3250 1850
Connection ~ 3250 1850
Wire Wire Line
	3250 1850 2950 1850
$Comp
L Driver_Motor:L298HN U?
U 1 1 6143A573
P 9650 4050
F 0 "U?" H 9650 4928 50  0000 C CNN
F 1 "L298HN" H 9650 4837 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-220-15_P2.54x2.54mm_StaggerOdd_Lead4.58mm_Vertical" H 9700 3400 50  0001 L CNN
F 3 "http://www.st.com/st-web-ui/static/active/en/resource/technical/document/datasheet/CD00000240.pdf" H 9800 4300 50  0001 C CNN
	1    9650 4050
	1    0    0    -1  
$EndComp
Wire Wire Line
	8500 5050 9650 5050
Wire Wire Line
	9650 5050 9650 4750
Connection ~ 8500 5050
Wire Wire Line
	4300 4100 4200 4100
Wire Wire Line
	4200 4100 4200 4800
Wire Wire Line
	4200 4800 8850 4800
Wire Wire Line
	8850 4800 8850 3550
Wire Wire Line
	8850 3550 9050 3550
Wire Wire Line
	9050 3650 8950 3650
Wire Wire Line
	8950 3650 8950 4900
Wire Wire Line
	8950 4900 4100 4900
Wire Wire Line
	4100 4900 4100 4000
Wire Wire Line
	4100 4000 4300 4000
Wire Wire Line
	9650 3350 9650 2050
Wire Wire Line
	9650 2050 7600 2050
Wire Wire Line
	7600 2050 7600 1500
Connection ~ 7600 1500
Wire Wire Line
	7600 1500 8600 1500
$Comp
L Connector:Conn_01x02_Female J?
U 1 1 61447990
P 10800 3850
F 0 "J?" H 10827 3826 50  0000 L CNN
F 1 "Motor out" H 10827 3735 50  0000 L CNN
F 2 "" H 10800 3850 50  0001 C CNN
F 3 "~" H 10800 3850 50  0001 C CNN
	1    10800 3850
	1    0    0    -1  
$EndComp
Wire Wire Line
	10600 3850 10250 3850
Wire Wire Line
	10600 3950 10250 3950
$Comp
L Connector:Conn_01x02_Female J?
U 1 1 6144CFE9
P 10700 3150
F 0 "J?" H 10727 3126 50  0000 L CNN
F 1 "12V power in" H 10727 3035 50  0000 L CNN
F 2 "" H 10700 3150 50  0001 C CNN
F 3 "~" H 10700 3150 50  0001 C CNN
	1    10700 3150
	1    0    0    -1  
$EndComp
Wire Wire Line
	10500 3150 9750 3150
Wire Wire Line
	9750 3150 9750 3350
Wire Wire Line
	10500 3250 10500 5050
Wire Wire Line
	10500 5050 9650 5050
Connection ~ 9650 5050
Wire Wire Line
	5900 3200 5950 3200
Wire Wire Line
	5950 3200 5950 5450
$Comp
L Transistor_FET:IRLZ34N Q?
U 1 1 614850A3
P 8300 5700
F 0 "Q?" H 8505 5746 50  0000 L CNN
F 1 "IRLZ34N" H 8505 5655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-220-3_Vertical" H 8550 5625 50  0001 L CIN
F 3 "http://www.infineon.com/dgdl/irlz34npbf.pdf?fileId=5546d462533600a40153567206892720" H 8300 5700 50  0001 L CNN
	1    8300 5700
	1    0    0    -1  
$EndComp
$Comp
L Transistor_FET:IRLZ34N Q?
U 1 1 614851FB
P 7500 5700
F 0 "Q?" H 7705 5746 50  0000 L CNN
F 1 "IRLZ34N" H 7705 5655 50  0000 L CNN
F 2 "Package_TO_SOT_THT:TO-220-3_Vertical" H 7750 5625 50  0001 L CIN
F 3 "http://www.infineon.com/dgdl/irlz34npbf.pdf?fileId=5546d462533600a40153567206892720" H 7500 5700 50  0001 L CNN
	1    7500 5700
	1    0    0    -1  
$EndComp
Wire Wire Line
	6250 5300 8100 5300
Wire Wire Line
	8100 5300 8100 5700
Wire Wire Line
	5950 5450 7300 5450
Wire Wire Line
	7300 5450 7300 5700
Wire Wire Line
	6900 5050 6900 6050
Wire Wire Line
	6900 6050 7600 6050
Wire Wire Line
	8400 6050 8400 5900
Connection ~ 6900 5050
Wire Wire Line
	7600 5900 7600 6050
Connection ~ 7600 6050
Wire Wire Line
	7600 6050 8400 6050
$Comp
L Connector:Conn_01x03_Female J?
U 1 1 614A5C3E
P 9700 5400
F 0 "J?" H 9727 5426 50  0000 L CNN
F 1 "Lights" H 9727 5335 50  0000 L CNN
F 2 "" H 9700 5400 50  0001 C CNN
F 3 "~" H 9700 5400 50  0001 C CNN
	1    9700 5400
	1    0    0    -1  
$EndComp
Wire Wire Line
	9500 5500 8400 5500
Wire Wire Line
	9500 5400 7600 5400
Wire Wire Line
	7600 5400 7600 5500
Wire Wire Line
	9750 3150 8650 3150
Wire Wire Line
	8650 3150 8650 5300
Wire Wire Line
	8650 5300 9500 5300
Connection ~ 9750 3150
$Comp
L Relay_SolidState:S102S01 U?
U 1 1 614ADD53
P 4400 6000
F 0 "U?" H 4400 6325 50  0000 C CNN
F 1 "S102S01" H 4400 6234 50  0000 C CNN
F 2 "Package_SIP:SIP4_Sharp-SSR_P7.62mm_Straight" H 4200 5800 50  0001 L CIN
F 3 "http://www.sharp-world.com/products/device/lineup/data/pdf/datasheet/s102s01_e.pdf" H 4400 6000 50  0001 L CNN
	1    4400 6000
	1    0    0    -1  
$EndComp
$Comp
L Relay_SolidState:S102S01 U?
U 1 1 614ADE1A
P 4450 6700
F 0 "U?" H 4450 7025 50  0000 C CNN
F 1 "S102S01" H 4450 6934 50  0000 C CNN
F 2 "Package_SIP:SIP4_Sharp-SSR_P7.62mm_Straight" H 4250 6500 50  0001 L CIN
F 3 "http://www.sharp-world.com/products/device/lineup/data/pdf/datasheet/s102s01_e.pdf" H 4450 6700 50  0001 L CNN
	1    4450 6700
	1    0    0    -1  
$EndComp
Wire Wire Line
	2950 6200 3550 6200
Wire Wire Line
	3550 6200 3550 5900
Wire Wire Line
	3550 5900 4100 5900
Connection ~ 2950 6200
Wire Wire Line
	2250 6100 2250 6600
Connection ~ 2250 6100
Wire Wire Line
	2250 6600 4150 6600
Wire Wire Line
	3800 5050 3800 6100
Wire Wire Line
	3800 6800 4150 6800
Connection ~ 3800 5050
Wire Wire Line
	4100 6100 3800 6100
Connection ~ 3800 6100
Wire Wire Line
	3800 6100 3800 6800
Wire Wire Line
	750  1500 2050 1500
$Comp
L Connector:Conn_01x03_Female J?
U 1 1 614EA54A
P 5850 6300
F 0 "J?" H 5878 6326 50  0000 L CNN
F 1 "mains" H 5878 6235 50  0000 L CNN
F 2 "" H 5850 6300 50  0001 C CNN
F 3 "~" H 5850 6300 50  0001 C CNN
	1    5850 6300
	1    0    0    -1  
$EndComp
Wire Wire Line
	5650 6300 5350 6300
Wire Wire Line
	5350 6300 5350 5900
Wire Wire Line
	5350 5900 4700 5900
Wire Wire Line
	4750 6600 5350 6600
Wire Wire Line
	5350 6600 5350 6300
Connection ~ 5350 6300
Wire Wire Line
	5650 6400 5650 6800
Wire Wire Line
	5650 6800 4750 6800
Wire Wire Line
	5650 6200 5650 6100
Wire Wire Line
	5650 6100 4700 6100
$Comp
L Sensor_Temperature:DS18B20 U?
U 1 1 614F59A0
P 7100 3700
F 0 "U?" H 6870 3746 50  0000 R CNN
F 1 "DS18B20" H 6870 3655 50  0000 R CNN
F 2 "Package_TO_SOT_THT:TO-92_Inline" H 6100 3450 50  0001 C CNN
F 3 "http://datasheets.maximintegrated.com/en/ds/DS18B20.pdf" H 6950 3950 50  0001 C CNN
	1    7100 3700
	1    0    0    -1  
$EndComp
Wire Wire Line
	7100 4000 7100 5050
Wire Wire Line
	6900 5050 7100 5050
Connection ~ 7100 5050
Wire Wire Line
	7100 5050 8500 5050
Wire Wire Line
	5200 1850 7100 1850
Wire Wire Line
	7100 1850 7100 3400
Connection ~ 5200 1850
$Comp
L Device:R_Small R?
U 1 1 614FBEDF
P 7450 2800
F 0 "R?" H 7509 2846 50  0000 L CNN
F 1 "10k" H 7509 2755 50  0000 L CNN
F 2 "" H 7450 2800 50  0001 C CNN
F 3 "~" H 7450 2800 50  0001 C CNN
	1    7450 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	7450 3700 7400 3700
Wire Wire Line
	7100 1850 7450 1850
Wire Wire Line
	7450 1850 7450 2700
Connection ~ 7100 1850
Wire Wire Line
	7450 2900 7450 3100
Wire Wire Line
	8150 2450 8150 2550
Wire Wire Line
	8150 2550 6650 2550
Wire Wire Line
	6650 2550 6650 1700
Wire Wire Line
	6650 1700 4000 1700
Wire Wire Line
	4000 1700 4000 2800
Wire Wire Line
	4000 2800 4300 2800
Connection ~ 8150 2550
Wire Wire Line
	8150 2550 8150 3300
Wire Wire Line
	5900 3100 7450 3100
Connection ~ 7450 3100
Wire Wire Line
	7450 3100 7450 3700
$EndSCHEMATC
