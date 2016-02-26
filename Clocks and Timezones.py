from datetime import datetime
from pytz import timezone
from pytz import all_timezones
import pygame
import time
import math

def textObjects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def smallMessageDisplay(text, clockNumber, location):
    smallText = pygame.font.Font("freesansbold.ttf", 18)
    textSurf, textRect = textObjects(text, smallText, white)
    if location == "Above":
        y= int(clockHeight / float(4))
    elif location == "Mid":
        y = clockHeight *2 + clockMargin
    else:
        y = clockHeight *2.25 + clockMargin
    textRect.center = (int(int((clockNumber*3*(clockWidth+clockMargin))/float(3)))+clockX, y)
    clockDisplay.blit(textSurf, textRect)

times = [0,0,0,0]
branchOpenHoursInLocalTime = [9, 21]
fmt = "%H:%M:%S"
now_utc = datetime.now(timezone('UTC')) #Put the current time in UTC
times[0] = now_utc.astimezone(timezone('US/Pacific')).strftime(fmt)
times[1] = now_utc.astimezone(timezone('US/Eastern')).strftime(fmt)
times[2] = now_utc.astimezone(timezone('Europe/London')).strftime(fmt)
#times[3] = now_utc.astimezone(timezone('Canada/Newfoundland')).strftime(fmt)

secondLength = 100
minuteLength = 100
hourLength = .5*minuteLength
clockMargin = 30
clockTickLength = 20
clockTickInnerPadding = 15
clockWidth = (minuteLength*2) + (clockTickLength*2) + (clockTickInnerPadding*2)
clockHeight = clockWidth
clockX = (minuteLength) + (clockTickLength) + (clockTickInnerPadding) + clockMargin

pygame.init()
black = (0,0,0)
clock = pygame.time.Clock()
display_width = int(3*(clockWidth+clockMargin))+clockMargin
display_height = 768
myCharacter = ""
clockDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Clocks')
exiting = False
brightness = 2

while exiting == False:
    brightness = min(brightness * 1.25, 255)
    white = (brightness, brightness, brightness)
    red = (brightness, 0, 0)
    secondColor = red
    minuteColor = white
    hourColor = white
    clockTickColor = white
    
    
    now_utc = datetime.now(timezone('UTC')) #Put the current time in UTC
    #try:
    for i in range(3):
        for j in range(12):
            pygame.draw.line(clockDisplay, clockTickColor,
            (int(i*(clockWidth + clockMargin) + clockX + (int(round((minuteLength + clockTickInnerPadding) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
            int(clockHeight + clockMargin + int(round((minuteLength + clockTickInnerPadding) * math.sin((math.pi/180)*(((j+1)/float(12)))*360))))),
            (int(i*(clockWidth + clockMargin) + clockX  + (int(round((minuteLength + clockTickInnerPadding + clockTickLength) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
            int(clockHeight + clockMargin + int(round((minuteLength + clockTickInnerPadding + clockTickLength) * math.sin((math.pi/180)*(((j+1)/float(12)))*360))))))
        if i == 0:
            myTimeZone = 'US/Pacific'
            myCity = "Portland"
        elif i == 1:
            myTimeZone = 'US/Eastern'
            myCity = "New York"
        elif i ==2:
            myTimeZone = 'Europe/London'
            myCity = "London"
        myCityTime = now_utc.astimezone(timezone(myTimeZone)).strftime("%m-%d-%Y %H:%M:%S %Z%z")
        seconds = float(now_utc.astimezone(timezone(myTimeZone)).strftime("%S"))
        minutes = float(now_utc.astimezone(timezone(myTimeZone)).strftime("%M"))
        hours = float(now_utc.astimezone(timezone(myTimeZone)).strftime("%H"))
        #if hours in branchOpenHoursInLocalTime == True:
        #    thisCityBranchOpen = "Branch Open"
        #else:
        #    thisCityBranchOpen = "Branch Closed"
        smallMessageDisplay(myCity, i, "Above")
        smallMessageDisplay(myCityTime, i, "Mid")
        #smallMessageDisplay(thisCityBranchOpen, i, "Below")
        #DRAW HOUR HAND
        pygame.draw.line(clockDisplay, hourColor, (i*(clockWidth + clockMargin) + clockX , clockHeight + clockMargin),
                         (int(i*(clockWidth + clockMargin) + clockX  + (int(round(hourLength * math.cos((math.pi/180)*((((hours-3)%float(12))/float(12))+(minutes/float(60)/12))*360))))),
                          int(clockHeight + clockMargin + int(round(hourLength * math.sin((math.pi/180)*((((hours-3)%float(12))/float(12))+(minutes/float(60)/12))*360))))), 2)
        #DRAW MINUTE HAND
        pygame.draw.line(clockDisplay, minuteColor, (i*(clockWidth + clockMargin) + clockX , clockHeight + clockMargin),
                         (int(i*(clockWidth + clockMargin) + clockX  + (int(round(minuteLength * math.cos((math.pi/180)*((minutes-15)/float(60))*360))))),
                          int(clockHeight + clockMargin + int(round(minuteLength * math.sin((math.pi/180)*((minutes-15)/float(60))*360))))), 2)
        #DRAW SECOND HAND
        pygame.draw.line(clockDisplay, secondColor, (i*(clockWidth + clockMargin) + clockX , clockHeight + clockMargin),
                         (int(i*(clockWidth + clockMargin) + clockX  + (int(round(secondLength * math.cos((math.pi/180)*((seconds-15)/float(60))*360))))),
                          int(clockHeight + clockMargin + int(round(secondLength * math.sin((math.pi/180)*((seconds-15)/float(60))*360))))), 1)
    pygame.display.update()
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exiting = True
    clockDisplay.fill(black)
pygame.quit()
quit()



#for zone in all_timezones:
#    print zone
