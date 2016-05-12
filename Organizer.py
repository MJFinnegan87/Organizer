import wx
import datetime
from pytz import timezone
from pytz import all_timezones
import time
import math

class Frame(wx.Frame):
    def __init__(self, parent, title, windowWidth, windowHeight):
        super(Frame, self).__init__(parent, title=title, 
            size=(windowWidth, windowHeight), style=wx.NO_BORDER)# | wx.STAY_ON_TOP)
        self.justLoading = True
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.mouseOver = True
        self.numberOfClocks = 3

        self.thisMonthCalDayColor = (255,255,255)
        self.otherMonthCalDayColor = (96,96,96)
        self.calTodayColor = (255,0,0)
        self.black = (0,0,0) 
        #self.display_width = int(3*(self.clockWidth+self.clockMargin))+self.clockMargin
        #self.display_height = 768

        self.bgColorMouseOver = (15, 15, 15)
        self.fgColorMouseOver = (255, 255, 255)
        self.bgColorMouseAway = (15, 15, 15)
        self.fgColorMouseAway = (255, 255, 255)
        
        self.SetBackgroundColour(self.bgColorMouseOver)
        self.mostOpaqueLevel = 254 #254
        self.leastOpaqueLevel = 164 #212
        self.alphaTransparency = self.leastOpaqueLevel
        self.transparencyChangeSpeed = 1000
        self.transparencyChangeAmount = 1
        self.SetBackgroundColour(self.bgColorMouseOver)
        self.displayTitleBar = False
        self.tzArray = ['America/Los_Angeles', 'America/New_York', 'Europe/London']
        self.tzDescArray = ["Seattle", "New York", "London"]
        self.changeAlpha_timer = wx.Timer(self)
        self.changeAlpha_timer.Start(self.transparencyChangeSpeed)

        self.appClocks =[]
        for i in xrange(self.numberOfClocks):
            self.appClocks.append(clocks(self.tzArray[i], self.tzDescArray[i]))


        #self.Bind(wx.EVT_LEAVE_WINDOW, self.mouseAway) #THIS WAY, CLICKING WINDOW TEXT DOESN'T RESULT IN TRANSPARENT WINDOW
        self.Bind(wx.EVT_KILL_FOCUS, self.mouseAway)
        #self.Bind(wx.EVT_ENTER_WINDOW, self.mouseReturn) #THIS WAY, CLICKING WINDOW TEXT DOESN'T RESULT IN TRANSPARENT WINDOW
        self.Bind(wx.EVT_SET_FOCUS, self.mouseReturn)
        self.Bind(wx.EVT_LEFT_DCLICK, self.toggleTitleBar)
        self.Bind(wx.EVT_CLOSE, self.closeWindow)
        self.Bind(wx.EVT_MOTION, self.mouseMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftDown)
        
        self.Bind(wx.EVT_TIMER, self.updateAndDrawClocks)
        self.lastMouseClickPos = (0,0)
        self.justLoading = False
        self.Centre()
        self.Show()
        self.drawCalendar()
        self.updateAndDrawClocks()
        self.drawClockText(self.appClocks)
        del self.tzArray
        del self.tzDescArray


        #for zone in all_timezones:
        #    print zone


    def selectTimeZone(self):
        if self.justLoading == False:
            listOfAvailableTimeZones = []
            for zone in all_timezones:
                listOfAvailableTimeZones.append(zone)

            chooseOneBox = wx.SingleChoiceDialog(None, "What time zone should this clock show?", "Time Zone Selection", listOfAvailableTimeZones)
            if chooseOneBox.ShowModal() == wx.ID_OK:
                selTimeZone = chooseOneBox.GetStringSelection()

    def createTextObj(self, displayText, x, y, displayColor, alignX, alignY, displayFont):
        dc = wx.ClientDC(self)
        dc.SetFont(displayFont)
        #dc.SetFont(wx.Font(pointSize = 16, family = wx.DECORATIVE, style = wx.NORMAL, weight = wx.NORMAL))#, faceName = 'Consolas'))
        textObj = wx.StaticText(self, -1, displayText)
        textObj.SetFont(displayFont)#, faceName = 'Consolas'))
        textObj.SetForegroundColour(displayColor)
        if alignX == "C" and alignY == "C":
            w,h = dc.GetTextExtent(displayText)
            textObj.SetPosition((int(x-(w/float(2))), int(y-h/float(2))))
        elif alignX == "L" and alignY == "T":
            textObj.SetPosition((int(x), int(y)))
        return textObj

    def drawClockText(self, displayClocks):
        self.timeZoneCityLabel1 = self.createTextObj(displayClocks[0].tzDesc, 0*3*(displayClocks[0].clockWidth+displayClocks[0].clockMargin)/float(3) + displayClocks[0].clockX, displayClocks[0].clockY, self.fgColorMouseOver, "C", "C",  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel2 = self.createTextObj(displayClocks[1].tzDesc, 1*3*(displayClocks[1].clockWidth+displayClocks[1].clockMargin)/float(3) + displayClocks[1].clockX, displayClocks[1].clockY, self.fgColorMouseOver, "C", "C",  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel3 = self.createTextObj(displayClocks[2].tzDesc, 2*3*(displayClocks[2].clockWidth+displayClocks[2].clockMargin)/float(3) + displayClocks[2].clockX, displayClocks[2].clockY, self.fgColorMouseOver, "C", "C", displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        #self.timeZoneTimeLabel1 = self.createTextObj(displayClocks[0].tzDescArray[0], 0*3*(displayClocks.clockWidth+self.clockMargin)/float(3) + displayClocks.clockX, displayClocks.clockY, self.fgColorMouseOver, displayCentered=True,  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        #self.timeZoneTimeLabel2 = self.createTextObj(displayClocks[0].tzDescArray[0], 0*3*(displayClocks.clockWidth+self.clockMargin)/float(3) + displayClocks.clockX, displayClocks.clockY, self.fgColorMouseOver, displayCentered=True,  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        #self.timeZoneTimeLabel3 = self.createTextObj(displayClocks[0].tzDescArray[0], 0*3*(displayClocks.clockWidth+self.clockMargin)/float(3) + displayClocks.clockX, displayClocks.clockY, self.fgColorMouseOver, displayCentered=True,  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        
##        dc = wx.ClientDC(self)
##        dc.SetFont(wx.Font(pointSize = 16, family = wx.DECORATIVE, style = wx.NORMAL, weight = wx.NORMAL))#, faceName = 'Consolas'))
##
##        self.timeZoneCityLabel1 = wx.StaticText(self, -1, self.tzDescArray[0])
##        self.timeZoneCityLabel2 = wx.StaticText(self, -1, self.tzDescArray[1])
##        self.timeZoneCityLabel3 = wx.StaticText(self, -1, self.tzDescArray[2])
##
##        self.timeZoneCityLabel1.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))#, faceName = 'Consolas'))
##        self.timeZoneCityLabel1.SetForegroundColour(self.fgColorMouseOver)
##        self.timeZoneCityLabel2.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
##        self.timeZoneCityLabel2.SetForegroundColour(self.fgColorMouseOver)
##        self.timeZoneCityLabel3.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
##        self.timeZoneCityLabel3.SetForegroundColour(self.fgColorMouseOver)
##
##        #CENTER ALIGN NOW THAT TEXT HAS BEEN DRAWN AND LENGTH IS KNOWN
##        w,h = dc.GetTextExtent(self.tzDescArray[0])
##        self.timeZoneCityLabel1.SetPosition((int(int((0*3*(self.clockWidth+self.clockMargin))/float(3)))+self.clockX-w/2, int(self.clockHeight / float(4))))
##        w,h = dc.GetTextExtent(self.tzDescArray[1])
##        self.timeZoneCityLabel2.SetPosition((int(int((1*3*(self.clockWidth+self.clockMargin))/float(3)))+self.clockX-w/2, int(self.clockHeight / float(4))))
##        w,h = dc.GetTextExtent(self.tzDescArray[2])
##        self.timeZoneCityLabel3.SetPosition((int(int((2*3*(self.clockWidth+self.clockMargin))/float(3)))+self.clockX-w/2, int(self.clockHeight / float(4))))
        
    def drawCalendar(self):
        ithDay = 1
        jthRow = 0
        monthToDraw = -1
    
        while monthToDraw <= 1:
            if datetime.datetime.today().month + monthToDraw < 1:
                prevMonthDec = datetime.datetime.today().month + monthToDraw + 12
                yearAdj = -1
            else:
                prevMonthDec = 0
                yearAdj = 0
            try:
                thisDate = datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + monthToDraw + prevMonthDec, ithDay, 0, 0, 0, 0)
                self.calDate1 = wx.StaticText(self, -1, str(ithDay), pos=(700 + 35*((thisDate.weekday() + 1)%7), 40 + 35*jthRow))
                self.calDate1.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
                if (datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + monthToDraw + prevMonthDec, ithDay, 0, 0, 0, 0) == datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 0, 0, 0, 0)):
                    self.calDate1.SetForegroundColour(self.calTodayColor)
                else:
                    if monthToDraw == 0:
                        self.calDate1.SetForegroundColour(self.thisMonthCalDayColor)
                    else:
                        self.calDate1.SetForegroundColour(self.otherMonthCalDayColor)
                self.calDate1.Bind(wx.EVT_LEFT_DOWN, self.calendarDaySelect)
                ithDay = ithDay + 1
                if thisDate.weekday() == 5:
                    jthRow = jthRow + 1
            except:        
                ithDay = 1
                monthToDraw = monthToDraw + 1

    def calendarDaySelect(self, e=None):
        print str(self.calDate1)

    def clearDrawings(self):
        dc = wx.ClientDC(self)
        dc.Clear()

    def drawLine(self, x1, y1, x2, y2, strokeWidth,  lineColor):
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen(lineColor, strokeWidth))
        dc.DrawLine(x1, y1, x2, y2)

    def mouseAway(self, e):
        #WE WANT TO MAKE BACKGROUND TRANSPARENT ON MOUSE AWAY FROM WINDOW, BUT
        #NOT IF THE MOUSE AWAY IS ACTUALLY MOUSE OVER THE WINDOW'S OWN TEXT
        #if self.mouseOver == False:
        self.SetBackgroundColour(self.bgColorMouseAway)
        self.SetTransparent(self.leastOpaqueLevel)
        self.mouseOver = False
        #self.drawClocks(self.appClocks)
        self.updateAndDrawClocks()
            
    def mouseReturn(self, e):
        #self.SetBackgroundColour(self.bgColorMouseOver)
        self.SetTransparent(self.mostOpaqueLevel)
        self.mouseOver = True
        #self.drawClocks(self.appClocks)
        self.updateAndDrawClocks()

    def mouseMotion(self, e):
        #print str(wx.GetMousePosition())
        
        if e.LeftIsDown():
            self.Move(wx.Point(wx.GetMousePosition()[0] - self.lastMouseClickPos[0], wx.GetMousePosition()[1] - self.lastMouseClickPos[1]))
        e.Skip()
 
    def leftDown(self, e):
        self.lastMouseClickPos = e.GetPosition()
        e.Skip()

    def toggleTitleBar(self, e):
        if (self.displayTitleBar == True):
            self.style = wx.NO_BORDER
            self.displayTitleBar = False
            self.Show()
            
        elif (self.displayTitleBar == False):
            self.style = wx.SIMPLE_BORDER
            self.displayTitleBar = True
            self.Show()

    def closeWindow(self, e):
        self.changeAlpha_timer.Stop()
        del self.changeAlpha_timer       # avoid a memory leak
        self.Destroy()

    def updateAndDrawClocks(self, e = None):
        for i in self.appClocks:
            i.updateTime()
        self.drawClocks(self.appClocks)

    def drawClocks(self, displayClocks):
        #try:
        self.clearDrawings()
        
        for i in xrange(len(displayClocks)):
            for j in xrange(12):
                self.drawLine(
                int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX + (int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
                int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin) * math.sin((math.pi/180)*(((j+1)/float(12)))*360)))),
                int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin + displayClocks[i].clockTickLength) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
                int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin + displayClocks[i].clockTickLength) * math.sin((math.pi/180)*(((j+1)/float(12)))*360)))), displayClocks[i].tickThick, displayClocks[i].tickColor)

            #DRAW CLOCK HANDS
            #LINE(X1,
            #Y1,
            #X2,
            #Y2,
            #THICKNESS, COLOR)
            
            #DRAW HOUR HAND
            self.drawLine(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX ,
                          displayClocks[i].clockHeight + displayClocks[i].clockMargin,
                          int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round(displayClocks[i].hourLength * math.cos((math.pi/180)*((((displayClocks[i].hours-3)%float(12))/float(12))+(displayClocks[i].minutes/float(60)/12))*360))))),
                          int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round(displayClocks[i].hourLength * math.sin((math.pi/180)*((((displayClocks[i].hours-3)%float(12))/float(12))+(displayClocks[i].minutes/float(60)/12))*360)))),
                          displayClocks[i].hourThick, displayClocks[i].hourColor)
            
            #DRAW MINUTE HAND
            self.drawLine(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX ,
                          displayClocks[i].clockHeight + displayClocks[i].clockMargin,
                          int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round(displayClocks[i].minuteLength * math.cos((math.pi/180)*((displayClocks[i].minutes-15)/float(60))*360))))),
                          int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round(displayClocks[i].minuteLength * math.sin((math.pi/180)*((displayClocks[i].minutes-15)/float(60))*360)))),
                          displayClocks[i].minuteThick, displayClocks[i].minuteColor)

            #DRAW SECOND HAND
            self.drawLine(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX ,
                          displayClocks[i].clockHeight + displayClocks[i].clockMargin,
                          int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round(displayClocks[i].secondLength * math.cos((math.pi/180)*((displayClocks[i].seconds-15)/float(60))*360))))),
                          int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round(displayClocks[i].secondLength * math.sin((math.pi/180)*((displayClocks[i].seconds-15)/float(60))*360)))),
                          displayClocks[i].secondThick, displayClocks[i].secondColor)
class clocks(object):
    def __init__(self, tz, tzDesc):
        self.secondColor = (255, 0, 0)
        self.minuteColor = (255, 255, 255)
        self.hourColor = (255, 255, 255)
        self.tickColor = (255, 255, 255)
        self.secondThick = 2
        self.minuteThick = 4
        self.hourThick = 4
        self.tickThick = 2
        self.secondLength = 50
        self.minuteLength = 50
        self.hourLength = .5*self.minuteLength
        self.clockMargin = 15
        self.clockTickLength = 10
        self.clockTickInnerMargin = 8
        self.clockWidth = (self.minuteLength*2) + (self.clockTickLength*2) + (self.clockTickInnerMargin*2)
        self.clockHeight = self.clockWidth
        self.clockX = (self.minuteLength) + (self.clockTickLength) + (self.clockTickInnerMargin) + self.clockMargin
        self.clockY = self.clockHeight / float(4)
        self.tz = tz
        self.tzDesc = tzDesc
        self.tzTime = ""

    def updateTime(self):
        now_utc = datetime.datetime.now(timezone('UTC')) #Put the current time in UTC
        self.seconds = float(now_utc.astimezone(timezone(self.tz)).strftime("%S"))
        self.minutes = float(now_utc.astimezone(timezone(self.tz)).strftime("%M"))
        self.hours = float(now_utc.astimezone(timezone(self.tz)).strftime("%H"))

    
        
if __name__ == '__main__':
    app = wx.App()
    myFrame = Frame(None, 'Organizer', 1000, 800)
    app.MainLoop()
